"""Module 4: Selling Decision Guide — specs/03-market-intelligence.md §4.2.

Storage economics calculator, price threshold logic (above MSP, below MSP, seasonal patterns).
Publishes sell/store/hold recommendations to the Recommendation Bus.
Drives Gate 4 (SellingWindowGate) via selling_window field in constraint_state.

calculate_storage_benefit() implements the spec §4.2 function signature.
publish_selling_recommendation() is already implemented in bus_integration.py.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from enum import Enum
from typing import Optional

from .bus_integration import publish_selling_recommendation
from .mandi_prices import MandiPriceService, MandiPriceResult, publish_mandi_price_recommendation

logger = logging.getLogger(__name__)


class SellingRecommendation(str, Enum):
    """Canonical selling recommendation outcomes."""
    SELL_NOW = "SELL NOW"
    STORE_VIABLE = "STORE VIABLE"
    STORE_BORDERLINE = "STORE BORDERLINE"
    HOLD = "HOLD"
    EMERGENCY_SELL = "EMERGENCY SELL"


class StorageDecision:
    """Result of storage economics calculation."""

    def __init__(
        self,
        recommendation: SellingRecommendation,
        current_price: float,
        expected_price_peak: Optional[float],
        storage_cost_per_quintal: float,
        quality_loss_percent: float,
        quantity_quintal: float,
        gross_gain: float,
        net_gain: float,
        effective_gain: float,
        payback_days: Optional[int],
        reason: str,
    ):
        self.recommendation = recommendation
        self.current_price = current_price
        self.expected_price_peak = expected_price_peak
        self.storage_cost_per_quintal = storage_cost_per_quintal
        self.quality_loss_percent = quality_loss_percent
        self.quantity_quintal = quantity_quintal
        self.gross_gain = gross_gain
        self.net_gain = net_gain
        self.effective_gain = effective_gain
        self.payback_days = payback_days
        self.reason = reason

    @property
    def effective_gain_per_quintal(self) -> float:
        return self.effective_gain / self.quantity_quintal if self.quantity_quintal > 0 else 0.0

    def to_metadata(self) -> dict:
        return {
            "recommendation": self.recommendation.value,
            "current_price": self.current_price,
            "expected_price_peak": self.expected_price_peak,
            "storage_cost_per_quintal": self.storage_cost_per_quintal,
            "quality_loss_percent": self.quality_loss_percent,
            "quantity_quintal": self.quantity_quintal,
            "gross_gain": self.gross_gain,
            "net_gain": self.net_gain,
            "effective_gain": self.effective_gain,
            "effective_gain_per_quintal": self.effective_gain_per_quintal,
        }


def calculate_storage_benefit(
    current_price: float,
    expected_price_peak: float,
    storage_cost_per_quintal: float,
    quality_loss_percent: float,
    quantity_quintal: float,
    cash_need_urgency: int,
) -> StorageDecision:
    """Calculate storage economics for a farmer's crop.

    Implements specs/03-market-intelligence.md §4.2 calculate_storage_benefit().

    Args:
        current_price: Rs/quintal today
        expected_price_peak: Rs/quintal at seasonal peak
        storage_cost_per_quintal: Rs/quintal for the season (facility + handling)
        quality_loss_percent: % weight loss in storage (e.g. 5.0 for 5%)
        quantity_quintal: Quintals to potentially store
        cash_need_urgency: 1-5 scale; 4+ = urgent need for cash

    Returns:
        StorageDecision with recommendation, gains, and reasoning
    """
    gross_gain = (expected_price_peak - current_price) * quantity_quintal

    # Net gain = gross - storage costs
    total_storage_cost = storage_cost_per_quintal * quantity_quintal
    net_gain = gross_gain - total_storage_cost

    # Effective gain accounting for quality loss
    adjusted_quantity = quantity_quintal * (1 - quality_loss_percent / 100.0)
    effective_gain = (
        expected_price_peak * adjusted_quantity
    ) - (current_price * quantity_quintal) - total_storage_cost

    # Decision logic
    if cash_need_urgency >= 4:
        recommendation = SellingRecommendation.EMERGENCY_SELL
        reason = (
            f"Emergency sell: cash need urgency {cash_need_urgency}/5 is high. "
            f"Storage gains ₹{net_gain:.0f} but liquidity takes priority."
        )
    elif net_gain < 0:
        recommendation = SellingRecommendation.SELL_NOW
        reason = (
            f"Sell now: storage not profitable. "
            f"Net loss of ₹{abs(net_gain):.0f} (cost ₹{total_storage_cost:.0f} "
            f"vs expected gain ₹{gross_gain:.0f})."
        )
    elif net_gain < total_storage_cost * 0.3:
        recommendation = SellingRecommendation.STORE_BORDERLINE
        reason = (
            f"Borderline: net gain ₹{net_gain:.0f} "
            f"({net_gain / total_storage_cost * 100:.0f}% of storage cost). "
            f"Depends on your cash position."
        )
    elif expected_price_peak > current_price * 1.15:
        # >15% expected appreciation — clearly viable
        recommendation = SellingRecommendation.STORE_VIABLE
        reason = (
            f"Store viable: ₹{net_gain:.0f} net gain ({expected_price_peak / current_price - 1:.0%} "
            f"price appreciation, {effective_gain / quantity_quintal:.0f}/quintal effective gain)."
        )
    else:
        recommendation = SellingRecommendation.STORE_BORDERLINE
        reason = (
            f"Storage marginal: ₹{net_gain:.0f} net gain. "
            f"Expected appreciation {expected_price_peak / current_price - 1:.0%} "
            f"barely covers storage costs."
        )

    return StorageDecision(
        recommendation=recommendation,
        current_price=current_price,
        expected_price_peak=expected_price_peak,
        storage_cost_per_quintal=storage_cost_per_quintal,
        quality_loss_percent=quality_loss_percent,
        quantity_quintal=quantity_quintal,
        gross_gain=gross_gain,
        net_gain=net_gain,
        effective_gain=effective_gain,
        payback_days=None,
        reason=reason,
    )


class SellingDecisionGuide:
    """Guides farmers through sell/store/hold decisions.

    Combines price data (MandiPriceService), storage economics, and
    cash need to produce a recommendation published to the bus.
    """

    def __init__(self, price_service: Optional[MandiPriceService] = None):
        self._price_service = price_service or MandiPriceService()

    def evaluate(
        self,
        commodity_code: str,
        state: str,
        district: str,
        variety: Optional[str],
        quantity_quintal: float,
        current_price: Optional[float],
        storage_available: bool,
        cash_need_urgency: int = 1,
        expected_storage_months: int = 2,
    ) -> StorageDecision:
        """Evaluate selling decision for a farmer's crop.

        Args:
            commodity_code: NPCS commodity code
            state: Farmer's state
            district: Farmer's district
            variety: Optional crop variety
            quantity_quintal: Harvest quantity in quintals
            current_price: Rs/quintal if known (from farmer self-report or mandi)
            storage_available: True if farmer has storage capacity
            cash_need_urgency: 1-5 scale (4+ = urgent)
            expected_storage_months: How long crop can be stored

        Returns:
            StorageDecision with recommendation
        """
        # Fetch current market prices
        price_result = self._price_service.get_prices_for_farmer(
            farmer_village="",
            district=district,
            state=state,
            commodity_code=commodity_code,
            variety=variety,
        )

        if price_result.has_data and current_price is None:
            current_price = price_result.avg_modal_price

        if current_price is None or current_price <= 0:
            # Cannot make a decision without a price
            return StorageDecision(
                recommendation=SellingRecommendation.HOLD,
                current_price=0,
                expected_price_peak=None,
                storage_cost_per_quintal=0,
                quality_loss_percent=0,
                quantity_quintal=quantity_quintal,
                gross_gain=0,
                net_gain=0,
                effective_gain=0,
                payback_days=None,
                reason="Cannot evaluate: no current price available.",
            )

        # Check MSP
        msp = self._price_service.get_msp_for_commodity(commodity_code, state)
        if msp is not None:
            price_above_msp = current_price >= msp
        else:
            price_above_msp = None

        # Get seasonal peak price estimate
        expected_price_peak = self._estimate_seasonal_peak(commodity_code, current_price, state)

        # Estimate storage costs
        storage_cost = self._estimate_storage_cost(commodity_code, state, expected_storage_months)

        # Quality loss varies by commodity
        quality_loss = self._quality_loss_rate(commodity_code)

        decision = calculate_storage_benefit(
            current_price=current_price,
            expected_price_peak=expected_price_peak,
            storage_cost_per_quintal=storage_cost,
            quality_loss_percent=quality_loss,
            quantity_quintal=quantity_quintal,
            cash_need_urgency=cash_need_urgency,
        )

        return decision

    def _estimate_seasonal_peak(
        self,
        commodity_code: str,
        current_price: float,
        state: str,
    ) -> float:
        """Estimate seasonal peak price based on historical patterns.

        Phase 1: static seasonal factors per commodity.
        Phase 2: ML-based forecast using PriceTrend.forecast_7day per specs/03-market-intelligence.md §2.3.
        """
        # Seasonal appreciation factors (realistic for Indian agriculture)
        seasonal_factors = {
            "ONION": 1.25,     # ~25% gain from Oct low to Feb peak
            "POTATO": 1.20,
            "TOMATO": 1.30,    # Perishable, higher seasonality
            "WHEAT": 1.10,     # Stable, smaller seasonal swing
            "SOYABEAN": 1.15,
            "MUSTARD": 1.12,
            "COTTON": 1.08,
            "RICE": 1.05,
            "PADDY": 1.05,
            "MAIZE": 1.12,
        }
        factor = seasonal_factors.get(commodity_code, 1.10)
        return current_price * factor

    def _estimate_storage_cost(
        self,
        commodity_code: str,
        state: str,
        months: int,
    ) -> float:
        """Estimate storage cost per quintal per month.

        Phase 1: static cost table.
        Phase 2: would use actual cold storage/warehouse rates by location.
        """
        # Rs per quintal per month (facility cost only, excludes quality loss)
        monthly_cost_per_quintal = {
            "ONION": 80.0,     # Cold storage for onions
            "POTATO": 60.0,
            "TOMATO": 100.0,   # Cold storage essential
            "WHEAT": 30.0,
            "SOYABEAN": 40.0,
            "MUSTARD": 35.0,
            "COTTON": 50.0,
            "RICE": 25.0,
            "PADDY": 25.0,
            "MAIZE": 30.0,
        }
        base = monthly_cost_per_quintal.get(commodity_code, 50.0)
        return base * months

    def _quality_loss_rate(self, commodity_code: str) -> float:
        """Estimated quality loss percentage during storage."""
        loss_rates = {
            "ONION": 8.0,
            "POTATO": 5.0,
            "TOMATO": 15.0,
            "WHEAT": 2.0,
            "SOYABEAN": 3.0,
            "MUSTARD": 2.0,
            "COTTON": 1.0,
            "RICE": 1.0,
            "PADDY": 2.0,
            "MAIZE": 3.0,
        }
        return loss_rates.get(commodity_code, 5.0)

    def publish_recommendation(
        self,
        commodity_code: str,
        state: str,
        district: str,
        variety: Optional[str],
        quantity_quintal: float,
        current_price: Optional[float],
        storage_available: bool,
        cash_need_urgency: int,
        days_until_harvest: Optional[int] = None,
    ) -> StorageDecision:
        """Evaluate and publish a selling recommendation to the bus.

        Returns the StorageDecision for display.
        """
        decision = self.evaluate(
            commodity_code=commodity_code,
            state=state,
            district=district,
            variety=variety,
            quantity_quintal=quantity_quintal,
            current_price=current_price,
            storage_available=storage_available,
            cash_need_urgency=cash_need_urgency,
        )

        # Build action text
        if decision.recommendation == SellingRecommendation.EMERGENCY_SELL:
            action = f"⚠️ Sell now — urgent cash need. {decision.reason}"
        elif decision.recommendation == SellingRecommendation.SELL_NOW:
            action = f"💰 Sell now: {decision.reason}"
        elif decision.recommendation == SellingRecommendation.STORE_VIABLE:
            action = f"📦 Store viable: {decision.reason}"
        elif decision.recommendation == SellingRecommendation.STORE_BORDERLINE:
            action = f"⚖️ Storage borderline: {decision.reason}"
        else:
            action = f"⏸️ Hold: {decision.reason}"

        msp = self._price_service.get_msp_for_commodity(commodity_code, state)

        # Module 3: publish mandi price recommendation to the bus
        publish_mandi_price_recommendation(
            commodity_code=commodity_code,
            district=district,
            state=state,
            variety=variety,
        )

        publish_selling_recommendation(
            action=action,
            price_above_msp=(current_price >= msp) if msp and current_price else None,
            days_until_harvest=days_until_harvest,
            priority=1,
        )

        return decision


def recommend_sell_or_store(
    commodity_code: str,
    state: str,
    district: str,
    quantity_quintal: float,
    current_price: float,
    storage_available: bool,
    cash_need_urgency: int = 1,
    days_until_harvest: Optional[int] = None,
) -> StorageDecision:
    """Convenience function — evaluate and publish a single selling decision.

    Equivalent to:
        guide = SellingDecisionGuide()
        guide.publish_recommendation(...)
    """
    guide = SellingDecisionGuide()
    return guide.publish_recommendation(
        commodity_code=commodity_code,
        state=state,
        district=district,
        variety=None,
        quantity_quintal=quantity_quintal,
        current_price=current_price,
        storage_available=storage_available,
        cash_need_urgency=cash_need_urgency,
        days_until_harvest=days_until_harvest,
    )
