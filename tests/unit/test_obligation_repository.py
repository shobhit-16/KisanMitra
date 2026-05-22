"""Unit tests for ObligationRepository — all CRUD operations with in-memory SQLite."""

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

from kisanmitra.models import ObligationCreate, Obligation, ObligationType
from kisanmitra.obligation_repository import (
    ObligationRepository,
    ObligationNotFoundError,
    compute_priority,
    due_in_days,
    ObligationPriority,
)


@pytest.fixture
async def repo(tmp_path: Path) -> ObligationRepository:
    """File-backed SQLite repo with schema loaded (file so repo can open it)."""
    db_path = str(tmp_path / "test_obligations.db")

    # Load schema before creating repo
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


async def _create_test_obligation(
    repo: ObligationRepository,
    phone: str = "9876543210",
    amount: int = 5000,
    due_days: int = 10,
    obligation_type: ObligationType = ObligationType.SCHOOL_FEE,
) -> Obligation:
    """Create a test obligation with due_date relative to today."""
    due_date = date.today() + timedelta(days=due_days)
    return await repo.create(
        ObligationCreate(
            id=f"ob-{phone}-{due_days}",
            phone=phone,
            type=obligation_type,
            amount=amount,
            due_date=due_date,
            description=f"Test obligation due in {due_days} days",
        )
    )


class TestComputePriority:
    """Tests for priority computation."""

    def test_critical_leq_3_days(self):
        today = date.today()
        assert compute_priority(today + timedelta(days=3), today) == ObligationPriority.CRITICAL
        assert compute_priority(today + timedelta(days=2), today) == ObligationPriority.CRITICAL
        assert compute_priority(today + timedelta(days=1), today) == ObligationPriority.CRITICAL

    def test_urgent_leq_7_days(self):
        today = date.today()
        assert compute_priority(today + timedelta(days=4), today) == ObligationPriority.URGENT
        assert compute_priority(today + timedelta(days=7), today) == ObligationPriority.URGENT

    def test_soon_leq_30_days(self):
        today = date.today()
        assert compute_priority(today + timedelta(days=8), today) == ObligationPriority.SOON
        assert compute_priority(today + timedelta(days=30), today) == ObligationPriority.SOON

    def test_normal_gt_30_days(self):
        today = date.today()
        assert compute_priority(today + timedelta(days=31), today) == ObligationPriority.NORMAL
        assert compute_priority(today + timedelta(days=60), today) == ObligationPriority.NORMAL

    def test_overdue_is_critical(self):
        today = date.today()
        assert compute_priority(today - timedelta(days=1), today) == ObligationPriority.CRITICAL


class TestDueInDays:
    """Tests for due_in_days calculation."""

    def test_future_date(self):
        today = date.today()
        future = today + timedelta(days=5)
        assert due_in_days(future, today) == 5

    def test_past_date(self):
        today = date.today()
        past = today - timedelta(days=3)
        assert due_in_days(past, today) == -3

    def test_today(self):
        today = date.today()
        assert due_in_days(today, today) == 0


class TestCreate:
    """POST /api/farmers/{phone}/obligations equivalent — create obligation."""

    async def test_create_success(self, repo: ObligationRepository):
        obligation = await _create_test_obligation(repo, due_days=10)
        assert obligation.phone == "9876543210"
        assert obligation.amount == 5000
        assert obligation.is_paid is False
        assert obligation.reminder_flag is False
        assert obligation.paid_date is None
        assert obligation.paid_amount is None

    async def test_create_with_reminder(self, repo: ObligationRepository):
        due_date = date.today() + timedelta(days=10)
        reminder_date = date.today() + timedelta(days=8)
        obligation = await repo.create(
            ObligationCreate(
                id="ob-with-reminder",
                phone="9876543210",
                type=ObligationType.KCC_EMI,
                amount=3200,
                due_date=due_date,
                reminder_date=reminder_date,
                reminder_flag=True,
                description="KCC EMI",
            )
        )
        assert obligation.reminder_flag is True
        assert obligation.reminder_date == reminder_date

    async def test_create_due_date_in_past_raises(self, repo: ObligationRepository):
        with pytest.raises(ValueError, match="due_date cannot be in the past"):
            await repo.create(
                ObligationCreate(
                    id="ob-past",
                    phone="9876543210",
                    type=ObligationType.LAND_RENT,
                    amount=2000,
                    due_date=date.today() - timedelta(days=1),
                )
            )

    async def test_create_reminder_after_due_date_raises(self, repo: ObligationRepository):
        due_date = date.today() + timedelta(days=10)
        reminder_date = date.today() + timedelta(days=15)
        with pytest.raises(ValueError, match="reminder_date must be <= due_date"):
            await repo.create(
                ObligationCreate(
                    id="ob-bad-reminder",
                    phone="9876543210",
                    type=ObligationType.LAND_RENT,
                    amount=2000,
                    due_date=due_date,
                    reminder_date=reminder_date,
                )
            )


class TestGetById:
    """GET /api/farmers/{phone}/obligations/{id} equivalent."""

    async def test_get_success(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo)
        ob = await repo.get_by_id(created.id, "9876543210")
        assert ob.id == created.id
        assert ob.amount == created.amount

    async def test_get_not_found_raises(self, repo: ObligationRepository):
        with pytest.raises(ObligationNotFoundError):
            await repo.get_by_id("nonexistent", "9876543210")

    async def test_get_wrong_phone_raises(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo)
        with pytest.raises(ObligationNotFoundError):
            await repo.get_by_id(created.id, "1111111111")


class TestListByPhone:
    """GET /api/farmers/{phone}/obligations equivalent — list all."""

    async def test_list_pending(self, repo: ObligationRepository):
        await _create_test_obligation(repo, due_days=5, amount=3000)
        await _create_test_obligation(repo, due_days=15, amount=7000)
        # Mark one as paid
        paid = await _create_test_obligation(repo, due_days=20, amount=1000)
        await repo.mark_paid(paid.id, "9876543210")

        pending = await repo.list_by_phone("9876543210", status="pending")
        assert len(pending) == 2
        assert all(not ob.is_paid for ob in pending)
        # Sorted by due_date
        assert pending[0].amount == 3000
        assert pending[1].amount == 7000

    async def test_list_paid(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo, due_days=30)
        await repo.mark_paid(created.id, "9876543210")

        paid = await repo.list_by_phone("9876543210", status="paid")
        assert len(paid) == 1
        assert paid[0].id == created.id
        assert paid[0].is_paid is True

    async def test_list_all(self, repo: ObligationRepository):
        ob1 = await _create_test_obligation(repo, due_days=5)
        ob2 = await _create_test_obligation(repo, due_days=15)
        await repo.mark_paid(ob1.id, "9876543210")

        all_obs = await repo.list_by_phone("9876543210", status="all")
        assert len(all_obs) == 2


class TestListUrgent:
    """GET /api/farmers/{phone}/obligations/urgent equivalent — due <= 7 days."""

    async def test_list_urgent_filters_correctly(self, repo: ObligationRepository):
        # Within 7 days
        await _create_test_obligation(repo, due_days=3, amount=5000)
        await _create_test_obligation(repo, due_days=7, amount=3000)
        # Outside 7 days
        await _create_test_obligation(repo, due_days=10, amount=2000)
        await _create_test_obligation(repo, due_days=30, amount=1000)

        urgent = await repo.list_urgent("9876543210")
        assert len(urgent) == 2
        assert all(due_in_days(ob.due_date) <= 7 for ob in urgent)


class TestUpdateReminder:
    """PUT /api/farmers/{phone}/obligations/{id}/reminder equivalent."""

    async def test_update_reminder_flag(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo)
        updated = await repo.update_reminder(created.id, "9876543210", reminder_flag=True)
        assert updated.reminder_flag is True

    async def test_update_reminder_flag_to_false(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo, due_days=5)
        await repo.update_reminder(created.id, "9876543210", reminder_flag=True)
        updated = await repo.update_reminder(created.id, "9876543210", reminder_flag=False)
        assert updated.reminder_flag is False

    async def test_update_reminder_date(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo, due_days=15)
        new_reminder = date.today() + timedelta(days=10)
        updated = await repo.update_reminder(
            created.id, "9876543210", reminder_flag=True, reminder_date=new_reminder
        )
        assert updated.reminder_date == new_reminder
        assert updated.reminder_flag is True

    async def test_update_reminder_not_found(self, repo: ObligationRepository):
        with pytest.raises(ObligationNotFoundError):
            await repo.update_reminder("nonexistent", "9876543210", reminder_flag=True)


class TestMarkPaid:
    """DELETE /api/farmers/{phone}/obligations/{id} equivalent — mark as paid."""

    async def test_mark_paid_no_amount(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo, amount=5000)
        updated = await repo.mark_paid(created.id, "9876543210")
        assert updated.is_paid is True
        assert updated.paid_date is not None
        assert updated.paid_amount == 5000  # Original amount

    async def test_mark_paid_with_amount(self, repo: ObligationRepository):
        created = await _create_test_obligation(repo, amount=5000)
        updated = await repo.mark_paid(created.id, "9876543210", paid_amount=4500)
        assert updated.is_paid is True
        assert updated.paid_amount == 4500  # Partial payment

    async def test_mark_paid_not_found(self, repo: ObligationRepository):
        with pytest.raises(ObligationNotFoundError):
            await repo.mark_paid("nonexistent", "9876543210")


class TestIdempotency:
    """Verify the CRUD contract holds across repeated operations."""

    async def test_create_get_update_reminder_mark_paid_flow(self, repo: ObligationRepository):
        # Create
        created = await _create_test_obligation(repo, due_days=10)
        assert created.is_paid is False

        # Get
        ob = await repo.get_by_id(created.id, "9876543210")
        assert ob.amount == created.amount

        # Update reminder
        updated = await repo.update_reminder(created.id, "9876543210", reminder_flag=True)
        assert updated.reminder_flag is True

        # Mark paid
        paid = await repo.mark_paid(created.id, "9876543210")
        assert paid.is_paid is True
        assert paid.paid_date is not None

        # List paid
        paid_list = await repo.list_by_phone("9876543210", status="paid")
        assert len(paid_list) == 1
        assert paid_list[0].id == created.id