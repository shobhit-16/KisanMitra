# Domain Spec: Multi-Channel Delivery Architecture

## Overview

This spec defines the multi-channel delivery system. Given that 30-45% of target farmers have smartphones and 30% have digital literacy, the product must be designed for **human-mediated, voice-first** delivery — not a traditional app-first approach.

---

## 1. Channel Architecture

### 1.1 Channel Prioritization Matrix

| Farmer Segment | Primary | Secondary | Tertiary |
|---|---|---|---|
| Marginal (<1ha), Low literacy | IVR (incoming) | Village agent | SMS fallback |
| Marginal (<1ha), Some literacy | WhatsApp | IVR | Village agent |
| Small (1-2ha), Any literacy | WhatsApp | IVR | App |
| Semi-medium+ (2+ha), Literate | App | WhatsApp | IVR |

### 1.2 Channel Comparison

| Channel | Reach | Cost/Farmer | Interactivity | Content Richness | Offline |
|---|---|---|---|---|---|
| IVR | 90%+ have phone | Medium | Low | Text-to-speech | N/A |
| WhatsApp | 60-70% have it | Low | Medium | Text + audio + images | Limited |
| SMS | 95%+ | Very Low | None | Text only | N/A |
| App | 30-40% | Low | High | Full multimedia | Limited |
| USSD | 90%+ | Low | Low | Text | N/A |
| Village Agent | 100% | High | Very High | Full | Yes |

---

## 2. Voice/IVR System

### 2.1 IVR Architecture

```
Incoming Call
      ↓
[Authentication]
Phone number → Farmer ID (lookup)
      ↓
[Main Menu — Text-to-Speech]
"Press 1 for weather. Press 2 for prices. Press 3 for scheme info. Press 4 to talk to an agent."
      ↓
[Route to specific service]
      ↓
[Personalized Content — TTS]
"Today's weather in [Village]: Heavy rain expected. Delay pesticide spray."
      ↓
[Capture feedback if any]
"Was this helpful? Press 1 for yes, 2 for no."
```

### 2.2 IVR Script Principles

**TTS (Text-to-Speech) Guidelines:**
- Keep sentences short (<15 words)
- Avoid technical jargon
- Use simple verb forms
- Repeat critical information
- Allow callback for more detail

**Example Script:**
```
Welcome to FarmWise. Calling from [Village]?

Today's weather: Heavy rain expected tomorrow in [Block].

For your cotton crop in squaring stage:
Avoid pesticide spray tomorrow.
Check drainage in low-lying plots.

For more details, press 1.
To repeat, press 2.
To talk to an agent, press 0.
```

### 2.3 IVR Content Format

```python
IVR_CONTENT = {
    "weather": {
        "greeting": "Namaste. Weather update for {village}.",
        "format": "{condition} expected on {date}. {temperature_range}. {advisory}",
        "advisory_templates": {
            "heavy_rain": "Avoid {field_operation} on {date}. {why}",
            "heat_wave": "Avoid fieldwork 12 se 4 baje. {crop_impact}",
            "dry_spell": "No rain expected for {days} days. {irrigation_advice}"
        }
    },
    "prices": {
        "greeting": "MandI bhav today.",
        "format": "{commodity} ka price {mandi} mein {price} rupaye per quintal. MSP se {msp_comparison}.",
        "trend": "Pichhe hafte se {trend}."
    }
}
```

---

## 3. WhatsApp Integration

### 3.1 WhatsApp Business API Setup

```
Platform → WhatsApp Business API → Farmer's WhatsApp
```

**Message Types Supported:**
| Type | Use Case | Format |
|---|---|---|
| Text | Price alerts, scheme info | Text + emojis |
| Image | Crop health visuals | PNG/JPG with caption |
| Audio | Voice messages for low-literacy | MP3/OGG |
| Document | Scheme forms, receipts | PDF |
| Buttons | Quick responses | Interactive buttons |
| List | Structured options | List message |

### 3.2 WhatsApp Message Templates

**Weather Alert Template:**
```
🌧️ *WEATHER ALERT — YOUR AREA*

📍 [Village], [District]
📅 [Date]

{condition_icon} {condition}

🌡️ Temp: {min}-{max}°C
💧 Rain: {probability}% chance, {amount}mm

📋 *ADVISORY FOR YOUR [CROP]:*
✅ DO: {action_1}
✅ DO: {action_2}
❌ DON'T: {action_3}

⏰ Valid until: {valid_until}

---
Reply *MORE* for details
Reply *STOP* to unsubscribe
```

**Price Alert Template:**
```
📊 *PRICE UPDATE — [COMMODITY]*

🏪 [Mandi Name]: ₹[price]/quintal
📈 vs last week: [+/-][%] [arrow]

vs MSP: {[above/at/below]} MSP

💡 *Tip:* {selling_recommendation}

🗓️ *Next:*
Best selling window: [month]
Expected peak: ₹[predicted]/Q

---
Reply *STORAGE* for storage calculator
Reply *TRANSPORT* for mandi directions
```

### 3.3 WhatsApp Bot States

```python
class WhatsAppBot:
    STATE_INIT = "init"              # New user, no context
    STATE_VERIFIED = "verified"      # Phone linked to farmer
    STATE_CONTEXT = "context"        # Active session (checking prices, etc.)
    STATE_PREFERENCE = "preference"  # Setting language, crop, location

    def handle_message(self, from_number, message, state):
        if state == self.STATE_INIT:
            return self.handle_new_user(from_number, message)

        elif state == self.STATE_CONTEXT:
            if "price" in message:
                return self.handle_price_query(from_number)
            elif "weather" in message:
                return self.handle_weather_query(from_number)
            elif "scheme" in message:
                return self.handle_scheme_query(from_number)

        elif message == "STOP":
            return self.unsubscribe(from_number)

        return self.unknown_response()
```

---

## 4. Mobile App (For Commercial Farmers)

### 4.1 App Architecture

```
┌─────────────────────────────────────────────┐
│                 MOBILE APP                  │
│  (React Native / Flutter)                   │
├─────────────────────────────────────────────┤
│  Screens:                                   │
│  • Dashboard (weather + prices + alerts)    │
│  • Crop Management                         │
│  • Market Place                            │
│  • Scheme Checker                          │
│  • Profile & Settings                      │
└──────────────────────┬──────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────┐
│              PLATFORM BACKEND                │
│  • Node.js / FastAPI                        │
│  • PostgreSQL (farmer data)                 │
│  • Redis (cache/sessions)                   │
│  • S3 (media storage)                      │
└─────────────────────────────────────────────┘
```

### 4.2 App for Commercial Farmers Only

The app is NOT for marginal farmers. It's designed for:
- Semi-medium to large farmers (2+ ha)
- FPO staff and field agents
- Agricultural entrepreneurs
- KVK scientists and extension officers

### 4.3 App Features by User Type

| Feature | Marginal Farmer | Commercial Farmer | Field Agent |
|---|---|---|---|
| Weather | IVR | App + WhatsApp | App |
| Prices | WhatsApp | App + WhatsApp | App |
| Soil advisory | Via agent | App + WhatsApp | App |
| Scheme access | Via agent | Self-service | App |
| Crop log | None | App | App |
| Market transactions | Via arthiya | App (future) | App |

---

## 5. Offline-First Architecture

### 5.1 Offline Requirements

Rural connectivity is poor:
- 2G still common in many agricultural areas
- 3G/4G available but expensive for heavy use
- Network outages during monsoons

**Solution: Offline-first design**

```
┌─────────────────────────────────────────────────────┐
│                   LOCAL STORAGE                      │
│  SQLite / AsyncStorage                              │
│  • Cached farmer profile                           │
│  • Last 7 days weather                             │
│  • Last 30 days prices                             │
│  • Pending operations queue                        │
└──────────────────────┬────────────────────────────┘
                       │ Sync when online
                       ▼
┌─────────────────────────────────────────────────────┐
│                    CLOUD BACKEND                    │
│  • Master farmer records                           │
│  • Real-time prices                               │
│  • Weather forecasts                              │
│  • Government APIs                                │
└─────────────────────────────────────────────────────┘
```

### 5.2 Offline Capabilities

| Feature | Online | Offline |
|---|---|---|
| View weather (cached) | ✅ | ✅ |
| View prices (cached) | ✅ | ✅ |
| Get new weather | ✅ | ❌ |
| Get new prices | ✅ | ❌ |
| Submit crop log | ✅ (queued) | ✅ (queued) |
| Submit feedback | ✅ (queued) | ✅ (queued) |
| Scheme eligibility check | ✅ | ❌ |

### 5.3 Sync Strategy

```python
class OfflineSyncManager:
    def sync(self):
        # 1. Push pending operations
        pending = self.local_db.get_pending_operations()
        for op in pending:
            try:
                self.cloud_api.submit(op)
                self.local_db.mark_synced(op)
            except NetworkError:
                break  # Stop on first failure, retry later

        # 2. Pull latest data
        try:
            self.pull_prices()
            self.pull_weather()
            self.pull_scheme_updates()
        except NetworkError:
            pass  # Use cached data

    def queue_operation(self, operation_type, payload):
        # Queue for later sync
        self.local_db.insert_pending({
            "type": operation_type,
            "payload": payload,
            "timestamp": now(),
            "retries": 0
        })
```

---

## 6. Local Agent Network

### 6.1 Why Human Agents Are Critical

Digital cannot replace human touch for many farmers:
- Low digital literacy
- Trust issues with technology
- Complex issues requiring judgment
- Social/emotional support during crop failure

### 6.2 Agent Types

| Agent Type | Profile | Role |
|---|---|---|
| **Village Agent** | Local youth, 10th pass, smartphone user | First touchpoint for marginal farmers |
| **FPO Staff** | Employed by FPO | Scheme access, aggregation, market link |
| **Input Dealer** | Business owner | Input quality, some advisory |
| **KVK Scientist** | Government | Technical advisory |
| **SHG Leader** | Women, community leader | Women farmer engagement |

### 6.3 Agent App

Agents use a specialized app:

```python
AGENT_APP_FEATURES = {
    "farmer_management": {
        "add_farmer": "Register new farmer with basic details",
        "update_profile": "Update crops, land, contact",
        "view_history": "View all interactions with farmer"
    },
    "advisory_delivery": {
        "send_weather": "Forward weather advisory to farmer",
        "send_price": "Forward price alert to farmer",
        "record_feedback": "Capture farmer's response to advisory"
    },
    "scheme_facilitation": {
        "check_eligibility": "Run eligibility for any scheme",
        "submit_application": "Submit scheme application on behalf",
        "track_status": "Track application status"
    },
    "data_collection": {
        "report_prices": "Report mandi prices from local market",
        "report_weather": "Report local weather observations",
        "report_pest": "Report pest/disease sightings"
    }
}
```

### 6.4 Agent Performance Metrics

| Metric | Target |
|---|---|
| Farmers per agent | 100-200 |
| Advisory delivery rate | >80% |
| Scheme application success rate | >70% |
| Farmer satisfaction | >3.5/5 |

---

## 7. Multi-Language Support

### 7.1 Language Priority

| Language | Coverage | Priority |
|---|---|---|
| Hindi | North + Central India | P0 |
| Marathi | Maharashtra | P0 |
| Telugu | Andhra + Telangana | P0 |
| Tamil | Tamil Nadu | P0 |
| Bengali | West Bengal | P1 |
| Gujarati | Gujarat | P1 |
| Kannada | Karnataka | P1 |
| Punjabi | Punjab | P1 |
| Odia | Odisha | P2 |
| Malayalam | Kerala | P2 |
| tribal languages | East + Central | P2 (limited) |

### 7.2 Content Translation

- Machine translation (Google Translate API) for initial
- Human review for critical content (scheme information)
- Local agent verification for regional accuracy
- Avoid literal translation; use natural phrasing

### 7.3 Literacy Adaptation

| Literacy Level | Content Format |
|---|---|
| None | Audio/IVR only |
| Low | Audio + visual (icons/emojis) |
| Medium | Simple text + audio |
| High | Standard text |

---

## 8. Message Scheduling

### 8.1 Optimal Timing

| Channel | Best Time | Rationale |
|---|---|---|
| IVR (incoming) | Farmer decides | No scheduling |
| IVR (outgoing) | 6-8 AM | Before farm work begins |
| WhatsApp | 6-8 AM, 6-8 PM | Low cost, high engagement |
| SMS | 6-8 AM | Simple, no media |
| App push | Anytime | User controls |

### 8.2 Message Frequency

| Message Type | Frequency | Channel |
|---|---|---|
| Daily weather | Daily | WhatsApp/SMS |
| Weekly prices | Weekly | WhatsApp |
| Seasonal advisory | As needed | IVR + WhatsApp |
| Scheme deadline | As needed | WhatsApp + IVR |
| Emergency alert | Immediate | All channels |

---

## 9. Metrics

### 9.1 Channel Metrics

| Metric | Target |
|---|---|
| WhatsApp open rate | >60% |
| IVR completion rate | >70% |
| App DAU/MAU | >30% |
| Message delivery rate | >95% |

### 9.2 Engagement Metrics

| Metric | Target |
|---|---|
| Weekly active reach | >50% of registered |
| Monthly active reach | >75% of registered |
| Advisory action rate | >30% |
| Feedback response rate | >10% |

---

## 10. Edge Cases

### 10.1 Farmer Changes Phone Number
- Re-authenticate with OTP
- Update phone in profile
- Re-link WhatsApp if needed

### 10.2 Shared Phone (Common in Rural Areas)
- One phone, multiple family members
- Track primary user per phone
- Allow secondary users with consent

### 10.3 Network Outage
- Queue all operations
- Show "last updated" timestamp
- Resume automatically when online

### 10.4 WhatsApp Privacy
- Don't store message content
- Don't use read receipts for tracking
- Comply with WhatsApp Business policies

---

*Spec authority: Multi-Channel Delivery Architecture*
*Version: 1.0*
