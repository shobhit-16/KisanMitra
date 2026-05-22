"""Unit tests for FarmerRepository — all CRUD operations with in-memory SQLite."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

# Ensure src is on the path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from kisanmitra.models import FarmerCreate, Farmer, LandTenure, CropType, Season, Language
from kisanmitra.repository import (
    FarmerRepository,
    PhoneFormatError,
    LandSizeError,
    DuplicatePhoneError,
    FarmerNotFoundError,
)


@pytest.fixture
async def repo(tmp_path: Path) -> FarmerRepository:
    """File-backed SQLite repo with schema loaded (file so repo can open it)."""
    db_path = str(tmp_path / "test_farmers.db")

    # Load schema before creating repo (aiosqlite methods are async)
    import aiosqlite
    conn = await aiosqlite.connect(db_path)
    schema = Path(__file__).parent.parent.parent / "src" / "kisanmitra" / "db" / "schema.sql"
    await conn.executescript(schema.read_text())
    await conn.commit()
    await conn.close()

    repo = FarmerRepository(db_path)
    yield repo
    await repo.close()


async def _create_demo_farmer(repo: FarmerRepository) -> Farmer:
    """Create the demo Rambhau Gite farmer."""
    return await repo.create(
        FarmerCreate(
            phone="9876543210",
            name="Ram",
            village="Ozar",
            block="Niphad",
            district="NASHIK",
            state="MAHARASHTRA",
            land_size=2.0,
            land_tenure=LandTenure.OWNER,
            crop_type=CropType.RABI_ONION,
            season=Season.RABI,
            primary_language=Language.MARATHI,
        )
    )


class TestCreate:
    """POST /api/farmers equivalent — create farmer."""

    async def test_create_success(self, repo: FarmerRepository):
        farmer = await _create_demo_farmer(repo)
        assert farmer.phone == "9876543210"
        assert farmer.name == "Ram"
        assert farmer.district == "NASHIK"
        assert farmer.land_size == 2.0
        assert farmer.land_tenure == LandTenure.OWNER
        assert farmer.crop_type == CropType.RABI_ONION
        assert farmer.season == Season.RABI
        assert farmer.primary_language == Language.MARATHI
        assert farmer.is_active is True
        assert farmer.created_at is not None
        assert farmer.updated_at is not None

    async def test_create_duplicate_phone_raises_duplicate_error(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        with pytest.raises(DuplicatePhoneError):
            await repo.create(
                FarmerCreate(
                    phone="9876543210",
                    name="Someone Else",
                    village="Other",
                    block="Other",
                    district="NASHIK",
                    state="MAHARASHTRA",
                    land_size=1.0,
                    land_tenure=LandTenure.TENANT,
                    crop_type=CropType.RABI_WHEAT,
                    season=Season.RABI,
                    primary_language=Language.HINDI,
                )
            )

    async def test_create_phone_not_10_digits_raises_pydantic_validation(
        self, repo: FarmerRepository
    ):
        """Phone too short — Pydantic validates before repository."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            await repo.create(
                FarmerCreate(
                    phone="12345",  # too short
                    name="Bad Phone",
                    village="V",
                    block="B",
                    district="NASHIK",
                    state="MAHARASHTRA",
                    land_size=1.0,
                    land_tenure=LandTenure.OWNER,
                    crop_type=CropType.RABI_ONION,
                    season=Season.RABI,
                    primary_language=Language.MARATHI,
                )
            )

    async def test_create_phone_non_digits_raises_pydantic_validation(
        self, repo: FarmerRepository
    ):
        """Phone with letter — Pydantic validates before repository."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            await repo.create(
                FarmerCreate(
                    phone="987654321A",
                    name="Bad Phone",
                    village="V",
                    block="B",
                    district="NASHIK",
                    state="MAHARASHTRA",
                    land_size=1.0,
                    land_tenure=LandTenure.OWNER,
                    crop_type=CropType.RABI_ONION,
                    season=Season.RABI,
                    primary_language=Language.MARATHI,
                )
            )

    async def test_create_land_size_zero_raises_pydantic_validation(
        self, repo: FarmerRepository
    ):
        """land_size = 0 — Pydantic validates before repository."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            await repo.create(
                FarmerCreate(
                    phone="9876543210",
                    name="Zero Land",
                    village="V",
                    block="B",
                    district="NASHIK",
                    state="MAHARASHTRA",
                    land_size=0.0,
                    land_tenure=LandTenure.OWNER,
                    crop_type=CropType.RABI_ONION,
                    season=Season.RABI,
                    primary_language=Language.MARATHI,
                )
            )

    async def test_create_land_size_negative_raises_pydantic_validation(
        self, repo: FarmerRepository
    ):
        """land_size < 0 — Pydantic validates before repository."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            await repo.create(
                FarmerCreate(
                    phone="9876543210",
                    name="Negative Land",
                    village="V",
                    block="B",
                    district="NASHIK",
                    state="MAHARASHTRA",
                    land_size=-1.0,
                    land_tenure=LandTenure.OWNER,
                    crop_type=CropType.RABI_ONION,
                    season=Season.RABI,
                    primary_language=Language.MARATHI,
                )
            )


class TestGetByPhone:
    """GET /api/farmers/{phone} equivalent."""

    async def test_get_success(self, repo: FarmerRepository):
        created = await _create_demo_farmer(repo)
        farmer = await repo.get_by_phone("9876543210")
        assert farmer.phone == created.phone
        assert farmer.name == created.name

    async def test_get_not_found_raises(self, repo: FarmerRepository):
        with pytest.raises(FarmerNotFoundError):
            await repo.get_by_phone("1111111111")

    async def test_get_phone_not_10_digits_raises(self, repo: FarmerRepository):
        with pytest.raises(PhoneFormatError):
            await repo.get_by_phone("12345")


class TestUpdate:
    """PUT /api/farmers/{phone} equivalent."""

    async def test_update_name_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {"name": "Ram Gite Updated"})
        assert farmer.name == "Ram Gite Updated"
        # Other fields unchanged
        assert farmer.land_size == 2.0

    async def test_update_land_size_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {"land_size": 5.5})
        assert farmer.land_size == 5.5

    async def test_update_land_tenure_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {"land_tenure": LandTenure.TENANT})
        assert farmer.land_tenure == LandTenure.TENANT

    async def test_update_crop_type_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {"crop_type": CropType.KHARIF_PADDY})
        assert farmer.crop_type == CropType.KHARIF_PADDY

    async def test_update_season_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {"season": Season.KHARIF})
        assert farmer.season == Season.KHARIF

    async def test_update_primary_language_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {"primary_language": Language.HINDI})
        assert farmer.primary_language == Language.HINDI

    async def test_update_multiple_fields(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {
            "name": "New Name",
            "land_size": 3.5,
            "season": Season.SUMMER,
        })
        assert farmer.name == "New Name"
        assert farmer.land_size == 3.5
        assert farmer.season == Season.SUMMER

    async def test_update_non_updatable_field_ignored(self, repo: FarmerRepository):
        """phone, district, state, created_at are not updatable."""
        await _create_demo_farmer(repo)
        farmer = await repo.update("9876543210", {
            "name": "Updated",
            "phone": "9999999999",  # should be ignored
            "district": "PUNE",  # should be ignored
        })
        assert farmer.name == "Updated"
        assert farmer.phone == "9876543210"
        assert farmer.district == "NASHIK"

    async def test_update_not_found_raises(self, repo: FarmerRepository):
        with pytest.raises(FarmerNotFoundError):
            await repo.update("1111111111", {"name": "Ghost"})

    async def test_update_phone_not_10_digits_raises(self, repo: FarmerRepository):
        with pytest.raises(PhoneFormatError):
            await repo.update("12345", {"name": "Bad"})

    async def test_update_land_size_zero_raises(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        with pytest.raises(LandSizeError):
            await repo.update("9876543210", {"land_size": 0.0})

    async def test_update_land_size_negative_raises(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        with pytest.raises(LandSizeError):
            await repo.update("9876543210", {"land_size": -0.5})


class TestDelete:
    """DELETE /api/farmers/{phone} equivalent — soft delete."""

    async def test_delete_success(self, repo: FarmerRepository):
        await _create_demo_farmer(repo)
        await repo.delete("9876543210")
        # Farmer is no longer active — get should raise
        with pytest.raises(FarmerNotFoundError):
            await repo.get_by_phone("9876543210")

    async def test_delete_not_found_raises(self, repo: FarmerRepository):
        with pytest.raises(FarmerNotFoundError):
            await repo.delete("1111111111")

    async def test_delete_phone_not_10_digits_raises(self, repo: FarmerRepository):
        with pytest.raises(PhoneFormatError):
            await repo.delete("12345")


class TestIdempotency:
    """Verify the CRUD contract holds across repeated operations."""

    async def test_create_get_update_delete_get_flow(self, repo: FarmerRepository):
        # Create
        created = await _create_demo_farmer(repo)
        assert created.phone == "9876543210"

        # Get
        farmer = await repo.get_by_phone("9876543210")
        assert farmer.name == "Ram"

        # Update
        updated = await repo.update("9876543210", {
            "name": "Ram Gite",
            "land_size": 3.0,
        })
        assert updated.name == "Ram Gite"
        assert updated.land_size == 3.0

        # Delete
        await repo.delete("9876543210")

        # Get after delete
        with pytest.raises(FarmerNotFoundError):
            await repo.get_by_phone("9876543210")
