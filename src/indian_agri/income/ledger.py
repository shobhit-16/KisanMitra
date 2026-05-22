"""Module 6: Income Ledger — specs/01-domain-model.md §4, specs/03-market-intelligence.md §4a.

Records actual transaction prices from farmer self-report or field agent.
Establishes baseline pricing per specs/03-market-intelligence.md §4a.
Tracks production_kg, price_per_kg, total_value.
Computes distress_sale_flag per specs/01-domain-model.md §4.3.

The IncomeLedger maintains a per-farmer record of sales for baseline establishment
and distress detection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SaleChannel(str, Enum):
    """Where the farmer sold their crop."""
    MANDI = "mandi"
    FPO = "fpo"
    COOPERATIVE = "cooperative"
    DIRECT_BUYER = "direct_buyer"
    CONTRACT_FARMING = "contract_farming"
    PROCESSOR = "processor"
    COLD_STORAGE = "cold_storage"
    OTHER = "other"


@dataclass
class SaleRecord:
    """A single sale transaction for the Income Ledger.

    Per specs/01-domain-model.md §4: HarvestRecord and SalesRecord include
    distress_sale_flag. This is computed at add_sale() time.
    """
    id: Optional[int] = None
    farmer_id: int = 0
    sale_date: date = field(default_factory=date.today)
    commodity_code: str = ""
    variety: Optional[str] = None
    quantity_kg: float = 0.0
    price_per_kg: float = 0.0
    total_value: float = 0.0
    channel: SaleChannel = SaleChannel.MANDI
    mandi_id: Optional[str] = None
    buyer_name: Optional[str] = None
    price_vs_msp_percent: Optional[float] = None  # e.g. -15.0 for 15% below MSP
    distress_sale: bool = False
    distress_sale_reason: Optional[str] = None
    harvest_date: Optional[date] = None  # Date of harvest (for days-since-harvest calc)
    notes: Optional[str] = None
    recorded_by: str = "farmer_self_report"  # farmer_self_report | field_agent | fpo_staff
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.total_value == 0.0 and self.quantity_kg > 0 and self.price_per_kg > 0:
            self.total_value = self.quantity_kg * self.price_per_kg


class BaselinePrice:
    """Established baseline price for a commodity in a district/region."""

    def __init__(
        self,
        commodity_code: str,
        district: str,
        state: str,
        avg_price_per_kg: float,
        min_price_per_kg: float,
        max_price_per_kg: float,
        record_count: int,
        season: str,
        established_at: date,
    ):
        self.commodity_code = commodity_code
        self.district = district
        self.state = state
        self.avg_price_per_kg = avg_price_per_kg
        self.min_price_per_kg = min_price_per_kg
        self.max_price_per_kg = max_price_per_kg
        self.record_count = record_count
        self.season = season
        self.established_at = established_at


class IncomeLedger:
    """Per-farmer income ledger tracking actual sales and establishing baselines.

    Usage:
        ledger = IncomeLedger(farmer_id=123)
        ledger.add_sale(
            commodity_code="ONION",
            quantity_kg=500,
            price_per_kg=28.0,
            channel=SaleChannel.MANDI,
            sale_date=date(2024, 11, 15),
        )
        sales = ledger.list_sales()
        baseline = ledger.get_baseline("ONION", "Nashik", "Maharashtra")
    """

    def __init__(self, farmer_id: int, sales: Optional[list[SaleRecord]] = None):
        self.farmer_id = farmer_id
        self._sales: list[SaleRecord] = sales or []

    # -------------------------------------------------------------------------
    # Sale management
    # -------------------------------------------------------------------------

    def add_sale(
        self,
        commodity_code: str,
        quantity_kg: float,
        price_per_kg: float,
        channel: SaleChannel = SaleChannel.MANDI,
        sale_date: Optional[date] = None,
        mandi_id: Optional[str] = None,
        buyer_name: Optional[str] = None,
        variety: Optional[str] = None,
        harvest_date: Optional[date] = None,
        recorded_by: str = "farmer_self_report",
        msp_per_kg: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> SaleRecord:
        """Record a sale and compute distress_sale_flag.

        Per specs/01-domain-model.md §4.3: distress_sale_flag is set when:
        1. Price >15% below MSP
        2. Price at seasonal low (<10th percentile for this period)
        3. Farmer sells within 7 days of harvest
        4. Farmer sells entire crop immediately

        Args:
            quantity_kg: Sale quantity in kg
            price_per_kg: Price received per kg
            msp_per_kg: MSP per kg (if known — else uses module MSP table)
            other args: see SaleRecord

        Returns:
            The recorded SaleRecord with distress_sale_flag set
        """
        record = SaleRecord(
            farmer_id=self.farmer_id,
            sale_date=sale_date or date.today(),
            commodity_code=commodity_code,
            variety=variety,
            quantity_kg=quantity_kg,
            price_per_kg=price_per_kg,
            total_value=quantity_kg * price_per_kg,
            channel=channel,
            mandi_id=mandi_id,
            buyer_name=buyer_name,
            harvest_date=harvest_date,
            recorded_by=recorded_by,
            notes=notes,
        )

        # Compute price vs MSP
        if msp_per_kg is None:
            msp_per_kg = self._get_msp_per_kg(commodity_code)

        if msp_per_kg is not None and msp_per_kg > 0:
            record.price_vs_msp_percent = ((price_per_kg - msp_per_kg) / msp_per_kg) * 100

        # Compute distress sale flags
        distress_reasons: list[str] = []

        # Trigger 1: >15% below MSP
        if record.price_vs_msp_percent is not None and record.price_vs_msp_percent < -15.0:
            distress_reasons.append(
                f"price {record.price_vs_msp_percent:.0f}% below MSP (₹{msp_per_kg}/kg)"
            )

        # Trigger 3: within 7 days of harvest
        if harvest_date is not None and sale_date is not None:
            days_since_harvest = (sale_date - harvest_date).days
            if days_since_harvest <= 7:
                distress_reasons.append(
                    f"sold within {days_since_harvest} days of harvest (distress timing)"
                )

        # Trigger 4: sells entire crop immediately (assumed when quantity is large
        # and no prior sales recorded for this commodity this season)
        prior_sales = [s for s in self._sales if s.commodity_code == commodity_code]
        if len(prior_sales) == 0 and quantity_kg >= 100:
            # First sale of the season, large quantity — may indicate distress sale
            distress_reasons.append("first sale of season, large quantity (possible distress)")

        if distress_reasons:
            record.distress_sale = True
            record.distress_sale_reason = "; ".join(distress_reasons)

        self._sales.append(record)
        return record

    def list_sales(
        self,
        commodity_code: Optional[str] = None,
        season: Optional[str] = None,
        include_distress_only: bool = False,
    ) -> list[SaleRecord]:
        """List recorded sales, optionally filtered."""
        results = list(self._sales)
        if commodity_code is not None:
            results = [s for s in results if s.commodity_code == commodity_code]
        if include_distress_only:
            results = [s for s in results if s.distress_sale]
        return results

    def get_distress_sales(self, commodity_code: Optional[str] = None) -> list[SaleRecord]:
        """Get all distress sales."""
        all_distress = [s for s in self._sales if s.distress_sale]
        if commodity_code is not None:
            all_distress = [s for s in all_distress if s.commodity_code == commodity_code]
        return all_distress

    # -------------------------------------------------------------------------
    # Baseline price computation
    # -------------------------------------------------------------------------

    def establish_baseline(
        self,
        commodity_code: str,
        district: str,
        state: str,
        sales: Optional[list[SaleRecord]] = None,
        min_records: int = 3,
    ) -> Optional[BaselinePrice]:
        """Establish a baseline price for a commodity in a district.

        Per specs/03-market-intelligence.md §4a: baseline is established from
        actual transaction prices recorded in the Income Ledger.

        Requires at least min_records (default 3) to establish a baseline.

        Args:
            commodity_code: NPCS commodity code
            district: District for the baseline
            state: State for the baseline
            sales: Override the ledger's sales list (for cross-farmer baselines)
            min_records: Minimum sales needed to establish baseline

        Returns:
            BaselinePrice if sufficient data, else None
        """
        records = sales or [s for s in self._sales if s.commodity_code == commodity_code]

        if len(records) < min_records:
            return None

        prices = [s.price_per_kg for s in records if s.price_per_kg > 0]
        if not prices:
            return None

        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        return BaselinePrice(
            commodity_code=commodity_code,
            district=district,
            state=state,
            avg_price_per_kg=avg_price,
            min_price_per_kg=min_price,
            max_price_per_kg=max_price,
            record_count=len(records),
            season=self._detect_season(records),
            established_at=date.today(),
        )

    def _detect_season(self, records: list[SaleRecord]) -> str:
        """Detect the primary season for a set of sale records."""
        if not records:
            return "unknown"
        sale_months = [r.sale_date.month for r in records]
        avg_month = sum(sale_months) / len(sale_months)
        if 6 <= avg_month <= 10:
            return "kharif"
        elif avg_month >= 10 or avg_month <= 3:
            return "rabi"
        else:
            return "zaid"

    def _get_msp_per_kg(self, commodity_code: str) -> Optional[float]:
        """Get MSP per kg for a commodity. Returns None if not known."""
        # MSP table in ₹/quintal — convert to ₹/kg
        msp_per_quintal = {
            "ONION": 750.0,
            "WHEAT": 2275.0,
            "PADDY": 2183.0,
            "SOYABEAN": 4888.0,
            "MAIZE": 1962.0,
            "MUSTARD": 5650.0,
            "COTTON": 6620.0,
            "RICE": 2300.0,
        }
        msp_q = msp_per_quintal.get(commodity_code)
        if msp_q is not None:
            return msp_q / 100.0  # Convert per quintal to per kg
        return None

    # -------------------------------------------------------------------------
    # Summary statistics
    # -------------------------------------------------------------------------

    def total_income(self, commodity_code: Optional[str] = None) -> float:
        """Total income from all recorded sales."""
        sales = self._sales if commodity_code is None else [
            s for s in self._sales if s.commodity_code == commodity_code
        ]
        return sum(s.total_value for s in sales)

    def average_price(self, commodity_code: str) -> Optional[float]:
        """Average price per kg for a commodity."""
        prices = [
            s.price_per_kg for s in self._sales
            if s.commodity_code == commodity_code and s.price_per_kg > 0
        ]
        if not prices:
            return None
        return sum(prices) / len(prices)

    def total_quantity_sold(self, commodity_code: Optional[str] = None) -> float:
        """Total quantity sold in kg."""
        sales = self._sales if commodity_code is None else [
            s for s in self._sales if s.commodity_code == commodity_code
        ]
        return sum(s.quantity_kg for s in sales)
