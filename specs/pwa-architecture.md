# PWA Architecture — Domain Spec

**Spec File:** `pwa-architecture.md`
**Domain:** Mobile Application
**Phase:** 1
**Last Updated:** 2026-05-22

---

## Purpose

Replace the single-file `demo.html` prototype with a production-quality Progressive Web App (PWA) that is installable on Android and iOS, works offline, and implements all 17 demo screens with real API integration.

---

## App Name & Identity

| Property | Value |
|---|---|
| App name | Kisanmitra (किसानमित्र) |
| Tagline | "Your farming companion" |
| PWA manifest name | Kisanmitra |
| PWA manifest short_name | Kisanmitra |
| Theme color | `#1B5E20` (forest green) |
| Background color | `#FFFDE7` (warm cream) |
| Icons | Bullock cart or wheat stalk SVG, 192x192 and 512x512 |

---

## Screen Inventory

All 17 screens from demo.html must be migrated:

| Screen ID | Name | File | Description |
|---|---|---|---|
| S1 | Language Select | `screens/lang-select.html` | EN/HI/MR language picker |
| S2 | Dashboard | `screens/dashboard.html` | Home screen with crop card, weather chip, nav icons |
| S3 | Obligations | `screens/obligations.html` | Timeline of obligations with color coding |
| S4 | Mandi Prices | `screens/mandi-prices.html` | Price display, MSP comparison, trend sparkline |
| S5 | Sell Decision | `screens/sell-decision.html` | Quantity stepper, storage toggle, recommendation card |
| S6 | Soil Health | `screens/soil.html` | Phase 2 — coming soon card |
| S7 | Soil Passport | `screens/soil-passport.html` | Phase 2 — soil test results |
| S8 | Climate | `screens/climate.html` | 7-day weather forecast, alerts |
| S9 | Emergency Credit | `screens/credit.html` | Ayushman Bharat resource card, health trigger |
| S10 | CPE Simulator | `screens/cpe.html` | Animated pipeline visualization |
| S11 | Income Ledger | `screens/ledger.html` | Sales table, baseline card, distress flags |
| S12 | Timeline | `screens/timeline.html` | Season timeline with obligations |
| S13 | FPO Advisor | `screens/fpo.html` | FPO partnership information |
| S14 | Summary | `screens/summary.html` | Season summary, income vs expenses |
| S15 | Community | `screens/community.html` | FPO community, shared knowledge |
| S16 | News | `screens/news.html` | Agricultural news, price alerts |
| S17 | Knowledge | `screens/knowledge.html` | Tips, best practices |

---

## PWA Structure

```
apps/mobile/
├── manifest.json
├── sw.js                    # Service worker
├── index.html               # App shell
├── css/
│   ├── base.css            # CSS variables, reset
│   ├── components.css      # Buttons, cards, chips
│   └── screens.css        # Per-screen styles
├── js/
│   ├── app.js              # Main app, screen router
│   ├── state.js           # Farmer state store
│   ├── api.js             # API client
│   ├── i18n.js            # Translation system
│   ├── voice.js           # Voice input
│   └── audio.js           # Alert tones
└── screens/
    ├── lang-select.html
    ├── dashboard.html
    ├── obligations.html
    ├── mandi-prices.html
    ├── sell-decision.html
    ├── soil.html
    ├── soil-passport.html
    ├── climate.html
    ├── credit.html
    ├── cpe.html
    ├── ledger.html
    ├── timeline.html
    ├── fpo.html
    ├── summary.html
    ├── community.html
    ├── news.html
    └── knowledge.html
```

---

## State Management

### Farmer State Store

```javascript
const state = {
  farmer: {
    phone: "9876543210",
    name: "रामभाऊ गिते",
    district: "NASHIK",
    land_size: 2.0,
    land_tenure: "OWNER",
    crop_type: "RABI_ONION",
    season: "RABI",
    primary_language: "MARATHI"
  },
  currentScreen: "dashboard",
  language: "MARATHI",
  obligations: [],       // Loaded from API
  sales: [],             // Loaded from API
  mandiPrices: null,    // Cached from e-NAM
  weather: null,        // Cached from IMD
  cashflow: null,       // Computed from obligations
  recommendations: []    // From CPE
}
```

### State Persistence

- Farmer state persisted to `localStorage` on every change
- On app load: read from `localStorage`, then sync with server
- Screen state (scroll position, active filters) persisted per-screen

---

## Offline Strategy

### Service Worker Caching

```javascript
// Cache strategies by resource type
const CACHE_STRATEGIES = {
  // App shell — cache first, network fallback
  shell: ["/", "/index.html", "/css/base.css", "/css/components.css"],

  // Static assets — cache first
  static: ["/css/screens.css", "/js/app.js", "/js/state.js", "/js/api.js"],

  // API responses — network first, cache fallback
  api: ["/api/farmers", "/api/mandi", "/api/weather"],

  // Screen HTML — cache first
  screens: ["/screens/*.html"],

  // No cache — dynamic data
  noCache: ["/api/cpe/evaluate"]
}
```

### Offline Fallback Page

When network unavailable and no cached response exists:

```html
<div id="offline-banner">
  <span>Offline — showing cached data</span>
  <button onclick="retry()">Retry</button>
</div>
```

---

## i18n System

### Translation Structure

```javascript
const T = {
  MARATHI: {
    welcome: "नमस्ते",
    dashboard: {
      greeting: "नमस्ते {name}",
      crop_card: "रबी कांदा — {days} दिवस शिल्लक",
      weather: "{temp}°C, {condition}"
    },
    obligations: {
      title: "आपका नियम",
      due_in: "{days} दिवस",
      urgent: "तातडीचे",
      critical: "अति तातडीचे"
    }
  },
  HINDI: { /* ... */ },
  ENGLISH: { /* ... */ }
}
```

### Translation Function

```javascript
function t(key, lang, params = {}) {
  const keys = key.split(".")
  let value = T[lang]
  for (const k of keys) {
    value = value?.[k]
  }
  if (!value) return key // Fallback to key

  // Replace {param} placeholders
  return value.replace(/\{(\w+)\}/g, (_, k) => params[k] ?? `{${k}}`)
}
```

### Attribute-Based Translation

```html
<span data-i="welcome.greeting" data-params='{"name": "रामभाऊ"}'>नमस्ते रामभाऊ</span>
```

On language change: scan all `data-i` elements, call `t(key, newLang, params)`, update `textContent`.

---

## Voice Input

### Web Speech API Integration

```javascript
async function startVoiceInput() {
  if (!("webkitSpeechRecognition" in window)) {
    showFallbackModal()  // Show keyword chips as fallback
    return
  }

  const recognition = new webkitSpeechRecognition()
  recognition.lang = getSpeechLang(farmer.primary_language)  // mr-IN, hi-IN, en-IN
  recognition.continuous = false
  recognition.interimResults = false

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    handleVoiceCommand(transcript)
  }

  recognition.start()
}
```

### Keyword Routing

```javascript
const VOICE_KEYWORDS = {
  MARATHI: {
    "दाम": "mandi",
    "कांदा दाम": "mandi",
    "बेचना": "sell",
    "शिल्लक किती": "balance",
    "आज का बाजार": "mandi"
  },
  HINDI: {
    "दाम क्या है": "mandi",
    "मंडी भाव": "mandi",
    "बेचना": "sell",
    "बैलेंस": "balance"
  },
  ENGLISH: {
    "mandi price": "mandi",
    "sell": "sell",
    "balance": "balance"
  }
}
```

### Fallback Modal

When Web Speech API unavailable:

```html
<div id="voice-modal" class="modal">
  <div class="modal-content">
    <p>Select what you want:</p>
    <div class="keyword-chips">
      <button onclick="navigate('mandi')">📊 Mandi Price</button>
      <button onclick="navigate('sell')">⚖️ Sell/Store</button>
      <button onclick="navigate('balance')">💰 Balance</button>
      <button onclick="navigate('obligation')">📋 Obligations</button>
    </div>
  </div>
</div>
```

---

## Push Notifications

### Notification Types

| Type | Trigger | Content |
|---|---|---|
| Price alert | e-NAM price crosses threshold | "Onion price dropped to ₹{price} at {mandi}" |
| Obligation reminder | 3 days before due date | "{amount} due in 3 days — {type}" |
| Weather alert | IMD heavy rain forecast | "Heavy rain expected on {date} — delay spraying" |
| Recommendation | New recommendation from CPE | "{title}" |

### Notification Contract

```javascript
async function requestNotificationPermission() {
  if (!("Notification" in window)) return false
  const permission = await Notification.requestPermission()
  return permission === "granted"
}

async function sendNotification(type, title, body, icon) {
  if (Notification.permission !== "granted") return

  const registration = await navigator.serviceWorker.ready
  await registration.showNotification(title, {
    body,
    icon: icon || "/icons/notification-icon.png",
    badge: "/icons/badge-32.png",
    tag: type,  // Replaces existing notification of same type
    data: { type, url: "/screens/" }
  })
}
```

### Service Worker Notification Handler

```javascript
self.addEventListener("notificationclick", (event) => {
  event.notification.close()
  const screen = event.notification.data.url
  event.waitUntil(
    clients.matchAll({ type: "window" }).then((clientList) => {
      // Focus or open app to the relevant screen
      for (const client of clientList) {
        if (client.url.includes(screen) && "focus" in client) {
          return client.focus()
        }
      }
      return clients.openWindow(screen)
    })
  )
})
```

---

## App Shell Architecture

```html
<!-- index.html — App shell -->
<div id="app">
  <header id="app-header">
    <button id="back-btn" class="nav-btn" hidden>←</button>
    <h1 id="screen-title">Kisanmitra</h1>
    <button id="lang-btn" class="nav-btn">🌐</button>
  </header>

  <main id="screen-container">
    <!-- Screen content loaded here -->
  </main>

  <nav id="bottom-nav">
    <button data-screen="obligations" class="nav-icon">📋</button>
    <button data-screen="mandi" class="nav-icon">📊</button>
    <button data-screen="sell" class="nav-icon">⚖️</button>
    <button data-screen="credit" class="nav-icon">🏥</button>
    <button data-screen="ledger" class="nav-icon">📖</button>
  </nav>

  <button id="voice-fab" class="fab">🎤</button>
</div>
```

---

## Design Language

### CSS Variables

```css
:root {
  --green: #1B5E20;
  --green-light: #4CAF50;
  --gold: #F9A825;
  --gold-light: #FDD835;
  --red: #C62828;
  --yellow-bg: #FFF9C4;
  --cream: #FFFDE7;
  --card: #FFFFFF;
  --text: #1A1A1A;
  --muted: #757575;
  --border: #E0E0E0;
  --shadow: 0 2px 8px rgba(0,0,0,0.1);
  --radius: 12px;
  --tap: 48px;
  --font: "Noto Sans", system-ui, sans-serif;
  --soil-brown: #795548;
  --soil-amber: #FF8F00;
  --climate-blue: #1565C0;
}
```

### Typography

```css
html {
  font-family: var(--font);
  font-size: 16px;
  line-height: 1.5;
}

h1 { font-size: 1.5rem; font-weight: 600; }
h2 { font-size: 1.25rem; font-weight: 600; }
h3 { font-size: 1.1rem; font-weight: 600; }

.price-hero { font-size: 2.5rem; font-weight: 700; }
.amount { font-size: 1.75rem; font-weight: 700; color: var(--green); }
```

### Spacing

```css
.padding-screen { padding: 16px; }
.gap-sm { gap: 8px; }
.gap-md { gap: 16px; }
.gap-lg { gap: 24px; }
.card { padding: 16px; border-radius: var(--radius); background: var(--card); box-shadow: var(--shadow); }
```

### Accessibility

- All interactive elements: `min-height: var(--tap)` (48px)
- Color not sole indicator: icon + text always accompany color
- Focus states: `outline: 2px solid var(--gold)`
- No scrolling required for primary action on any screen
