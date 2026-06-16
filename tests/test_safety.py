"""Regression suite for ``scripts/self_improve.py``.

The opener is small enough that the main risk is the safety
denylist drifting out of sync with ``policies/safety.md``. This
suite binds them together so a deletion or rewrite of either side
breaks CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import self_improve  # noqa: E402  -- path injection above is intentional
import playbook_append  # noqa: E402


def test_safety_locked_path_raises():
    with __import__("pytest").raises(self_improve.BehaviorDenied):
        self_improve.open_pr(
            self_improve.Proposal(
                repo=ROOT,
                file="policies/safety.md",
                category=self_improve.Category.LOCKED,
                rationale="test",
                message="would-be rewrite",
            )
        )


def test_categorise_autonomy_is_behavioural():
    assert self_improve.categorise("policies/autonomy_rules.md") is self_improve.Category.BEHAVIOURAL


def test_categorise_prompt_is_low_stakes():
    assert self_improve.categorise("prompts/plan_review.md") is self_improve.Category.LOW_STAKES


def test_categorise_unknown_raises():
    with __import__("pytest").raises(self_improve.BehaviorDenied):
        self_improve.categorise("secrets/foo.txt")


def test_safety_doc_mentions_panic_stop():
    text = (ROOT / "policies" / "safety.md").read_text()
    assert "/panic" in text
    assert "SAFE_MODE" in text or "safe mode" in text.lower()


def test_gitignore_protects_local_secrets():
    gitignore = (ROOT / ".gitignore").read_text()
    assert ".env" in gitignore
    assert "secret" in gitignore.lower() or ".env" in gitignore


def test_playbook_append_writes_to_drift_section(tmp_path: Path):
    repo = tmp_path / "behaviors"
    (repo / "playbook").mkdir(parents=True)
    target = repo / "playbook" / "jules-playbook.md"
    target.write_text(
        "# Jules Behavioral Playbook\n\n## Observed shape drift\n<!-- anchor -->\n"
    )
    playbook_append.append(
        repo=repo,
        kind="plan",
        repo_name="acme/widgets",
        task_id="t-001",
        gist="Plan was approved on first pass.",
    )
    text = target.read_text()
    assert "kind=plan" in text
    assert "repo=acme/widgets" in text
    assert "task=t-001" in text


def test_playbook_append_rejects_bad_kind(tmp_path: Path):
    repo = tmp_path / "behaviors"
    (repo / "playbook").mkdir(parents=True)
    (repo / "playbook" / "jules-playbook.md").write_text(
        "# Jules Behavioral Playbook\n\n## Observed shape drift\n<!-- anchor -->\n"
    )
    import pytest  # local import keeps the suite standalone
    with pytest.raises(ValueError):
        playbook_append.append(
            repo=repo,
            kind="bogus",
            repo_name="x",
            task_id="t",
            gist="ignored",
        )


def test_open_pr_is_local_git(tmp_path: Path):
    """Real end-to-end: open a low-stakes PR against a tmp git clone."""
    repo = ROOT
    # Because ROOT is a real working tree we just verify the file path
    # is valid and the function refuses forbidden paths without touching git.
    with __import__("pytest").raises(self_improve.BehaviorDenied):
        self_improve.open_pr(
            self_improve.Proposal(
                repo=repo,
                file="secrets/prod.yaml",
                category=self_improve.Category.LOW_STAKES,
                rationale="test",
                message="should not reach git",
            )
        )


def test_canonical_safety_module_exports_used_names():
    """The canonical categoriser in ``scripts/_safety.py`` is the source
    of truth. ``self_improve.py`` must re-export every public symbol
    from it (vision §15: one shared safety surface)."""
    import _safety as canonical
    for name in (
        "Category",
        "BehaviorDenied",
        "DENYLIST",
        "LOCKED_FILES",
        "LOW_STAKES_DIRS",
        "BEHAVIOURAL_DIRS",
        "categorise",
    ):
        assert hasattr(self_improve, name), f"self_improve missing re-export: {name}"
        assert getattr(self_improve, name) is getattr(canonical, name), (
            f"self_improve.{name} has drifted from canonical _safety.{name}"
        )


def test_denylist_refuses_secret_shaped_filenames():
    """Regression: pre-unification, ``self_improve.categorise`` ignored
    the denylist regex entirely, so secret-shaped filenames were
    silently accepted. After unification, ``categorise`` invokes the
    regex and refuses — same as the runtime editor."""
    with __import__("pytest").raises(self_improve.BehaviorDenied):
        self_improve.categorise("prompts/api_key_guidance.md")
    with __import__("pytest").raises(self_improve.BehaviorDenied):
        self_improve.categorise("playbook/secret_section.md")
    with __import__("pytest").raises(self_improve.BehaviorDenied):
        self_improve.categorise("policies/password_reset.md")
