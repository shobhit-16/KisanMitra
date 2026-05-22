# TODO-400-Mobile-PWA-Architecture

**GitHub Issue**: N/A
**Status**: SUPERSEDED — replaced by TODO-410/411/412/413

## Description

Design PWA architecture replacing demo.html with production vanilla JS PWA with service workers and offline support.

## Context

Demo.html is a 4,805-line single HTML file with embedded CSS and JS. Needs to be replaced with modular PWA structure while preserving all 17 screens and i18n.

## Acceptance Criteria

- [ ] PWA manifest with app name "Kisanmitra", icons, theme color #1B5E20
- [ ] Service worker with cache-first strategy for static assets
- [ ] Offline fallback page when network unavailable
- [ ] App shell architecture: header, nav-bar, content area
- [ ] Screen router: hash-based routing matching demo.html screen IDs
- [ ] State management: single source of truth for farmer state
- [ ] All 17 demo.html screens migrated to PWA structure

## Subtasks

- [ ] Create PWA manifest (Est: 30 min) - manifest.json with icons, theme
- [ ] Create service worker skeleton (Est: 1h) - cache strategies, offline detection
- [ ] Create app shell HTML (Est: 1h) - header, nav, content slots
- [ ] Create screen router (Est: 2h) - hash navigation, screen transitions
- [ ] Create state store (Est: 1h) - farmer state, screen state
- [ ] Migrate CSS from demo.html (Est: 2h) - extract styles, organize by component
- [ ] Migrate all 17 screens (Est: 3h) - one pass per screen

## Definition of Done

- [ ] All acceptance criteria met
- [ ] PWA installable on Android/iOS
- [ ] App works offline with cached data
- [ ] 17 screens all render correctly

## Dependencies

- TODO-100 (Farmer Profile CRUD)
