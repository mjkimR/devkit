"""The bundled guidance states the direct acceptance and the session reclassification of a queued draft
(``SPEC-draft-direct-acceptance`` AC-12): the contract phrases an agent acts on, not the wording around them."""

from __future__ import annotations

import re
from pathlib import Path

from devkit_spec.features.proposals import create_proposal

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle"
ACCEPT = "devkit spec proposal accept"


def _read(rel: str) -> str:
    return re.sub(r"\s+", " ", _rendered(BUNDLE / rel))


def test_acceptances_are_recorded_with_the_accept_command() -> None:
    for rel in (
        "workflows/sdd-proposal.md",
        "AGENTS.md",
        "skills/spec/SKILL.md",
        "skills/spec-orchestrate/SKILL.md",
        "skills/spec-next/references/workflow-signals.md",
        "seed/docs/proposals/README.md",
    ):
        assert ACCEPT in _read(rel), rel
    workflow = _read("workflows/sdd-proposal.md")
    assert "--action accept --by user`, written only after" not in workflow  # no hand-recorded plan-accept


def test_backlog_states_the_direct_acceptance_procedure() -> None:
    backlog = _read("skills/spec/references/backlog.md")
    assert "Until direct acceptance exists" not in backlog
    for phrase in (
        f"{ACCEPT} <slug> --by user --direct --check",
        f"{ACCEPT} <slug> --by user|policy --direct --note",
        "Planning skipped",
        "pull_request = required",
        "collect-feedback",
        "No Planning run, `activity-effort` or `worker` envelope",
        "only on the base checkout",
        "SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED",
    ):
        assert phrase in backlog, phrase
    assert "Planning skipped" in _read("workflows/sdd-proposal.md") or "Planning: skipped" in _read(
        "workflows/sdd-proposal.md"
    )
    assert "a direct acceptance included: it has no Planning run" in _read("skills/spec/references/effort.md")


def test_the_lowering_rule_names_the_session_reclassification() -> None:
    for rel in ("AGENTS.md", "skills/spec/references/classification.md"):
        assert "session reclassification of a queued draft" in _read(rel), rel
    backlog = _read("skills/spec/references/backlog.md")
    assert "## Session reclassification of a queued draft" in _rendered(BUNDLE / "skills/spec/references/backlog.md")
    for phrase in ("within the authorized goal, scope and constraints", "no `PADR-*.md`", "new slug", "git revert"):
        assert phrase in backlog, phrase
    assert "session reclassification" in _read("skills/spec/references/feedback-retirement.md")
    assert "session reclassification" in _read("skills/spec-next/references/next-work.md")


def test_the_scaffold_lifecycle_holds_for_a_direct_acceptance(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    text = re.sub(r"\s+", " ", (tmp_path / create_proposal(tmp_path, "idea").path).read_text(encoding="utf-8"))
    assert f"{ACCEPT} idea --by user" in text and "--direct" in text
    assert "set status: accepted and merge the Planning branch" not in text


def _rendered(path: Path) -> str:
    from devkit_dist.features.distribution.services.bundles.templates import render_template

    if path.name.endswith(".md.jinja"):
        return render_template(path.read_bytes(), {}, str(path), environment="local").decode()
    if path.exists():
        return path.read_text(encoding="utf-8")
    source = path.with_name(path.name + ".jinja")
    return render_template(source.read_bytes(), {}, str(source), environment="local").decode()
