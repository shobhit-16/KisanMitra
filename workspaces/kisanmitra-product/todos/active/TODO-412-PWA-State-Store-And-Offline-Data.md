# TODO-412-PWA-State-Store-And-Offline-Data

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Create farmer state store with localStorage persistence and offline data sync.

## Context

Part of TODO-400 decomposition. This shard covers the state management layer: farmer profile state, obligations, sales, mandi prices, weather — all persisted to localStorage and synced when online. Does NOT cover individual screen rendering or API integration.

## Acceptance Criteria

- [ ] Farmer state store: `state.farmer`, `state.obligations`, `state.sales`, `state.mandiPrices`, `state.weather`
- [ ] localStorage persistence: save on every state change, load on app start
- [ ] State hydration: merge localStorage state with server state on online
- [ ] Offline mutation queue: queue writes when offline, replay when online
- [ ] State subscriptions: screens can subscribe to state changes and re-render
- [ ] Cache invalidation: mandi prices expire after 15 minutes, weather after 1 hour
- [ ] Unit tests: save/load roundtrip, merge logic, cache expiry
- [ ] Integration tests: offline queue replay, state consistency after sync

## Subtasks

- [ ] Create state store (Est: 1h) - observable state with get/set/subscribe
- [ ] Add localStorage persistence (Est: 1h) - save on change, load on start
- [ ] Implement state hydration (Est: 1h) - merge local + server state
- [ ] Implement offline mutation queue (Est: 2h) - queue writes, replay on reconnect
- [ ] Add cache expiry logic (Est: 1h) - mandi 15min, weather 1hr
- [ ] Implement state subscription system (Est: 1h) - pub/sub for screen updates
- [ ] Write unit tests (Est: 1h) - roundtrip, merge, expiry
- [ ] Write integration tests (Est: 1h) - offline queue, sync

## Definition of Done

- [ ] All acceptance criteria met
- [ ] App shows cached data when offline
- [ ] Mutations made offline are replayed on reconnect
- [ ] Prices show "cached" indicator with age

## Dependencies

- TODO-410 (PWA Manifest + Service Worker)
- TODO-411 (App Shell + Screen Router)

## Spec Reference

- `specs/pwa-architecture.md` § State Management, § Offline Strategy
