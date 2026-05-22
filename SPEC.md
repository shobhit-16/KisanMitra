# Kisanmitra — Stakeholder Demo Specification

**Purpose:** Live demo for key stakeholders (state agriculture officials, ICAR/SAUs, FPO leaders, public-spirited lenders, NGOs). 15–20 minutes. Mobile-first prototype.

**What it demonstrates:** A pocket companion ("Kisanmitra — किसानमित्र") that sits in a farmer's pocket, watches their crop cycle, protects them from market exploitation, crisis, and bad decisions — using the Income Engine and CPE.

---

## 1. The Problem We're Solving

A small farmer in Nashik faces:
- **Market failure**: Sells to mandi at the worst possible time because they don't know prices
- **Cash flow surprise**: KCC EMI due same week as school fee — forced to sell at a loss
- **Distress selling**: Sells immediately after harvest because they need cash, even when storage would earn 25% more
- **Crisis with no backstop**: Hospital bill → sells standing crop at any price
- **Digital illiteracy**: Existing apps have 47 screens and require reading; this farmer has a 2nd-grade literacy level

**The product**: One screen, one decision at a time. Voice-first. Works in Hindi and Marathi. Shows exactly what the farmer needs when they need it.

---

## 2. Farmer Persona

**Rambhau Gite, 38**
- Village: Ozar, Block: Niphad, District: Nashik, Maharashtra
- 2 hectares, irrigated, owner-operated
- Crops: Rabi Onion (sowing Nov, harvest Feb–Mar), Kharif Paddy (June–Oct)
- Crops: Onion + Paddy, 2 ha
- Language: Marathi primary, Hindi understood, limited English
- Phone: Basic smartphone (Jio, 4G available)
- Literacy: Functional — can read Marathi, numbers, phone numbers

---

## 3. Crop Cycle (Rabi Onion, Nashik)

| Month | Activity | Kisanmitra Role |
|---|---|---|
| Nov | Sowing | Soil prep reminder, seed cost calculator |
| Dec–Jan | Growth | Irrigation alert, NPK recommendation |
| Jan | First harvest planning | Mandi price watch, storage math |
| Feb | Harvest | "Today is the day" + selling recommendation |
| Mar | Post-harvest | Sale recording, baseline establishment |

---

## 4. Screens & UX

### S1: Welcome / Language
- Three big buttons: English | हिंदी | मराठी
- Each button has audio: tap plays "Press to select" in that language
- Below fold: "12 languages available — more coming"

### S2: Dashboard (Home)
- Top bar: "नमस्ते Rambhau" + date chip
- Active crop card: "Rabi Onion — 47 days to harvest" with small progress bar
- Weather chip: "☀️ 28°C, Clear — Nashik"
- Five navigation icons at bottom (no words — icons only):
  - 📋 Obligations
  - 📊 Mandi Prices
  - ⚖️ Sell/Store
  - 🏥 Credit
  - 📖 Ledger
- FAB (floating action button): 🎤 microphone — tap to speak

### S3: Obligations Calendar ("Aapka Niyam — आपका नियम")
- Timeline list of upcoming obligations
- Each item: icon + description + amount + due date
- Color: 🔴 red (<7 days), 🟡 yellow (7–30 days), 🟢 green (>30 days)
- Cash flow health bar at bottom: shows 30-day net position

**Data shown:**
- School fee: ₹5,000 — due April 15 (red)
- KCC EMI: ₹3,200 — due in 12 days (yellow)
- Land rent: ₹2,000 — due in 60 days (green)

### S4: Mandi Prices ("Aajcha Market — आजचा मंडी")
- Hero price: **₹28/quintal** (large, bold) — Lasalgaon modal
- Comparison table: Lasalgaon ₹28 | Yeola ₹27.50 | Niphad ₹28.30
- MSP chip: "MSP ₹750/quintal → You're ₹2,050 above floor price"
- Trend sparkline: ↗️ +8% this week
- "Alert me if price drops ₹2 or more" toggle

### S5: Sell or Store ("Bechana Ka Sirf?" — बेचना कब?")
- Quantity input: stepper — 5 quintal
- Current price: ₹28/quintal (auto-filled from mandi)
- Storage toggle: "Store 2 months" / "Sell Now"
- Result card:
  - If Store: 📦 STORE VIABLE — "₹715 net gain after ₹160 storage cost. Price peaks ₹35 in Feb"
  - If Sell Now: 💰 SELL — "₹14,000 today. Storage could earn ₹715 more by Feb"
- CPE gate status: Gate 4 shown as ✅ OPEN (harvest date entered)

### S6: Emergency Credit ("Rashi Ki Seva" — राशि की सेवा)
- Trigger card: large hospital icon — "Tap if you or family member is in hospital"
- Resource card (shown after trigger):
  - Ayushman Bharat PM-JAY — ₹5 lakh coverage
  - "No premium for eligible families"
  - "Apply at CSC or call 📞 14555"
- All other recommendations: SUPPRESSED BY GATE 1 (shown as crossed-out cards)

### S7: Income Ledger ("Aapki Kitaab" — आपकी किताब)
- Season's sales table: Date | Qty | Price | Total | Status
- Status: ✓ सामान्य (Normal) or ⚠️ तनाव (Distress)
- Baseline card: "Your baseline: ₹27/kg this season — today's price ₹28 is above baseline"
- Distress explanation (shown for flagged sales): "This sale was flagged because price was 15% below MSP"

### S8: CPE in Action ("Kya Hota Hai" — क्या होता है)
- Animated pipeline: [Engine] → [Bus] → [Gate 1] → [Gate 2] → ... → [Farmer]
- Farmer state toggles (for demo):
  - Gate 1 Health: NORMAL / 🔴 CRISIS
  - Gate 2 Tenure: OWNER / TENANT
  - Gate 3 Cash Flow: SURPLUS / BALANCED / 🔴 DEFICIT
  - Gate 4 Selling: CLOSED / ✅ OPEN
  - Gate 5 Time: MEDIUM / ⚡ IMMEDIATE
- Recommendations appear at top, animate through pipeline, get blocked or pass
- Suppression card: "यह सिफारिश रोकी गई" + reason in Hindi

### S9: What's Coming (Phase 2 & 3)
- Soil Health Card: "Your soil needs 20kg N/acre — subsidized urea ₹270/bag"
- Weather: "🌧️ Heavy rain expected Nashik, 28th — delay pesticide"
- "Coming in your area by 2026"

---

## 5. Design Language

**Colors:**
- Primary: `#1B5E20` (forest green — trust, agriculture)
- Secondary: `#F9A825` (harvest gold — warmth, optimism)
- Urgent: `#C62828` (red)
- Safe: `#2E7D32` (green)
- Background: `#FFFDE7` (warm cream — paper, approachable)
- Card: `#FFFFFF`
- Text: `#1A1A1A` (near-black)

**Typography:**
- Primary font: Noto Sans (Google Fonts CDN) — supports Devanagari + Latin
- Fallback: system-ui, sans-serif
- Headings: 600 weight, 1.2 line-height
- Body: 400 weight, 1.5 line-height
- Minimum body size: 16px (accessibility)

**Icons:** Inline SVG, 2px stroke, rounded caps — consistent across all screens

**Layout:** Single column, max-width 428px, centered, 16px horizontal padding

**Accessibility:**
- All tap targets minimum 48×48px
- Color not sole indicator (icons + text always accompany color)
- Touch-friendly steppers, toggles, large buttons
- No scrolling required for primary action on any screen

**Language pairs:**
- UI labels: native script + romanization
- Numbers: Arabic numerals (universal)
- Currency: ₹ symbol + Indian comma notation
- Dates: local format (DD MMM YYYY)

---

## 6. Voice Interaction (Simulated)

The microphone button simulates voice input:
- Tap → shows "Listening..." for 1.5 seconds
- Shows keyword chips: ["mandi price", "bechana", "kyu hua", "reminder"]
- Demo operator selects keyword → navigates to correct screen
- In production: would use ASR (automatic speech recognition) via Kailash Nexus

**Keywords (Hindi-dominant):**
- "दाम क्या hai" / "mandi price" → Mandi Prices screen
- "bechana" / "sell" → Selling Decision screen
- "ki samasya" / "hospital" → Emergency Credit screen
- "kitna baaki hai" / "balance" → Obligations screen
- "record sale" → Add Sale in Ledger screen

---

## 7. CPE Visualization

The 5-gate pipeline is shown as an animated flow:

```
[Income Engine] → [Rec Bus] → [G1: Health] → [G2: Tenure]
                             → [G3: Cash Flow] → [G4: Selling] → [G5: Time]
                             → [Output]
```

**For each gate:** toggle button showing ACTIVE (blocks) / PASS (allows)

**Suppression animation:**
- Card enters at top, floats down pipeline
- At each gate: card either passes (→) or is caught and grayed out with "रोकी गई" stamp
- Suppressed cards stack in a "held" tray below the pipeline
- One card (health crisis resource) always passes through all gates when G1=CRISIS

---

## 8. Phase Coverage

| Phase | Engines | Status |
|---|---|---|
| Phase 1 | Income Engine (all 6 modules) | Demo shows all 6 |
| Phase 2 | Soil Engine | Shown as "Coming" cards |
| Phase 3 | Climate Engine | Shown as "Coming" cards |

**Phase 1 modules in demo:**
1. Obligation Calendar — Act 2 ✓
2. Cash Flow Assessment — Act 2 ✓
3. Mandi Price Visibility — Act 3 ✓
4. Selling Decision Guide — Act 4 ✓
5. Emergency Credit Pathway — Act 5 ✓
6. Income Ledger — Act 6 ✓

---

## 9. Demo Script (20 Minutes)

| Minute | Segment | Screen | Key Message |
|---|---|---|---|
| 0:00 | Setup | — | Open demo.html on projector + phone |
| 1:00 | Language | S1 | "Choose your language — Hindi, Marathi, English" |
| 2:00 | Welcome | S2 | "Rambhau Gite, Nashik, Rabi Onion, 47 days to harvest" |
| 3:00 | Obligations | S3 | "See everything due — KCC EMI, school fee, land rent" |
| 5:00 | Cash Flow | S3 | "After KCC EMI, you still have ₹8,500 surplus this month" |
| 6:00 | Mandi Prices | S4 | "Onion at ₹28 today — MSP is ₹7.50, you're ₹20.50 above floor" |
| 8:00 | Selling | S5 | "Storage 2 months: costs ₹160, gains ₹875, net ₹715" |
| 9:00 | Selling Gate | S5 | "Gate 4 fires: harvest date entered → selling window OPEN" |
| 10:00 | Emergency | S6 | "Hospital bill scenario: Ayushman Bharat ₹5 lakh, no premium" |
| 11:00 | Gate 1 Demo | S8 | "Watch: only health_crisis_resource passes Gate 1 when health=crisis" |
| 13:00 | Ledger | S7 | "3 sales recorded — baseline ₹27/kg — this sale ₹28 is above baseline ✓" |
| 14:00 | Distress Explain | S7 | "This sale flagged: price was ₹5/kg, 33% below MSP" |
| 15:00 | CPE Full | S8 | "Healthy owner farmer: all gates pass" → "Deficit: Gate 3 blocks" |
| 17:00 | What's Coming | S9 | "Soil health card — subsidized urea — Weather alert — Coming Phase 2" |
| 18:00 | How to Build | — | "This runs on a basic Jio phone. No app store needed." |
| 19:00 | Close | — | "One district, 6 months, 5,000 farmers — we can do this" |

---

## 10. Constraints Addressed

| Challenge | Design Safeguard |
|---|---|
| Low literacy | Icons + numbers, no long prose, voice input |
| No internet | Offline-first, local storage, cached prices |
| Language barrier | 3 languages at launch, voice in local dialect |
| Feature overload | One screen, one task, one decision |
| Trust | Government schemes (Ayushman, MSP) — not a sales channel |
| Data accuracy | e-NAM mandi prices (real), MSP from government table |
| Privacy | Farmer consent, DPDP-compliant, no data sold |
