# Domain Spec: Government Scheme Access Facilitation

## Overview

This spec addresses the gap between government agricultural schemes (PM-KISAN, Soil Health Card, PMFBY, etc.) and the farmers who need them. The goal is NOT to replace government systems, but to **reduce exclusion errors** and **increase effective coverage** of existing schemes.

---

## 1. Scheme Landscape

### 1.1 Major Agricultural Schemes

| Scheme | Ministry | Benefit | Coverage | Key Problem |
|---|---|---|---|---|
| PM-KISAN | Agriculture | ₹6,000/year | 114M families | 15-25% payment failures |
| PMFBY | Agriculture | Crop insurance | 13.5M (declining) | Basis risk, delayed claims |
| Soil Health Card | Agriculture | Soil testing | 230M farmers issued | 15-18% usage |
| Kisan Credit Card | Agriculture | Credit @ 4% | ~70M cards | Formal credit exclusion |
| PMKSY | Agriculture | Irrigation investment | Ongoing | Slow implementation |
| FPO Promotion | Agriculture | Group formation | 5,000+ FPOs | Most non-functional |

### 1.2 Why Farmers Are Excluded

**PM-KISAN Exclusion Reasons:**
| Reason | % of Exclusions |
|---|---|
| Land record errors | 40-50% |
| Aadhaar linkage issues | 15-20% |
| Tenant farmers (not in land records) | 20-25% |
| Bank account issues | 10-15% |
| Other documentation | 5-10% |

**PMFBY Exclusion Reasons:**
| Reason | % of Non-Enrollment |
|---|---|
| Lack of awareness | 78% |
| Distrust of insurance | 65% |
| Basis risk (area not matching farm) | 45% |
| Complex procedures | 40% |
| Premium affordability | 25% |

---

## 2. Eligibility Engine

### 2.1 Eligibility Rules by Scheme

```python
class EligibilityEngine:

    def check_pm_kisan(self, farmer: Farmer, land: LandHolding) -> dict:
        # Basic eligibility
        if farmer.age < 18:
            return {"eligible": False, "reason": "Age below 18"}

        if land.area_hectares > 2:
            return {"eligible": False, "reason": "Land holding exceeds 2 ha"}

        # Land record validation
        land_record_status = self.verify_land_record(farmer.aadhaar, land.plot_number)

        if land_record_status == "not_found":
            # Tenant farmer scenario
            if self.is_tenant(farmer):
                return {
                    "eligible": False,
                    "reason": "Tenant farmers not eligible",
                    "action": "Explore state-specific alternatives"
                }
            else:
                return {
                    "eligible": False,
                    "reason": "Land records not found; need correction",
                    "action": "Visit patwari with land documents"
                }

        if land_record_status == "name_mismatch":
            return {
                "eligible": False,
                "reason": "Land records don't match Aadhaar name",
                "action": "Submit name correction at tehsil"
            }

        # Bank account validation
        if not self.has_valid_bank_account(farmer):
            return {
                "eligible": False,
                "reason": "Bank account not linked or invalid",
                "action": "Update bank details at PM-KISAN portal"
            }

        return {"eligible": True}

    def check_pm_fby(self, farmer: Farmer, land: LandHolding, crop: CropCycle) -> dict:
        # PMFBY eligibility
        if not self.has_loanee_account(farmer):
            # Non-loanee can apply but procedurally complex
            return {"eligible": True, "note": "Non-loanee path more complex"}

        if land.irrigation_type == "rainfed":
            return {"eligible": True, "note": "Rainfed crops have lower premium"}

        return {"eligible": True}
```

### 2.2 Document Checklist Generator

For each scheme, generate a personalized document checklist:

```python
def generate_document_checklist(scheme: str, farmer: Farmer, exclusion_reason: str) -> list:
    base_docs = {
        "PM-KISAN": [
            "Aadhaar card",
            "Land records (Khatauni)",
            "Bank passbook",
            "Passport photo"
        ],
        "PMFBY": [
            "Aadhaar card",
            "Land records",
            "Sowing certificate from village official",
            "Bank account details"
        ],
        "Soil Health Card": [
            "Land location details",
            "GPS coordinates (if available)",
            "Aadhaar (for digital card)"
        ]
    }

    # Add scheme-specific based on exclusion reason
    if exclusion_reason == "name_mismatch":
        base_docs["PM-KISAN"].append("Name correction document")

    if exclusion_reason == "tenant":
        base_docs["PM-KISAN"].append("Lease agreement (if available)")
        base_docs["PM-KISAN"].append("Affidavit for tenant cultivation")

    return base_docs.get(scheme, [])
```

---

## 3. Enrollment Assistance

### 3.1 Application Journey

```
[Farmer identifies as potentially eligible]
         ↓
[Platform checks basic eligibility criteria]
         ↓
[If eligible → generate document checklist]
         ↓
[If excluded → identify specific exclusion reason]
         ↓
[If exclusion fixable → provide correction path]
         ↓
[If tenant/land record issue → explore alternatives]
         ↓
[Help with application submission]
         ↓
[Track application status]
         ↓
[Alert when payment/benefit received]
```

### 3.2 Grievance Redressal

| Exclusion Type | Correction Path | Timeline |
|---|---|---|
| Land record error | Visit Patwari with documents | 2-4 weeks |
| Aadhaar mismatch | Update at Aadhaar center | 1-2 weeks |
| Bank account issue | Update at bank + PM-KISAN portal | 2-4 weeks |
| Name correction | Tehsil office | 4-8 weeks |

### 3.3 Status Tracking

For submitted applications:

| Status | Description | Next Action |
|---|---|---|
| Submitted | Application received | Wait for processing |
| Under Review | Being verified | Follow up with local office |
| Approved | Eligible, awaiting payment | Expect payment in 1-2 months |
| Rejected | Not eligible | Get reason; if wrong, appeal |
| Payment Pending | Approved, payment initiated | Check bank account |
| Payment Failed | Payment rejected | Check bank details |

---

## 4. Tenant Farmer Pathways

### 4.1 The Tenant Farmer Problem

**Scale**: ~20% of cultivated land in India is under tenant cultivation
**Exclusion**: Tenants are NOT eligible for PM-KISAN, KCC, or most schemes

**Why this matters**: Tenants are often the MOST marginalized farmers (landless or near-landless)

### 4.2 Alternative Pathways

| State | Scheme/Provision | Tenant Access |
|---|---|---|
| West Bengal | Svadeshi | Cultivator certificate for scheme access |
| Karnataka | Raitha Siri | Some provisions for tenant farmers |
| Odisha | Kalia | Cultivator certificate accepted |
| Bihar | CM-KISAN | State scheme with tenant provisions |

### 4.3 Platform Support for Tenants

- Track tenant status separately
- Recommend states with tenant-inclusive schemes
- Help obtain cultivator certificate where available
- Flag when tenant farmer applies (not eligible for some schemes)

---

## 5. Women Farmer Access

### 5.1 Barriers Women Face

| Barrier | Description |
|---|---|
| Land in male name | Women listed as "member" not "head" |
| Can't approach government offices | Social barriers, mobility restrictions |
| Limited mobile ownership | Primary phone often male-owned |
| Lower literacy | Form filling is challenge |
| Male family member as intermediary | Information filtered/biased |

### 5.2 Platform Approach for Women

- Track female farmers separately
- Allow alternate contact (husband's phone as secondary)
- Audio/IVR content (overcomes literacy)
- Village-level camps (where women can access in group)
- Female field staff for registration help

---

## 6. Scheme Benefit Calculator

### 6.1 Benefit Estimation

```python
def estimate_scheme_benefits(farmer: Farmer) -> dict:
    schemes = []

    # PM-KISAN
    if check_eligibility_pm_kisan(farmer):
        schemes.append({
            "scheme": "PM-KISAN",
            "annual_benefit": 6000,
            "frequency": "3 installments of ₹2000",
            "next_payment": "₹2000 within 30 days if enrolled"
        })

    # PMFBY (if crop cycle exists)
    if farmer.active_crop:
        premium = estimate_premium(farmer.active_crop)
        sum_insured = estimate_sum_insured(farmer.active_crop)
        schemes.append({
            "scheme": "PMFBY",
            "annual_cost": premium,
            "coverage": sum_insured,
            "note": "Claim if yield loss >10%"
        })

    # KCC
    if check_eligibility_kcc(farmer):
        credit_limit = estimate_kcc_limit(farmer)
        schemes.append({
            "scheme": "Kisan Credit Card",
            "credit_available": credit_limit,
            "interest_rate": "4% for up to 3 lakh"
        })

    return {
        "total_annual_benefit": sum(s['annual_benefit'] for s in schemes),
        "schemes": schemes
    }
```

### 6.2 What ₹6,000 PM-KISAN Means

- For a marginal farmer with 0.5 ha: ~15-20% of annual income
- Can cover: 1 quintal of wheat seed + part of fertilizer cost
- Not transformative alone, but meaningful for subsistence farmers

---

## 7. Scheme Discovery

### 7.1 Personalized Scheme Recommendations

Based on farmer profile, suggest applicable schemes:

```python
def recommend_schemes(farmer: Farmer, land: LandHolding) -> list:
    schemes = []

    # Always check PM-KISAN
    if land.area_hectares <= 2:
        schemes.append("PM-KISAN")

    # PMFBY if crop cycle exists
    if farmer.crop_cycles and is_insurable_crop(farmer.crop_cycles[0]):
        schemes.append("PMFBY")

    # KCC if not already issued
    if not farmer.has_kcc:
        schemes.append("Kisan Credit Card")

    # Soil Health Card if not received or expired (>2 years)
    if not farmer.has_valid_shc:
        schemes.append("Soil Health Card")

    # FPO membership if farmer is small/marginal
    if land.area_hectares <= 2 and not farmer.is_fpo_member:
        schemes.append("FPO Membership")

    # State-specific schemes
    state_schemes = get_state_schemes(farmer.state)
    for scheme in state_schemes:
        if is_eligible(farmer, scheme):
            schemes.append(scheme)

    return schemes
```

### 7.2 Scheme Gaps

**Gaps platform can help fill:**
| Gap | Platform Role |
|---|---|
| Farmer doesn't know scheme exists | Awareness + eligibility check |
| Farmer knows but doesn't apply | Application assistance |
| Farmer applies but gets rejected | Grievance redressal |
| Farmer approved but doesn't get payment | Status tracking + escalation |

---

## 8. Integration with Government APIs

### 8.1 API Access (where available)

| System | Data Available | Access Method |
|---|---|---|
| PM-KISAN | Beneficiary status, payment history | Registered API |
| Soil Health Card | Card data, test results | Registered API |
| e-NAM | Transaction data | Open API |
| PMFBY | Enrollment, claims | Restricted API |

### 8.2 Data Quality Handling

Government data is often:
- Out of date (land records from 1980s surveys)
- Inconsistent across states
- Missing tenant farmers
- Aadhaar linkage incomplete

**Platform approach:**
- Don't trust any single government source
- Cross-validate with multiple sources
- Flag discrepancies, don't hide them
- Allow farmer self-correction with documentation

---

## 9. FPO Scheme Access

### 9.1 FPO-Specific Benefits

FPOs can access:
- Bulk input procurement (cheaper)
- Bulk storage facilities
- Direct market access (skipping arthiya)
- Processing infrastructure
- Export market access

### 9.2 FPO Member Scheme Benefits

When farmer joins FPO:
- FPO can apply for collective scheme benefits
- FPO provides aggregation and marketing support
- FPO can negotiate better prices

---

## 10. Metrics

### 10.1 Access Improvement Metrics

| Metric | Baseline | Target |
|---|---|---|
| PM-KISAN payment failure rate | 15-25% | <5% |
| Scheme awareness (targeted farmer) | 40% | >80% |
| Successful enrollment rate | 60% | >85% |
| Time to enrollment | 2-3 months | <1 month |

### 10.2 Platform Metrics

| Metric | Target |
|---|---|
| Eligibility check completions | >50% of active farmers |
| Application submissions facilitated | >25% of eligible |
| Successful payments tracked | >80% of enrolled |
| Exclusion error identification | >30% of rejected cases |

---

## 11. Edge Cases

### 11.1 Farmer Has No Land Records
- Common in tribal areas, some eastern states
- Can apply for "Khatauni" creation
- May need community land records
- Slower process (6-12 months)

### 11.2 Farmer's Name Doesn't Match Documents
- Common for women (married name change)
- Needs legal name correction
- Platform helps identify which document is wrong

### 11.3 Farmer Applied But Status Unknown
- Track via application number
- Escalate to local district officials if stuck >3 months
- Document for future reference

---

*Spec authority: Government Scheme Access Facilitation*
*Version: 1.0*
