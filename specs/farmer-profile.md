# Farmer Profile — Domain Spec

**Spec File:** `farmer-profile.md`
**Domain:** Farmer Identity
**Phase:** 1
**Last Updated:** 2026-05-22

---

## Farmer Entity

### Attributes

| Field | Type | Required | Description |
|---|---|---|---|
| `phone` | string(10) | YES | Primary identifier — 10-digit Indian mobile |
| `name` | string | YES | Full name |
| `village` | string | YES | Village name |
| `block` | string | YES | Block/tehsil name |
| `district` | string | YES | District name — Nashik for pilot |
| `state` | string | YES | State — Maharashtra for pilot |
| `land_size` | float | YES | Land operated (hectares) |
| `land_tenure` | enum | YES | `OWNER`, `TENANT`, `SHARECROPPER` |
| `crop_type` | enum | YES | `RABI_ONION`, `KHARIF_PADDY`, `RABI_WHEAT`, `SUMMER_MAIZE` |
| `season` | enum | YES | `RABI`, `KHARIF`, `SUMMER` |
| `primary_language` | enum | YES | `MARATHI`, `HINDI`, `ENGLISH` |
| `created_at` | datetime | YES | Account creation timestamp |
| `updated_at` | datetime | YES | Last modification timestamp |
| `is_active` | bool | YES | Soft delete flag — default true |

### Constraints

- `phone` is unique index — no two farmers share same phone number
- `land_size` must be > 0 and ≤ 100 (max practical for Maharashtra)
- At pilot launch, only `district=NASHIK` is supported
- Only `crop_type=RABI_ONION` and `KHARIF_PADDY` supported in Phase 1

---

## Authentication

### Phone + OTP Flow

1. Farmer enters 10-digit phone number
2. System generates 6-digit OTP, sends via SMS
3. Farmer enters OTP — validated against 6-digit code and 5-minute expiry
4. On success: issue JWT (24-hour expiry for demo; 30-day for production)
5. JWT stored in `localStorage` on mobile app

### JWT Claims

```json
{
  "sub": "<phone>",
  "name": "<farmer_name>",
  "district": "NASHIK",
  "exp": "<unix_timestamp>"
}
```

### Security

- OTP rate limit: max 3 OTP requests per phone per hour
- OTP must be 6 digits — reject 4-digit or 8-digit inputs
- OTP expiry: 5 minutes exactly
- After 3 failed OTP attempts: lock phone for 15 minutes
- JWT secret stored in `.env` — never hardcoded

---

## CRUD Operations

### POST /api/farmers — Create

**Request:**
```json
{
  "phone": "9876543210",
  "name": "रामभाऊ गिते",
  "village": "ओजर",
  "block": "निफाड",
  "district": "NASHIK",
  "state": "MAHARASHTRA",
  "land_size": 2.0,
  "land_tenure": "OWNER",
  "crop_type": "RABI_ONION",
  "season": "RABI",
  "primary_language": "MARATHI"
}
```

**Response (201):**
```json
{
  "phone": "9876543210",
  "name": "रामभाऊ गिते",
  "district": "NASHIK",
  "land_size": 2.0,
  "land_tenure": "OWNER",
  "crop_type": "RABI_ONION",
  "season": "RABI",
  "created_at": "2026-05-22T10:00:00Z"
}
```

**Errors:**
- `400` — phone not 10 digits, land_size ≤ 0, invalid enum
- `409` — phone already exists

### GET /api/farmers/{phone} — Read

**Response (200):** Full farmer object (all fields above)

**Errors:**
- `404` — phone not found

### PUT /api/farmers/{phone} — Update

**Updatable fields:** `name`, `land_size`, `land_tenure`, `crop_type`, `season`, `primary_language`

**Non-updatable:** `phone`, `district`, `state`, `created_at`

**Response (200):** Updated farmer object

**Errors:**
- `404` — phone not found
- `400` — invalid field value

### DELETE /api/farmers/{phone} — Soft Delete

Sets `is_active = false`. Does NOT remove record.

**Response (204):** No content

**Errors:**
- `404` — phone not found

---

## Demo Data

For the pilot, the default farmer is:

```json
{
  "phone": "9876543210",
  "name": "रामभाऊ गिते",
  "village": "ओजर",
  "block": "निफाड",
  "district": "NASHIK",
  "state": "MAHARASHTRA",
  "land_size": 2.0,
  "land_tenure": "OWNER",
  "crop_type": "RABI_ONION",
  "season": "RABI",
  "primary_language": "MARATHI",
  "is_active": true
}
```
