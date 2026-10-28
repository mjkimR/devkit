"""Document ID aliases through the proposals lifecycle: handoff carriage, translation, rewrite and clash refusal."""

from __future__ import annotations

import re
from pathlib import Path

import devkit_docs
import pytest
from devkit_agt.features.rules.services.testing import check, load_rule
from devkit_core.core.frontmatter import parse
from spec_support.proposals import TODAY, accept, spec_dir
from spec_support.types import Write

from devkit_spec.base.errors import (
    ProposalDecisionExistsError,
    ProposalExistsError,
    ProposalSlugConflictError,
    ProposalTargetExistsError,
    SpecExistsError,
)
from devkit_spec.features.proposals import create_proposal, create_spec, handoff_proposal
from devkit_spec.features.proposals.usecases.scaffold import CreateProposalDecisionUseCase

RULE = load_rule(Path(devkit_docs.__file__).parent / "bundles/docs/bundle/rules/document_reference/rule.py")


def _proposal(root: Path, slug: str, aliases: str = "") -> Path:
    proposal = root / create_proposal(root, slug, today=TODAY).path
    accept(proposal, f"\naliases: [{aliases}]" if aliases else "")
    return proposal


def _padr(root: Path, slug: str, title: str, aliases: str, body: str = "") -> Path:
    path = root / CreateProposalDecisionUseCase().execute(root, slug, title).path
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(id: .*)$", rf"\1\naliases: [{aliases}]", text, count=1)
    path.write_text(text + body, encoding="utf-8")
    return path


def _meta(path: Path) -> dict[str, object]:
    data = parse(path.read_text(encoding="utf-8")).data
    assert data is not None
    return data


def test_handoff_carries_translates_and_rewrites_aliases(workspace: Path, write: Write) -> None:
    _proposal(workspace, "carry", "PROP-carry-old")
    _padr(workspace, "carry", "Choice", "PADR-choice-old")
    _padr(workspace, "carry", "Cite", "PADR-cite-old", "\nSee `PADR-choice-old` and `PROP-carry-old`.\n")
    adr = write(
        "docs/decisions/2026-01/20260101-earlier.md",
        "---\nid: ADR-earlier\nstatus: accepted\n---\n# [ADR-earlier] Earlier\n\n`PROP-carry-old` `PADR-choice-old`\n",
    )
    other = write(
        "docs/proposals/PROP-other/proposal.md",
        "---\nid: PROP-other\nstatus: draft\ndepends_on: [PROP-carry-old]\n---\n# [PROP-other] Other\n",
    )
    result = handoff_proposal(workspace, "carry", today=TODAY)
    spec = spec_dir(workspace, "carry") / "spec.md"
    assert _meta(spec)["aliases"] == ["SPEC-carry-old"]
    decisions = {d.id: workspace / d.path for d in result.decisions}
    assert _meta(decisions["ADR-choice"])["aliases"] == ["ADR-choice-old"]
    cite = decisions["ADR-cite"].read_text(encoding="utf-8")
    assert _meta(decisions["ADR-cite"])["aliases"] == ["ADR-cite-old"]
    assert "See `ADR-choice` and `SPEC-carry`." in cite
    assert adr.read_text(encoding="utf-8").endswith("`SPEC-carry` `ADR-choice`\n")
    assert _meta(other)["depends_on"] == ["SPEC-carry"]
    assert check(RULE, workspace) == []


def test_handoff_refuses_a_translated_alias_that_is_taken(workspace: Path, write: Write) -> None:
    proposal = _proposal(workspace, "taken", "PROP-earlier")
    write("specs/2026-01/20260101-earlier/spec.md", "---\nid: SPEC-earlier\nstatus: completed\n---\n")
    with pytest.raises(ProposalTargetExistsError) as raised:
        handoff_proposal(workspace, "taken", today=TODAY)
    assert raised.value.target_files == ("specs/2026-01/20260101-earlier/spec.md",)
    assert proposal.is_file() and not spec_dir(workspace, "taken").exists()


def test_handoff_refuses_a_graduating_adr_that_is_an_existing_alias(workspace: Path, write: Write) -> None:
    proposal = _proposal(workspace, "shadow")
    CreateProposalDecisionUseCase().execute(workspace, "shadow", "Same")
    write("docs/decisions/2026-01/20260101-kept.md", "---\nid: ADR-kept\nstatus: accepted\naliases: [ADR-same]\n---\n")
    with pytest.raises(ProposalTargetExistsError):
        handoff_proposal(workspace, "shadow", today=TODAY)
    assert proposal.is_file()


def test_handoff_refuses_two_padrs_declaring_one_alias(workspace: Path) -> None:
    proposal = _proposal(workspace, "pair")
    _padr(workspace, "pair", "One", "PADR-shared")
    _padr(workspace, "pair", "Two", "PADR-shared")
    with pytest.raises(ProposalTargetExistsError) as raised:
        handoff_proposal(workspace, "pair", today=TODAY)
    assert raised.value.target_files == ("ADR-shared",)
    assert proposal.is_file() and not spec_dir(workspace, "pair").exists()


def test_handoff_refuses_a_spec_id_that_is_an_existing_alias(workspace: Path, write: Write) -> None:
    proposal = _proposal(workspace, "renamed")
    write(
        "specs/2026-01/20260101-current/spec.md",
        "---\nid: SPEC-current\nstatus: completed\naliases: [SPEC-renamed]\n---\n",
    )
    with pytest.raises(ProposalSlugConflictError):
        handoff_proposal(workspace, "renamed", today=TODAY)
    assert proposal.is_file()


def test_scaffolding_treats_a_spec_alias_like_a_declared_spec(workspace: Path, write: Write) -> None:
    write(
        "specs/2026-01/20260101-current/spec.md", "---\nid: SPEC-current\nstatus: completed\naliases: [SPEC-old]\n---\n"
    )
    with pytest.raises(ProposalSlugConflictError):
        create_proposal(workspace, "old", today=TODAY)
    with pytest.raises(SpecExistsError):
        create_spec(workspace, "old", day=TODAY)
    create_proposal(workspace, "fresh", today=TODAY)
    write("docs/decisions/2026-01/20260101-kept.md", "---\nid: ADR-kept\nstatus: accepted\n---\n")
    write(
        "docs/proposals/PROP-fresh/decisions/PADR-first.md",
        "---\nid: PADR-first\nstatus: draft\naliases: [PADR-taken]\n---\n",
    )
    with pytest.raises(ProposalDecisionExistsError):
        CreateProposalDecisionUseCase().execute(workspace, "fresh", "Taken")


def test_handoff_refuses_an_alias_that_would_become_a_dated_spec_id(workspace: Path) -> None:
    from devkit_spec.base.errors import ProposalInvalidError

    proposal = _proposal(workspace, "dated", "PROP-20260101-dated")
    with pytest.raises(ProposalInvalidError, match="SPEC-20260101-dated"):
        handoff_proposal(workspace, "dated", today=TODAY)
    assert proposal.is_file() and not spec_dir(workspace, "dated").exists()


def test_new_proposal_refuses_a_slug_declared_as_an_alias(workspace: Path, write: Write) -> None:
    write("docs/proposals/PROP-current/proposal.md", "---\nid: PROP-current\nstatus: draft\naliases: [PROP-old]\n---\n")
    with pytest.raises(ProposalExistsError, match="already declared as an alias"):
        create_proposal(workspace, "old", today=TODAY)
    assert not (workspace / "docs/proposals/PROP-old").exists()
