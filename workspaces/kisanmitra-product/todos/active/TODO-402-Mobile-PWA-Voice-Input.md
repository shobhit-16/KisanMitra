# TODO-402-Mobile-PWA-Voice-Input

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Implement real voice input using Web Speech API, replacing demo.html keyword simulation with actual voice recognition.

## Context

Demo.html Screen 0+ has FAB button with voice modal using simulated keyword buttons (mandi/bechana/balance/soil/climate/credit/cpe/record). Need real speech-to-text for Hindi/Marathi keywords.

## Acceptance Criteria

- [ ] FAB button opens voice modal with Web Speech API integration
- [ ] Real-time speech recognition for Hindi and Marathi keywords
- [ ] Keyword mapping: "mandi" → mandi screen, "bechana" → sell screen, "balance" → obligations, "soil" → soil, "climate" → climate, "credit" → credit, "cpe" → cpe, "record" → ledger
- [ ] Fallback to keyword button UI if speech recognition unavailable
- [ ] Visual feedback during listening (pulsing microphone icon)
- [ ] Error handling: microphone permission denied, speech not recognized
- [ ] **Test coverage:** Voice modal unit tests: open/close, keyword chip navigation
- [ ] **Test coverage:** Keyword routing tests: each keyword maps to correct screen
- [ ] **Test coverage:** Fallback UI tests: keyword buttons navigate correctly when speech unavailable

## Subtasks

- [ ] Implement SpeechRecognition wrapper (Est: 2h) - browser API detection, Hindi/MR language
- [ ] Create voice modal UI (Est: 1h) - microphone animation, status text
- [ ] Implement keyword extraction (Est: 1h) - map recognized text to screen actions
- [ ] Add permission handling (Est: 1h) - graceful degradation if denied
- [ ] Add continuous listening mode option (Est: 1h) - for accessibility
- [ ] Test on Chrome Android (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Voice navigation works on Android Chrome
- [ ] Falls back to buttons on iOS Safari (speech API limited)

## Dependencies

- TODO-400 (PWA Architecture)
