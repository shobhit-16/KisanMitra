# TODO-410-PWA-Manifest-And-Service-Worker

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Create PWA manifest and service worker skeleton with cache strategies for offline support.

## Context

Part of TODO-400 decomposition. This shard covers the PWA foundation: manifest.json, service worker registration, and cache strategies. Does NOT cover screen content or state management.

## Acceptance Criteria

- [ ] `manifest.json` created with app name "Kisanmitra", theme color `#1B5E20`, icons
- [ ] Service worker registered on app load
- [ ] Cache-first strategy for app shell files (index.html, base.css, components.css, app.js)
- [ ] Network-first with cache fallback for API responses
- [ ] Offline fallback page shown when network unavailable and no cache exists
- [ ] `manifest.json` passes PWA audit (Chrome DevTools Lighthouse)
- [ ] App installable on Android Chrome (add to home screen prompt)
- [ ] Unit tests: cache hit/miss behavior, offline fallback rendering

## Subtasks

- [ ] Create manifest.json (Est: 15 min) - name, icons, theme, display mode
- [ ] Create service worker registration (Est: 15 min) - navigator.serviceWorker.register
- [ ] Implement cache-first strategy (Est: 1h) - shell files cached on install
- [ ] Implement network-first strategy (Est: 1h) - API responses with offline fallback
- [ ] Create offline fallback HTML (Est: 30 min) - friendly "offline" message
- [ ] Add cache expiration (Est: 30 min) - stale cache cleanup
- [ ] Write unit tests for cache strategies (Est: 1h) - hit/miss/expire

## Definition of Done

- [ ] All acceptance criteria met
- [ ] App loads fully offline after first visit
- [ ] API failures show cached data with "offline" indicator

## Dependencies

- TODO-000 (Foundation Project Scaffold)

## Spec Reference

- `specs/pwa-architecture.md` § PWA Structure, § Offline Strategy
