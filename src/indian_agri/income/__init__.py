"""Income Engine — Phase 1 publishing to Recommendation Bus.

Per specs/09-constraint-priority-engine.md §5.1: Income Engine is the only
engine publishing in Phase 1. All 5 CPE gates are active.

Modules:
- obligations: ObligationCalendar, Obligation, ObligationType, Season
- cash_flow: CashFlowAssessment, assess(), update_constraint_state_from_assessment()
- mandi_prices: MandiPriceService, MandiPriceResult, publish_mandi_price_recommendation()
- selling: SellingDecisionGuide, calculate_storage_benefit(), recommend_sell_or_store()
- emergency_credit: EmergencyCreditPathway, publish_health_crisis_resource()
- ledger: IncomeLedger, SaleRecord, SaleChannel, BaselinePrice
"""

from .bus_integration import (
    get_recommendation_bus,
    publish_recommendation,
    publish_selling_recommendation,
    publish_emergency_credit,
)
from .obligations import (
    Obligation,
    ObligationCalendar,
    ObligationType,
    Season as ObligationSeason,
)
from .cash_flow import (
    CashFlowAssessmentResult,
    CashFlowConfidence,
    assess as cash_flow_assess,
    update_constraint_state_from_assessment,
)
from .mandi_prices import (
    MandiPriceResult,
    MandiPriceService,
    clear_price_cache,
    get_price_cache,
    publish_mandi_price_recommendation,
)
from .selling import (
    SellingDecisionGuide,
    StorageDecision,
    calculate_storage_benefit,
    recommend_sell_or_store,
)
from .emergency_credit import (
    CrisisType,
    EmergencyCreditInfo,
    EmergencyCreditPathway,
    get_emergency_health_resources,
    is_health_crisis_event,
    publish_health_crisis_resource,
)
from .ledger import (
    BaselinePrice,
    IncomeLedger,
    SaleChannel,
    SaleRecord,
)

__all__ = [
    # Bus
    "get_recommendation_bus",
    "publish_recommendation",
    "publish_selling_recommendation",
    "publish_emergency_credit",
    # Module 1
    "Obligation",
    "ObligationCalendar",
    "ObligationType",
    "ObligationSeason",
    # Module 2
    "CashFlowAssessmentResult",
    "CashFlowConfidence",
    "cash_flow_assess",
    "update_constraint_state_from_assessment",
    # Module 3
    "MandiPriceResult",
    "MandiPriceService",
    "clear_price_cache",
    "get_price_cache",
    "publish_mandi_price_recommendation",
    # Module 4
    "SellingDecisionGuide",
    "StorageDecision",
    "calculate_storage_benefit",
    "recommend_sell_or_store",
    # Module 5
    "CrisisType",
    "EmergencyCreditInfo",
    "EmergencyCreditPathway",
    "get_emergency_health_resources",
    "is_health_crisis_event",
    "publish_health_crisis_resource",
    # Module 6
    "BaselinePrice",
    "IncomeLedger",
    "SaleChannel",
    "SaleRecord",
]
