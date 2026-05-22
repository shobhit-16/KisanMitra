"""Cash flow service — computes farmer financial health from obligations."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from .obligation_repository import ObligationRepository, ObligationPriority, due_in_days, compute_priority


class CashFlowStatus:
    DEFICIT = "DEFICIT"
    TIGHT = "TIGHT"
    BALANCED = "BALANCED"
    HEALTHY = "HEALTHY"


def compute_cash_flow_status(surplus: int, critical_count: int) -> str:
    """
    Compute cash flow status based on surplus and critical obligation count.

    Rules per spec:
    - DEFICIT: surplus < 0 (any critical count)
    - TIGHT: 0 <= surplus <= 5000 AND critical_count > 0
    - BALANCED: 5000 < surplus <= 10000 AND critical_count == 0
    - HEALTHY: surplus > 10000 AND critical_count == 0
    """
    if surplus < 0:
        return CashFlowStatus.DEFICIT
    if critical_count > 0 and surplus < 5000:
        return CashFlowStatus.TIGHT
    if surplus > 10000:
        return CashFlowStatus.HEALTHY
    return CashFlowStatus.BALANCED


def status_detail(status: str, surplus: int, critical_count: int) -> str:
    """Return human-readable detail for a cash flow status."""
    if status == CashFlowStatus.DEFICIT:
        return f"Cash flow deficit — ₹{abs(surplus)} shortfall"
    if status == CashFlowStatus.TIGHT:
        return f"Cash flow tight — ₹{surplus} after critical obligations"
    if status == CashFlowStatus.BALANCED:
        return f"Cash flow balanced — ₹{surplus} surplus"
    return f"Cash flow healthy — ₹{surplus} surplus"


class CashFlowService:
    """Computes cash flow health for a farmer over a configurable window."""

    # Default expected income sources (can be overridden)
    DEFAULT_EXPECTED_SALE_REVENUE = 0
    DEFAULT_OTHER_INCOME = 0

    def __init__(self, obligation_repo: ObligationRepository):
        self._repo = obligation_repo

    async def compute(
        self,
        phone: str,
        window_days: int = 30,
        expected_sale_revenue: int | None = None,
        other_income: int | None = None,
    ) -> dict:
        """
        Compute cash flow for a farmer over the next N days.

        Parameters
        ----------
        phone: 10-digit farmer phone
        window_days: number of days to analyze (default 30, max 90)
        expected_sale_revenue: expected from crop sales (default 0)
        other_income: other income sources (default 0)

        Returns
        -------
        dict with income, obligations breakdown, surplus, and status
        """
        window_days = max(1, min(window_days, 90))
        today = date.today()
        end_date = today + timedelta(days=window_days)

        # Fetch all pending obligations
        pending = await self._repo.list_by_phone(phone, status="pending")

        # Filter to those within window
        window_obligations = [
            ob for ob in pending
            if today <= ob.due_date <= end_date
        ]

        # Calculate totals by type
        total_due = sum(ob.amount for ob in window_obligations)
        count_urgent = sum(
            1 for ob in window_obligations
            if due_in_days(ob.due_date, today) <= 7
        )

        by_type = {}
        for ob in window_obligations:
            type_key = ob.type.value
            if type_key not in by_type:
                priority = compute_priority(ob.due_date, today)
                by_type[type_key] = {
                    "amount": 0,
                    "due_in_days": due_in_days(ob.due_date, today),
                    "priority": priority.value,
                }
            by_type[type_key]["amount"] += ob.amount

        # Compute critical count (due <= 3 days)
        critical_count = sum(
            1 for ob in window_obligations
            if due_in_days(ob.due_date, today) <= 3
        )

        # Income
        sale_revenue = expected_sale_revenue if expected_sale_revenue is not None else self.DEFAULT_EXPECTED_SALE_REVENUE
        other = other_income if other_income is not None else self.DEFAULT_OTHER_INCOME
        total_income = sale_revenue + other

        # Cash flow
        surplus = total_income - total_due
        surplus_after_critical = total_income - sum(
            ob.amount for ob in window_obligations
            if due_in_days(ob.due_date, today) <= 3
        )

        status = compute_cash_flow_status(surplus, critical_count)
        detail = status_detail(status, surplus, critical_count)

        return {
            "phone": phone,
            "window_days": window_days,
            "calculated_at": f"{today.isoformat()}T00:00:00Z",
            "income": {
                "expected_sale_revenue": sale_revenue,
                "other_income": other,
                "total_income": total_income,
            },
            "obligations": {
                "total_due": total_due,
                "count_urgent": count_urgent,
                "by_type": by_type,
            },
            "cash_flow": {
                "surplus": surplus,
                "surplus_after_critical": surplus_after_critical,
                "status": status,
                "status_detail": detail,
            },
        }