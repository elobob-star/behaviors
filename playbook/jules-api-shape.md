# Jules API Shape — verified 2026-06-16 (first live validation)

> **Living reference** (vision section 7). Everything below was
> observed end-to-end against
> `sources/github/elobob-star/julia-sandbox` with a real Jules API
> key. Update this file when new endpoints or shapes appear; treat
> the relevant `Julia/src/julia/jules/*.py` code as a *projection*
> of this file (vision section 8 — behavior as code).

## Base URL

```
https://jules.googleapis.com/v1alpha
```

The 404 we initially observed on `POST /v1alpha/sessions` turned
out to be transient — the endpoint works. Don't change the URL
without first re-probing against the current docs.

## Authentication

* `X-Goog-Api-Key: <API_KEY>` works for **most** read paths
  (`GET /sessions/`, `GET /sources`, `GET /sessions/{id}`) and for
  `POST /sessions` (create) and `:approvePlan` (action).
* `GET /sessions/{id}/activities` accepts `X-Goog-Api-Key` *only
  when the session has produced at least one activity*. An
  empty session returns `{}`, not `{"activities": []}` — treat
  the empty dict as "no activities yet" and don't error.
* Drives the orchestrator's `_drive_session` to skip the response
  when the dict is empty.

(A future iteration may need OAuth for some methods; if a 401
shows up "ACCESS_TOKEN_TYPE_UNSUPPORTED", escalate to the owner.)

## Activity discriminator

The dossier (in `src/julia/jules/dossier.py`, prior version)
assumed `activities[i].type` was a string discriminator. It is
not. Jules uses **event-shaped payloads** instead. The
discriminator is the *presence of one of these keys*:

| Key | Meaning | Vision mapping |
| --- | --- | --- |
| `planGenerated` | Jules proposed a plan | `plan` |
| `planApproved` | Owner (or pre-approval) accepted it | progress, transition out of `plan` |
| `agentMessaged` | Jules asked a clarifying question | `question` |
| `progressUpdated` | Step progress, work in flight, code review, commit | `progress` / `question` / `completed` (depends on sub-key) |
| `sessionCompleted` | All plan steps done; PR-shaped artifacts on `artifacts[]` | `completed` |
| `sessionFailed` | Jules abandoned the task | `failed` |

Each activity has both an `id` field and a `name` field
(`sessions/{id}/activities/{a}`); either is a stable key. The
prior dossier's `activity_key` should prefer `id` over `name`
because `id` is shorter to interpolate; both work.

## Artifact shape

Activities may carry `artifacts: []`. The interesting payloads:

* `artifacts[].changeSet.gitPatch.unidiffPatch` — full unidiff
  patch of the proposed change. Use it as the *content* of the
  PR if Jules doesn't open a PR for you.
* `artifacts[].changeSet.gitPatch.baseCommitId` — the SHA the
  patch applies on top of.
* `artifacts[].changeSet.gitPatch.suggestedCommitMessage` —
  Jules' suggested commit title and body (good for the PR title
  when applying the patch manually).
* When the session completes, the `sessionCompleted` activity
  carries the final patch. **A PR URL is not always present.**
  For low-rigor tasks (single-line changes), Jules fell short of
  actually opening the GitHub PR; we received the `gitPatch` as
  a fallback artifact in the 2026-06-16 first live validation.

This means: the orchestrator's `_on_completed` should handle a
missing `pullRequestUrl` gracefully — apply the `gitPatch`
artifact as a brand-new PR (vision section 18: "what is never
done autonomously" does *not* include "open a PR from a Jules
artifact").

## Plan shape

Plans are *stepped*, not free-form text:

```json
{
  "id": "306fa3768fe74e6ea1725b74d1c28f94",
  "steps": [
    {"id": "...", "title": "Create CANARY.md with the requested content", "index": 0},
    {"id": "...", "title": "Run tests / verification / review",   "index": 1},
    {"id": "...", "title": "Submit the changes",                   "index": 2}
  ]
}
```

For `prompts/plan_review.md`, the field to look at is
`planGenerated.plan.steps[*].title` joined with newlines, not the
free-form `description` the dossier used to assume. The model
verdict stays "APPROVE / REVISE" the same way.

## PR shape

When Jules opens a pull request, `sessionCompleted` also carries
`pullRequestUrl` (verified against existing fixtures and the
`FakeJulesClient`'s shape; not yet observed live because the
2026-06-16 canary task did not reach the PR-stage).

## Things we *don't* yet know

* Whether `JULIA_JULES_DAILY_QUOTA` is enforced server-side
  (we have clients; we haven't seen a 429 yet).
* Whether `agentMessaged` (clarification) returns `question`
  or lives at a different key in vN.
* How the orchestrator should react to a session that lands
  `sessionCompleted` *without* a `gitPatch` artifact (a rare
  edge — Jules may discard a session for being off-goal).

All three of these go into `playbook/jules-playbook.md` as new
`kind=drift` entries the next time they appear.

## See also

* Dossier projection: `Julia/src/julia/jules/dossier.py`
  (`ACTIVITY_*` constants, `classify_activity`, `activity_key`).
* Phase 2.2 commit in elobob-star/Julia documenting the
  `(empty) sessions/{id}/activities` behavior.
* Phase 1 commit (9ed5ec7) — original posture.
