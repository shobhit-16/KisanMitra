# Domain Spec: Farmer & Farm Entity Model

## Overview

This spec defines the core data model for representing farmers, their land holdings, crops, and farm-level attributes. This is the foundational entity model that all other specs depend upon.

---

## 1. Farmer Entity

### 1.1 Core Attributes

| Field | Type | Required | Description |
|---|---|---|---|
| `farmer_id` | UUID | Yes | Unique identifier (linked to Agristack Farmer ID) |
| `aadhaar_hash` | String | No | SHA-256 hash of Aadhaar (consent required) |
| `name` | String | Yes | Full name as per land records |
| `phone` | String | Yes | Primary contact phone (for WhatsApp/IVR) |
| `alt_phone` | String | No | Secondary contact |
| `language` | Enum | Yes | Preferred language (Hindi, Marathi, Telugu, Tamil, etc.) |
| `literacy_level` | Enum | Yes | None, Low, Medium, High — affects content format |
| `created_at` | Timestamp | Yes | Record creation |
| `updated_at` | Timestamp | Yes | Last modification |
| `consent_status` | Enum | Yes | None, Pending, Given, Withdrawn |

### 1.2 Demographic Attributes

| Field | Type | Required | Description |
|---|---|---|---|
| `category` | Enum | No | General, SC, ST, OBC, Other |
| `gender` | Enum | Yes | Male, Female, Other |
| `age_group` | Enum | Yes | 18-30, 31-45, 46-60, 60+ |
| `education_years` | Integer | No | Years of formal education |

### 1.3 Address

| Field | Type | Required | Description |
|---|---|---|---|
| `village` | String | Yes | Village name |
| `block` | String | Yes | Block/Taluka name |
| `district` | String | Yes | District name |
| `state` | Enum | Yes | State code |
| `pincode` | String | Yes | 6-digit PIN code |
| `geo_lat` | Float | No | GPS latitude |
| `geo_lon` | Float | No | GPS longitude |

---

## 2. Land Holding Entity

### 2.1 Primary Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `holding_id` | UUID | Yes | Unique holding identifier |
| `farmer_id` | UUID | Yes | FK to Farmer |
| `plot_number` | String | Yes | As per land records |
| `area_hectares` | Float | Yes | Total area in hectares |
| `area_acre` | Float | No | Area in acres (computed) |
| `irrigation_type` | Enum | Yes | Rainfed, Well, Canal, Tank, Mixed |
| `soil_type` | String | No | Reference to soil type classification |
| `land_tenure` | Enum | Yes | Owner, Tenant, Lease, Community |

### 2.2 Irrigation Details

| Field | Type | Required | Description |
|---|---|---|---|
| `water_source_primary` | Enum | Yes | Well, Borewell, Canal, Rainwater, Tank |
| `water_source_secondary` | Enum | No | Backup water source |
| `groundwater_depth_m` | Float | No | Current groundwater depth |
| `water_quality` | Enum | No | Fresh, Saline, Alkaline |
| `irrigation_infrastructure` | List[Enum] | No | Drip, Sprinkler, Flood, Furrow |

### 2.3 Soil Data Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `soil_health_card_id` | String | No | SHC number if issued |
| `shc_issue_date` | Date | No | When SHC was issued |
| `n_level` | Enum | No | Low, Medium, High, Very High |
| `p_level` | Enum | No | Low, Medium, High, Very High |
| `k_level` | Enum | No | Low, Medium, High, Very High |
| `ph` | Float | No | Soil pH |
| `oc_percent` | Float | No | Organic carbon percentage |
| `micronutrient_status` | JSON | No | {zinc: ..., boron: ..., iron: ...} |

---

## 3. Crop Cycle Entity

### 3.1 Season Model

India has **two primary seasons** + **irrigated winter**:

| Season | Local Names | Typical Period |
|---|---|---|
| Kharif | Rainy season, Monsoon | June–October |
| Rabi | Winter season | October–March |
| Zaid | Summer/irrigated | March–June |

### 3.2 Crop Cycle Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `cycle_id` | UUID | Yes | Unique cycle identifier |
| `holding_id` | UUID | Yes | FK to Land Holding |
| `season` | Enum | Yes | Kharif, Rabi, Zaid |
| `year` | Integer | Yes | Crop year |
| `crop_code` | String | Yes | Crop identifier (NPCS standard) |
| `crop_name` | String | Yes | Crop name in local language |
| `variety` | String | No | Variety/ cultivar |
| `sowing_date` | Date | No | Actual/predicted sowing date |
| `expected_harvest_date` | Date | No | Expected harvest window |
| `actual_harvest_date` | Date | No | When actually harvested |
| `area_sown_hectares` | Float | Yes | Area planted with this crop |
| `status` | Enum | Yes | Planned, Sown, Growing, Harvested, Failed |

### 3.3 Crop Operations Log

| Field | Type | Required | Description |
|---|---|---|---|
| `operation_id` | UUID | Yes | Unique operation identifier |
| `cycle_id` | UUID | Yes | FK to Crop Cycle |
| `operation_type` | Enum | Yes | Sowing, Irrigation, Fertilizer, Pesticide, Harvest |
| `operation_date` | Date | Yes | When performed |
| `input_used` | JSON | No | {type, quantity, cost} |
| `notes` | String | No | Free-text notes |

---

## 4. Income & Market Entity

### 4.1 Harvest Record

| Field | Type | Required | Description |
|---|---|---|---|
| `harvest_id` | UUID | Yes | Unique harvest identifier |
| `cycle_id` | UUID | Yes | FK to Crop Cycle |
| `production_kg` | Float | Yes | Total production in kg |
| `production_quintal` | Float | No | In quintals (computed) |
| `quality_grade` | Enum | No | A, B, C, Ungraded |
| `harvest_date` | Date | Yes | When harvested |
| `storage_used` | Boolean | Yes | Was harvest stored? |
| `storage_duration_days` | Integer | No | How long stored |

### 4.2 Sales Record

| Field | Type | Required | Description |
|---|---|---|---|
| `sale_id` | UUID | Yes | Unique sale identifier |
| `harvest_id` | UUID | Yes | FK to Harvest |
| `sale_date` | Date | Yes | When sold |
| `buyer_type` | Enum | Yes | Arthiya, Mandi, Processor, Direct, FPO |
| `buyer_name` | String | No | If known |
| `quantity_kg` | Float | Yes | Quantity sold |
| `price_per_kg` | Float | Yes | Price received |
| `total_value` | Float | Yes | Computed: quantity × price |
| `payment_timing` | Enum | Yes | Immediate, WithinWeek, WithinMonth, Delayed |
| `distress_sale_flag` | Boolean | Yes | Was this a distress sale? |

### 4.3 Distress Sale Definition

A sale is flagged as **distress sale** if ANY of:
- Sale within 7 days of harvest
- Sale at >20% below prevailing mandi price
- Sale to avoid spoilage with no storage option
- Sale to repay urgent debt/obligation

---

## 5. Scheme Eligibility Entity

### 5.1 Enrollment Status

| Field | Type | Required | Description |
|---|---|---|---|
| `enrollment_id` | UUID | Yes | Unique enrollment record |
| `farmer_id` | UUID | Yes | FK to Farmer |
| `scheme_code` | String | Yes | PM-KISAN, SHC, PMFBY, etc. |
| `status` | Enum | Yes | Eligible, Enrolled, Rejected, Excluded |
| `exclusion_reason` | String | No | Why excluded (land record error, etc.) |
| `enrollment_date` | Date | No | When enrolled |
| `last_payment_date` | Date | No | Last benefit received |
| `last_payment_amount` | Float | No | Amount of last payment |

---

## 6. Computed Farmer Segments

### 6.1 Farm Size Classification

| Segment | Size | Description |
|---|---|---|
| Marginal | <1 ha | Most vulnerable, least connected |
| Small | 1-2 ha | Limited buffer capacity |
| Semi-medium | 2-4 ha | Some commercial potential |
| Medium | 4-10 ha | Can benefit from advisory |
| Large | >10 ha | Direct app users possible |

### 6.2 Commercial Orientation Index

Computed per farmer based on:
- % of production sold vs consumed
- Use of purchased inputs (vs own seed/ manure)
- Use of hired labor
- Crop choice (commercial vs subsistence)

---

## 7. Data Silos Problem

### 7.1 Current Government Data Sources

| Source | Data Available | Access Method |
|---|---|---|
| Soil Health Card DB | N, P, K, pH, OC for ~230M farmers | API (restricted) |
| PM-KISAN | Land records, payment history | API (restricted) |
| e-NAM | Mandi transactions (modal prices) | Public dashboard |
| PMFBY | Enrollment, area insured, claims | API (restricted) |
| Kisan Credit Card | Credit limits, drawals | Not accessible |

### 7.2 The Fragmentation Problem

- **No farmer-level unified view**: Same farmer appears in multiple systems with different IDs
- **Linkage key**: Aadhaar or land plot number as unique key
- **Data quality**: Land records incomplete in many states (Bihar, Jharkhand worst)
- **Temporal inconsistency**: Records updated at different frequencies

### 7.3 Platform Approach

The platform does NOT replace these systems. Instead:
1. **Read** from government APIs (where accessible)
2. **Augment** with farmer self-reported or field-collected data
3. **Serve** through channel partners who interact with farmers
4. **Update** government systems when farmer makes scheme applications through platform

---

## 8. Edge Cases

### 8.1 Tenant Farmers
- Often not in land records → excluded from PM-KISAN
- Platform model: track separately, flag as "tenant", help with lease agreement documentation

### 8.2 Multiple Land Holdings
- Same farmer may have plots in different villages/states
- Model: multiple Land Holding records per Farmer

### 8.3 Joint Land Ownership
- Land in multiple names
- Model: multiple Farmer IDs linked to same holding with ownership share

### 8.4 Migrant Farmers
- Farm in one location, live in another
- Model: separate "farm location" from "residence address"

### 8.5 Female Farmers
- Often not primary name on land records
- Model: track "cultivator" vs "landowner" distinction

---

## 9. Constraints

### 9.1 Data Privacy
- Aadhaar data: hash only, never store raw
- Consent required before any government data access
- Farmer can request data export or deletion

### 9.2 Data Quality
- Self-reported data must be flagged as "unverified"
- Government data must be flagged as "government-source"
- Contradictions between sources must be surfaced, not hidden

### 9.3 Offline Capability
- All entity data must be cacheable locally
- Sync conflict resolution: last-write-wins with timestamp
- Never block on data sync — farmer interaction continues offline

---

*Spec authority: Farmer & Farm Entity Model*
*Version: 1.0*
