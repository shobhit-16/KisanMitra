"""Obligation repository — async CRUD operations using aiosqlite."""

from __future__ import annotations

import enum
import warnings
from datetime import date, datetime
from typing import Optional

import aiosqlite

from .models import ObligationCreate, Obligation, ObligationType


class ObligationNotFoundError(Exception):
    """No obligation found with this ID for this phone."""


class ObligationPriority(str, enum.Enum):
    CRITICAL = "CRITICAL"  # <= 3 days
    URGENT = "URGENT"      # <= 7 days
    SOON = "SOON"          # <= 30 days
    NORMAL = "NORMAL"     # > 30 days


def compute_priority(due_date: date, from_date: date | None = None) -> ObligationPriority:
    """Compute priority based on days until due_date from from_date (default: today)."""
    if from_date is None:
        from_date = date.today()
    days_until = (due_date - from_date).days
    if days_until <= 3:
        return ObligationPriority.CRITICAL
    if days_until <= 7:
        return ObligationPriority.URGENT
    if days_until <= 30:
        return ObligationPriority.SOON
    return ObligationPriority.NORMAL


def due_in_days(due_date: date, from_date: date | None = None) -> int:
    """Return number of days until due_date (negative if overdue)."""
    if from_date is None:
        from_date = date.today()
    return (due_date - from_date).days


class ObligationRepository:
    """Async repository for Obligation CRUD operations against SQLite."""

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
    def _row_to_obligation(row: aiosqlite.Row) -> Obligation:
        """Convert a sqlite Row to an Obligation model."""
        return Obligation(
            id=row["id"],
            phone=row["phone"],
            type=ObligationType(row["type"]),
            amount=row["amount"],
            due_date=date.fromisoformat(row["due_date"]),
            description=row["description"],
            reminder_date=date.fromisoformat(row["reminder_date"]) if row["reminder_date"] else None,
            reminder_flag=bool(row["reminder_flag"]),
            is_paid=bool(row["is_paid"]),
            paid_date=date.fromisoformat(row["paid_date"]) if row["paid_date"] else None,
            paid_amount=row["paid_amount"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    async def create(self, data: ObligationCreate) -> Obligation:
        """
        Create a new obligation for a farmer.

        Raises
        ------
        ValueError
            due_date is in the past.
        """
        now = datetime.utcnow()
        today = now.date()

        # Constraint: due_date must be >= today
        if data.due_date < today:
            raise ValueError("due_date cannot be in the past")

        # Constraint: reminder_date must be <= due_date
        if data.reminder_date is not None and data.reminder_date > data.due_date:
            raise ValueError("reminder_date must be <= due_date")

        conn = await self._get_conn()
        now_iso = now.isoformat()
        await conn.execute(
            """
            INSERT INTO obligations
                (id, phone, type, amount, due_date, description, reminder_date,
                 reminder_flag, is_paid, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                data.id,
                data.phone,
                data.type.value,
                data.amount,
                data.due_date.isoformat(),
                data.description,
                data.reminder_date.isoformat() if data.reminder_date else None,
                1 if data.reminder_flag else 0,
                now_iso,
                now_iso,
            ),
        )
        await conn.commit()

        return Obligation(
            id=data.id,
            phone=data.phone,
            type=data.type,
            amount=data.amount,
            due_date=data.due_date,
            description=data.description,
            reminder_date=data.reminder_date,
            reminder_flag=data.reminder_flag,
            is_paid=False,
            paid_date=None,
            paid_amount=None,
            created_at=now,
            updated_at=now,
        )

    async def get_by_id(self, obligation_id: str, phone: str) -> Obligation:
        """
        Retrieve an obligation by ID and phone.

        Raises
        ------
        ObligationNotFoundError
            No obligation with this ID for this phone.
        """
        conn = await self._get_conn()
        cursor = await conn.execute(
            "SELECT * FROM obligations WHERE id = ? AND phone = ?",
            (obligation_id, phone),
        )
        row = await cursor.fetchone()
        if row is None:
            raise ObligationNotFoundError(
                f"No obligation found with id {obligation_id} for phone {phone}"
            )
        return self._row_to_obligation(row)

    async def list_by_phone(
        self,
        phone: str,
        status: str = "pending",
    ) -> list[Obligation]:
        """
        List all obligations for a farmer.

        Parameters
        ----------
        phone: 10-digit phone number
        status: "pending" (default), "paid", or "all"
        """
        conn = await self._get_conn()
        if status == "pending":
            cursor = await conn.execute(
                "SELECT * FROM obligations WHERE phone = ? AND is_paid = 0 ORDER BY due_date ASC",
                (phone,),
            )
        elif status == "paid":
            cursor = await conn.execute(
                "SELECT * FROM obligations WHERE phone = ? AND is_paid = 1 ORDER BY paid_date DESC",
                (phone,),
            )
        else:  # all
            cursor = await conn.execute(
                "SELECT * FROM obligations WHERE phone = ? ORDER BY due_date ASC",
                (phone,),
            )
        rows = await cursor.fetchall()
        return [self._row_to_obligation(row) for row in rows]

    async def list_urgent(self, phone: str) -> list[Obligation]:
        """
        List obligations due within 7 days for a farmer.
        """
        today = date.today()
        future = today.replace(day=today.day + 7) if today.day + 7 <= 28 else today
        # Use a simpler approach: get all pending, filter in Python
        pending = await self.list_by_phone(phone, status="pending")
        return [
            ob for ob in pending
            if due_in_days(ob.due_date, today) <= 7
        ]

    async def update_reminder(
        self,
        obligation_id: str,
        phone: str,
        reminder_flag: bool,
        reminder_date: date | None = None,
    ) -> Obligation:
        """
        Update reminder flag and optionally reminder_date for an obligation.

        Raises
        ------
        ObligationNotFoundError
            No obligation with this ID for this phone.
        ValueError
            reminder_date > due_date.
        """
        obligation = await self.get_by_id(obligation_id, phone)

        if reminder_date is not None and reminder_date > obligation.due_date:
            raise ValueError("reminder_date must be <= due_date")

        now = datetime.utcnow().isoformat()
        conn = await self._get_conn()
        await conn.execute(
            "UPDATE obligations SET reminder_flag = ?, reminder_date = ?, updated_at = ? "
            "WHERE id = ? AND phone = ?",
            (
                1 if reminder_flag else 0,
                reminder_date.isoformat() if reminder_date else obligation.reminder_date.isoformat() if obligation.reminder_date else None,
                now,
                obligation_id,
                phone,
            ),
        )
        await conn.commit()
        return await self.get_by_id(obligation_id, phone)

    async def mark_paid(
        self,
        obligation_id: str,
        phone: str,
        paid_amount: int | None = None,
    ) -> Obligation:
        """
        Mark an obligation as paid (soft delete).

        Sets is_paid=True, paid_date=today, paid_amount if provided.

        Raises
        ------
        ObligationNotFoundError
            No obligation with this ID for this phone.
        """
        await self.get_by_id(obligation_id, phone)  # Verify exists

        today = date.today()
        now = datetime.utcnow().isoformat()
        conn = await self._get_conn()

        if paid_amount is not None:
            await conn.execute(
                "UPDATE obligations SET is_paid = 1, paid_date = ?, paid_amount = ?, updated_at = ? "
                "WHERE id = ? AND phone = ?",
                (today.isoformat(), paid_amount, now, obligation_id, phone),
            )
        else:
            # Use the original amount as paid_amount
            await conn.execute(
                "UPDATE obligations SET is_paid = 1, paid_date = ?, paid_amount = amount, updated_at = ? "
                "WHERE id = ? AND phone = ?",
                (today.isoformat(), now, obligation_id, phone),
            )
        await conn.commit()
        return await self.get_by_id(obligation_id, phone)

    def __del__(self, _warnings=warnings):
        if self._pool is not None:
            _warnings.warn(
                f"{type(self).__name__} not closed; call await repo.close()",
                ResourceWarning,
                stacklevel=2,
            )