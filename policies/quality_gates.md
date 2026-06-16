# Quality Gates (vision §18)

Every PR that Julia intends to merge — autonomously or as part of
`/approve` — must clear the local gate:

## Today (Phase 1)

`GitHubAPI.pr_checks_passed(pr_url)` aggregates GitHub check-runs for
the PR's head SHA. If the repo has no CI configured, the gate passes
by absence — this is logged in the decision trace so the absence is
visible and the absence itself is reviewable.

## Tomorrow (vision §9 — local verification)

When a sandbox workspace lands, the gate becomes a layered poll:

1. GitHub check-runs pass (network).
2. Local sandbox builds + lint + pytest before merge authorises.
3. Render MCP deploys to a preview environment for PRs touching
   `main` of repos at `risk-tier >= 2`.

Gate strictness scales with **repo risk tier** (vision §18, §20):
hobby repos at tier 1 pass on GitHub CI only; tier 3 repos require
local sandbox + preview deploy before a merge.

## On gate failure

`_on_completed` comments back to Jules on the PR with the failing
checks and records `gates_failed` in the decision trace. The task
transitions to `FAILED` with `error='quality gates failed'`. The
ladder records one anomaly for the repo (subject to the auto-drop
rule in `autonomy_rules.md`).

## What rungs accept which gates

- rungs 0–1: gates are not consulted (no merge happens).
- rung 2: gates must pass **and** an approval must queue.
- rungs 3–4: gates must pass; then merge is automatic.

## Tier proposal (vision §18)

A repo's risk tier is proposed at onboarding by the wizard
(Phase 3) and approved by the owner. Defaults: small helpers → 1,
primary products → 2, anything touching secrets, billing, or
destruction → 3.
