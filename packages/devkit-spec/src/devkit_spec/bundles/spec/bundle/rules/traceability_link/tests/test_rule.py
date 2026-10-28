"""``RULE-traceability-link``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Autofixable, RuleContext, Violation
from devkit_agt.features.rules.services.testing import check, load_rule, write_files

RULE = load_rule(__file__)
USECASE = "docs/usecases/governance/UC-test-usecase.md"
CAP = "docs/capabilities/governance/CAP-TEST-contract.md"


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    """``(file, line, message)`` of the violations that remain (not fixed)."""
    return [(v.file, v.line, v.message) for v in violations if not v.fixed]


def _namespaces(*names: str) -> str:
    """``.devkit/config.toml`` registering a namespace per name, with source path ``packages/<name>``."""
    return "".join(f'[[tool.docs.namespaces]]\nname = "{name}"\npath = "packages/{name}"\n\n' for name in names)


def _doc(document_id: str, header: str = "", status: str = "active") -> str:
    return f"---\nid: {document_id}\nstatus: {status}\n{header}---\n# {document_id}\n"


def _one_sided(root: Path, cap_header: str = "usecases: []\n") -> Path:
    write_files(
        root,
        {
            USECASE: _doc("UC-test-usecase", "capabilities:\n  - CAP-TEST-contract\n"),
            "docs/usecases/README.md": "# Use Cases\n",
            "docs/usecases/delivery/UC-other.md": _doc("UC-other", "capabilities:\n  - CAP-OTHER-contract\n"),
            "docs/capabilities/governance/CAP-OTHER-contract.md": _doc(
                "CAP-OTHER-contract", "usecases:\n  - UC-other\n"
            ),
            CAP: _doc("CAP-TEST-contract", cap_header),
        },
    )
    return root / CAP


def test_missing_reverse_link_is_reported_and_fixed(tmp_path: Path) -> None:
    cap = _one_sided(tmp_path)
    violations = check(RULE, tmp_path)
    assert _found(violations) == [
        (CAP, 1, f"CAP-TEST-contract is missing the reverse use case link to UC-test-usecase ({USECASE})")
    ]
    assert violations[0].fixable and "UC-test-usecase" in violations[0].remediation

    dry = RuleContext(workspace_root=tmp_path, fix=True, dry_run=True)
    assert isinstance(RULE, Autofixable)
    assert RULE.fix(dry) == [CAP]
    assert "usecases: []" in cap.read_text() and len(check(RULE, tmp_path)) == 1

    fixed = check(RULE, tmp_path, fix=True)
    assert _found(fixed) == [] and all(v.fixed for v in fixed)
    assert "usecases: [UC-test-usecase]\n" in cap.read_text()
    assert check(RULE, tmp_path) == []
    assert check(RULE, tmp_path, fix=True) == []


def test_missing_reverse_capability_link(tmp_path: Path) -> None:
    files = {
        "docs/capabilities/a/CAP-A-one.md": _doc("CAP-A-one", "usecases: [UC-one, UC-two]\n"),
        "docs/usecases/a/UC-one.md": _doc("UC-one", "capabilities:\n  - CAP-A-zero\n"),
        "docs/usecases/a/UC-two.md": _doc("UC-two"),
        "docs/capabilities/a/CAP-A-zero.md": _doc("CAP-A-zero", "usecases:\n  - UC-one\n"),
    }
    assert [(f, m) for f, _, m in _found(check(RULE, tmp_path, files))] == [
        (
            "docs/usecases/a/UC-one.md",
            "UC-one is missing the reverse capability link to CAP-A-one (docs/capabilities/a/CAP-A-one.md)",
        ),
        (
            "docs/usecases/a/UC-two.md",
            "UC-two is missing the reverse capability link to CAP-A-one (docs/capabilities/a/CAP-A-one.md)",
        ),
    ]
    assert _found(check(RULE, tmp_path, fix=True)) == []
    assert "capabilities:\n  - CAP-A-zero\n  - CAP-A-one\n---" in (tmp_path / "docs/usecases/a/UC-one.md").read_text()
    assert "status: active\ncapabilities:\n  - CAP-A-one\n---" in (tmp_path / "docs/usecases/a/UC-two.md").read_text()


def test_fix_keeps_list_style(tmp_path: Path) -> None:
    cap = "docs/capabilities/a/CAP-A-one.md"
    files = {
        "docs/usecases/a/UC-one.md": _doc("UC-one", "capabilities: [CAP-A-one]\n"),
        "docs/usecases/a/UC-two.md": _doc("UC-two", "capabilities: [CAP-A-one]\n"),
        cap: _doc("CAP-A-one", "usecases:\n- 'UC-zero'  # first\ntitle: x\n"),
        "docs/usecases/a/UC-zero.md": _doc("UC-zero", 'capabilities: ["CAP-A-one"]\n'),
    }
    assert _found(check(RULE, tmp_path, files, fix=True)) == []
    assert "usecases:\n- 'UC-zero'  # first\n- UC-one\n- UC-two\ntitle: x\n" in (tmp_path / cap).read_text()


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
@pytest.mark.parametrize("style", [">-", "|-"])
@pytest.mark.parametrize("following", ["title: 한글 # keep\n", ""])
def test_fix_after_block_scalar_preserves_other_bytes(tmp_path: Path, newline: str, style: str, following: str) -> None:
    header = f"usecases:\n  - {style}\n    UC-zero\n{following}"
    cap = _one_sided(tmp_path, header)
    original = cap.read_bytes().replace(b"\n", newline.encode())
    cap.write_bytes(original)
    assert isinstance(RULE, Autofixable)
    assert RULE.fix(RuleContext(workspace_root=tmp_path, fix=True)) == [CAP]
    expected = original.replace(
        f"    UC-zero{newline}".encode(),
        f"    UC-zero{newline}  - UC-test-usecase{newline}".encode(),
    )
    assert cap.read_bytes() == expected


def test_fix_refuses_alias_changes_to_other_fields(tmp_path: Path) -> None:
    cap = _one_sided(tmp_path, "usecases: &links [UC-zero]\nother: *links\n")
    original = cap.read_bytes()
    assert isinstance(RULE, Autofixable)
    assert RULE.fix(RuleContext(workspace_root=tmp_path, fix=True)) == []
    assert cap.read_bytes() == original


def test_exact_ids_only(tmp_path: Path) -> None:
    files = {
        "docs/usecases/a/UC-one.md": _doc("UC-one", "capabilities: [CAP-A-one]\n"),
        "docs/capabilities/a/CAP-A-one.md": _doc("CAP-A-one", "usecases: [UC-one-extra, docs/usecases/a/UC-one.md]\n"),
    }
    assert len(_found(check(RULE, tmp_path, files))) == 1


def test_ambiguous_ids_are_not_fixed(tmp_path: Path) -> None:
    first = "docs/capabilities/test/CAP-TEST-one.md"
    second = "docs/capabilities/other/CAP-TEST-one.md"
    files = {
        "docs/usecases/test/UC-one.md": "---\nid: UC-one\ncapabilities: [CAP-TEST-one]\n---\n",
        first: "---\nid: CAP-TEST-one\nusecases: []\n---\n",
        second: "---\nid: CAP-TEST-one\nusecases: []\n---\n",
    }
    violations = check(RULE, tmp_path, files, fix=True)
    assert len(_found(violations)) == 2 and not any(v.fixable for v in violations)
    assert "usecases: []" in (tmp_path / first).read_text() and "usecases: []" in (tmp_path / second).read_text()


def test_malformed_field_is_not_fixed(tmp_path: Path) -> None:
    cap = "docs/capabilities/a/CAP-A-one.md"
    files = {
        "docs/usecases/a/UC-one.md": _doc("UC-one", "capabilities: [CAP-A-one]\n"),
        cap: _doc("CAP-A-one", "usecases: UC-zero\n"),
    }
    violations = check(RULE, tmp_path, files, fix=True)
    assert len(_found(violations)) == 1 and not violations[0].fixable
    assert "usecases: UC-zero\n" in (tmp_path / cap).read_text()


def test_targeting(tmp_path: Path) -> None:
    cap = _one_sided(tmp_path)
    assert _found(check(RULE, tmp_path, targets=[CAP])) == [
        (CAP, 1, f"CAP-TEST-contract is missing the reverse use case link to UC-test-usecase ({USECASE})")
    ]
    # Only the use case is targeted: the one-sided link is reported where it is declared, and not fixed there.
    violations = check(RULE, tmp_path, targets=[USECASE], fix=True)
    assert _found(violations) == [
        (USECASE, 5, f"UC-test-usecase links CAP-TEST-contract, but {CAP} does not list UC-test-usecase in usecases")
    ]
    assert f"devkit rules fix {CAP}" in violations[0].remediation and not violations[0].fixable
    assert "usecases: []" in cap.read_text()
    assert check(RULE, tmp_path, targets=["docs/capabilities/governance/CAP-OTHER-contract.md"]) == []


def test_materials_are_skipped(tmp_path: Path) -> None:
    files = {
        "docs/usecases/materials/UC-m.md": _doc("UC-m", "capabilities: [CAP-A-one]\n"),
        "docs/capabilities/a/CAP-A-one.md": _doc("CAP-A-one"),
    }
    assert check(RULE, tmp_path, files) == []


def test_namespace_documents_link_like_global_ones(tmp_path: Path) -> None:
    usecase = "docs/packages/api/usecases/auth/UC-api-login.md"
    cap = "docs/packages/api/capabilities/auth/CAP-API-login.md"
    files = {
        usecase: _doc("UC-api-login", "capabilities:\n  - CAP-API-login\n  - CAP-TEST-contract\n"),
        cap: _doc("CAP-API-login", "usecases: []\n"),
        CAP: _doc("CAP-TEST-contract", "usecases: [UC-api-login]\n"),
    }
    assert check(RULE, tmp_path, files) == []

    assert _found(check(RULE, tmp_path, {".devkit/config.toml": _namespaces("api")})) == [
        (cap, 1, f"CAP-API-login is missing the reverse use case link to UC-api-login ({usecase})")
    ]
    assert _found(check(RULE, tmp_path, fix=True)) == []
    assert "usecases: [UC-api-login]\n" in (tmp_path / cap).read_text()


def test_links_written_with_an_alias_count_without_a_duplicate_fix(tmp_path: Path) -> None:
    other = "docs/usecases/governance/UC-other.md"
    files = {
        USECASE: _doc("UC-test-usecase", "aliases: [UC-old-usecase]\ncapabilities:\n  - CAP-TEST-contract\n"),
        CAP: _doc("CAP-TEST-contract", "aliases: [CAP-TEST-old]\nusecases:\n  - UC-old-usecase\n"),
        other: _doc("UC-other", "capabilities: [CAP-TEST-old]\n"),
    }
    found = _found(check(RULE, tmp_path, files))
    assert found == [(CAP, 1, f"CAP-TEST-contract is missing the reverse use case link to UC-other ({other})")]
    check(RULE, tmp_path, fix=True)
    text = (tmp_path / CAP).read_text()
    assert text.count("UC-test-usecase") == 0 and "  - UC-old-usecase\n  - UC-other\n" in text
