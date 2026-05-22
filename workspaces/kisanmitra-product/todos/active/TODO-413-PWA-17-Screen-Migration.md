# TODO-413-PWA-17-Screen-Migration

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Migrate all 17 demo.html screens to PWA structure with modular HTML, CSS, and JavaScript.

## Context

Part of TODO-400 decomposition. This is the largest shard — migrating all 17 screens from the single 4,805-line demo.html into modular screen files. Screens are grouped by data dependency to fit the capacity budget.

## Screen Groups

### Group A: Core Finance (S2, S3, S4, S5)
Dashboard, Obligations, Mandi Prices, Sell Decision

### Group B: Credit + CPE (S9, S10)
Emergency Credit, CPE Simulator

### Group C: Ledger + Timeline (S11, S12)
Income Ledger, Season Timeline

### Group D: Soil + Climate (S6, S7, S8, S13, S14, S15, S16, S17)
Soil Health, Soil Passport, Climate, FPO Advisor, Summary, Community, News, Knowledge

## Acceptance Criteria

- [ ] All 17 screens migrated to `screens/` directory
- [ ] Each screen: separate HTML file with linked CSS and JS
- [ ] CSS extracted from demo.html: `screens.css` organized by screen
- [ ] Language system: `data-i` attributes work across all screens, 3 languages
- [ ] All demo.html interactive behaviors preserved: steppers, toggles, voice modal, etc.
- [ ] Voice modal with keyword chips functional in PWA structure
- [ ] CPE simulator gate toggle animations preserved
- [ ] Loading states, empty states, error states for all screens
- [ ] Unit tests per screen: render, language switch, interaction
- [ ] E2E tests: full user flows across multiple screens

## Subtasks

- [ ] Migrate Group A screens (Est: 3h) - S2, S3, S4, S5
- [ ] Migrate Group B screens (Est: 2h) - S9, S10
- [ ] Migrate Group C screens (Est: 2h) - S11, S12
- [ ] Migrate Group D screens (Est: 3h) - S6, S7, S8, S13, S14, S15, S16, S17
- [ ] Extract and organize CSS (Est: 2h) - screens.css from demo.html
- [ ] Extract translation strings (Est: 1h) - build T dictionary
- [ ] Implement voice modal in PWA (Est: 1h) - keyword chips + speech API
- [ ] Write unit tests per screen (Est: 3h) - render + interaction tests
- [ ] Write E2E tests (Est: 2h) - full flows (login → sell → ledger)

## Definition of Done

- [ ] All 17 screens render correctly in PWA
- [ ] Language switching works on all screens
- [ ] All interactive elements functional
- [ ] All unit tests pass
- [ ] All E2E tests pass

## Dependencies

- TODO-410 (PWA Manifest + Service Worker)
- TODO-411 (App Shell + Screen Router)
- TODO-412 (State Store + Offline Data)

## Spec Reference

- `specs/pwa-architecture.md` § Screen Inventory, § i18n System, § Voice Input
