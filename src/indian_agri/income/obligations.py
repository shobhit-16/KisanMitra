"""Module 1: Obligation Calendar — specs/09-constraint-priority-engine.md §5.1.

Captures season-based obligations: school fees (April, June, October), loan repayments,
social obligations. Drives cash_flow_status computation for Module 2.

ObligationCalendar is instantiated per-farmer and tracks upcoming obligations
and their cash flow impact.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ObligationType(str, Enum):
    SCHOOL_FEE = "school_fee"       # April, June, October terms
    LOAN_REPAYMENT = "loan_repayment"  # KCC, MAHADB, institutional
    SOCIAL_OBLIGATION = "social_obligation"  # weddings, festivals, ceremonies
    LAND_RENT = "land_rent"       # For tenant farmers
    INPUT_COST = "input_cost"      # Seeds, fertilizer ahead of sowing


class Season(str, Enum):
    KHARIF = "kharif"      # June–October (monsoon)
    RABI = "rabi"          # October–March (winter)
    ZAID = "zaid"          # March–June (summer)
    ANNUAL = "annual"       # Year-round obligations


class Obligation(BaseModel):
    """A single obligation with amount, due date, and type."""

    id: Optional[int] = None
    farmer_id: Optional[int] = None
    obligation_type: ObligationType
    description: str = Field(max_length=300)
    amount_rupees: float = Field(ge=0)
    due_date: date
    season: Optional[Season] = None
    is_recurring: bool = False
    recurring_months: Optional[list[int]] = None  # 1-12 for recurring obligations
    paid: bool = False
    paid_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_overdue(self, as_of: Optional[date] = None) -> bool:
        """Return True if this obligation is unpaid and past due_date."""
        if self.paid:
            return False
        check_date = as_of or date.today()
        return check_date > self.due_date

    def days_until_due(self, as_of: Optional[date] = None) -> int:
        """Days until due (negative if overdue)."""
        check_date = as_of or date.today()
        delta = self.due_date - check_date
        return delta.days


class ObligationCalendar:
    """Per-farmer obligation tracker for cash flow impact computation.

    This is a service class (not a Pydantic entity) that manages a farmer's
    obligations and computes their near-term cash flow impact.
    """

    def __init__(self, farmer_id: int, obligations: Optional[list[Obligation]] = None):
        self.farmer_id = farmer_id
        self._obligations: list[Obligation] = obligations or []

    # -------------------------------------------------------------------------
    # Obligation management
    # -------------------------------------------------------------------------

    def add_obligation(self, obligation: Obligation) -> None:
        """Add an obligation to the calendar."""
        obligation.farmer_id = self.farmer_id
        self._obligations.append(obligation)

    def get_obligation(self, obligation_id: int) -> Optional[Obligation]:
        """Get an obligation by ID."""
        for ob in self._obligations:
            if ob.id == obligation_id:
                return ob
        return None

    def list_obligations(
        self,
        include_paid: bool = False,
        upcoming_within_days: Optional[int] = None,
    ) -> list[Obligation]:
        """List obligations, optionally filtered.

        Args:
            include_paid: If False (default), exclude paid obligations.
            upcoming_within_days: If set, only return obligations due within N days.
        """
        results = []
        cutoff = None
        if upcoming_within_days is not None:
            cutoff = date.today()
            from datetime import timedelta
            cutoff = cutoff + timedelta(days=upcoming_within_days)

        for ob in self._obligations:
            if not include_paid and ob.paid:
                continue
            if cutoff is not None and ob.due_date > cutoff:
                continue
            results.append(ob)

        return results

    def mark_paid(self, obligation_id: int, paid_on: Optional[date] = None) -> bool:
        """Mark an obligation as paid. Returns True if found and updated."""
        for ob in self._obligations:
            if ob.id == obligation_id:
                ob.paid = True
                ob.paid_date = paid_on or date.today()
                ob.updated_at = datetime.utcnow()
                return True
        return False

    # -------------------------------------------------------------------------
    # Cash flow impact computation — used by Module 2 (CashFlowAssessment)
    # -------------------------------------------------------------------------

    def compute_cash_flow_impact(
        self,
        as_of: Optional[date] = None,
    ) -> dict:
        """Compute total outstanding obligations by urgency.

        Called by CashFlowAssessment.assess() to determine whether upcoming
        obligations contribute to a deficit/emergency cash flow status.

        Returns:
            dict with:
                total_outstanding_30d: float — total rupees due within 30 days
                total_outstanding_90d: float — total rupees due within 90 days
                overdue_amount: float — total overdue (past due, unpaid)
                obligation_count_30d: int
                has_urgent_obligation: bool — True if any obligation due within 7 days
        """
        check_date = as_of or date.today()
        from datetime import timedelta

        total_30d: float = 0.0
        total_90d: float = 0.0
        total_overdue: float = 0.0
        count_30d: int = 0
        has_urgent: bool = False

        cutoff_30d = check_date + timedelta(days=30)
        cutoff_90d = check_date + timedelta(days=90)

        for ob in self._obligations:
            if ob.paid:
                continue

            if ob.is_overdue(check_date):
                total_overdue += ob.amount_rupees
            elif ob.due_date <= cutoff_30d:
                total_30d += ob.amount_rupees
                count_30d += 1

            if ob.due_date <= cutoff_90d:
                total_90d += ob.amount_rupees

            # Urgent: due within 7 days
            cutoff_urgent = check_date + timedelta(days=7)
            if ob.due_date <= cutoff_urgent:
                has_urgent = True

        return {
            "total_outstanding_30d": total_30d,
            "total_outstanding_90d": total_90d,
            "overdue_amount": total_overdue,
            "obligation_count_30d": count_30d,
            "has_urgent_obligation": has_urgent,
        }

    # -------------------------------------------------------------------------
    # Season-based obligation helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def school_fee_months() -> list[int]:
        """India school fee payment months: April (term 1), June (term 2), October (term 3)."""
        return [4, 6, 10]

    @staticmethod
    def kharif_sowing_months() -> list[int]:
        """Kharif sowing period: June–July."""
        return [6, 7]

    @staticmethod
    def rabi_sowing_months() -> list[int]:
        """Rabi sowing period: October–November."""
        return [10, 11]

    @staticmethod
    def suggest_loan_repayment_schedule(
        principal_rupees: float,
        annual_rate_percent: float,
        tenure_months: int,
        start_month: int,
    ) -> list[Obligation]:
        """Suggest a monthly loan repayment schedule for a KCC/MAHADB loan.

        Generates Obligation records with approximate monthly EMI.
        Callers can adjust amounts based on actual loan statements.
        """
        if tenure_months <= 0 or principal_rupees <= 0:
            return []

        # Simple EMI approximation (not accounting for compound interest precisely)
        monthly_rate = annual_rate_percent / 100 / 12
        if monthly_rate > 0:
            emi = principal_rupees * monthly_rate * (1 + monthly_rate) ** tenure_months / \
                ((1 + monthly_rate) ** tenure_months - 1)
        else:
            emi = principal_rupees / tenure_months

        emi = round(emi, 2)
        obligations = []
        current_month = start_month

        for month_offset in range(tenure_months):
            due_month = ((current_month + month_offset - 1) % 12) + 1
            due_year = start_month + month_offset // 12
            # Default to 1st of month (can be overridden)
            due_date = date(due_year, due_month, 1)

            ob = Obligation(
                farmer_id=0,  # Will be set by add_obligation
                obligation_type=ObligationType.LOAN_REPAYMENT,
                description=f"EMI #{month_offset + 1} (₹{emi}/month)",
                amount_rupees=emi,
                due_date=due_date,
                season=Season.ANNUAL,
                is_recurring=False,
            )
            obligations.append(ob)

        return obligations
