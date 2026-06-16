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



## 2026-06-16 - kind=drift - repo=elobob-star/julia-sandbox - task=2421384606932503230
First live validation. Observed against the real Jules API on
2026-06-16 via session /sessions/2421384606932503230.

Key drift from the v3.0 vision dossier:

1. `activities[i].type` does NOT exist; the discriminator is the
   presence of event-shaped keys (`planGenerated`, `planApproved`,
   `agentMessaged`, `progressUpdated`, `sessionCompleted`,
   `sessionFailed`).
2. Plans are stepped (`plan.steps[].title`), not free text. The
   plan-review prompt needs to read `steps[i].title` joined with
   newlines.
3. `sessionCompleted` does not always carry `pullRequestUrl`. For
   trivial single-line changes, Jules fell short of opening a
   GitHub PR; the orchestrator should apply the
   `artifacts[].changeSet.gitPatch.unidiffPatch` as a fallback.
4. `GET /sessions/{id}/activities` returns `{}` (empty dict,
   not `{"activities": []}`) when no activities have appeared
   yet. Treat the empty dict as a no-op poll, not an error.

Fix-all-the-above in `Julia/src/julia/jules/dossier.py` and
`Julia/src/julia/jules/client.py`; this entry is the
authoritative reference until the dossier is updated.

The session itself completed successfully (state=COMPLETED,
url=https://jules.google.com/session/2421384606932503230). The
contents of CANARY.md landed as a real gitPatch artifact.

Recovery used: the orchestrator's `_run_task` recorded a
`task_failed` decision with the HTTP 404 exception; this entry
is written by the engineer (Fable 5), not by the orchestrator,
because the editor's playbook entry is gated on the failing path
that triggered it. Once the orchestrator can read activities
correctly, future drift will be auto-recorded.


<!-- self_improve.py appends here. Format: -->
<!-- ## YYYY-MM-DD — kind=<plan|question|drift|completion> — repo=<owner/name> — task=<task-id> -->
<!-- <one-paragraph gist with quoted activity payload fragment> -->

## Failed prompts and recovered versions

<!-- self_improve.py appends here when a prompt change followed a failure. -->

## Behavioral notes (manual, never auto-merged)

`scripts/self_improve.py` will not append here; this section is the
human-curated partner to the auto-learned entries above. Engineer
edits are normal PRs against this file.
