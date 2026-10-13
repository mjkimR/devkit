from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from devkit.rules import ManagedRules, RuleRegistry, resolve_managed_rules
from testsupport.rules import write_receipt

RULE = """from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


class ManagedRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-managed-{n}", name="managed", description="from a bundle")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []
"""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _receipt(root: Path, assets: list[dict[str, object]], files: dict[str, str] | None = None) -> None:
    write_receipt(root, assets, files)


def _rel(root: Path, paths: tuple[Path, ...]) -> list[str]:
    return [p.relative_to(root).as_posix() for p in paths]


def test_resolve_managed_rules_reads_rule_assets_only(tmp_path: Path) -> None:
    (tmp_path / ".devkit/managed/team/rules").mkdir(parents=True)
    (tmp_path / ".devkit/managed/team/rules/a.py").write_text(RULE.format(n="a"))
    (tmp_path / ".devkit/managed/team/rules/README.md").write_text("doc\n")
    (tmp_path / ".devkit/overrides/team/rules").mkdir(parents=True)
    (tmp_path / ".devkit/overrides/team/rules/b.py").write_text(RULE.format(n="b"))
    _receipt(
        tmp_path,
        [
            {
                "bundle": "team",
                "id": "rules",
                "kind": "rule",
                "paths": [
                    ".devkit/managed/team/rules/README.md",
                    ".devkit/managed/team/rules/a.py",
                    ".devkit/overrides/team/rules/b.py",
                ],
            },
            {"bundle": "team", "id": "flow", "kind": "workflow", "paths": [".devkit/managed/team/flow.py"]},
        ],
        {".devkit/managed/team/rules/a.py": _sha(RULE.format(n="a"))},
    )
    managed = resolve_managed_rules(tmp_path)
    assert managed.errors == ()
    assert _rel(tmp_path, managed.paths) == [".devkit/managed/team/rules/a.py", ".devkit/overrides/team/rules/b.py"]
    registry = RuleRegistry()
    discovered = registry.discover_from_files(managed.paths)
    assert sorted(r.id for r in discovered) == ["RULE-managed-a", "RULE-managed-b"]


def test_receipt_listed_rule_files_load_whatever_their_name(tmp_path: Path) -> None:
    rel = ".devkit/managed/team/rules/_private.py"
    (tmp_path / rel).parent.mkdir(parents=True)
    (tmp_path / rel).write_text(RULE.format(n="private"))
    entry = ".devkit/managed/team/rules/entry.py"
    (tmp_path / entry).write_text(RULE.format(n="entry"))
    _receipt(
        tmp_path,
        [{"bundle": "team", "id": "rules", "kind": "rule", "entrypoints": [entry], "paths": [rel, entry]}],
        {rel: _sha(RULE.format(n="private")), entry: _sha(RULE.format(n="entry"))},
    )
    managed = resolve_managed_rules(tmp_path)
    assert managed.errors == ()
    assert _rel(tmp_path, managed.paths) == [entry, rel]  # entrypoints first, no duplicates, no name filter
    discovered = RuleRegistry().discover_from_files(managed.paths)
    assert sorted(r.id for r in discovered) == ["RULE-managed-entry", "RULE-managed-private"]


def test_resolve_managed_rules_reports_missing_file(tmp_path: Path) -> None:
    _receipt(tmp_path, [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/r.py"]}])
    managed = resolve_managed_rules(tmp_path)
    assert managed.paths == ()
    assert len(managed.errors) == 1
    assert "synchronized rule .devkit/managed/team/r.py is missing" in str(managed.errors[0])
    assert "devkit sync" not in str(managed.errors[0])  # remediation lives in fix, not in the message
    assert managed.errors[0].code == "RULES_LOAD_FAILED"
    assert managed.errors[0].target_files == (".devkit/managed/team/r.py",) and managed.errors[0].fix


def test_resolve_managed_rules_without_receipt_or_rule_assets_is_empty(tmp_path: Path) -> None:
    assert resolve_managed_rules(tmp_path) == ManagedRules()
    _receipt(tmp_path, [])
    assert resolve_managed_rules(tmp_path) == ManagedRules()


@pytest.mark.parametrize(
    ("content", "problem"),
    [
        ("{not json", "invalid JSON"),
        (json.dumps({"schema": 1, "assets": []}), "missing keys"),
        ('{"schema": 1, "schema": 1}', "duplicate JSON key"),
    ],
)
def test_resolve_managed_rules_reports_a_malformed_receipt(tmp_path: Path, content: str, problem: str) -> None:
    # A present but unusable receipt is an error, never "no synchronized rules": that would be a false pass.
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/installation.json").write_text(content)
    managed = resolve_managed_rules(tmp_path)
    assert managed.paths == ()
    assert len(managed.errors) == 1
    assert str(managed.errors[0]).startswith("invalid installation receipt: .devkit/installation.json")
    assert problem in str(managed.errors[0]) and "devkit sync" not in str(managed.errors[0])
    assert managed.errors[0].target_files == (".devkit/installation.json",)


def test_resolve_managed_rules_rejects_unsafe_receipt_paths(tmp_path: Path) -> None:
    _receipt(tmp_path, [{"bundle": "team", "id": "rules", "kind": "rule", "paths": ["../outside/rule.py"]}])
    managed = resolve_managed_rules(tmp_path)
    assert managed.paths == () and "unsafe path" in str(managed.errors[0])


def test_resolve_managed_rules_falls_back_to_source_root_by_hash(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot"
    source = tmp_path / "worktree"
    # The snapshot carries the receipt and the tracked override; the managed copies are ignored by Git.
    (snapshot / ".devkit/overrides/team/rules").mkdir(parents=True)
    (snapshot / ".devkit/overrides/team/rules/b.py").write_text(RULE.format(n="b"))
    (source / ".devkit/managed/team/rules").mkdir(parents=True)
    (source / ".devkit/managed/team/rules/a.py").write_text(RULE.format(n="a"))
    (source / ".devkit/managed/team/rules/drift.py").write_text(RULE.format(n="drift"))
    (source / ".devkit/managed/team/rules/unhashed.py").write_text(RULE.format(n="unhashed"))
    paths = [
        ".devkit/managed/team/rules/a.py",
        ".devkit/overrides/team/rules/b.py",
        ".devkit/managed/team/rules/drift.py",
        ".devkit/managed/team/rules/gone.py",
        ".devkit/managed/team/rules/unhashed.py",
    ]
    _receipt(
        snapshot,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": paths}],
        files={
            ".devkit/managed/team/rules/a.py": _sha(RULE.format(n="a")),
            ".devkit/overrides/team/rules/b.py": _sha(RULE.format(n="b")),
            ".devkit/managed/team/rules/drift.py": _sha("something else"),
            ".devkit/managed/team/rules/gone.py": _sha(RULE.format(n="gone")),
        },
    )
    managed = resolve_managed_rules(snapshot, source_root=source)
    assert managed.paths == (source / ".devkit/managed/team/rules/a.py", snapshot / ".devkit/overrides/team/rules/b.py")
    assert [str(e) for e in managed.errors] == [
        "synchronized rule .devkit/managed/team/rules/drift.py differs from the hash in the receipt",
        "synchronized rule .devkit/managed/team/rules/gone.py is missing from the working tree",
        "synchronized rule .devkit/managed/team/rules/unhashed.py has no hash in the receipt",
    ]
    assert all(e.fix is not None and "devkit sync" in e.fix for e in managed.errors)


def test_plain_check_verifies_managed_rules_against_the_receipt_hash(tmp_path: Path) -> None:
    managed_rel = ".devkit/managed/team/rules/a.py"
    override_rel = ".devkit/overrides/team/rules/b.py"
    (tmp_path / ".devkit/managed/team/rules").mkdir(parents=True)
    (tmp_path / managed_rel).write_text(RULE.format(n="a"))
    (tmp_path / ".devkit/overrides/team/rules").mkdir(parents=True)
    (tmp_path / override_rel).write_text(RULE.format(n="b") + "# a project override, not recorded\n")
    _receipt(
        tmp_path,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [managed_rel, override_rel]}],
        files={managed_rel: _sha(RULE.format(n="a"))},
    )
    assert resolve_managed_rules(tmp_path) == ManagedRules((tmp_path / managed_rel, tmp_path / override_rel), ())

    (tmp_path / managed_rel).write_text(RULE.format(n="a") + "# edited by hand\n")
    managed = resolve_managed_rules(tmp_path)
    assert managed.paths == (tmp_path / override_rel,)
    [error] = managed.errors
    assert error.code == "RULES_LOAD_FAILED" and error.target_files == (managed_rel,)
    assert str(error).startswith(f"synchronized rule {managed_rel} differs from the hash in the receipt")
    assert error.fix is not None and "devkit sync" in error.fix and "devkit override create team:rules" in error.fix


def test_plain_and_snapshot_runs_share_the_check_with_the_gate_registry() -> None:
    import inspect

    from devkit.gate.engine import registry
    from devkit.rules.engine import discovery
    from devkit.workflow.project import plugins

    for module in (discovery, registry, plugins):
        assert "verified_asset_files(" in inspect.getsource(module)
