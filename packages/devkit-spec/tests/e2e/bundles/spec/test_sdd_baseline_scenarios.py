"""Scripted playbook exercises with real CLI/app checks and explicitly simulated user decisions.

There is no baseline readiness engine. These tests follow its coordinator procedure and retain
reports of actual terminal observations; passing assertions alone do not prove an autonomous agent.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

APP = """import json, sys
from pathlib import Path
store = Path(sys.argv[1])
notes = json.loads(store.read_text()) if store.exists() else []
if sys.argv[2] == 'add':
    notes.append(sys.argv[3])
    store.write_text(json.dumps(notes))
print(json.dumps(notes))
"""
CHECK = """import json, subprocess, sys, tempfile, unittest
from pathlib import Path
app = Path(__file__).resolve().parents[1] / 'app.py'
class NotesCheck(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            store = str(Path(folder) / 'notes.json')
            subprocess.run([sys.executable, str(app), store, 'add', 'retained'], check=True, capture_output=True)
            result = subprocess.run([sys.executable, str(app), store, 'list'], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout), ['retained'])
if __name__ == '__main__': unittest.main()
"""
DOC = """---
id: CAP-APP-notes
title: Retained notes
summary: "Stores and lists local notes through a command-line flow, excluding multi-user and network behavior."
area: app
status: active
created_at: 2026-10-28
usecases: []
---

# [CAP-APP-notes] Retained notes

## 1. Summary

The local app appends a supplied note and lists stored notes in insertion order as JSON.

## 2. Scope & Boundary

- In scope: local JSON storage and add/list commands.
- Out of scope: network access and multiple users.

## 3. Business Rules & Policies

The app MUST preserve an added note when it subsequently lists the same local store.

## 4. Interfaces & Data Contracts

Run `python app.py <store> add <text>` or `python app.py <store> list`.

## 5. Verification

Run `python checks/check_notes.py`; exercise add and list against the same store.
"""


class Exercise:
    def __init__(self, root: Path, provider: str = "project") -> None:
        self.root = root
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("DEVKIT_", "PYTHONPATH"))}
        self.observations: list[dict[str, object]] = []
        self.run("git", "init", "-q", "-b", "dev-next-change", str(root), cwd=root.parent)
        self.run("git", "config", "user.name", "Synthetic baseline exercise")
        self.run("git", "config", "user.email", "synthetic@example.invalid")
        (root / ".devkit").mkdir()
        self.configure("incubation", provider)
        (root / "app.py").write_text(APP)
        (root / "checks").mkdir()
        (root / "checks/check_notes.py").write_text(CHECK)
        doc = root / "docs/capabilities/app/CAP-APP-notes.md"
        doc.parent.mkdir(parents=True)
        doc.write_text(DOC)
        (root / ".devkit/incubation.md").write_text(
            "# Current product\nGoal: local notes. Retained choice: JSON file.\n"
            "Run: python app.py <store> add <text>; list. Next: verify baseline.\n"
        )
        self.cli("sync")
        self.cli("add", "incubation")
        self.cli("playbook", "get", "spec/sdd-baseline")
        self.cli("get-context", "incubation")
        self.run("git", "add", "app.py", "checks", "docs", ".devkit/config.toml", ".devkit/incubation.md")
        self.run("git", "commit", "-qm", "retain synthetic note product")
        self.revision = self.run("git", "rev-parse", "HEAD").stdout.strip()
        self.source = self.source_identity()

    def run(self, *args: str, expected: int = 0, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(args, cwd=cwd or self.root, env=self.env, text=True, capture_output=True, check=False)
        self.observations.append(
            {"argv": list(args), "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        )
        assert result.returncode == expected, result.stdout + result.stderr
        return result

    def cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        return self.run(sys.executable, "-m", "devkit_dist", *args, "-w", str(self.root), expected=expected)

    def configure(self, approach: str, provider: str, preset: str = "core") -> None:
        (self.root / ".devkit/config.toml").write_text(
            f'[development]\napproach="{approach}"\n[integration]\nprovider="{provider}"\n[presets]\nspec="{preset}"\n'
        )

    def config(self) -> dict:
        return json.loads(self.cli("config", "show").stdout)["configuration"]

    def source_identity(self) -> str:
        return hashlib.sha256((self.root / "app.py").read_bytes()).hexdigest()

    def verify_product(self) -> None:
        self.run(sys.executable, "checks/check_notes.py")
        store = str(self.root / "observed-notes.json")
        added = self.run(sys.executable, "app.py", store, "add", "retained")
        listed = self.run(sys.executable, "app.py", store, "list")
        assert json.loads(added.stdout) == json.loads(listed.stdout) == ["retained"]
        self.cli("rules", "check")

    def report(self, status: str, detail: str, decision: str = "pending") -> Path:
        path = self.root / "docs/materials/2026-10/20261028-sdd-baseline/report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Synthetic SDD baseline exercise\n\nRevision: {self.revision}\n"
            f"Evidence app SHA256: {self.source}\nCurrent app SHA256: {self.source_identity()}\n"
            "Retained scope: local add/list notes; excludes multi-user/network behavior.\n"
            "Document: docs/capabilities/app/CAP-APP-notes.md; implementation: app.py.\n"
            f"Retained coverage status: {status}. {detail}\n"
            f"Simulated user decision (test data, not real user authority): {decision}\n"
            f"Observed final configuration: {json.dumps(self.config(), sort_keys=True)}\n\n"
            + "\n".join(json.dumps(item, sort_keys=True) for item in self.observations)
        )
        return path


@pytest.mark.parametrize("initial_provider", ["project", "spec"])
def test_ready_product_activates_exact_effects_and_next_change_uses_sdd(tmp_path: Path, initial_provider: str) -> None:
    exercise = Exercise(tmp_path / "consumer", initial_provider)
    assert exercise.config()["development"]["approach"] == "incubation"
    inactive = exercise.cli("spec", "new", "next-change", expected=2)
    assert "SPEC_LIFECYCLE_INACTIVE" in inactive.stderr
    exercise.verify_product()
    exercise.report("verified", "Independent test, actual add/list and document checks passed.")
    assert not (exercise.root / "specs").exists()
    # Simulated decision covers this exact source, retained scope, approach and necessary project-to-spec provider switch.
    decision = f"activate {exercise.source} local notes; approach=sdd; provider=spec (was {initial_provider})"
    assert exercise.source_identity() == exercise.source
    exercise.configure("sdd", "spec")
    exercise.cli("sync")
    assert exercise.config()["development"]["approach"] == "sdd"
    assert exercise.config()["integration"]["provider"] == "spec"
    assert "approach=sdd" in exercise.cli("spec", "policy").stdout
    exercise.cli("sync", "--check")
    exercise.cli(
        "spec",
        "new",
        "next-change",
        "--summary",
        "Defines a subsequent synthetic change after adoption.",
        "--date",
        "2026-10-28",
    )
    next_unit = exercise.root / "specs/2026-10/20261028-next-change"
    assert next_unit.is_dir()
    route = exercise.cli("workflow", "next", "--unit", str(next_unit))
    assert "plan-intent" in route.stdout
    exercise.report("verified", "Activation succeeded; next requested change uses ordinary SDD plan-intent.", decision)


def test_missing_required_usage_evidence_keeps_incubation_despite_format_pass(tmp_path: Path) -> None:
    exercise = Exercise(tmp_path / "consumer")
    exercise.cli("rules", "check")
    report = exercise.report("gap", "Usage was intentionally not executed; format pass alone is insufficient.")
    assert "status: gap" in report.read_text()
    assert exercise.config()["development"]["approach"] == "incubation"
    assert not (exercise.root / "specs").exists()


def test_changed_source_invalidates_observation_until_rechecked(tmp_path: Path) -> None:
    exercise = Exercise(tmp_path / "consumer")
    exercise.verify_product()
    exercise.report("verified", "Initial source was exercised.")
    app = exercise.root / "app.py"
    app.write_text(app.read_text().replace("notes.append(sys.argv[3])", "notes.append(sys.argv[3].upper())"))
    assert exercise.source_identity() != exercise.source
    failed = exercise.run(sys.executable, "checks/check_notes.py", expected=1)
    assert "AssertionError" in failed.stderr
    report = exercise.report(
        "gap", "Relevant source changed; recheck failed the retained behavior, so activation is blocked."
    )
    assert "status: gap" in report.read_text()
    assert exercise.config()["development"]["approach"] == "incubation"


def test_actual_sync_failure_reports_partial_state_and_supported_recovery(tmp_path: Path) -> None:
    exercise = Exercise(tmp_path / "consumer")
    exercise.verify_product()
    # Deliberately invalid selection is labelled test failure injection; no runtime is stubbed.
    exercise.configure("sdd", "spec", preset="missing-synthetic-preset")
    failure = exercise.cli("sync", expected=2)
    assert "missing-synthetic-preset" in failure.stderr
    assert exercise.config()["development"]["approach"] == "sdd"  # no automatic rollback
    report = exercise.report(
        "gap",
        "Actual sync failed after policy edit; partial state is SDD. Restore valid preset, sync, then revalidate.",
        "synthetic activation + failure injection",
    )
    assert "partial state is SDD" in report.read_text()
    exercise.configure("sdd", "spec")
    exercise.cli("sync")
    exercise.cli("sync", "--check")
    exercise.report(
        "verified",
        "Explicit recovery restored core selection and sync consistency; original app evidence unchanged.",
        "synthetic recovery for same effects",
    )
