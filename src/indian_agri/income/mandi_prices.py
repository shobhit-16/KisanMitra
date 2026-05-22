"""Module 3: Mandi Price Visibility — specs/03-market-intelligence.md §1–2.

e-NAM API integration for daily modal prices. Fetches commodity × variety × mandi
prices for a farmer's crop and nearest 3 mandis. Caches in Redis with 24h TTL.
Graceful degradation when data is missing per §9.1.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Optional

import httpx

from ..integrations.enam import ENAMClient, ENAMAPIError, MandiPrice
from .bus_integration import publish_recommendation

logger = logging.getLogger(__name__)


class PriceCache:
    """In-memory price cache (24h TTL). Replaces Redis for Phase 1.

    In production this would be backed by Redis. Phase 1 uses a simple dict
    with TTL tracking. Thread-unsafe — acceptable for single-process Phase 1.
    """

    def __init__(self, ttl_hours: int = 24):
        self._cache: dict[str, tuple[MandiPrice, datetime]] = {}
        self._ttl_hours = ttl_hours

    def _key(self, mandi_id: str, commodity_code: str, price_date: date) -> str:
        return f"{mandi_id}:{commodity_code}:{price_date.isoformat()}"

    def get(self, mandi_id: str, commodity_code: str, price_date: date) -> Optional[MandiPrice]:
        """Return cached price if still valid, else None."""
        entry = self._cache.get(self._key(mandi_id, commodity_code, price_date))
        if entry is None:
            return None
        price, cached_at = entry
        if datetime.utcnow() - cached_at > timedelta(hours=self._ttl_hours):
            del self._cache[self._key(mandi_id, commodity_code, price_date)]
            return None
        return price

    def set(self, mandi_id: str, commodity_code: str, price_date: date, price: MandiPrice) -> None:
        self._cache[self._key(mandi_id, commodity_code, price_date)] = (price, datetime.utcnow())

    def clear(self) -> None:
        self._cache.clear()


# Module-level cache instance
_price_cache: Optional[PriceCache] = None


def get_price_cache() -> PriceCache:
    global _price_cache
    if _price_cache is None:
        _price_cache = PriceCache()
    return _price_cache


def clear_price_cache() -> None:
    global _price_cache
    if _price_cache is not None:
        _price_cache.clear()


class MandiPriceService:
    """Service for fetching and caching mandi prices.

    Usage:
        service = MandiPriceService()
        prices = service.get_prices_for_farmer(
            farmer_village="Lasalgaon",
            district="Nashik",
            commodity_code="ONION",
            state="Maharashtra",
        )
    """

    def __init__(
        self,
        enam_client: Optional[ENAMClient] = None,
        cache: Optional[PriceCache] = None,
    ):
        self._enam = enam_client or ENAMClient()
        self._cache = cache or get_price_cache()

    def get_prices_for_farmer(
        self,
        farmer_village: str,
        district: str,
        state: str,
        commodity_code: str,
        variety: Optional[str] = None,
        as_of_date: Optional[date] = None,
    ) -> "MandiPriceResult":
        """Fetch prices for the nearest 3 mandis for a farmer's crop.

        Per specs/03-market-intelligence.md §3.1: compute nearest 3 mandis by
        road distance. Falls back to district mandis if distance data unavailable.

        Args:
            farmer_village: Village name for distance calculation
            district: District for mandi lookup
            state: State for mandi filtering
            commodity_code: NPCS commodity code (e.g. "ONION", "WHEAT")
            variety: Optional variety (e.g. "Medium Grain")
            as_of_date: Price date (default: today)

        Returns:
            MandiPriceResult with prices, staleness info, and fallback metadata
        """
        check_date = as_of_date or date.today()
        prices: list[MandiPrice] = []
        source_info: list[str] = []
        is_stale: bool = False

        # Try cache first
        nearest_mandi_ids = self._get_nearest_mandi_ids(district, state)

        for mandi_id in nearest_mandi_ids:
            cached = self._cache.get(mandi_id, commodity_code, check_date)
            if cached is not None:
                prices.append(cached)
                source_info.append(f"{mandi_id}: cache")
            else:
                try:
                    price = self._enam.get_modal_price(
                        mandi_id=mandi_id,
                        commodity_code=commodity_code,
                        variety=variety,
                        date=check_date,
                    )
                    if price is not None:
                        self._cache.set(mandi_id, commodity_code, check_date, price)
                        prices.append(price)
                        source_info.append(f"{mandi_id}: enam")
                except ENAMAPIError as e:
                    logger.warning("e-NAM API error for mandi=%s: %s", mandi_id, e)
                    source_info.append(f"{mandi_id}: error={e}")

        # If no prices from e-NAM, fall back to last-known prices
        if not prices:
            is_stale = True
            prices = self._get_fallback_prices(district, commodity_code, variety)
            source_info = [f"{p.mandi_id}: fallback" for p in prices]

        return MandiPriceResult(
            prices=prices,
            as_of_date=check_date,
            source_info=source_info,
            is_stale=is_stale,
            commodity_code=commodity_code,
            farmer_district=district,
        )

    def _get_nearest_mandi_ids(self, district: str, state: str) -> list[str]:
        """Return nearest mandi IDs for a district.

        Phase 1: simple district-level lookup. Distance-based routing is Phase 2.
        Returns up to 3 mandis known to trade the commodity in the state.
        """
        # Phase 1 static mandi registry by state/district
        # These would come from a geospatial service in Phase 2
        registry = _MANDI_REGISTRY.get(state, {}).get(district, [])
        return registry[:3]

    def _get_fallback_prices(
        self,
        district: str,
        commodity_code: str,
        variety: Optional[str],
    ) -> list[MandiPrice]:
        """Return last-known prices from cache (no date filter) as fallback.

        Per specs/03-market-intelligence.md §9.1: when price data is missing,
        show from nearest comparable mandi with explicit staleness label.
        """
        fallback: list[MandiPrice] = []
        for key, (price, _) in self._cache._cache.items():
            if price.commodity_code == commodity_code:
                # Include regardless of date — this is the fallback
                if len(fallback) < 3:
                    fallback.append(price)
        return fallback

    def get_msp_for_commodity(self, commodity_code: str, state: str) -> Optional[float]:
        """Return the Minimum Support Price for a commodity.

        MSP data is static per season. Returns None if MSP not known.
        """
        return _MSP_TABLE.get(commodity_code)


class MandiPriceResult:
    """Result container for mandi price queries."""

    def __init__(
        self,
        prices: list[MandiPrice],
        as_of_date: date,
        source_info: list[str],
        is_stale: bool,
        commodity_code: str,
        farmer_district: str,
    ):
        self.prices = prices
        self.as_of_date = as_of_date
        self.source_info = source_info
        self.is_stale = is_stale
        self.commodity_code = commodity_code
        self.farmer_district = farmer_district

    @property
    def has_data(self) -> bool:
        return len(self.prices) > 0

    @property
    def modal_prices(self) -> list[float]:
        return [p.price_modal for p in self.prices]

    @property
    def max_modal_price(self) -> Optional[float]:
        return max(self.modal_prices) if self.modal_prices else None

    @property
    def min_modal_price(self) -> Optional[float]:
        return min(self.modal_prices) if self.modal_prices else None

    @property
    def avg_modal_price(self) -> Optional[float]:
        if not self.modal_prices:
            return None
        return sum(self.modal_prices) / len(self.modal_prices)


# ---------------------------------------------------------------------------
# Static MSP table (Phase 1 — would come from government API in Phase 2)
# Per quintal (100 kg) — Maharashtra Kharif 2024-25
# ---------------------------------------------------------------------------
_MSP_TABLE: dict[str, float] = {
    "ONION": 750.0,        # ₹750/quintal Kharif 2024
    "WHEAT": 2275.0,        # ₹2275/quintal RMS 2024-25
    "PADDY": 2183.0,        # ₹2183/quintal Common Grade
    "RICE": 2300.0,         # ₹2300/quintal Grade A
    "SOYABEAN": 4888.0,     # ₹4888/quintal MSP Kharif 2024
    "MAIZE": 1962.0,        # ₹1962/quintal Kharif 2024
    "MUSTARD": 5650.0,      # ₹5650/quintal RMS 2024-25
    "COTTON": 6620.0,       # ₹6620/quintal Medium Staple
    "GROUNDNUT": 6783.0,    # ₹6783/quintal Kharif 2024
    "TUR": 7000.0,          # ₹7000/quintal Tur (Arhar) MSP 2024-25
    "MOONG": 8682.0,        # ₹8682/quintal Green Gram MSP 2024-25
    "URAD": 7380.0,         # ₹7380/quintal Black Gram MSP 2024-25
    "CHANA": 5440.0,        # ₹5440/quintal Gram MSP 2024-25
    "MASOOR": 6425.0,        # ₹6425/quintal Lentil MSP 2024-25
}


# ---------------------------------------------------------------------------
# Static mandi registry (Phase 1 — would come from geospatial service in Phase 2)
# Format: state -> district -> list of mandi_ids
# ---------------------------------------------------------------------------
_MANDI_REGISTRY: dict[str, dict[str, list[str]]] = {
    "Maharashtra": {
        "Nashik": ["MHI001", "MHI002", "MHI003"],  # Lasalgaon, Yeola, Sinnar
        "Pune": ["MHI004", "MHI005"],               # Pune, Baramati
        "Solapur": ["MHI006", "MHI007"],
        "Ahmednagar": ["MHI008", "MHI009"],
        "Jalgaon": ["MHI010", "MHI011"],
        "Nagpur": ["MHI012", "MHI013"],
        "Aurangabad": ["MHI014", "MHI015"],
    },
    "Karnataka": {
        "Belgaum": ["MKI001", "MKI002", "MKI003"],
        "Dharwad": ["MKI004", "MKI005"],
        "Bagalkot": ["MKI006", "MKI007"],
        "Raichur": ["MKI008", "MKI009"],
        "Gulbarga": ["MKI010", "MKI011"],
    },
    "Gujarat": {
        "Ahmedabad": ["MGU001", "MGU002"],
        "Surat": ["MGU003", "MGU004"],
        "Vadodara": ["MGU005", "MGU006"],
        "Rajkot": ["MGU007", "MGU008"],
        "Bhavnagar": ["MGU009", "MGU010"],
    },
    "Madhya Pradesh": {
        "Bhopal": ["MMP001", "MMP002"],
        "Indore": ["MMP003", "MMP004"],
        "Ujjain": ["MMP005", "MMP006"],
        "Jabalpur": ["MMP007", "MMP008"],
    },
    "Uttar Pradesh": {
        "Agra": ["MUP001", "MUP002"],
        "Lucknow": ["MUP003", "MUP004"],
        "Varanasi": ["MUP005", "MUP006"],
        "Kanpur": ["MUP007", "MUP008"],
    },
    "Rajasthan": {
        "Jaipur": ["MRJ001", "MRJ002", "MRJ003"],
        "Jodhpur": ["MRJ004", "MRJ005"],
        "Bikaner": ["MRJ006", "MRJ007"],
        "Kota": ["MRJ008", "MRJ009"],
    },
}


def publish_mandi_price_recommendation(
    commodity_code: str,
    district: str,
    state: str,
    variety: Optional[str] = None,
) -> Optional[MandiPriceResult]:
    """Fetch mandi prices and publish an information recommendation to the bus.

    This is the public entry point for Module 3. Called by the income engine
    when a farmer queries prices or when a price alert fires.

    Returns the MandiPriceResult for display/analysis.
    """
    service = MandiPriceService()
    result = service.get_prices_for_farmer(
        farmer_village="",
        district=district,
        state=state,
        commodity_code=commodity_code,
        variety=variety,
    )

    # Build recommendation metadata
    metadata = {
        "commodity_code": commodity_code,
        "district": district,
        "state": state,
        "variety": variety,
        "price_count": len(result.prices),
        "is_stale": result.is_stale,
        "as_of_date": result.as_of_date.isoformat() if result.as_of_date else None,
        "prices": [
            {
                "mandi_id": p.mandi_id,
                "modal_price": p.price_modal,
                "min_price": p.price_min,
                "max_price": p.price_max,
                "volume": p.volume_traded,
            }
            for p in result.prices
        ],
    }

    if result.has_data:
        msp = service.get_msp_for_commodity(commodity_code, state)
        avg_price = result.avg_modal_price
        if avg_price is not None and msp is not None:
            above_msp = avg_price >= msp
            price_status = f"above MSP (₹{msp})" if above_msp else f"below MSP (₹{msp})"
            action = f"{commodity_code} prices at ₹{avg_price:.0f}/quintal, {price_status}"
        else:
            action = f"{commodity_code} prices available: ₹{avg_price:.0f}/quintal avg"
    else:
        action = f"No price data available for {commodity_code} in {district}. Showing last available prices."
        metadata["no_data"] = True

    from ..cpe.types import CapitalIntensity, RecommendationCategory, TimeToAction

    publish_recommendation(
        module="module_3_mandi_prices",
        category=RecommendationCategory.INFORMATION,
        action=action,
        capital_intensity=CapitalIntensity.NONE,
        time_to_action=TimeToAction.DAYS,
        priority_for_engine=3,
        metadata=metadata,
    )

    return result
