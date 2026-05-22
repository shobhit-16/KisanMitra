# TODO-403-Mobile-PWA-Push-Notifications

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Implement push notifications for price alerts, obligation reminders, and weather warnings.

## Context

Demo.html has audio alert toggle but no actual push notification implementation. Need to implement browser push notifications for farmers without app store distribution.

## Acceptance Criteria

- [ ] Notification permission request flow (gentle, not aggressive)
- [ ] Price drop alert: notify when configured mandi price drops by threshold
- [ ] Obligation reminder: notify 1 day before due date
- [ ] Weather alert: notify when heavy rain/storm forecast
- [ ] Push notification subscription stored per farmer in backend
- [ ] Notification preferences screen: toggle each alert type
- [ ] "Test notification" button in settings

## Subtasks

- [ ] Create notification service (Est: 2h) - permission handling, subscription management
- [ ] Implement VAPID key setup (Est: 1h) - for web push
- [ ] Create notification preferences UI (Est: 1h) - toggles for price/obligations/weather
- [ ] Implement price alert trigger (Est: 1h) - background check against eNAM
- [ ] Implement obligation reminder trigger (Est: 1h) - daily job at 8am
- [ ] Implement weather alert trigger (Est: 1h) - on new forecast
- [ ] Write tests (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Notifications work on Android Chrome
- [ ] Graceful degradation on iOS (no push support)

## Dependencies

- TODO-400 (PWA Architecture)
- TODO-300 (eNAM Integration)
- TODO-301 (IMD Weather)
