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


def _modules(root: Path, managed: ManagedRules) -> list[dict[str, str]]:
    """Each package's modules as ``{dotted: path relative to root}``."""
    return [{name: path.relative_to(root).as_posix() for name, path in p.modules.items()} for p in managed.packages]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_resolve_managed_rules_reads_rule_assets_only(tmp_path: Path) -> None:
    _write(tmp_path / ".devkit/managed/team/rules/x/a.py", RULE.format(n="a"))
    _write(tmp_path / ".devkit/managed/team/rules/x/README.md", "doc\n")
    _write(tmp_path / ".devkit/overrides/team/rules/x/b.py", RULE.format(n="b"))
    _receipt(
        tmp_path,
        [
            {
                "bundle": "team",
                "id": "rules",
                "kind": "rule",
                "paths": [
                    ".devkit/managed/team/rules/x/README.md",
                    ".devkit/managed/team/rules/x/a.py",
                    ".devkit/overrides/team/rules/x/b.py",
                ],
            },
            {"bundle": "team", "id": "flow", "kind": "workflow", "paths": [".devkit/managed/team/flow.py"]},
        ],
        {".devkit/managed/team/rules/x/a.py": _sha(RULE.format(n="a"))},
    )
    managed = resolve_managed_rules(tmp_path)
    assert managed.errors == ()
    assert _modules(tmp_path, managed) == [
        {"a": ".devkit/managed/team/rules/x/a.py", "b": ".devkit/overrides/team/rules/x/b.py"}
    ]
    registry = RuleRegistry()
    discovered = registry.discover_from_packages(managed.packages)
    assert sorted(r.id for r in discovered) == ["RULE-managed-a", "RULE-managed-b"]


def test_receipt_listed_rule_modules_load_whatever_their_name_and_import_each_other(tmp_path: Path) -> None:
    helper = ".devkit/managed/team/rules/x/_private.py"
    rule = ".devkit/managed/team/rules/x/rule.py"
    test = ".devkit/managed/team/rules/x/tests/test_rule.py"
    sources = {
        helper: "LIMIT = 3\n",
        rule: RULE.format(n="entry").replace(
            "from devkit.rules import", "from ._private import LIMIT\nfrom devkit.rules import"
        ),
        test: "raise RuntimeError('tests are never imported')\n",
    }
    for rel, text in sources.items():
        _write(tmp_path / rel, text)
    _receipt(
        tmp_path,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": sorted(sources)}],
        {rel: _sha(text) for rel, text in sources.items()},
    )
    managed = resolve_managed_rules(tmp_path)
    assert managed.errors == ()
    assert _modules(tmp_path, managed) == [{"_private": helper, "rule": rule}]  # no name filter, tests excluded
    registry = RuleRegistry()
    assert [r.id for r in registry.discover_from_packages(managed.packages)] == ["RULE-managed-entry"]
    assert registry.errors == []


def test_resolve_managed_rules_reports_missing_file(tmp_path: Path) -> None:
    _receipt(tmp_path, [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/r.py"]}])
    managed = resolve_managed_rules(tmp_path)
    assert managed.packages == ()
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
    assert managed.packages == ()
    assert len(managed.errors) == 1
    assert str(managed.errors[0]).startswith("invalid installation receipt: .devkit/installation.json")
    assert problem in str(managed.errors[0]) and "devkit sync" not in str(managed.errors[0])
    assert managed.errors[0].target_files == (".devkit/installation.json",)


def test_resolve_managed_rules_rejects_unsafe_receipt_paths(tmp_path: Path) -> None:
    _receipt(tmp_path, [{"bundle": "team", "id": "rules", "kind": "rule", "paths": ["../outside/rule.py"]}])
    managed = resolve_managed_rules(tmp_path)
    assert managed.packages == () and "unsafe path" in str(managed.errors[0])


def test_resolve_managed_rules_falls_back_to_source_root_by_hash(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot"
    source = tmp_path / "worktree"
    # The snapshot carries the receipt and the tracked override; the managed copies are ignored by Git.
    _write(snapshot / ".devkit/overrides/team/rules/b.py", RULE.format(n="b"))
    _write(source / ".devkit/managed/team/rules/a.py", RULE.format(n="a"))
    _write(source / ".devkit/managed/team/rules/drift.py", RULE.format(n="drift"))
    _write(source / ".devkit/managed/team/rules/unhashed.py", RULE.format(n="unhashed"))
    _write(source / ".devkit/managed/team/split/a.py", RULE.format(n="split"))
    paths = [
        ".devkit/managed/team/rules/a.py",
        ".devkit/overrides/team/rules/b.py",
        ".devkit/managed/team/rules/drift.py",
        ".devkit/managed/team/rules/gone.py",
        ".devkit/managed/team/rules/unhashed.py",
    ]
    split = [".devkit/managed/team/split/a.py", ".devkit/overrides/team/split/b.py"]
    _write(snapshot / split[1], "from .a import ManagedRule\n")
    _receipt(
        snapshot,
        [
            {"bundle": "team", "id": "rules", "kind": "rule", "paths": paths},
            {"bundle": "team", "id": "split", "kind": "rule", "paths": split},
        ],
        files={
            ".devkit/managed/team/rules/a.py": _sha(RULE.format(n="a")),
            ".devkit/overrides/team/rules/b.py": _sha(RULE.format(n="b")),
            ".devkit/managed/team/rules/drift.py": _sha("something else"),
            ".devkit/managed/team/rules/gone.py": _sha(RULE.format(n="gone")),
            split[0]: _sha(RULE.format(n="split")),
        },
    )
    managed = resolve_managed_rules(snapshot, source_root=source)
    # A package with an unusable file is not loaded; a package split over the snapshot and the working tree is.
    (package,) = managed.packages
    assert dict(package.modules) == {"a": source / split[0], "b": snapshot / split[1]}
    assert [r.id for r in RuleRegistry().discover_from_packages(managed.packages)] == ["RULE-managed-split"]
    assert [str(e) for e in managed.errors] == [
        "synchronized rule .devkit/managed/team/rules/drift.py differs from the hash in the receipt",
        "synchronized rule .devkit/managed/team/rules/gone.py is missing from the working tree",
        "synchronized rule .devkit/managed/team/rules/unhashed.py has no hash in the receipt",
    ]
    assert all(e.fix is not None and "devkit sync" in e.fix for e in managed.errors)


def test_plain_check_verifies_managed_rules_against_the_receipt_hash(tmp_path: Path) -> None:
    managed_rel = ".devkit/managed/team/rules/a/a.py"
    override_rel = ".devkit/overrides/team/rules/b/b.py"
    _write(tmp_path / managed_rel, RULE.format(n="a"))
    _write(tmp_path / override_rel, RULE.format(n="b") + "# a project override, not recorded\n")
    _receipt(
        tmp_path,
        [
            {"bundle": "team", "id": "rules", "kind": "rule", "paths": [managed_rel]},
            {"bundle": "team", "id": "other", "kind": "rule", "paths": [override_rel]},
        ],
        files={managed_rel: _sha(RULE.format(n="a"))},
    )
    assert _modules(tmp_path, resolve_managed_rules(tmp_path)) == [{"a": managed_rel}, {"b": override_rel}]

    (tmp_path / managed_rel).write_text(RULE.format(n="a") + "# edited by hand\n")
    managed = resolve_managed_rules(tmp_path)
    assert _modules(tmp_path, managed) == [{"b": override_rel}]
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
        assert "verified_asset_packages(" in inspect.getsource(module)
