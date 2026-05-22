# TODO-03-DELIVERY-CHANNELS

**Status**: ACTIVE

## Description

Multi-channel delivery infrastructure: IVR voice hotline (primary), WhatsApp Business API, USSD fallback, offline-first queue-and-sync, SMS alert infrastructure, village agent dashboard. All channels consume CPE output.

Per `specs/06-delivery-channels.md`, IVR is primary channel (no smartphone required); WhatsApp secondary; USSD fallback; offline-first architecture is mandatory for Challenge 1 connectivity safeguards.

## Spec Reference

- `specs/06-delivery-channels.md` — channel architecture, IVR script principles, WhatsApp message templates, offline-first sync, village agent app features
- `specs/09-constraint-priority-engine.md §6.2` — suppression notification format: "Right now, [active_constraint] is your main priority. We have [topic] advice ready — we'll share it once [constraint] resolves."
- Ground Challenges: `specs/09-constraint-priority-engine.md` Challenge 1 safeguards: offline-first, USSD fallback, SMS alert queue

## Acceptance Criteria

- [ ] IVR voice hotline at `src/indian_agri/channels/ivr/` — Text-to-Speech output, phone → farmer ID lookup, main menu routing (weather/prices/scheme info/agent), personalized recommendation playback, harvest status reporting
- [ ] IVR TTS scripts in Hindi and Marathi templates per `specs/06-delivery-channels.md §2` — short sentences (<15 words), simple verb forms, repeat critical info
- [ ] WhatsApp Business API at `src/indian_agri/channels/whatsapp/` — weather alert template, price alert template, scheme info template, bot state machine (init/verified/context/preference)
- [ ] WhatsApp message templates match `specs/06-delivery-channels.md §3.2` exactly — emoji usage, formatting, MSP comparison line
- [ ] USSD fallback at `src/indian_agri/channels/ussd/` — basic GSM phone support, binary/small-choice decisions (sell now/wait, accept scheme/decline), one USSD screen = one CPE recommendation
- [ ] Offline-first queue-and-sync at `src/indian_agri/sync/` — `OfflineSyncManager` with `queue_operation()` and `sync()`; pending operations stored in local SQLite; network resume trigger; last-write-wins conflict resolution per `specs/01-domain-model.md §9.3`
- [ ] SMS alert infrastructure at `src/indian_agri/channels/sms/` — price threshold trigger alerts, weather warnings, scheme eligibility alerts; delivery receipt tracking
- [ ] Village agent dashboard API at `src/indian_agri/agents/dashboard/` — structured CPE recommendation summaries for field agents, suppression notification display, farmer interaction history
- [ ] All channels consume `CPEOutput` and render appropriately — recommendation action OR suppression notification
- [ ] Suppression notifications delivered via all channels in plain language (no technical jargon) per `specs/09-constraint-priority-engine.md §6.2`

## Subtasks

- [ ] BUILD-1 (Est: 3h) — IVR system at `src/indian_agri/channels/ivr/` — `IVRRouter` class, phone → farmer lookup, menu state machine, TTS rendering, recommendation playback, feedback capture, session logging
- [ ] BUILD-2 (Est: 2h) — IVR content templates at `src/indian_agri/channels/ivr/content.py` — Hindi + Marathi TTS scripts for weather, prices, schemes, suppression notifications; per `specs/06-delivery-channels.md §2.2` script format
- [ ] BUILD-3 (Est: 3h) — WhatsApp Bot at `src/indian_agri/channels/whatsapp/bot.py` — state machine (init/verified/context/preference), message handlers for price/weather/scheme queries, WhatsApp Business API client
- [ ] BUILD-4 (Est: 2h) — WhatsApp message templates at `src/indian_agri/channels/whatsapp/templates.py` — weather alert, price alert, scheme info templates matching spec exactly
- [ ] BUILD-5 (Est: 2h) — USSD system at `src/indian_agri/channels/ussd/` — USSD session management, binary choice handling, CPE output → USSD screen rendering
- [ ] BUILD-6 (Est: 3h) — Offline-first sync at `src/indian_agri/sync/offline_manager.py` — `OfflineSyncManager`, queue_operation, sync with exponential backoff, local SQLite pending operations table, conflict resolution
- [ ] BUILD-7 (Est: 2h) — SMS alert system at `src/indian_agri/channels/sms/alerts.py` — price threshold triggers, weather warnings, scheme eligibility; delivery receipt tracking
- [ ] BUILD-8 (Est: 2h) — Village agent dashboard API at `src/indian_agri/agents/dashboard.py` — structured recommendation summaries, suppression notification display, farmer list with constraint state overview
- [ ] WIRE-1 (Est: 1h) — Wire all channels to CPE: `CPEOutput` rendered by each channel's output formatter; suppression notifications go to all active channels for farmer
- [ ] WIRE-2 (Est: 1h) — Wire offline sync to Income Engine: farmer self-reported prices and harvest status queued offline, synced when connected, populating Module 6 (IncomeLedger) and Module 4 (SellingDecisionGuide)

## Definition of Done

- [ ] IVR plays back a CPE recommendation in TTS — farmer can understand without reading
- [ ] WhatsApp bot responds to "price" query with price alert template showing mandi prices vs MSP
- [ ] USSD shows exactly one decision per screen — sell now or wait
- [ ] OfflineSyncManager queues operations when offline; syncs when connectivity returns
- [ ] Village agent dashboard shows suppression notifications in plain language
- [ ] All channels render suppression notification per `specs/09-constraint-priority-engine.md §6.2` format
