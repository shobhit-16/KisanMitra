# TODO-501-Pilot-Auth-Phone-OTP

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Implement phone OTP authentication for farmer login, replacing pilot phone-number-as-ID approach.

## Context

Pilot uses phone number as farmer identifier without authentication. For production, need OTP verification to secure farmer data.

## Acceptance Criteria

- [ ] `POST /api/auth/request-otp` sends 6-digit OTP to registered phone
- [ ] `POST /api/auth/verify-otp` validates OTP, returns JWT token
- [ ] JWT token included in Authorization header for all authenticated requests
- [ ] OTP expires after 10 minutes
- [ ] Max 3 OTP requests per phone per hour (rate limiting)
- [ ] Demo mode: OTP "123456" works for all numbers during pilot

## Subtasks

- [ ] Create auth endpoints (Est: 1h) - request-otp, verify-otp
- [ ] Generate and store OTP with TTL (Est: 1h) - in-memory or Redis
- [ ] Implement JWT token generation (Est: 1h) - with farmer phone in payload
- [ ] Add JWT middleware to protected routes (Est: 1h)
- [ ] Add rate limiting (Est: 1h) - 3 requests/hour limit
- [ ] Write tests (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Protected endpoints reject requests without valid JWT
- [ ] OTP flow works end-to-end

## Dependencies

- TODO-100 (Farmer Profile CRUD)
