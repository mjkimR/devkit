from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agent_rule_engine import RuleRegistry, resolve_managed_rules

RULE = """from agent_rule_engine import RuleContext, Violation
from agent_rule_engine.rules import BaseRule


class ManagedRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-managed-{n}", name="managed", description="from a bundle")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []
"""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _receipt(root: Path, assets: list[dict[str, object]], files: dict[str, str] | None = None) -> None:
    path = root / ".devkit/installation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, object] = {"schema": 1, "assets": assets}
    if files is not None:
        data["files"] = {name: {"sha256": digest, "mode": 420} for name, digest in files.items()}
    path.write_text(json.dumps(data))


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
    )
    managed = resolve_managed_rules(tmp_path)
    assert managed.errors == ()
    assert _rel(tmp_path, managed.paths) == [".devkit/managed/team/rules/a.py", ".devkit/overrides/team/rules/b.py"]
    registry = RuleRegistry()
    discovered = registry.discover_from_files(managed.paths)
    assert sorted(r.id for r in discovered) == ["RULE-managed-a", "RULE-managed-b"]


def test_resolve_managed_rules_reports_missing_file(tmp_path: Path) -> None:
    _receipt(tmp_path, [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/r.py"]}])
    managed = resolve_managed_rules(tmp_path)
    assert managed.paths == ()
    assert len(managed.errors) == 1
    assert "synchronized rule .devkit/managed/team/r.py is missing" in managed.errors[0]
    assert "devkit sync" in managed.errors[0]


def test_resolve_managed_rules_tolerates_missing_or_invalid_receipt(tmp_path: Path) -> None:
    assert resolve_managed_rules(tmp_path).paths == ()
    _receipt(tmp_path, [])
    assert resolve_managed_rules(tmp_path).paths == ()
    (tmp_path / ".devkit/installation.json").write_text("{not json")
    assert resolve_managed_rules(tmp_path) == resolve_managed_rules(tmp_path / "nowhere")


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
    assert [e.split(";")[0] for e in managed.errors] == [
        "synchronized rule .devkit/managed/team/rules/drift.py differs from the hash in the receipt",
        "synchronized rule .devkit/managed/team/rules/gone.py is missing from the working tree",
        "synchronized rule .devkit/managed/team/rules/unhashed.py has no hash in the receipt",
    ]
    assert all("devkit sync" in e for e in managed.errors)
