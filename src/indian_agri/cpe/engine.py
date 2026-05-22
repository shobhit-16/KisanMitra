"""CPE orchestrator — per specs/09-constraint-priority-engine.md §1.1, §6.

Evaluates recommendations through gates in strict priority order.
Returns exactly one recommendation OR one suppression notification.
Never returns zero items.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..models.constraint_state import ConstraintState
from .bus import RecommendationBus
from .gates import (
    GateResult,
    health_gate,
    tenure_gate,
    cash_flow_gate,
    selling_window_gate,
    time_criticality_gate,
)
from .types import CPEOutput, Recommendation, SuppressedReason


@dataclass
class CPE:
    """Constraint Priority Engine orchestrator.

    Evaluates all published recommendations against the farmer's constraint state,
    returns exactly one output (recommendation or suppression).
    """

    bus: RecommendationBus
    constraint_state: ConstraintState

    # Gate priority order (1 = highest)
    GATE_ORDER = [
        ("gate1_health", health_gate),
        ("gate2_tenure", tenure_gate),
        ("gate3_cashflow", cash_flow_gate),
        ("gate4_selling_window", selling_window_gate),
        ("gate5_time_criticality", time_criticality_gate),
    ]

    def evaluate(self) -> CPEOutput:
        """Evaluate all recommendations from the bus against constraint state.

        Returns exactly one CPEOutput — never zero, never more than one.
        Per specs/09-constraint-priority-engine.md §6.
        """
        recommendations = self.bus.get_all()

        if not recommendations:
            # No recommendations — this shouldn't happen in normal operation
            # but handle gracefully
            return CPEOutput(
                output_type="suppression",
                active_constraint=None,
                confidence_note="No recommendations available",
            )

        # Evaluate each recommendation through all gates
        passed: list[tuple[Recommendation, list[SuppressedReason]]] = []
        suppressed_count = 0

        for rec in recommendations:
            suppressed_reasons: list[SuppressedReason] = []

            for gate_name, gate_fn in self.GATE_ORDER:
                result: GateResult = gate_fn(rec, self.constraint_state)
                if not result.passed:
                    suppressed_count += 1
                    suppressed_reasons.append(SuppressedReason(
                        engine=rec.engine,
                        module=rec.module,
                        recommendation_id=rec.recommendation_id,
                        reason=result.reason or "suppressed",
                        gate=int(gate_name.replace("gate", "").replace("_", "")[0]),
                    ))

            if not suppressed_reasons:
                passed.append((rec, []))
            # Note: we don't add to passed if there were any suppressions

        # One-recommendation rule: specs/09-constraint-priority-engine.md §6
        # Priority order: Gate 1 (health) > Gate 4 (selling window) > engine priority
        if not passed:
            # All recommendations were suppressed
            return self._build_suppression_output(recommendations, suppressed_count)

        # Sort passed recommendations by engine priority
        # Health crisis resources first, then by engine priority
        def recommendation_priority(rec: Recommendation) -> tuple[int, int]:
            # Primary sort: health crisis resources first
            if rec.category.value == "health_crisis_resource":
                sort_key = 0
            elif rec.category.value == "selling":
                sort_key = 1
            else:
                sort_key = 2
            # Secondary sort: engine priority
            return (sort_key, rec.priority_for_engine)

        passed.sort(key=lambda x: recommendation_priority(x[0]))
        winner = passed[0][0]

        # Collect all suppressed reasons for the winner
        all_suppressed: list[SuppressedReason] = []
        for rec, reasons in passed[1:]:  # All others that were suppressed
            all_suppressed.extend(reasons)
        # Also add any suppressed reasons from the winner itself (should be none since it passed)

        return CPEOutput(
            output_type="recommendation",
            recommendation=winner,
            suppressed_reasons=all_suppressed,
            active_constraint=None,  # A recommendation passed, no active constraint
            confidence_note=None,
        )

    def _build_suppression_output(
        self,
        recommendations: list[Recommendation],
        suppressed_count: int,
    ) -> CPEOutput:
        """Build suppression notification when all recommendations are blocked.

        Per specs/09-constraint-priority-engine.md §6.2.
        """
        # Determine the active constraint (highest-priority active gate)
        active_constraint = self._get_active_constraint_name()

        # Build suppressed reasons from all recommendations
        all_suppressed: list[SuppressedReason] = []
        for rec in recommendations:
            for gate_name, gate_fn in self.GATE_ORDER:
                result = gate_fn(rec, self.constraint_state)
                if not result.passed:
                    all_suppressed.append(SuppressedReason(
                        engine=rec.engine,
                        module=rec.module,
                        recommendation_id=rec.recommendation_id,
                        reason=result.reason or "suppressed",
                        gate=int(gate_name.replace("gate", "").replace("_", "")[0]),
                    ))

        return CPEOutput(
            output_type="suppression",
            recommendation=None,
            suppressed_reasons=all_suppressed,
            active_constraint=active_constraint,
            confidence_note=f"{suppressed_count} recommendations suppressed",
        )

    def _get_active_constraint_name(self) -> str | None:
        """Get the highest-priority active constraint name."""
        cs = self.constraint_state

        if cs.health_status == "crisis":
            return "health"
        if cs.tenure_type in ("tenant", "lease"):
            return "tenure"
        if cs.cash_flow_status in ("deficit", "emergency"):
            return "cash_flow"
        if cs.selling_window == "open" and cs.harvest_within_7_days:
            return "selling"
        if cs.time_criticality in ("immediate", "near_term"):
            return "timing"

        return None
