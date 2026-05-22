"""Farmer repository — async CRUD operations using aiosqlite."""

from __future__ import annotations

import aiosqlite
import warnings
from datetime import datetime
from typing import Optional

from .models import FarmerCreate, Farmer, LandTenure, CropType, Season, Language


class PhoneFormatError(ValueError):
    """Phone number is not exactly 10 digits."""


class LandSizeError(ValueError):
    """Land size must be > 0."""


class DuplicatePhoneError(Exception):
    """A farmer with this phone already exists."""


class FarmerNotFoundError(Exception):
    """No farmer found with this phone number."""


class FarmerRepository:
    """Async repository for Farmer CRUD operations against SQLite."""

    UPDATABLE_FIELDS = frozenset([
        "name", "land_size", "land_tenure", "crop_type", "season", "primary_language"
    ])

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

    def _validate_phone(self, phone: str) -> str:
        """Validate phone is exactly 10 decimal digits. Returns normalised string."""
        if not (isinstance(phone, str) and phone.isdigit() and len(phone) == 10):
            raise PhoneFormatError("phone must be exactly 10 decimal digits")
        return phone

    def _validate_land_size(self, land_size: float) -> float:
        """Validate land_size > 0."""
        if not (isinstance(land_size, (int, float)) and land_size > 0):
            raise LandSizeError("land_size must be > 0")
        return float(land_size)

    @staticmethod
    def _row_to_farmer(row: aiosqlite.Row) -> Farmer:
        """Convert a sqlite Row to a Farmer model."""
        return Farmer(
            phone=row["phone"],
            name=row["name"],
            village=row["village"],
            block=row["block"],
            district=row["district"],
            state=row["state"],
            land_size=row["land_size"],
            land_tenure=LandTenure(row["land_tenure"]),
            crop_type=CropType(row["crop_type"]),
            season=Season(row["season"]),
            primary_language=Language(row["primary_language"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            is_active=bool(row["is_active"]),
        )

    async def create(self, data: FarmerCreate) -> Farmer:
        """
        Create a new farmer profile.

        Raises
        ------
        PhoneFormatError
            phone is not exactly 10 decimal digits.
        DuplicatePhoneError
            A farmer with this phone already exists.
        """
        phone = self._validate_phone(data.phone)
        land_size = self._validate_land_size(data.land_size)

        now = datetime.utcnow().isoformat()
        try:
            conn = await self._get_conn()
            await conn.execute(
                """
                INSERT INTO farmers
                    (phone, name, village, block, district, state,
                     land_size, land_tenure, crop_type, season,
                     primary_language, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    phone, data.name, data.village, data.block,
                    data.district, data.state, land_size,
                    data.land_tenure.value, data.crop_type.value,
                    data.season.value, data.primary_language.value,
                    now, now,
                ),
            )
            await conn.commit()
        except aiosqlite.IntegrityError as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise DuplicatePhoneError(f"Farmer with phone {phone} already exists") from exc
            raise

        return Farmer(
            phone=phone, name=data.name, village=data.village, block=data.block,
            district=data.district, state=data.state, land_size=land_size,
            land_tenure=data.land_tenure, crop_type=data.crop_type,
            season=data.season, primary_language=data.primary_language,
            created_at=datetime.fromisoformat(now), updated_at=datetime.fromisoformat(now),
            is_active=True,
        )

    async def get_by_phone(self, phone: str) -> Farmer:
        """
        Retrieve a farmer by phone number.

        Raises
        ------
        PhoneFormatError
            phone is not exactly 10 decimal digits.
        FarmerNotFoundError
            No active farmer with this phone.
        """
        phone = self._validate_phone(phone)
        conn = await self._get_conn()
        cursor = await conn.execute(
            "SELECT * FROM farmers WHERE phone = ? AND is_active = 1",
            (phone,),
        )
        row = await cursor.fetchone()
        if row is None:
            raise FarmerNotFoundError(f"No active farmer found with phone {phone}")
        return self._row_to_farmer(row)

    async def update(self, phone: str, fields: dict) -> Farmer:
        """
        Update updatable fields for a farmer.

        Only these fields are accepted: name, land_size, land_tenure,
        crop_type, season, primary_language.

        Raises
        ------
        PhoneFormatError
            phone is not exactly 10 decimal digits.
        FarmerNotFoundError
            No active farmer with this phone.
        ValueError
            A field name is not updatable.
        """
        phone = self._validate_phone(phone)

        # Filter to only updatable fields
        update_fields = {}
        for key in self.UPDATABLE_FIELDS:
            if key in fields:
                update_fields[key] = fields[key]

        if not update_fields:
            # No-op update — return current farmer
            return await self.get_by_phone(phone)

        # Validate land_size if provided
        if "land_size" in update_fields:
            update_fields["land_size"] = self._validate_land_size(update_fields["land_size"])

        now = datetime.utcnow().isoformat()
        set_clauses = [f"{k} = ?" for k in update_fields]
        set_clauses.append("updated_at = ?")
        values = list(update_fields.values())
        values.append(now)
        values.append(phone)

        conn = await self._get_conn()
        cursor = await conn.execute(
            f"UPDATE farmers SET {', '.join(set_clauses)} "
            "WHERE phone = ? AND is_active = 1",
            values,
        )
        await conn.commit()

        if cursor.rowcount == 0:
            raise FarmerNotFoundError(f"No active farmer found with phone {phone}")

        return await self.get_by_phone(phone)

    async def delete(self, phone: str) -> None:
        """
        Soft-delete a farmer (sets is_active = 0).

        Raises
        ------
        PhoneFormatError
            phone is not exactly 10 decimal digits.
        FarmerNotFoundError
            No active farmer with this phone.
        """
        phone = self._validate_phone(phone)
        conn = await self._get_conn()
        now = datetime.utcnow().isoformat()
        cursor = await conn.execute(
            "UPDATE farmers SET is_active = 0, updated_at = ? "
            "WHERE phone = ? AND is_active = 1",
            (now, phone),
        )
        await conn.commit()
        if cursor.rowcount == 0:
            raise FarmerNotFoundError(f"No active farmer found with phone {phone}")

    def __del__(self, _warnings=warnings):
        if self._pool is not None:
            _warnings.warn(
                f"{type(self).__name__} not closed; call await repo.close()",
                ResourceWarning,
                stacklevel=2,
            )
