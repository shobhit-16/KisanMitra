# 0002-GAP-pwa-todo-exceeds-capacity-budget

**Type:** GAP
**Date:** 2026-05-22
**Round:** kisanmitra-product redteam Round 1

## Finding

TODO-400 (Mobile PWA Architecture) is estimated at 1,200 LOC, 12 invariants, and 5 call-graph hops. Per `autonomous-execution.md` § Per-Session Capacity Budget, a single shard must stay within ≤500 LOC load-bearing logic, ≤10 invariants, and ≤4 call-graph hops.

TODO-400 exceeds all three thresholds simultaneously. This is the only todo in the 18-todo list that exceeds the budget in all three dimensions.

## Why This Is a Gap

A shard that exceeds the budget will not converge cleanly in one implementation pass. The model's attention will overflow mid-shard — invariants will be dropped, cross-file reasoning will be lost, and errors will surface at `/redteam` rather than during implementation. Recovery requires re-sharding mid-flight, which is more expensive than pre-sharding.

The TODO itself acknowledges the scope: "Migrate all 17 screens" is 7 distinct sub-tasks totaling 3 hours of estimated work. This is clearly multiple shards, not one.

## How to Resolve

Decompose TODO-400 into 4 sub-todos:

| Sub-todo | Scope | LOC Est | Invariants | Hops |
|---|---|---|---|---|
| TODO-410 | PWA manifest + service worker skeleton | 200 | 3 | 1 |
| TODO-411 | App shell + screen router | 300 | 4 | 2 |
| TODO-412 | State store + offline data sync | 350 | 5 | 3 |
| TODO-413 | 17-screen migration (grouped) | 500 | 6 | 3 |

TODO-413 may itself need further decomposition (screens grouped by data dependency: dashboard/obligations/mandi/sell/ledger vs. soil/climate/credit/CPE vs. FPO/community/news/knowledge).

## Status

OPEN — TODO-400 must be decomposed before implementation reaches it.
