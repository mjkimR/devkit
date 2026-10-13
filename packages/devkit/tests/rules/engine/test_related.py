"""A rule's ``related`` instructions and playbooks, resolved through the installation receipt."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from devkit.rules import RelatedAsset, resolve_related
from devkit.rules.engine.errors import RuleDefinitionError
from devkit.rules.rules import BaseRule


class _Rule(BaseRule):
    def __init__(self, *related: str) -> None:
        super().__init__(id="RULE-x", name="x", description="x", related=related)

    def check(self, ctx):  # type: ignore[no-untyped-def]
        return []


def _devkit(*args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("DEVKIT_")}
    return subprocess.run(
        [sys.executable, "-m", "devkit", *args], capture_output=True, text=True, encoding="utf-8", env=env, check=False
    )


def test_malformed_references_are_definition_errors() -> None:
    for ref in ("skill-authoring", "Authoring:x", "a:b:c", "a:"):
        with pytest.raises(RuleDefinitionError):
            _Rule(ref)


def test_unresolved_references_are_notices(tmp_path: Path) -> None:
    related, notices = resolve_related(tmp_path, _Rule("authoring:skill-authoring"))
    assert related == [RelatedAsset("authoring:skill-authoring", None, None)]
    assert [n.code for n in notices] == ["RULES_RELATED_UNRESOLVED"]
    assert notices[0].fix == "devkit add authoring"
    assert resolve_related(tmp_path, _Rule()) == ([], [])


def test_explain_resolves_related_playbooks(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert _devkit("add", "authoring", "-w", str(tmp_path)).returncode == 0
    result = _devkit("rules", "explain", "RULE-skill-document-size", "-w", str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert (
        "[RELATED: authoring:skill-authoring kind=playbook path=.devkit/managed/authoring/playbooks/skill-authoring/SKILL.md]"
        in result.stdout
    )
    payload = json.loads(
        _devkit("rules", "explain", "RULE-skill-document-size", "-w", str(tmp_path), "--format", "json").stdout
    )
    assert payload["rule"]["related"] == [
        {
            "ref": "authoring:skill-authoring",
            "kind": "playbook",
            "path": ".devkit/managed/authoring/playbooks/skill-authoring/SKILL.md",
        }
    ]
