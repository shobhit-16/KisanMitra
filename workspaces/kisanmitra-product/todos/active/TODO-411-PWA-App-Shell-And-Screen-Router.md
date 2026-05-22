# TODO-411-PWA-App-Shell-And-Screen-Router

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Create app shell HTML, screen router with hash-based navigation, and transition animations.

## Context

Part of TODO-400 decomposition. This shard covers the app shell (header, nav bar, content area) and the screen router that loads individual screen content. Does NOT cover individual screen implementations or state management.

## Acceptance Criteria

- [ ] App shell HTML: header with back/forward buttons, main content area, bottom nav bar with 5 icons
- [ ] Hash-based screen router: `/#/obligations`, `/#/mandi`, `/#/sell`, `/#/credit`, `/#/ledger`
- [ ] Screen transitions: CSS fade/slide animations between screens
- [ ] Bottom nav highlights active screen with icon state change
- [ ] Back button appears on screens beyond dashboard
- [ ] Language toggle button in header
- [ ] Screen title updates on navigation
- [ ] Unit tests: router parsing, active screen detection, transition triggering

## Subtasks

- [ ] Create app shell HTML (Est: 1h) - header, nav, content slots
- [ ] Implement hash router (Est: 2h) - parse hash, load screen, update nav
- [ ] Add CSS transitions (Est: 1h) - fade/slide between screens
- [ ] Implement nav state sync (Est: 1h) - active tab highlighting
- [ ] Add back button logic (Est: 30 min) - show on screens != dashboard
- [ ] Add screen title updates (Est: 30 min) - per-screen titles in current language
- [ ] Write unit tests for router (Est: 1h) - hash parsing, nav sync

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Navigating to `/#/mandi` shows mandi screen with correct nav highlight
- [ ] Transitions are smooth (no flicker)

## Dependencies

- TODO-410 (PWA Manifest + Service Worker)

## Spec Reference

- `specs/pwa-architecture.md` § App Shell Architecture, § Screen Inventory
