# 0001-RISK-missing-specs-directory-blocks-implement

**Type:** RISK
**Date:** 2026-05-22
**Round:** kisanmitra-product redteam Round 1

## Finding

`workspaces/kisanmitra-product/` has no `specs/` directory. Per `specs-authority.md` Rule 1 ("Every Project Has A `specs/` Directory With `_index.md`"), this is a hard prerequisite before `/implement` can proceed.

All 18 todos reference spec sections that do not exist. The implicit spec is demo.html — which was verified clean in the prior session (0 CRITICAL/0 HIGH/0 MEDIUM across 17 screens, 494 translations, CPE simulator). But demo.html is a prototype simulation, not an authoritative domain spec. The gap between "demo shows X" and "spec requires X under contract Y with edge cases Z" is exactly the class of drift this rule prevents.

## Why This Is a Risk

The todos were written against demo.html behavior. When implementation begins, developers will read demo.html and code to what they see — not to an explicit contract. Without spec files, there is no authoritative answer when questions arise like:
- What happens if eNAM API is unreachable for >2 seconds?
- What is the exact MSP threshold for onion distress flagging?
- What triggers Gate 3 (Cash Flow) to move from pass to partial?
- What is the exact FarmerState dataclass fields?

These are not academic — the todos have acceptance criteria for each. Without specs, the answers live in one developer's head, not in the codebase.

## How to Resolve

Create `specs/` directory with domain spec files before `/implement`. The minimum viable set:
- `specs/_index.md` — manifest
- `specs/farmer-profile.md` — entity + CRUD contracts
- `specs/cpe-engine.md` — 5-gate rule definitions
- `specs/income-engine.md` — mandi + storage + sell recommendation logic
- `specs/obligation-calendar.md` — obligation types + cash flow math
- `specs/integrations.md` — eNAM, IMD, govt scheme API contracts

Per `specs-authority.md` Rule 5b, every spec edit MUST trigger a full sibling-spec re-derivation sweep. This is especially important here — the domain is tightly coupled (CPE gates depend on farmer state; farmer state depends on obligation calendar; income engine depends on mandi prices).

## Status

OPEN — awaiting `specs/` creation before implementation begins.
