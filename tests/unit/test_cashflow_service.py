"""Unit tests for CashFlowService — cash flow computation."""

from __future__ import annotations

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Ensure src is on the path
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from kisanmitra.models import ObligationCreate, ObligationType
from kisanmitra.obligation_repository import ObligationRepository
from kisanmitra.cashflow_service import (
    CashFlowService,
    CashFlowStatus,
    compute_cash_flow_status,
    status_detail,
)


@pytest.fixture
async def repo(tmp_path: Path) -> ObligationRepository:
    """File-backed SQLite repo with schema loaded."""
    db_path = str(tmp_path / "test_cashflow.db")

    import aiosqlite
    conn = await aiosqlite.connect(db_path)
    schema = Path(__file__).parent.parent.parent / "src" / "kisanmitra" / "db" / "schema.sql"
    await conn.executescript(schema.read_text())
    # Create a test farmer (required for FK constraint on obligations)
    await conn.execute(
        """
        INSERT INTO farmers
            (phone, name, village, block, district, state,
             land_size, land_tenure, crop_type, season,
             primary_language, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            "9876543210", "Test Farmer", "Test Village", "Test Block",
            "NASHIK", "MAHARASHTRA", 2.0, "OWNER", "RABI_ONION", "RABI",
            "MARATHI",
        ),
    )
    await conn.commit()
    await conn.close()

    repo = ObligationRepository(db_path)
    yield repo
    await repo.close()


@pytest.fixture
def cashflow_service(repo: ObligationRepository) -> CashFlowService:
    return CashFlowService(repo)


async def _create_obligation(
    repo: ObligationRepository,
    phone: str,
    amount: int,
    due_days: int,
    obligation_type: ObligationType = ObligationType.OTHER,
) -> None:
    """Helper to create an obligation."""
    due_date = date.today() + timedelta(days=due_days)
    await repo.create(
        ObligationCreate(
            id=f"ob-{phone}-{due_days}-{obligation_type.value}",
            phone=phone,
            type=obligation_type,
            amount=amount,
            due_date=due_date,
        )
    )


class TestComputeCashFlowStatus:
    """Tests for cash flow status computation."""

    def test_deficit_when_surplus_negative(self):
        assert compute_cash_flow_status(-1000, 0) == CashFlowStatus.DEFICIT
        assert compute_cash_flow_status(-1000, 2) == CashFlowStatus.DEFICIT

    def test_tight_when_surplus_lt_5000_with_critical(self):
        assert compute_cash_flow_status(0, 1) == CashFlowStatus.TIGHT
        assert compute_cash_flow_status(4999, 1) == CashFlowStatus.TIGHT

    def test_tight_when_critical_and_surplus_lt_5000(self):
        assert compute_cash_flow_status(3000, 1) == CashFlowStatus.TIGHT

    def test_balanced_when_surplus_5000_to_10000_no_critical(self):
        assert compute_cash_flow_status(5000, 0) == CashFlowStatus.BALANCED
        assert compute_cash_flow_status(8000, 0) == CashFlowStatus.BALANCED
        assert compute_cash_flow_status(10000, 0) == CashFlowStatus.BALANCED

    def test_healthy_when_surplus_gt_10000_no_critical(self):
        assert compute_cash_flow_status(10001, 0) == CashFlowStatus.HEALTHY
        assert compute_cash_flow_status(50000, 0) == CashFlowStatus.HEALTHY


class TestStatusDetail:
    """Tests for status detail messages."""

    def test_deficit_detail(self):
        detail = status_detail(CashFlowStatus.DEFICIT, -5000, 0)
        assert "deficit" in detail.lower()
        assert "5000" in detail

    def test_tight_detail(self):
        detail = status_detail(CashFlowStatus.TIGHT, 3000, 1)
        assert "tight" in detail.lower()
        assert "3000" in detail

    def test_balanced_detail(self):
        detail = status_detail(CashFlowStatus.BALANCED, 8000, 0)
        assert "balanced" in detail.lower()
        assert "8000" in detail

    def test_healthy_detail(self):
        detail = status_detail(CashFlowStatus.HEALTHY, 15000, 0)
        assert "healthy" in detail.lower()
        assert "15000" in detail


class TestCashFlowCompute:
    """Tests for CashFlowService.compute()."""

    async def test_empty_obligations(self, cashflow_service: CashFlowService):
        result = await cashflow_service.compute("9876543210", window_days=30)
        assert result["phone"] == "9876543210"
        assert result["window_days"] == 30
        assert result["income"]["total_income"] == 0
        assert result["obligations"]["total_due"] == 0
        assert result["cash_flow"]["surplus"] == 0
        assert result["cash_flow"]["status"] == CashFlowStatus.BALANCED

    async def test_single_obligation_in_window(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        await _create_obligation(repo, "9876543210", amount=5000, due_days=10)
        result = await cashflow_service.compute("9876543210", window_days=30)
        assert result["obligations"]["total_due"] == 5000
        assert result["cash_flow"]["surplus"] == -5000
        assert result["cash_flow"]["status"] == CashFlowStatus.DEFICIT

    async def test_obligation_outside_window_not_counted(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        # 45 days out — outside 30-day window
        await _create_obligation(repo, "9876543210", amount=10000, due_days=45)
        result = await cashflow_service.compute("9876543210", window_days=30)
        assert result["obligations"]["total_due"] == 0
        assert result["cash_flow"]["surplus"] == 0

    async def test_multiple_obligations_by_type(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        await _create_obligation(repo, "9876543210", amount=3200, due_days=12, obligation_type=ObligationType.KCC_EMI)
        await _create_obligation(repo, "9876543210", amount=5000, due_days=4, obligation_type=ObligationType.SCHOOL_FEE)
        await _create_obligation(repo, "9876543210", amount=2000, due_days=25, obligation_type=ObligationType.LAND_RENT)

        result = await cashflow_service.compute("9876543210", window_days=30)

        assert result["obligations"]["total_due"] == 10200
        assert result["obligations"]["count_urgent"] == 1  # SCHOOL_FEE due in 4 days
        assert "KCC_EMI" in result["obligations"]["by_type"]
        assert "SCHOOL_FEE" in result["obligations"]["by_type"]
        assert "LAND_RENT" in result["obligations"]["by_type"]

    async def test_income_included(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        await _create_obligation(repo, "9876543210", amount=5000, due_days=10)
        result = await cashflow_service.compute(
            "9876543210",
            window_days=30,
            expected_sale_revenue=14000,
            other_income=2000,
        )
        assert result["income"]["expected_sale_revenue"] == 14000
        assert result["income"]["other_income"] == 2000
        assert result["income"]["total_income"] == 16000
        assert result["cash_flow"]["surplus"] == 11000  # 16000 - 5000

    async def test_critical_count_for_tight_status(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        # Critical: due in 2 days
        await _create_obligation(repo, "9876543210", amount=3000, due_days=2)
        result = await cashflow_service.compute(
            "9876543210",
            window_days=30,
            expected_sale_revenue=5000,
        )
        # Surplus = 5000 - 3000 = 2000, but has critical obligation
        assert result["cash_flow"]["status"] == CashFlowStatus.TIGHT
        assert result["cash_flow"]["surplus_after_critical"] == 2000

    async def test_window_days_max_90(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        result = await cashflow_service.compute("9876543210", window_days=200)
        assert result["window_days"] == 90

    async def test_window_days_clamped_to_1(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        await _create_obligation(repo, "9876543210", amount=5000, due_days=10)
        result = await cashflow_service.compute("9876543210", window_days=0)
        assert result["window_days"] == 1

    async def test_healthy_status(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        await _create_obligation(repo, "9876543210", amount=2000, due_days=30)
        result = await cashflow_service.compute(
            "9876543210",
            window_days=30,
            expected_sale_revenue=14000,
            other_income=2000,
        )
        # Total income = 16000, obligations = 2000, surplus = 14000
        assert result["cash_flow"]["surplus"] == 14000
        assert result["cash_flow"]["status"] == CashFlowStatus.HEALTHY

    async def test_by_type_has_priority_and_due_in_days(
        self, repo: ObligationRepository, cashflow_service: CashFlowService
    ):
        await _create_obligation(repo, "9876543210", amount=3200, due_days=12, obligation_type=ObligationType.KCC_EMI)
        result = await cashflow_service.compute("9876543210", window_days=30)
        kcc = result["obligations"]["by_type"]["KCC_EMI"]
        assert "priority" in kcc
        assert "due_in_days" in kcc
        assert kcc["priority"] in ("URGENT", "SOON", "NORMAL", "CRITICAL")