# Autonomy Rules (vision §5.5)

The autonomy ladder has five rungs. Changes to these rules are
**behavioural** — they require owner approval through the gateway
(`/approve-behavior <PR>`). The current rung for any repo is
persisted by the orchestrator at `~/.julia/julia.db` in the `kv`
table, keyed `rung:<owner/name>` (or `rung:__global__`).

| Rung | Name | Plans | Executes | Merges (gates passed) | Owner ping |
| --- | --- | --- | --- | --- | --- |
| 0 | SAFE_MODE | yes | no | no | every action |
| 1 | PROPOSE_ONLY | yes (queued) | no | no | every plan |
| 2 | SUPERVISED | yes | yes | no — queues for `/approve` | each queue |
| 3 | AUTO_NOTIFY | yes | yes | yes | per merge |
| 4 | FULL_AUTO | yes | yes | yes | digest only |

## Auto-drop rule

When the orchestrator records `ANOMALY_DROP_THRESHOLD = 3` anomalies
for one repo (or globally), the ladder drops one rung automatically
and the anomaly counter resets to zero. The ladder then climbs back up
only when the owner explicitly raises it via `/rung`. This is
intentionally conservative — confidence is recovered from observed
stability, not by ticking itself up.

## Per-repo overrides

The ladder implements `current(repo: str | None)` which checks
`rung:<repo>` first and falls back to `rung:__global__`. This lets
the owner (or Julia, with behavioural approval) pin a low-risk
**helper repo** to AUTO_NOTIFY (3) while keeping a financial-tracker
**production repo** at SUPERVISED (2) — using one host, one binary,
two postures.

## What rungs mean in code

See `julia-main/src/julia/autonomy.py`. `AutonomyLadder` exposes
`allows_execution(repo)` and `allows_merge(repo)`; the orchestrator
calls these *before* every consequential action. The rung is
read fresh from the store on every check — no caching, no JIT.

## Promoted posture

The orchestrator ships at rung 3 (AUTO_NOTIFY): autonomous except
that every merge pings the owner. Promotion to rung 4 is a deliberate
behavioural change and requires owner approval.
