"""Safety categoriser — the single source of truth for behavior-as-PRs.

Vision §8 + §15 promise one shared safety surface across every code
path that opens a behavior PR. Two implementations exist today
(``scripts/self_improve.py`` for offline, ``julia/behavior/editor.py``
for runtime) and they were drifting. The move: hoist all of this
into one module; have both the script and the runtime import from
here. A regression test in ``tests/test_safety.py`` asserts the
two import sites resolve to the same strings.

The bug this fixes: ``self_improve.py`` declared a ``DENYLIST``
regex but its ``categorise()`` never invoked it, so secret-shaped
filenames (e.g. ``prompts/api_key_guidance.md``) were silently
accepted. The runtime editor refused them. After this consolidation,
both refuse — uniformly.
"""

from __future__ import annotations

import enum
import re


LOW_STAKES_DIRS: tuple[str, ...] = ("playbook/", "prompts/")
BEHAVIOURAL_DIRS: tuple[str, ...] = ("policies/",)

# Files that must never be touched via a behavior PR — the vision
# itself ("the locked file policies/safety.md") plus any future
# additions. Frozen.
LOCKED_FILES: frozenset[str] = frozenset({"policies/safety.md"})

# Pattern that names a file too dangerous to PR against, regardless
# of which directory it lives in. Anchored where absolute certainty
# is wanted (``.env$`` / ``.key$`` mean "file ending in .env / .key");
# non-anchored tokens warn on secret-shaped names anywhere.
DENYLIST = re.compile(
    r"(secret|password|credential|api[_-]?key|token|\.env$|\.key$)",
    re.IGNORECASE,
)


class Category(str, enum.Enum):
    LOW_STAKES = "low-stakes"
    BEHAVIOURAL = "behavioural"
    LOCKED = "locked"


class BehaviorDenied(RuntimeError):
    """Raised when the categoriser refuses to open a behavior PR."""


def categorise(file: str) -> Category:
    """Resolve a target file path to its :class:`Category`.

    Refuses (raises :class:`BehaviorDenied`) when:
      * ``file`` is in :data:`LOCKED_FILES`,
      * ``file`` matches :data:`DENYLIST` (secret-shaped name),
      * ``file`` is not under a tracked behaviour directory.

    Vision §8 + §15 are the binding contract for this surface; a
    refusal here is final regardless of which caller invoked it.
    """
    if file in LOCKED_FILES:
        raise BehaviorDenied(
            f"refusing to open a PR against locked file {file!r}"
        )
    if DENYLIST.search(file):
        raise BehaviorDenied(
            f"refusing to open a PR: {file!r} matches the safety denylist"
        )
    if any(file.startswith(prefix) for prefix in BEHAVIOURAL_DIRS):
        return Category.BEHAVIOURAL
    if any(file.startswith(prefix) for prefix in LOW_STAKES_DIRS):
        return Category.LOW_STAKES
    raise BehaviorDenied(
        f"refusing to open a PR against {file!r}: not under a tracked directory"
    )
