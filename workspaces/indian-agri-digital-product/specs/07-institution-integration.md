# Domain Spec: B2B Institution Integration Platform

## Overview

This spec defines the B2B platform layer — how institutions (banks, input companies, food processors, FPOs, government bodies) integrate with the platform to reach and serve farmers. This is the **revenue model** — institutions pay for farmer access and engagement.

---

## 1. Platform Business Model

### 1.1 B2B2F Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     INSTITUTIONS (Paying Customers)           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │    Banks     │ │Input Companies│ │ Processors   │  ...   │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘        │
│         │                │                │                  │
│         │   APIs / SDKs / Webhooks                               │
└─────────┼────────────────┼────────────────┼──────────────────┘
          │                │                │
          ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                    PLATFORM CORE LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Farmer Graph │ Climate │ Markets │ Soil │ Schemes    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Channel Delivery (IVR, WhatsApp, App, Agent App)     │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                     FARMERS (End Users)                       │
│  Marginal ──────► IVR + Agent                              │
│  Small ─────────► WhatsApp + IVR                           │
│  Commercial ────► App + WhatsApp                           │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Revenue Model

| Revenue Type | Description | Unit Economics |
|---|---|---|
| **Platform Access Fee** | Base fee for API access | ₹50,000-5,00,000/year per institution |
| **Farmer Reach Fee** | Per farmer reached/engaged | ₹5-20/farmer/quarter |
| **Transaction Fee** | Per scheme enrollment, loan disbursed, etc. | ₹50-500/transaction |
| **Data Insights** | Aggregated analytics on farmer behavior | ₹1-5L/year |

### 1.3 Pricing Example

| Institution | Use Case | Estimated Annual Spend |
|---|---|---|
| Small bank | Crop loan targeting | ₹2-5L |
| Input company | Distributor network enablement | ₹5-15L |
| Food processor | Contract farming traceability | ₹10-30L |
| State govt | Scheme enrollment push | ₹10-50L |

---

## 2. API Architecture

### 2.1 API Design Principles

- **RESTful** with JSON payloads
- **Versioned** (v1, v2) with deprecation policy
- **Authenticated** via OAuth 2.0 or API keys
- **Rate-limited** to prevent abuse
- **Logged** for audit and debugging

### 2.2 Core APIs

```yaml
# Farmer Data API
/farmers:
  GET /farmers                    # List farmers (paginated)
  GET /farmers/{farmer_id}        # Get farmer profile
  POST /farmers                   # Register new farmer
  PATCH /farmers/{farmer_id}      # Update farmer

/climate:
  GET /climate/weather/{location}    # Current + forecast weather
  GET /climate/advisories/{farmer_id} # Active advisories for farmer
  POST /climate/feedback              # Submit advisory feedback

/markets:
  GET /markets/prices/{commodity}     # Current prices
  GET /markets/trends/{commodity}     # Price trends
  GET /markets/mandis                 # Nearby mandis

/soils:
  GET /soils/{farmer_id}             # Soil health data
  GET /soils/recommendations/{farmer_id}  # Input recommendations

/schemes:
  GET /schemes/eligibility/{farmer_id}   # Scheme eligibility
  POST /schemes/enrollments               # Submit enrollment
  GET /schemes/enrollments/{enrollment_id}/status  # Track status

/insights:
  GET /insights/farmer-segments      # Farmer segmentation
  GET /insights/advisory-performance # Advisory metrics
```

### 2.3 API Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 1234
    }
  },
  "errors": []
}
```

### 2.4 Error Handling

```json
{
  "success": false,
  "error": {
    "code": "FARMER_NOT_FOUND",
    "message": "Farmer with ID far_123 not found",
    "details": {
      "farmer_id": "far_123"
    }
  }
}
```

---

## 3. SDK Integration

### 3.1 SDK Packages

| Platform | Package | Use Case |
|---|---|---|
| Python | `agri-platform-python` | Backend integration |
| JavaScript/Node | `agri-platform-js` | Web apps, Node.js |
| Java | `agri-platform-java` | Android, enterprise |
| Flutter | `agri_platform_flutter` | Mobile apps |

### 3.2 SDK Example (Python)

```python
from agri_platform import AgriPlatform, FarmerProfile

# Initialize
agri = AgriPlatform(
    api_key="pk_live_xxxxx",
    environment="production"
)

# Get farmer profile
farmer = agri.farmers.get("far_123")

# Check scheme eligibility
eligibility = agri.schemes.check_eligibility(
    farmer_id="far_123",
    schemes=["pm_kisan", "pmfby"]
)

# Send custom advisory
agri.advisories.send(
    farmer_id="far_123",
    message="Weather alert: Heavy rain expected tomorrow. Delay pesticide spray.",
    channel="whatsapp"
)

# Get advisory feedback
feedback = agri.advisories.get_feedback(
    advisory_id="adv_456",
    limit=100
)
```

---

## 4. Partner Onboarding

### 4.1 Partner Types

| Partner Type | Onboarding Steps | Timeline |
|---|---|---|
| **Bank** | KYC, API provisioning, compliance review, sandbox testing | 4-8 weeks |
| **Input Company** | Company verification, API provisioning, go-live | 2-4 weeks |
| **Food Processor** | Company verification, integration, FPO linkage | 4-6 weeks |
| **FPO** | FPO verification, member onboarding, training | 2-4 weeks |
| **Government** | MOU, security review, data agreement, API access | 8-16 weeks |

### 4.2 Partner Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                  PARTNER DASHBOARD                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Overview                                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │ Farmers    │ │ Active     │ │ Trans-     │             │
│  │ Reached    │ │ Advisories │ │ actions    │             │
│  │ 45,230     │ │ 12,450     │ │ 234        │             │
│  └────────────┘ └────────────┘ └────────────┘             │
│                                                             │
│  Campaign Performance                                       │
│  [Chart: Farmers reached over time]                         │
│  [Chart: Advisory engagement rate]                         │
│                                                             │
│  Recent Activity                                            │
│  • Kisan Bank: 1,230 new farmer inquiries (today)         │
│  • AgroCorp: 45 scheme enrollments (this week)           │
│  • FreshFoods: 12 contract farming signups (today)       │
│                                                             │
│  API Usage                                                  │
│  [███████░░░] 70% of quota (7,000/10,000 calls)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Data Sharing & Consent

### 5.1 Consent Framework

**Principle**: Farmer controls their data. Institutions can only access data the farmer has consented to share.

```python
class ConsentManager:
    # Consent types
    CONSENT_BASIC = "basic"           # Name, location, crop (default)
    CONSENT_CLIMATE = "climate"        # Weather data, advisories
    CONSENT_MARKET = "market"          # Price data, market access
    CONSENT_SCHEME = "scheme"          # Government scheme participation
    CONSENT_LOAN = "loan"              # Credit history, loan applications

    def grant_consent(self, farmer_id, institution_id, consent_types):
        # Verify farmer is authenticated
        # Show consent explanation in farmer's language
        # Record consent with timestamp
        # Notify institution of consent grant

    def revoke_consent(self, farmer_id, institution_id):
        # Remove consent
        # Notify institution
        # Institution must stop using data within 30 days

    def get_consent_status(self, farmer_id, institution_id):
        # Return list of active consents
```

### 5.2 Data Access Levels

| Level | Data Available | Requires |
|---|---|---|
| **Public** | Crop type, region (no PII) | None |
| **Basic** | Name, phone, village, land size | Basic consent |
| **Extended** | Soil data, crop cycles, income | Explicit consent |
| **Full** | Aadhaar, bank details, transaction history | Special consent + verification |

### 5.3 Data Retention

- Institution must delete farmer data within 30 days of consent revocation
- Platform logs all data access for audit
- Annual consent renewal required for all partners

---

## 6. Compliance & Security

### 6.1 Data Privacy

- Farmer data protected under platform privacy policy
- Institutions are data processors under consent framework
- Regular audits of partner data handling
- Breach notification within 72 hours

### 6.2 API Security

```yaml
authentication:
  - OAuth 2.0 (recommended)
  - API Keys (simpler setup)
  - JWT tokens with 1-hour expiry

rate_limiting:
  default: 1000 requests/hour
  burst: 100 requests/minute

whitelisting:
  - IP whitelisting for server-to-server
  - Domain restriction for browser clients
```

### 6.3 Audit Trail

All data access is logged:
```json
{
  "event": "farmer_data_access",
  "farmer_id": "far_123",
  "institution_id": "inst_bank_456",
  "data_fields": ["name", "phone", "land_size"],
  "purpose": "crop_loan_assessment",
  "timestamp": "2024-01-15T10:30:00Z",
  "ip_address": "1.2.3.4"
}
```

---

## 7. Use Cases by Institution Type

### 7.1 Bank / Credit Provider

**Goal**: Target farmers for crop loans with better risk assessment

**Integration Points**:
- Farmer eligibility check (land size, crop, income estimate)
- Scheme enrollment (PM-KISAN adds to income proof)
- Advisory history (indicates farmer engagement level)
- KCC application facilitation

**Value**: Lower NPA through better targeting; higher loan disbursement

### 7.2 Input Company (Fertilizer/Seed/Pesticide)

**Goal**: Reach farmers with product recommendations and promotions

**Integration Points**:
- Soil data access (for targeted product recommendation)
- Crop stage data (for timing promotions)
- Advisory delivery (product integration in recommendations)
- Loyalty/reward tracking

**Value**: Better targeted marketing; reduced dealer dependency

### 7.3 Food Processor /Exporter

**Goal**: Ensure quality and traceability in supply chain

**Integration Points**:
- Contract farming enrollment
- Farm-level practice tracking
- Harvest quality documentation
- Payment tracking to farmers

**Value**: Guaranteed supply quality; farmer loyalty; export compliance

### 7.4 Insurance Company

**Goal**: Better risk selection and claims verification

**Integration Points**:
- Farm location risk data (flood, drought zones)
- Weather data for claims verification
- Yield estimates for area-yield claims
- Scheme enrollment (PMFBY linkage)

**Value**: Lower basis risk; faster claims processing

### 7.5 State Government / Department of Agriculture

**Goal**: Increase scheme coverage and reduce exclusion errors

**Integration Points**:
- Farmer identification and verification
- Scheme eligibility screening
- Enrollment application submission
- Payment tracking

**Value**: Higher coverage; reduced exclusion errors; better monitoring

---

## 8. Metrics & Reporting

### 8.1 Platform Metrics

| Metric | Description | Target |
|---|---|---|
| Institution count | Active paying institutions | 50+ by Year 2 |
| Revenue/run-rate | Monthly recurring revenue | ₹1Cr+ by Year 2 |
| Farmer reach | Unique farmers engaged | 1M+ by Year 2 |
| API uptime | Platform availability | >99.5% |
| API latency | Average response time | <200ms p95 |

### 8.2 Partner Metrics

| Metric | Description | Target |
|---|---|---|
| Farmer activation | Farmers who responded to institution's campaign | >30% |
| Engagement rate | Farmers with >3 interactions/month | >40% |
| Transaction rate | Campaigns resulting in transactions | >10% |
| NPS | Partner satisfaction score | >40 |

### 8.3 Farmer Welfare Metrics

| Metric | Description | Target |
|---|---|---|
| Income impact | Measured income improvement | >10% |
| Distress sale reduction | % farmers avoiding distress sales | >20% |
| Scheme coverage | % eligible farmers enrolled | >60% |
| Advisory adoption | % advisories resulting in action | >30% |

---

## 9. Edge Cases

### 9.1 Institution Misuses Data
- Monitor for unusual access patterns
- Auto-alert on bulk downloads
- Contractual penalties + termination for misuse

### 9.2 Farmer Complaints Against Institution
- Grievance redressal hotline
- Platform-mediated dispute resolution
- Institution rating/review system

### 9.3 Competing Institutions Want Same Farmer
- Farmer controls consent per institution
- No exclusivity requirements
- Institution sees only their consented data

### 9.4 Government Data Sharing Restrictions
- Some government data cannot be shared with private institutions
- Platform enforces data classification
- FPO and cooperative access may have different rules than banks

---

## 10. Integration Checklist

### For New Partner Onboarding:

- [ ] Company verification (PAN, GST, incorporation)
- [ ] Data Processing Agreement signed
- [ ] Privacy policy alignment
- [ ] API credentials issued
- [ ] Sandbox access provided
- [ ] Integration testing completed
- [ ] Go-live checklist signed off
- [ ] Support contacts exchanged
- [ ] SLA agreed (99.5% uptime, <200ms latency)
- [ ] Pricing agreement finalized

---

*Spec authority: B2B Institution Integration Platform*
*Version: 1.0*
