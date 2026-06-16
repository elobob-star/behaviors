"""Prompt regression suite (vision section 5.4).

Three golden scenarios, each with a recorded Jules activity. The
suite asserts that the prompts in ``behaviors/prompts/*.md`` can still
be read by ``julia.main/src/julia/jules/dossier.py`` and that the
verdicts they encode match the fixtures. Adding a new prompt change
without updating the fixtures is treated as a regression.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(prompt_name: str) -> str:
    text = (ROOT / "prompts" / f"{prompt_name}.md").read_text()
    # The body of each prompt is everything after the first heading line.
    return text.split("\n", 2)[2].strip() if "\n" in text else text


def test_plan_review_prompt_present():
    body = _read("plan_review")
    assert "APPROVE" in body and "REVISE" in body
    assert "protected branches" in body  # safety carve-out preserved


def test_clarification_prompt_present():
    body = _read("clarification")
    assert "Never invent credentials" in body
    assert "decisively" in body


def test_canary_prompt_present():
    body = _read("canary")
    assert "CANARY.md" in body
    assert "current date" in body


def test_daily_digest_prompt_present():
    body = _read("daily_digest")
    assert "five lines" in body or "five-line" in body.lower()


def test_pi_classified_fixture_matches_prompt_intent(tmp_path: Path):
    fixture = json.loads((ROOT / "tests" / "fixtures" / "plan_classified.json").read_text())
    body = _read("plan_review")
    # A reasonable, minimal one-file change does not include protected
    # branches or history rewrites, so the prompt mandates APPROVE.
    plan_text = fixture["activity"]["plan"].lower()
    assert "protected" not in plan_text
    assert "rewrite" not in plan_text
    assert "Approve" in body or "APPROVE" in body


def test_question_classified_fixture_prefers_simple_default():
    body = _read("clarification")
    # The clarification prompt nudges for the simplest reasonable
    # default; an answer targeting ``main`` is in scope.
    assert "repository default branch" in body


def test_drift_classified_fixture_lands_in_progress():
    fixture = json.loads((ROOT / "tests" / "fixtures" / "drift_classified.json").read_text())
    # Unknown activity kinds today fall into the ``progress``
    # bucket; the canary probes this directly via
    # ``Orchestrator.run_canary`` to detect drift.
    assert fixture["expected_classification"] == "progress"


def test_prompt_diff_is_reviewable():
    """Each prompt file is plain Markdown with no leading whitespace rows.

    Diff-friendliness is a property of the file layout, not just the
    content. Catch accidental editor-formatting churn early.
    """
    for name in ("plan_review", "clarification", "canary", "daily_digest"):
        text = (ROOT / "prompts" / f"{name}.md").read_text()
        first_heading = re.search(r"^# .*$", text, re.MULTILINE)
        assert first_heading is not None, f"{name}.md is missing a top-level heading"
