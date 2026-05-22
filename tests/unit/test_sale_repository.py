"""Unit tests for SaleRepository — sale CRUD, distress detection, baseline calculation."""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import date
import uuid

import pytest

# Ensure src is on the path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from kisanmitra.models import SaleCreate, Sale, FarmerCreate, LandTenure, CropType, Season, Language
from kisanmitra.repository import FarmerRepository
from kisanmitra.sale_repository import (
    SaleRepository,
    SaleNotFoundError,
    is_distress_sale,
    compute_distress_reason,
    compute_baseline_price,
    DISTRESS_THRESHOLD,
    MSP_ONION,
    DistressReason,
)


@pytest.fixture
async def sale_repo(tmp_path: Path) -> SaleRepository:
    """File-backed SQLite repo with schema loaded."""
    db_path = str(tmp_path / "test_sales.db")

    import aiosqlite
    conn = await aiosqlite.connect(db_path)
    schema = Path(__file__).parent.parent.parent / "src" / "kisanmitra" / "db" / "schema.sql"
    await conn.executescript(schema.read_text())
    await conn.commit()
    await conn.close()

    repo = SaleRepository(db_path)
    yield repo
    await repo.close()


@pytest.fixture
async def farmer_repo(tmp_path: Path) -> FarmerRepository:
    """File-backed SQLite repo with schema loaded."""
    db_path = str(tmp_path / "test_sales.db")

    import aiosqlite
    conn = await aiosqlite.connect(db_path)
    schema = Path(__file__).parent.parent.parent / "src" / "kisanmitra" / "db" / "schema.sql"
    await conn.executescript(schema.read_text())
    await conn.commit()
    await conn.close()

    repo = FarmerRepository(db_path)
    yield repo
    await repo.close()


async def _create_farmer(repo: FarmerRepository, phone: str = "9876543210") -> None:
    """Create a demo farmer."""
    await repo.create(
        FarmerCreate(
            phone=phone,
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


class TestDistressDetection:
    """Unit tests for distress detection logic."""

    def test_price_at_msp_is_not_distress(self):
        """Price exactly at MSP (750) is not distress."""
        assert is_distress_sale(750) is False

    def test_price_above_threshold_is_not_distress(self):
        """Price above 637.5 is not distress."""
        assert is_distress_sale(700) is False
        assert is_distress_sale(638) is False
        assert is_distress_sale(1000) is False

    def test_price_below_threshold_is_distress(self):
        """Price below 637.5 is distress."""
        assert is_distress_sale(637) is True
        assert is_distress_sale(500) is True
        assert is_distress_sale(0) is True

    def test_price_exactly_at_threshold_is_not_distress(self):
        """Price exactly at 637.5 is NOT distress (strict < comparison)."""
        assert is_distress_sale(637) is True
        assert is_distress_sale(638) is False
        # threshold = 637.5, so 637.5 itself is NOT distress (price < 637.5 is distress)


class TestDistressReasonAssignment:
    """Unit tests for distress reason auto-assignment."""

    def test_very_low_price_middleman_exploitation(self):
        """Price < MSP * 0.5 (375) → MIDDLEMAN_EXPLOITATION."""
        assert compute_distress_reason(300) == DistressReason.MIDDLEMAN_EXPLOITATION
        assert compute_distress_reason(374) == DistressReason.MIDDLEMAN_EXPLOITATION
        assert compute_distress_reason(0) == DistressReason.MIDDLEMAN_EXPLOITATION

    def test_moderately_low_price_weak_bargaining(self):
        """375 <= price < 637.5 → WEAK_BARGAINING."""
        assert compute_distress_reason(400) == DistressReason.WEAK_BARGAINING
        assert compute_distress_reason(500) == DistressReason.WEAK_BARGAINING
        assert compute_distress_reason(637) == DistressReason.WEAK_BARGAINING

    def test_boundary_at_half_msp(self):
        """Exactly MSP * 0.5 = 375 → WEAK_BARGAINING (strict < for middleman)."""
        assert compute_distress_reason(375) == DistressReason.WEAK_BARGAINING
        assert compute_distress_reason(376) == DistressReason.WEAK_BARGAINING


def _mk_sale(
    id: str,
    phone: str,
    sale_date: date,
    quantity_quintal: float,
    price_per_quintal: int,
    mandi: str,
    is_distress: bool,
    distress_reason: str | None = None,
    notes: str | None = None,
) -> Sale:
    """Factory to build a Sale for baseline testing without hitting DB."""
    from datetime import datetime
    return Sale(
        id=id,
        phone=phone,
        sale_date=sale_date,
        quantity_quintal=quantity_quintal,
        price_per_quintal=price_per_quintal,
        mandi=mandi,
        total_revenue=int(quantity_quintal * price_per_quintal),
        is_distress=is_distress,
        distress_reason=distress_reason,
        notes=notes,
        created_at=datetime(2026, 1, 1),
    )


class TestBaselinePriceCalculation:
    """Unit tests for weighted average baseline price calculation."""

    def test_no_sales_returns_none(self):
        assert compute_baseline_price([]) is None

    def test_all_distress_returns_none(self):
        """If all sales are distress, baseline is None."""
        sales = [
            _mk_sale("1", "1111111111", date(2026, 1, 1), 5, 500, "M",
                     is_distress=True, distress_reason=DistressReason.WEAK_BARGAINING),
        ]
        assert compute_baseline_price(sales) is None

    def test_single_non_distress_sale(self):
        """Single non-distress sale — baseline is its own price."""
        sales = [
            _mk_sale("1", "1111111111", date(2026, 1, 1), 5, 700, "M", is_distress=False),
        ]
        assert compute_baseline_price(sales) == 700.0

    def test_weighted_average_favors_larger_quantity(self):
        """
        Weighted average: 10q at ₹2800 and 5q at ₹3000
        → baseline should be (10*2800 + 5*3000) / 15 = (28000+15000)/15 = 2866.67
        NOT simple average of 2900.
        """
        sales = [
            _mk_sale("1", "1111111111", date(2026, 1, 1), 10, 2800, "M", is_distress=False),
            _mk_sale("2", "1111111112", date(2026, 1, 2), 5, 3000, "M", is_distress=False),
        ]
        baseline = compute_baseline_price(sales)
        # (10*2800 + 5*3000) / 15 = 43000 / 15 = 2866.67
        assert abs(baseline - 2866.67) < 0.01

    def test_mixed_distress_and_non_distress(self):
        """Distress sales are excluded from baseline calculation."""
        sales = [
            _mk_sale("1", "1111111111", date(2026, 1, 1), 5, 700, "M", is_distress=False),
            _mk_sale("2", "1111111112", date(2026, 1, 2), 4, 500, "M",
                     is_distress=True, distress_reason=DistressReason.WEAK_BARGAINING),
            _mk_sale("3", "1111111113", date(2026, 1, 3), 3, 800, "M", is_distress=False),
        ]
        # Baseline = (5*700 + 3*800) / (5+3) = (3500+2400) / 8 = 737.5
        assert compute_baseline_price(sales) == 737.5


class TestSaleRepositoryCreate:
    """POST /api/farmers/{phone}/sales equivalent — record a sale."""

    async def test_create_normal_sale_not_distress(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """Sale above 637.5 — is_distress=False, no distress_reason."""
        await _create_farmer(farmer_repo)
        data = SaleCreate(
            id=str(uuid.uuid4()),
            phone="9876543210",
            sale_date=date(2026, 2, 15),
            quantity_quintal=5.0,
            price_per_quintal=2800,
            mandi="Lasalgaon",
            notes="Good quality",
        )
        sale = await sale_repo.create(data)

        assert sale.is_distress is False
        assert sale.distress_reason is None
        assert sale.total_revenue == 5 * 2800  # 14000
        assert sale.mandi == "Lasalgaon"

    async def test_create_distress_sale_weak_bargaining(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """Sale 400-637.5 → is_distress=True, reason=WEAK_BARGAINING."""
        await _create_farmer(farmer_repo)
        data = SaleCreate(
            id=str(uuid.uuid4()),
            phone="9876543210",
            sale_date=date(2026, 2, 22),
            quantity_quintal=4.0,
            price_per_quintal=500,
            mandi="Village Trader",
        )
        sale = await sale_repo.create(data)

        assert sale.is_distress is True
        assert sale.distress_reason == DistressReason.WEAK_BARGAINING
        assert sale.total_revenue == 4 * 500  # 2000

    async def test_create_distress_sale_middleman_exploitation(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """Sale < 375 → is_distress=True, reason=MIDDLEMAN_EXPLOITATION."""
        await _create_farmer(farmer_repo)
        data = SaleCreate(
            id=str(uuid.uuid4()),
            phone="9876543210",
            sale_date=date(2026, 2, 20),
            quantity_quintal=2.0,
            price_per_quintal=300,
            mandi="Village Trader",
        )
        sale = await sale_repo.create(data)

        assert sale.is_distress is True
        assert sale.distress_reason == DistressReason.MIDDLEMAN_EXPLOITATION
        assert sale.total_revenue == 2 * 300  # 600

    async def test_create_sale_at_exact_threshold_not_distress(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """Price exactly at 637.5 (threshold) — is_distress=False (strict <)."""
        await _create_farmer(farmer_repo)
        data = SaleCreate(
            id=str(uuid.uuid4()),
            phone="9876543210",
            sale_date=date(2026, 2, 20),
            quantity_quintal=1.0,
            price_per_quintal=637,  # just below threshold
            mandi="Lasalgaon",
        )
        sale = await sale_repo.create(data)
        assert sale.is_distress is True  # 637 < 637.5

        data2 = SaleCreate(
            id=str(uuid.uuid4()),
            phone="9876543210",
            sale_date=date(2026, 2, 21),
            quantity_quintal=1.0,
            price_per_quintal=638,  # just above threshold
            mandi="Lasalgaon",
        )
        sale2 = await sale_repo.create(data2)
        assert sale2.is_distress is False  # 638 >= 637.5


class TestSaleRepositoryListByPhone:
    """List all sales for a farmer."""

    async def test_list_empty(self, sale_repo: SaleRepository, farmer_repo: FarmerRepository):
        """No sales yet — returns empty list."""
        await _create_farmer(farmer_repo)
        sales = await sale_repo.list_by_phone("9876543210")
        assert sales == []

    async def test_list_returns_all_sales_ordered_by_date(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """Sales returned in ascending sale_date order."""
        await _create_farmer(farmer_repo)
        await sale_repo.create(SaleCreate(
            id=str(uuid.uuid4()), phone="9876543210",
            sale_date=date(2026, 2, 20), quantity_quintal=5.0,
            price_per_quintal=2800, mandi="Lasalgaon",
        ))
        await sale_repo.create(SaleCreate(
            id=str(uuid.uuid4()), phone="9876543210",
            sale_date=date(2026, 2, 10), quantity_quintal=4.0,
            price_per_quintal=2700, mandi="Niphad",
        ))

        sales = await sale_repo.list_by_phone("9876543210")
        assert len(sales) == 2
        assert sales[0].sale_date == date(2026, 2, 10)
        assert sales[1].sale_date == date(2026, 2, 20)


class TestSaleRepositoryDelete:
    """Delete a sale by ID."""

    async def test_delete_success(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """Delete existing sale — get_by_id raises."""
        await _create_farmer(farmer_repo)
        sale_id = str(uuid.uuid4())
        await sale_repo.create(SaleCreate(
            id=sale_id, phone="9876543210",
            sale_date=date(2026, 2, 20), quantity_quintal=5.0,
            price_per_quintal=2800, mandi="Lasalgaon",
        ))

        await sale_repo.delete(sale_id)

        with pytest.raises(SaleNotFoundError):
            await sale_repo.get_by_id(sale_id)

    async def test_delete_not_found_raises(self, sale_repo: SaleRepository):
        with pytest.raises(SaleNotFoundError):
            await sale_repo.delete(str(uuid.uuid4()))


class TestEndToEnd:
    """Full flow: create farmer + multiple sales, verify ledger and baseline."""

    async def test_full_flow_distress_and_baseline(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """
        Demo data from spec:
        1. 5q at ₹2800 — normal (is_distress=False)
        2. 4q at ₹2700 — normal (is_distress=False)
        3. 3q at ₹2600 — normal (is_distress=False)
        4. 2q at ₹500  — DISTRESS, WEAK_BARGAINING

        Baseline = (5*2800 + 4*2700 + 3*2600) / (5+4+3)
                = (14000+10800+7800) / 12
                = 32600 / 12
                ≈ 2716.67
        """
        await _create_farmer(farmer_repo)
        phone = "9876543210"

        normal_sales = [
            (5, 2800, "Lasalgaon"),
            (4, 2700, "Niphad"),
            (3, 2600, "Yeola"),
        ]
        for qty, price, mandi in normal_sales:
            await sale_repo.create(SaleCreate(
                id=str(uuid.uuid4()), phone=phone,
                sale_date=date(2026, 2, 15), quantity_quintal=qty,
                price_per_quintal=price, mandi=mandi,
            ))

        # Distress sale
        await sale_repo.create(SaleCreate(
            id=str(uuid.uuid4()), phone=phone,
            sale_date=date(2026, 2, 22), quantity_quintal=2.0,
            price_per_quintal=500, mandi="Village Trader",
        ))

        sales = await sale_repo.list_by_phone(phone)
        assert len(sales) == 4
        distress_count = sum(1 for s in sales if s.is_distress)
        assert distress_count == 1

        baseline = compute_baseline_price(sales)
        expected_baseline = (5 * 2800 + 4 * 2700 + 3 * 2600) / (5 + 4 + 3)
        assert abs(baseline - expected_baseline) < 0.01

    async def test_all_distress_sales_baseline_is_none(
        self, sale_repo: SaleRepository, farmer_repo: FarmerRepository
    ):
        """All sales are below threshold → baseline = None."""
        await _create_farmer(farmer_repo)
        phone = "9876543210"

        for qty, price in [(5, 500), (3, 400), (2, 300)]:
            await sale_repo.create(SaleCreate(
                id=str(uuid.uuid4()), phone=phone,
                sale_date=date(2026, 2, 15), quantity_quintal=qty,
                price_per_quintal=price, mandi="Village Trader",
            ))

        sales = await sale_repo.list_by_phone(phone)
        assert all(s.is_distress for s in sales)
        assert compute_baseline_price(sales) is None
