"""e-NAM API integration — specs/03-market-intelligence.md §1.1.

e-NAM (electronic National Agriculture Market) provides daily modal prices for
1,361 mandis across India. This client wraps the e-NAM API for price data retrieval.

API Docs: https://api.enam.gov.in/
Phase 1: read-only, no authentication required for basic price queries.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class ENAMAPIError(Exception):
    """Raised when e-NAM API returns an error or times out."""

    def __init__(self, message: str, mandi_id: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.mandi_id = mandi_id
        self.status_code = status_code


class MandiPrice:
    """A single mandi price record from e-NAM."""

    def __init__(
        self,
        mandi_id: str,
        mandi_name: str,
        commodity_code: str,
        variety: str,
        grade: Optional[str],
        price_min: float,
        price_max: float,
        price_modal: float,
        volume_traded: Optional[float],
        date: date,
        state: str,
        district: str,
        source: str = "e-NAM",
    ):
        self.mandi_id = mandi_id
        self.mandi_name = mandi_name
        self.commodity_code = commodity_code
        self.variety = variety
        self.grade = grade
        self.price_min = price_min
        self.price_max = price_max
        self.price_modal = price_modal
        self.volume_traded = volume_traded
        self.date = date
        self.state = state
        self.district = district
        self.source = source

    def price_vs_msp(self, msp: float) -> float:
        """Return price difference from MSP as a fraction (e.g. 0.10 = +10% above MSP)."""
        if msp <= 0:
            return 0.0
        return (self.price_modal - msp) / msp

    def is_above_msp(self, msp: float) -> bool:
        return self.price_modal >= msp


class ENAMClient:
    """Client for e-NAM API.

    Phase 1: uses mock responses for development/demo.
    In production, replace _BASE_URL and _get() with real e-NAM API endpoints.
    """

    _BASE_URL = "https://api.enam.gov.in/epgr/prices"

    def __init__(self, timeout_seconds: float = 10.0):
        self._timeout = timeout_seconds

    def get_modal_price(
        self,
        mandi_id: str,
        commodity_code: str,
        variety: Optional[str] = None,
        date: Optional[date] = None,
    ) -> Optional[MandiPrice]:
        """Fetch modal price for a commodity at a specific mandi on a given date.

        Args:
            mandi_id: e-NAM mandi code (e.g. "MHI001")
            commodity_code: NPCS commodity code (e.g. "ONION")
            variety: Optional variety filter (e.g. "Medium Grain")
            date: Price date (default: today)

        Returns:
            MandiPrice if data available, None if no data for this date/mandi

        Raises:
            ENAMAPIError: On API error (timeout, HTTP error, parse failure)
        """
        check_date = date or date.today()

        try:
            response = self._get(mandi_id, commodity_code, check_date)
        except httpx.TimeoutException:
            raise ENAMAPIError(
                f"e-NAM API timeout after {self._timeout}s for mandi={mandi_id}",
                mandi_id=mandi_id,
            )
        except httpx.HTTPStatusError as e:
            raise ENAMAPIError(
                f"e-NAM HTTP {e.response.status_code} for mandi={mandi_id}",
                mandi_id=mandi_id,
                status_code=e.response.status_code,
            )

        if response is None or not response.get("data"):
            return None

        # Parse response — e-NAM returns a list under "data" key
        records = response.get("data", [])
        for record in records:
            if self._record_matches(record, mandi_id, commodity_code, variety):
                return self._parse_record(record, check_date)

        return None

    def _get(
        self,
        mandi_id: str,
        commodity_code: str,
        price_date: date,
    ) -> Optional[dict]:
        """Make the actual HTTP request to e-NAM API.

        Phase 1: returns mock data for development.
        Replace this method with real httpx.get() call in production.
        """
        # Phase 1: return mock data
        # Real implementation:
        # params = {
        #     "mandi_id": mandi_id,
        #     "commodity": commodity_code,
        #     "date": price_date.isoformat(),
        # }
        # async with httpx.AsyncClient() as client:
        #     resp = await client.get(self._BASE_URL, params=params, timeout=self._timeout)
        #     resp.raise_for_status()
        #     return resp.json()
        return self._mock_response(mandi_id, commodity_code, price_date)

    def _record_matches(
        self,
        record: dict,
        mandi_id: str,
        commodity_code: str,
        variety: Optional[str],
    ) -> bool:
        """Check if a record matches the query criteria."""
        # Phase 1: simple matching
        # Real e-NAM API returns records with different field names
        record_mandi = record.get("mandi_id") or record.get("market_code") or record.get("code", "")
        if record_mandi != mandi_id:
            return False
        record_commodity = record.get("commodity_code") or record.get("commodity") or ""
        if record_commodity.upper() != commodity_code.upper():
            return False
        if variety is not None:
            record_variety = record.get("variety", "").upper()
            if record_variety and record_variety != variety.upper():
                return False
        return True

    def _parse_record(self, record: dict, price_date: date) -> MandiPrice:
        """Parse a raw API record into a MandiPrice object."""
        return MandiPrice(
            mandi_id=record.get("mandi_id", record.get("market_code", "")),
            mandi_name=record.get("mandi_name", record.get("market", "Unknown")),
            commodity_code=record.get("commodity_code", record.get("commodity", "")),
            variety=record.get("variety", "Unknown"),
            grade=record.get("grade"),
            price_min=float(record.get("price_min", record.get("min_price", 0))),
            price_max=float(record.get("price_max", record.get("max_price", 0))),
            price_modal=float(record.get("price_modal", record.get("modal_price", 0))),
            volume_traded=float(record.get("volume_traded", record.get("quantity", 0)) or 0),
            date=price_date,
            state=record.get("state", ""),
            district=record.get("district", ""),
            source="e-NAM",
        )

    def _mock_response(
        self,
        mandi_id: str,
        commodity_code: str,
        price_date: date,
    ) -> Optional[dict]:
        """Return mock price data for Phase 1 development."""
        # Mock data for common commodities — realistic price ranges
        mock_prices = {
            "ONION": 2800.0,
            "WHEAT": 2400.0,
            "PADDY": 2200.0,
            "SOYABEAN": 4900.0,
            "MAIZE": 2000.0,
            "MUSTARD": 5700.0,
            "COTTON": 6700.0,
        }
        base_price = mock_prices.get(commodity_code, 2500.0)

        return {
            "data": [
                {
                    "mandi_id": mandi_id,
                    "market": f"Mandi {mandi_id}",
                    "commodity_code": commodity_code,
                    "commodity": commodity_code,
                    "variety": "Medium",
                    "grade": None,
                    "price_min": base_price * 0.9,
                    "price_max": base_price * 1.1,
                    "modal_price": base_price,
                    "quantity": 100.0,
                    "state": "Maharashtra",
                    "district": "Nashik",
                }
            ]
        }
