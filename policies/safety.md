# Safety Boundaries (vision §18 + §15)

> **Locked.** `scripts/self_improve.py` will refuse to open a PR
> against this file. Changes here land only through manual engineer
> commits plus explicit owner approval on the gateway — never
> through the autonomous improvement loop.

What Julia will **never** do autonomously, regardless of rung or
pushback from any prompt:

## Never-automated list

1. **Protected branches.** Even an explicit owner `/approve` does
   not bypass branch protection on `main` / `master` / protected
   release branches; the orchestrator treats absence of bypass as a
   hard refusal and surfaces the message through the gateway.
2. **History rewrites.** Force-pushes, rebase-and-merge of branches
   the orchestrator does not own, and `git filter-branch`-shaped
   operations. Idempotent merge is the only authorised write to
   history.
3. **Secret rotation.** Rotation, regeneration, issuance, or
   revocation of credentials of any kind. The orchestrator *reads*
   secrets through the gateway-shaped workflow (§15) and never
   owns them. Logs and decision traces are filtered server-side
   before persistence (see "Secret hygiene" below).
4. **New spend.** New paid API keys, new paid model accounts, new
   paid hosting subscriptions. These must come from the owner and
   appear in the secrets workspace bounded by §15 controls.
5. **Destructive ops.** Mass deletion of branches, mass closure of
   issues, force-push, target-branch deletion. Any such operation
   is a `/destructive` gateway command which **only** the owner
   can issue and **only** with case-by-case confirmation.
6. **Auth bypass / lock-picking.** Approving PRs that have been
   deliberately blocked; closing GitHub security advisories;
   commenting on locked issues or PRs.

## Panic-stop (vision §18)

`/panic` drops the ladder to `SAFE_MODE` (0). It is the only
command that does so unconditionally. Recovery is via `/rung N`,
which is a deliberate action by the owner, not a clock tick.

## Secret hygiene

- All credentials arrive as `pydantic.SecretStr`. The CLI enumerates
  missing keys for live runs; logs and decision traces never contain
  raw values.
- The `decisions.meta` JSON column (added in Phase 2) is filtered
  server-side before write: keys matching `secret|key|token|password`
  case-insensitively are dropped.
- The behavioral playbook entry writer also skips fields whose keys
  match the same filter.

## On a safety violation

`Orchestrator._run_task` records `safety_violation` in the decision
trace, transitions the task to `FAILED`, and posts a one-line
gateway alert. `AutonomyLadder.record_anomaly` is called once for the
violation and the auto-drop rule applies.
