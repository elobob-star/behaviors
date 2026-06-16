# Jules Behavioral Playbook

> *Living quirks log (vision §7 and §8). Julia learns Jules' behavior
> here. New entries are appended — never edited — by*
> `Julia/src/julia/behavior/self_improve.py`. Corrections and
> richer analyses come in as PRs, never as silent edits.

How to read this file: each entry is dated, kind-tagged, and links
back to the task ledger (`task_id`) that produced it. The playbook is
the orchestrator's cross-repo, cross-sessions knowledge — it sits
above Jules' per-repo native memory and complements it without
shadowing it.

## Canary baseline (vision §6)

The known-good shape that the daily canary probe expects to see from
Jules. Any drift from this baseline is treated as a `kind=drift`
playbook entry and (when persistent) opens a dossier PR.

- A canary run currently walks:
  `plan_generated -> agent_messaged -> session_completed` with
  one synthetic `pullRequestUrl`.
- Recorded fixture: `tests/fixtures/canary_baseline.json`.

## Observed shape drift
## kind=completion - repo=elobob-star/julia-sandbox - task=9f014c846a67
Merged https://github.com/elobob-star/julia-sandbox/pull/1.


## kind=question - repo=elobob-star/julia-sandbox - task=9f014c846a67
Clarification Q answered (q=29 chars).


## kind=plan - repo=elobob-star/julia-sandbox - task=9f014c846a67
Plan approved on first pass.


## kind=plan - repo=elobob-star/julia-sandbox - task=903d10602d9b
Plan approved on first pass.


## kind=completion - repo=elobob-star/julia-sandbox - task=fb8c1203e743
Merged https://github.com/elobob-star/julia-sandbox/pull/1.


## kind=question - repo=elobob-star/julia-sandbox - task=fb8c1203e743
Clarification Q answered (q=29 chars).


## kind=plan - repo=elobob-star/julia-sandbox - task=fb8c1203e743
Plan approved on first pass.



<!-- self_improve.py appends here. Format: -->
<!-- ## YYYY-MM-DD — kind=<plan|question|drift|completion> — repo=<owner/name> — task=<task-id> -->
<!-- <one-paragraph gist with quoted activity payload fragment> -->

## Failed prompts and recovered versions

<!-- self_improve.py appends here when a prompt change followed a failure. -->

## Behavioral notes (manual, never auto-merged)

`scripts/self_improve.py` will not append here; this section is the
human-curated partner to the auto-learned entries above. Engineer
edits are normal PRs against this file.
