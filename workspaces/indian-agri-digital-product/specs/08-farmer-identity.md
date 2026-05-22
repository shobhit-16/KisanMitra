# Domain Spec: Farmer Identity & Consent Management

## Overview

This spec addresses farmer identity verification and consent management — foundational infrastructure for the entire platform. Given the sensitive nature of agricultural data and the precedent of the 2022 Agristack breach (140M farmer records), identity and consent management is critical for building farmer trust.

---

## 1. Identity Landscape

### 1.1 Current Identity Systems

| System | ID | Coverage | Issues |
|---|---|---|---|
| Aadhaar | 12-digit UID | ~95% adults | Privacy concerns, mandatory linking |
| Land Records | Khatauni/Khesra | ~60% rural | Incomplete, outdated |
| Voter ID | EPIC | ~80% adults | Not farm-linked |
| Ration Card | 13-digit | ~90% households | Not unique to farmer |
| PM-KISAN | Generated | 114M families | Land record dependent |

### 1.2 Agristack

**What it is:**
- Government initiative to create unique farmer ID linked to land records
- Components:
  1. Farmer ID (unique, persistent)
  2. Geo-referenced cadastral maps
  3. Crop sown survey
  4. Land record digitization

**Current status:**
- Pilot in some states
- Privacy concerns due to mandatory Aadhaar linking
- 2022 data breach exposed 140M farmer records

### 1.3 Platform Identity Approach

**We do NOT create a new ID system.** We:
1. **Link to existing IDs** (Aadhaar hash, PM-KISAN ID, state farmer ID)
2. **Build our own farmer graph** with internal UUID
3. **Never store raw Aadhaar numbers**
4. **Require explicit consent** before any data sharing

---

## 2. Identity Model

### 2.1 Farmer Identity Record

```python
class FarmerIdentity:
    # Internal platform ID (UUID)
    platform_id: UUID

    # Linkage keys (hashed, never raw)
    aadhaar_hash: str          # SHA-256 of Aadhaar (if provided)
    pm_kisan_id: str           # Government PM-KISAN ID
    state_farmer_id: str       # State-specific farmer ID (if exists)
    land_record_id: str        # Khatauni/Khesra number

    # Verification status
    verification_status: Enum
    # None: Unverified
    # Aadhaar Verified: Aadhaar OTP confirmed
    # Land Verified: Land records cross-checked
    # Full Verified: Both + in-person verification

    # Consent records
    consents: List[ConsentRecord]

    # Created, updated timestamps
    created_at: datetime
    updated_at: datetime
```

### 2.2 Verification Levels

| Level | Verification Method | Data Access |
|---|---|---|
| **Unverified** | Phone number only | Basic (village, crop type) |
| **Phone Verified** | OTP to mobile | Basic + prices |
| **Aadhaar Hash** | Aadhaar OTP | Extended (scheme eligibility) |
| **Land Verified** | Land record match | Full (schemes, credit) |
| **Full Verified** | In-person by agent | Complete access |

### 2.3 Aadhaar Handling

**We NEVER store raw Aadhaar numbers.**

```python
def hash_aadhaar(aadhaar_number: str) -> str:
    # Remove spaces/hyphens
    cleaned = re.sub(r'[\s-]', '', aadhaar_number)
    # Validate 12 digits
    if not re.match(r'^\d{12}$', cleaned):
        raise ValueError("Invalid Aadhaar format")
    # Return SHA-256 hash
    return hashlib.sha256(cleaned.encode()).hexdigest()

def verify_aadhaar_otp(aadhaar_hash: str, otp: str) -> bool:
    # Use Aadhaar OTP API (UIDAI)
    # Returns True if OTP matches, False otherwise
    # We never see or store the Aadhaar number
    pass
```

---

## 3. Consent Management

### 3.1 Consent Model

```python
class ConsentRecord:
    consent_id: UUID
    platform_id: UUID          # Farmer
    institution_id: UUID        # Who data is shared with
    consent_type: ConsentType  # What data is shared
    granted_at: datetime
    expires_at: datetime        # Most consents expire 1 year
    revoked_at: datetime | None
    ip_address: str
    channel: str               # How consent was given (IVR, WhatsApp, App)

class ConsentType(Enum):
    BASIC_PROFILE = "basic_profile"       # Name, phone, village
    LAND_DETAILS = "land_details"        # Land size, soil type
    CROP_DATA = "crop_data"              # Crop cycles, yields
    FINANCIAL = "financial"              # Income estimates, scheme payments
    CREDIT_HISTORY = "credit_history"    # Loan applications, repayments
    LOCATION = "location"                # GPS coordinates
    ALL_DATA = "all_data"               # Everything
```

### 3.2 Consent Flow

```
[Farmer initiates action requiring data sharing]
           ↓
[Explain what data will be shared]
"Bank XYZ wants to see your land details and crop history
to assess your loan eligibility."
           ↓
[Show data that will be shared — in farmer's language]
"Bank will see: Your name, phone, village, land size,
crop types, and PM-KISAN payment history."
           ↓
[Ask for consent]
"Do you allow this? Reply YES to allow, NO to decline."
           ↓
[Record consent]
If YES: Record consent with timestamp, notify institution
If NO: Return error to institution, farmer sees no impact
```

### 3.3 Consent Via Channel

| Channel | Consent Method | Audit Trail |
|---|---|---|
| IVR | Voice recording + DTMF "press 1" | Call recording + log |
| WhatsApp | Interactive message with buttons | Message log |
| App | Checkbox + OTP | User action log |
| In-person | Paper form + agent attestation | Scanned document |

### 3.4 Consent Revocation

**Farmer can revoke consent at any time:**
- Via IVR: "I want to revoke my consent for bank"
- Via WhatsApp: Send "REVOKE"
- Via App: Settings → Data Sharing → Revoke
- Via Agent: Agent submits revocation request

**Effect of revocation:**
- Institution notified within 24 hours
- Institution must stop using data within 30 days
- Farmer's data access removed from institution's dashboard

---

## 4. Data Classification

### 4.1 Data Sensitivity Levels

| Level | Data | Examples | Sharing |
|---|---|---|---|
| **Public** | Aggregate, non-identifying | District crop statistics | Anyone |
| **Basic** | Identifying, non-sensitive | Name, village, crop type | With consent |
| **Sensitive** | Financial, locational | Land records, bank details | Explicit consent only |
| **Restricted** | Aadhaar, biometric | Raw Aadhaar, biometric | Never shared externally |

### 4.2 Data Retention

| Data Type | Retention | Disposal |
|---|---|---|
| Basic profile | Until revoked | Delete on request |
| Land records | 7 years after last update | Secure delete |
| Crop data | 7 years | Secure delete |
| Consent records | 7 years | Audit archive only |
| Transaction logs | 3 years | Delete |

---

## 5. Privacy by Design

### 5.1 Privacy Principles

1. **Data minimization**: Collect only what's needed
2. **Purpose limitation**: Use data only for stated purpose
3. **Consent**: Never share without explicit consent
4. **Security**: Encrypt at rest and in transit
5. **Transparency**: Farmer can see all data shared

### 5.2 Technical Safeguards

```python
class PrivacyEngine:

    def check_access(self, institution_id, data_type, purpose) -> bool:
        # Does institution have consent for this data type?
        consent = self.consent_manager.get_active_consent(
            institution_id=institution_id,
            data_type=data_type
        )
        if not consent:
            return False

        # Does purpose match consent purpose?
        if not self.purpose_compatible(consent.purpose, purpose):
            return False

        return True

    def audit_access(self, log_entry):
        # Log all data access for farmer review
        self.audit_log.insert(log_entry)

        # Alert on unusual patterns
        if self.is_anomalous_access(log_entry):
            self.flag_for_review(log_entry)
```

### 5.3 Farmer Data Portal

**Every farmer can see:**
- What data we hold about them
- Which institutions have accessed their data
- What consent they've given
- Download their data

```
┌─────────────────────────────────────────────────────────────┐
│  Your Data — FarmWise                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📋 Your Profile                                           │
│  Name: Ramesh Kumar                                        │
│  Village: Rampur, Block: Dibiyapur, Dist: Auraiya          │
│  Phone: 98765XXXXX                                         │
│  [Edit Profile]                                            │
│                                                             │
│  🤝 Data Sharing                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Kisan Bank                                           │  │
│  │ Access: Land details, crop data                      │  │
│  │ Given: Jan 2024 | Expires: Jan 2025                  │  │
│  │ [Revoke]                                             │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ AgroCorp India                                       │  │
│  │ Access: Basic profile only                            │  │
│  │ Given: Mar 2024 | Expires: Mar 2025                  │  │
│  │ [Revoke]                                             │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  📥 Download Your Data                                     │
│  [Download as PDF] [Download as CSV]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Security

### 6.1 Data Encryption

- **At rest**: AES-256 encryption for all stored data
- **In transit**: TLS 1.2+ for all API calls
- **Key management**: AWS KMS / HashiCorp Vault

### 6.2 Access Control

- Role-based access control (RBAC)
- Multi-factor authentication for internal systems
- IP whitelist for server access
- Audit logs for all admin access

### 6.3 Breach Response

| Scenario | Response |
|---|---|
| Farmer data accessed without consent | Notify farmer within 72 hours; investigate; terminate institution |
| Platform breach | Notify all affected farmers; regulatory compliance; security audit |
| Institution breach | Notify platform; farmer notification; contract termination |

---

## 7. Agristack Integration

### 7.1 Integration Approach

Once Agristack APIs are available and stable:
1. **Read-only** access to farmer and land data
2. **Consent-gated** — farmer must approve linking
3. **Verification only** — not storing Agristack data long-term
4. **Fallback** — if Agristack unavailable, use other verification methods

### 7.2 Farmer ID Mapping

```python
class AgristackIntegration:

    async def link_farmer_id(self, platform_farmer_id, agristack_farmer_id):
        # Verify farmer consent for linking
        consent = await self.consent_manager.get_consent(
            platform_farmer_id,
            "agrisatck_link"
        )
        if not consent.granted:
            raise ConsentRequiredError()

        # Verify farmer identity via OTP
        if not await self.verify_identity(platform_farmer_id):
            raise IdentityNotVerifiedError()

        # Create linkage record
        await self.db.link_farmer_ids(
            platform_id=platform_farmer_id,
            agristack_id=agristack_farmer_id,
            linked_at=datetime.now()
        )
```

---

## 8. Edge Cases

### 8.1 Farmer Disputes Identity Linkage
- Farmer claims wrong data linked to their ID
- Process: Identity verification + data audit + correction
- Timeline: 15 days resolution

### 8.2 Institution Claims Fraudulent Consent
- Institution claims farmer gave consent but farmer denies
- Burden of proof on institution to show consent record
- Platform mediates with consent audit log as evidence

### 8.3 Deceased Farmer
- Data retained per legal requirements (7 years)
- Family can request data closure
- No new consent can be given

### 8.4 Minor Farmer (Under 18)
- Cannot give consent
- Parent/guardian consent required
- Limited to basic profile data

---

## 9. Compliance

### 9.1 Relevant Regulations

| Regulation | Requirement |
|---|---|
| IT Act 2000 + SPDI Rules | Data accuracy, security, purpose limitation |
| Aadhaar Act 2016 | Aadhaar data handling (if applicable) |
| PDP Bill (proposed) | Consent, data principal rights, breach notification |
| RBI Guidelines | Credit data sharing |
| ICAR Data Guidelines | Agricultural research data |

### 9.2 Data Principal Rights

Under proposed data protection:
- Right to access: Farmer can see all data
- Right to correction: Farmer can correct errors
- Right to deletion: Farmer can request deletion (subject to legal retention)
- Right to portability: Farmer can export data
- Right to Grievance: Redressal mechanism required

---

## 10. Metrics

| Metric | Target |
|---|---|
| Farmer verification rate | >70% with phone |
| Consent audit completion | 100% |
| Data access compliance | >99% |
| Breach notification time | <72 hours |
| Farmer data portal usage | >30% of active farmers |

---

*Spec authority: Farmer Identity & Consent Management*
*Version: 1.0*
