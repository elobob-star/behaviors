# Behaviors — Julia's system of record for its own behavior

> *"This spec is the floor, not the ceiling."* — vision §21.
> This repository implements vision §8: the orchestrator's behavior
> (prompts, policies, the Jules behavioral playbook) lives here under
> version control and changes through **reviewable PRs flowing through
> the same pipeline Julia uses for user code**.

## What's in this repo

| Path | Purpose | Change policy |
| --- | --- | --- |
| `prompts/` | Runtime prompts (plan review, clarification, canary, daily digest) | **Low-stakes** — auto-merge after the prompt regression suite passes |
| `playbook/jules-playbook.md` | Living Jules quirks log | **Low-stakes** — append-only; auto-merged by `self_improve.py` |
| `policies/autonomy_rules.md` | Rung thresholds, per-repo overrides | **Behavioural** — owner approval required |
| `policies/quality_gates.md` | Gate strictness before merge | **Behavioural** — owner approval required |
| `policies/safety.md` | Never-automated list | **Locked** — `self_improve.py` will deny any PR against this file |
| `tests/` | Prompt regression suite (vision §5.4) | **Tests** — changes land alongside the prompt they cover |
| `scripts/self_improve.py` | The PR-opener called by the orchestrator | **Engineer-only** |

## The hard rule

Vision §8: **Jules owns repo-level memory; the orchestrator owns
everything above it.** The orchestrator *reads* this repo on
startup, *writes back* through `scripts/self_improve.py`, and never
silently rewrites its own behavior. A bad self-improvement is a
`git revert`, not an archaeology project.

## Change categories

When `scripts/self_improve.py` opens a PR, it tags it with a category:

1. **Low-stakes** (`playbook/`, `prompts/`): auto-merge after the
   prompt regression suite in `tests/` passes.
2. **Behavioural** (`policies/` other than `safety.md`): blocked at
   the gateway until the owner approves through `/approve-behavior`.
3. **Locked** (`policies/safety.md` and anything matching
   `self_improve.DENYLIST`): refuses to open the PR at all.

## Local quickstart

```bash
# Run the prompt regression suite by hand:
python -m pytest tests/

# Open a self-improvement PR (used by the orchestrator):
python scripts/self_improve.py --repo . \
    --file prompts/plan_review.md \
    --category low-stakes \
    --rationale "tightening the off-goal signal"
```

## See also

- Vision: [`../Vision and docs/vision.md`](../Vision%20and%20docs/vision.md)
  (canonical) — sections 5.4, 8, 17 are the binding contract for
  this repo.
- Orchestrator wiring: [`../julia-main/src/julia/behavior/`](../julia-main/src/julia/behavior/)
