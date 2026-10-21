"""``RULE-proposal-boundaries``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules import Severity, Violation
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)
CONFIG = ".devkit/config.toml"
EXISTING = {
    "packages/a/x.py": "",
    "docs/glossary.md": "# Glossary\n",
    "docs/capabilities/delivery/CAP-DLV-a.md": "---\nid: CAP-DLV-a\n---\n",
    "docs/stories/delivery/US-a.md": "---\nid: US-a\n---\n",
    "docs/packages/api/capabilities/core/CAP-CORE-a.md": "---\nid: CAP-CORE-a\n---\n",
    CONFIG: '[[tool.spec.namespaces]]\nname = "api"\npath = "packages/api"\n',
}


def _proposal(status: str, target_area: str | None, owns: str, extra: str = "") -> str:
    area = "" if target_area is None else f"target_area: {target_area}\n"
    return f"---\nid: PROP-x\ntitle: X\nstatus: {status}\n{area}{extra}boundaries:\n  owns:{owns}\n  excludes: [nowhere/]\n---\n# X\n"


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in violations]


# AC-08
def test_entries_that_resolve_pass(tmp_path: Path) -> None:
    owns = "\n    - packages/a/\n    - capabilities/delivery/\n    - stories/delivery\n    - delivery/\n    - docs/glossary.md\n    - ./packages/a/x.py"
    files = {
        **EXISTING,
        "docs/proposals/PROP-x/proposal.md": _proposal("reviewing", "delivery/", owns),
        "docs/proposals/PROP-y.md": _proposal("draft", "capabilities/delivery/", " []").replace("PROP-x", "PROP-y"),
        "docs/proposals/PROP-z/proposal.md": _proposal(
            "accepted", "core/", "\n    - core/\n    - capabilities/core/", extra="namespace: api\n"
        ).replace("PROP-x", "PROP-z"),
    }
    assert check(RULE, tmp_path, files) == []


# AC-09
def test_missing_placeholder_invalid_and_malformed_entries_are_warnings(tmp_path: Path) -> None:
    owns = "\n    - core/\n    - /abs\n    - src/*\n    - docs/glossary.md/\n    - 42\n    - delivery/"
    anchor = "docs/proposals/PROP-x/proposal.md"
    other = "docs/proposals/PROP-w/proposal.md"
    files = {
        **EXISTING,
        anchor: _proposal("draft", "capabilities/<area>/", owns),
        other: "---\nid: PROP-w\ntitle: W\nstatus: draft\ntarget_area: 7\nboundaries:\n  owns: delivery/\n---\n",
    }
    violations = check(RULE, tmp_path, files)
    assert {v.severity for v in violations} == {Severity.WARNING}
    assert _found(violations) == [
        (other, 5, "target_area must be a path string"),
        (other, 7, "boundaries.owns must be a list of path strings"),
        (anchor, 5, "target_area entry 'capabilities/<area>/' is the template placeholder; name the area"),
        (
            anchor,
            8,
            "boundaries.owns entry 'core/' names no existing directory (repository path, docs-root path or"
            " capability area)",
        ),
        (anchor, 9, "boundaries.owns entry '/abs' is not a literal repository-relative path"),
        (anchor, 10, "boundaries.owns entry 'src/*' is not a literal repository-relative path"),
        (
            anchor,
            11,
            "boundaries.owns entry 'docs/glossary.md/' names no existing directory (repository path, docs-root path"
            " or capability area)",
        ),
        (anchor, 12, "boundaries.owns must contain only path strings"),
    ]


def test_a_missing_file_entry_and_a_non_mapping_boundaries(tmp_path: Path) -> None:
    anchor = "docs/proposals/PROP-x.md"
    files = {
        anchor: "---\nid: PROP-x\ntitle: X\nstatus: reviewing\ntarget_area: docs/missing.md\nboundaries: [a]\n---\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [
        (
            anchor,
            5,
            "target_area entry 'docs/missing.md' names no existing path (repository path, docs-root path or"
            " capability area)",
        ),
        (anchor, 6, "boundaries must be a mapping with owns"),
    ]


def test_an_unregistered_namespace_falls_back_to_the_global_docs_root(tmp_path: Path) -> None:
    anchor = "docs/proposals/PROP-x/proposal.md"
    files = {**EXISTING, anchor: _proposal("draft", None, "\n    - core/", extra="namespace: web\n")}
    assert [line for _, line, _ in _found(check(RULE, tmp_path, files))] == [8]


# AC-10
def test_only_current_targeted_proposals_are_checked(tmp_path: Path) -> None:
    accepted = "docs/proposals/PROP-a/proposal.md"
    files = {
        **EXISTING,
        accepted: _proposal("accepted", None, "\n    - missing/").replace("PROP-x", "PROP-a"),
        "docs/proposals/PROP-r/proposal.md": _proposal("rejected", None, "\n    - missing/").replace(
            "PROP-x", "PROP-r"
        ),
        "docs/proposals/PROP-a/decisions/PADR-a.md": "---\nid: PADR-a\nstatus: draft\ntarget_area: missing/\n---\n",
        "docs/proposals/PROP-a/target-docs.md": "---\nid: PROP-a-target\nstatus: draft\ntarget_area: missing/\n---\n",
    }
    assert [file for file, _, _ in _found(check(RULE, tmp_path, files))] == [accepted]
    targeted = check(RULE, tmp_path, targets=["docs/capabilities/delivery/CAP-DLV-a.md"])
    assert targeted == []
    assert [file for file, _, _ in _found(check(RULE, tmp_path, targets=[accepted]))] == [accepted]
