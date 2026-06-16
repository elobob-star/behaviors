#!/usr/bin/env python3
"""Append a playbook entry to ``behaviors/playbook/jules-playbook.md``.

Subcommand of ``scripts/self_improve.py``: low-stakes, called per
completed task by the orchestrator to record what was learned. The
append-only format keeps the playbook auditable in git log:

    ## YYYY-MM-DD - kind=<kind> - repo=<owner/name> - task=<task-id>
    <one-paragraph gist>
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


_PLAYBOOK_HEADER = "## Observed shape drift"
_KIND_PATTERN = re.compile(r"^(plan|question|drift|completion|failure|info)$")


def append(repo: Path, kind: str, repo_name: str, task_id: str, gist: str) -> None:
    """Append one playbook entry under the ``Observed shape drift`` header."""
    if not _KIND_PATTERN.fullmatch(kind):
        raise ValueError(f"invalid kind: {kind!r}")
    target = repo / "playbook" / "jules-playbook.md"
    if not target.exists():
        raise FileNotFoundError(target)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block = (
        f"\n## {today} - kind={kind} - repo={repo_name} - task={task_id}\n"
        f"{gist.strip()}\n"
    )
    text = target.read_text()
    if _PLAYBOOK_HEADER not in text:
        text += "\n" + _PLAYBOOK_HEADER + "\n"
    # Insert directly after the drift header so the file remains human-readable
    # in linear order even before pull request tooling exists.
    head, tail = text.split(_PLAYBOOK_HEADER, 1)
    new_text = head + _PLAYBOOK_HEADER + block + tail
    target.write_text(new_text)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append a playbook entry")
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--repo-name", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--gist", required=True)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    append(
        repo=args.repo,
        kind=args.kind,
        repo_name=args.repo_name,
        task_id=args.task_id,
        gist=args.gist,
    )


if __name__ == "__main__":
    main()
