import enum


class TenureType(str, enum.Enum):
    OWNER = "owner"
    TENANT = "tenant"
    LEASE = "lease"
    COMMUNITY = "community"


class HealthStatus(str, enum.Enum):
    NORMAL = "normal"
    CRISIS = "crisis"


class CashFlowStatus(str, enum.Enum):
    SURPLUS = "surplus"
    BALANCED = "balanced"
    DEFICIT = "deficit"
    EMERGENCY = "emergency"


class SellingWindow(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class TimeCriticality(str, enum.Enum):
    IMMEDIATE = "immediate"  # harvest within 7 days
    NEAR_TERM = "near_term"  # 8-30 days
    MEDIUM_TERM = "medium_term"  # 31-90 days
    LONG_TERM = "long_term"  # 90+ days


class CropCycleStatus(str, enum.Enum):
    SOWING = "sowing"
    GROWING = "growing"
    HARVEST = "harvest"
    POST_HARVEST = "post_harvest"
    FALLOW = "fallow"


class Season(str, enum.Enum):
    KHARIF = "kharif"
    RABI = "rabi"
    ZAID = "zaid"
    ANNUAL = "annual"


class Language(str, enum.Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"
    KANNADA = "kn"


class LiteracyLevel(str, enum.Enum):
    ILLITERATE = "illiterate"
    FUNCTIONAL = "functional"  # can read
    LITERATE = "literate"


class ConsentStatus(str, enum.Enum):
    PENDING = "pending"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"


class IrrigationType(str, enum.Enum):
    RAINFED = "rainfed"
    WELL = "well"
    CANAL = "canal"
    BOREWELL = "borewell"
    TANK = "tank"
    MIXED = "mixed"


class BuyerType(str, enum.Enum):
    MANDI = "mandi"
    COMMISSION_AGENT = "commission_agent"
    DIRECT_BUYER = "direct_buyer"
    COOPERATIVE = "cooperative"
    CONTRACT = "contract"
