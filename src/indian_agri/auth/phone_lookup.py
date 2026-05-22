"""Farmer authentication — phone lookup and Agristack identity verification."""

import hashlib
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


class PhoneLookupService:
    """Phone → Farmer ID lookup for IVR authentication.

    Per specs/08-farmer-identity.md, farmers authenticate via phone number
    (OTP-less IVR flow — phone number IS the identity token for voice channel).
    """

    def __init__(self, db_session=None):
        self.db_session = db_session

    def lookup_by_phone(self, phone: str) -> Optional[dict]:
        """Look up farmer by phone number.

        Returns dict with farmer_id, language, district if found, else None.
        """
        if self.db_session is None:
            raise RuntimeError("PhoneLookupService requires a db_session")
        from ..models.farmer import FarmerPhoneLookup

        result = self.db_session.execute(
            "SELECT * FROM farmer_phone_lookup WHERE phone = %s", (phone,)
        ).fetchone()
        if result is None:
            return None
        return dict(result._mapping)

    def register_phone(
        self, phone: str, farmer_id: int, language: str, district: str
    ) -> None:
        """Register a phone number for a farmer."""
        from ..models.farmer import FarmerPhoneLookup

        entry = FarmerPhoneLookup(
            phone=phone,
            farmer_id=farmer_id,
            language=language,
            district=district,
        )
        self.db_session.insert(entry)


class AgristackVerifier:
    """Agristack farmer ID verification stub.

    Per specs/08-farmer-identity.md §agristack-integration,
    Agristack provides the canonical farmer ID (FID) after state-level rollout.

    This is a stub that returns a synthetic ID until real APIs are available.
    """

    def __init__(self):
        self.api_key = os.environ.get("AGRISACK_API_KEY", "")
        self.enabled = (
            os.environ.get("FARMER_ID_VERIFICATION_ENABLED", "false").lower() == "true"
        )

    async def verify_farmer(
        self,
        farmer_name: str,
        phone: str,
        district: str,
        state: str,
    ) -> dict:
        """Verify farmer identity against Agristack.

        Returns dict with:
            verified: bool
            agristack_id: str | None
            error: str | None
        """
        if not self.enabled:
            return {
                "verified": False,
                "agristack_id": None,
                "error": "Agristack verification not enabled",
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    "https://api.agristack.gov.in/v1/farmer/verify",
                    headers={"X-API-Key": self.api_key},
                    json={
                        "name": farmer_name,
                        "phone": phone,
                        "district": district,
                        "state": state,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "verified": True,
                        "agristack_id": data.get("farmer_id"),
                        "error": None,
                    }
                return {
                    "verified": False,
                    "agristack_id": None,
                    "error": f"Agristack API error: {response.status_code}",
                }
            except httpx.TimeoutException:
                return {
                    "verified": False,
                    "agristack_id": None,
                    "error": "Agristack API timeout",
                }
            except Exception as e:
                return {
                    "verified": False,
                    "agristack_id": None,
                    "error": str(e),
                }

    def generate_synthetic_id(
        self, farmer_name: str, phone: str, district: str
    ) -> str:
        """Generate a synthetic Agristack-style ID for testing.

        Format: AS-{state_code(2)}-{district_code(3)}-{hash}
        Only used when Agristack API is unavailable.
        """
        state_code = "MH"  # Maharashtra default — overridden in real use
        district_code = district[:3].upper().ljust(3, "X")
        raw = f"{farmer_name}:{phone}:{district}"
        hash_suffix = hashlib.md5(raw.encode()).hexdigest()[:8].upper()
        return f"AS-{state_code}-{district_code}-{hash_suffix}"
