#!/usr/bin/env python3
"""Self-improvement PR opener (vision section 8).

Called by Julia to convert an observed lesson into a behavioural PR
against the local clone of the behaviors repo. Three categories:

  * low-stakes: playbook entries, prompt wording. Auto-merge after
    the prompt regression suite (``behaviors/tests/``) passes.
  * behavioural: autonomy rules, gates, etc. Owner approval at the
    gateway before merge.
  * locked: paths in ``DENYLIST``. This script refuses to open a PR
    at all.

The orchestrator's runtime is Julia on a Mac Mini; this script runs
in a Python interpreter, never on Jules. Jules is a peer, not the
principal.

Usage::

    python scripts/self_improve.py \\
        --repo . \\
        --file prompts/plan_review.md \\
        --category low-stakes \\
        --rationale "tightening the off-goal signal"

Currently this script writes directly to the local clone via ``git``
commands. Phase 3 will swap the ``LocalCommitter`` for a
``GitHubCommitter`` once the behaviors repo lands on
github.com/<owner>/behaviors. Until then the local commit is the
authoritative behaviour change.
"""

from __future__ import annotations

import argparse
import subprocess  # nosec - B603 (subprocess called with controlled inputs)
import sys
from dataclasses import dataclass
from pathlib import Path

from _safety import (
    BehaviorDenied,
    Category,
    LOW_STAKES_DIRS,
    BEHAVIOURAL_DIRS,
    LOCKED_FILES,
    DENYLIST,
    categorise,
)


@dataclass(frozen=True)
class Proposal:
    repo: Path
    file: str
    category: Category
    rationale: str
    message: str


def _run(cmd: list[str], cwd: Path) -> str:
    return subprocess.run(  # nosec - B603
        cmd,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def open_pr(proposal: Proposal) -> str:
    """Apply the proposal to the local clone; return the resulting commit SHA.

    The orchestrator's behaviour PR opener is intentionally tiny:
    it does not touch any network. Phase 3 will swap the local
    commit for a real GitHub PR when the behaviors repo moves onto
    github.com.
    """
    category = categorise(proposal.file)
    if category is not proposal.category:
        raise BehaviorDenied(
            f"category mismatch for {proposal.file!r}: "
            f"file is {category.value}, claimed {proposal.category.value}"
        )
    target = proposal.repo / proposal.file
    if not target.exists():
        raise FileNotFoundError(f"{target} is not in the repo; refusing to invent a path")
    _run(["git", "checkout", "-b", f"self-improve/{proposal.file.replace('/', '-')}"], proposal.repo)
    target.write_text(proposal.message)
    _run(["git", "add", proposal.file], proposal.repo)
    _run(
        ["git", "commit", "-m", f"{proposal.category.value}: {proposal.rationale}"],
        proposal.repo,
    )
    sha = _run(["git", "rev-parse", "HEAD"], proposal.repo)
    return sha


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Open a behavioural PR against the behaviors repo")
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--file", required=True)
    parser.add_argument(
        "--category",
        required=True,
        choices=[c.value for c in Category],
    )
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--message", required=True, help="Full new file content")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    proposal = Proposal(
        repo=args.repo,
        file=args.file,
        category=Category(args.category),
        rationale=args.rationale,
        message=args.message,
    )
    try:
        sha = open_pr(proposal)
    except BehaviorDenied as exc:
        print(f"denied: {exc}", file=sys.stderr)
        sys.exit(2)
    print(f"opened PR with commit {sha} for {proposal.file} ({proposal.category.value})")


if __name__ == "__main__":
    main()
