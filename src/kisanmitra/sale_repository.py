"""Sale repository — async CRUD operations using aiosqlite."""

from __future__ import annotations

import aiosqlite
import warnings
from datetime import datetime, date
from typing import Optional

from .models import SaleCreate, Sale, SaleCreate


# MSP constants for onion (Rabi 2024-25)
MSP_ONION = 750  # ₹/quintal
DISTRESS_THRESHOLD = MSP_ONION * 0.85  # = 637.5


class DistressReason:
    """Distress reason values — matches spec enum."""

    FORCED_SELL = "FORCED_SELL"
    NO_STORAGE = "NO_STORAGE"
    WEAK_BARGAINING = "WEAK_BARGAINING"
    MIDDLEMAN_EXPLOITATION = "MIDDLEMAN_EXPLOITATION"


def is_distress_sale(price_per_quintal: int) -> bool:
    """Return True if the sale price is below the distress threshold."""
    return price_per_quintal < DISTRESS_THRESHOLD


def compute_distress_reason(price_per_quintal: int) -> str:
    """
    Auto-assign distress reason based on price.

    - < MSP * 0.5 (375)  → MIDDLEMAN_EXPLOITATION
    - otherwise            → WEAK_BARGAINING
    """
    if price_per_quintal < MSP_ONION * 0.5:
        return DistressReason.MIDDLEMAN_EXPLOITATION
    return DistressReason.WEAK_BARGAINING


def compute_baseline_price(sales: list[Sale]) -> Optional[float]:
    """
    Compute weighted average price of non-distress sales.

    Returns None if all sales are distress sales.
    """
    non_distress = [s for s in sales if not s.is_distress]
    if not non_distress:
        return None

    total_revenue = sum(s.quantity_quintal * s.price_per_quintal for s in non_distress)
    total_quantity = sum(s.quantity_quintal for s in non_distress)

    if total_quantity == 0:
        return None
    return total_revenue / total_quantity


class SaleNotFoundError(Exception):
    """No sale found with this ID."""


class SaleRepository:
    """Async repository for Sale CRUD operations against SQLite."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._pool: Optional[aiosqlite.Connection] = None

    async def _get_conn(self) -> aiosqlite.Connection:
        """Get or create a shared connection with WAL + busy_timeout PRAGMAs."""
        if self._pool is None:
            conn = await aiosqlite.connect(self._db_path, timeout=30.0)
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA busy_timeout=30000")
            await conn.execute("PRAGMA foreign_keys=ON")
            self._pool = conn
        return self._pool

    async def close(self) -> None:
        """Close the shared connection."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @staticmethod
    def _row_to_sale(row: aiosqlite.Row) -> Sale:
        """Convert a sqlite Row to a Sale model."""
        return Sale(
            id=row["id"],
            phone=row["phone"],
            sale_date=date.fromisoformat(row["sale_date"]),
            quantity_quintal=row["quantity_quintal"],
            price_per_quintal=row["price_per_quintal"],
            mandi=row["mandi"],
            total_revenue=row["total_revenue"],
            is_distress=bool(row["is_distress"]) if row["is_distress"] is not None else None,
            distress_reason=row["distress_reason"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    async def create(self, data: SaleCreate) -> Sale:
        """
        Create a new sale record.

        is_distress and distress_reason are computed server-side.
        total_revenue is computed from quantity and price.
        """
        price = data.price_per_quintal
        qty = data.quantity_quintal
        total_revenue = int(qty * price)
        is_distress = is_distress_sale(price)
        distress_reason = compute_distress_reason(price) if is_distress else None

        now = datetime.utcnow().isoformat()
        conn = await self._get_conn()
        # total_revenue is a SQLite GENERATED ALWAYS AS column — omit from INSERT
        await conn.execute(
            """
            INSERT INTO sales
                (id, phone, sale_date, quantity_quintal, price_per_quintal,
                 mandi, is_distress, distress_reason, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.id,
                data.phone,
                data.sale_date.isoformat(),
                qty,
                price,
                data.mandi,
                int(is_distress) if is_distress is not None else None,
                distress_reason,
                data.notes,
                now,
            ),
        )
        await conn.commit()

        # Read back the generated total_revenue
        cursor = await conn.execute(
            "SELECT total_revenue FROM sales WHERE id = ?",
            (data.id,),
        )
        row = await cursor.fetchone()
        db_total_revenue = row["total_revenue"]

        return Sale(
            id=data.id,
            phone=data.phone,
            sale_date=data.sale_date,
            quantity_quintal=qty,
            price_per_quintal=price,
            mandi=data.mandi,
            total_revenue=db_total_revenue,
            is_distress=is_distress,
            distress_reason=distress_reason,
            notes=data.notes,
            created_at=datetime.fromisoformat(now),
        )

    async def get_by_id(self, sale_id: str) -> Sale:
        """Retrieve a sale by its UUID."""
        conn = await self._get_conn()
        cursor = await conn.execute(
            "SELECT * FROM sales WHERE id = ?",
            (sale_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            raise SaleNotFoundError(f"No sale found with id {sale_id}")
        return self._row_to_sale(row)

    async def list_by_phone(self, phone: str) -> list[Sale]:
        """List all sales for a given farmer phone, ordered by sale_date."""
        conn = await self._get_conn()
        cursor = await conn.execute(
            "SELECT * FROM sales WHERE phone = ? ORDER BY sale_date ASC",
            (phone,),
        )
        rows = await cursor.fetchall()
        return [self._row_to_sale(row) for row in rows]

    async def delete(self, sale_id: str) -> None:
        """Delete a sale by ID."""
        conn = await self._get_conn()
        cursor = await conn.execute(
            "DELETE FROM sales WHERE id = ?",
            (sale_id,),
        )
        await conn.commit()
        if cursor.rowcount == 0:
            raise SaleNotFoundError(f"No sale found with id {sale_id}")

    def __del__(self, _warnings=warnings):
        if self._pool is not None:
            _warnings.warn(
                f"{type(self).__name__} not closed; call await repo.close()",
                ResourceWarning,
                stacklevel=2,
            )
