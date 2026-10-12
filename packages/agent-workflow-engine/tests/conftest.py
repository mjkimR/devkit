from __future__ import annotations

from pathlib import Path

import pytest

WORKFLOW = """---
id: direct-delivery
title: "Direct delivery"
status: active
schema_version: 1
checks:
  - { name: ci-passed, class: runner, description: "repository CI is green" }
stages:
  - id: intent
    name: Intent
    human_gate: direction
    entry: []
    exit: [anchor-exists]
    artifacts: [task.md]
    skills: [wf-intent]
    role: developer
    isolation: none
    returns: []
  - id: build-verify
    name: Build and verify
    human_gate: false
    entry: [tasks-exists]
    exit: [tasks-all-checked, lint-clean]
    artifacts: [tasks.md]
    skills: [wf-build]
    role: developer
    isolation: none
    returns:
      - { to: intent, when: new requirements }
  - id: review
    name: Review loop
    human_gate: false
    entry: [tasks-all-checked]
    exit: [envelope-review-passed]
    artifacts: [envelopes/review-NN.yaml]
    skills: [wf-review, wf-delegate]
    role: reviewer
    isolation: preferred
    returns:
      - { to: build-verify, when: defects }
  - id: integrate
    name: Integrate
    human_gate: integration
    entry: [envelope-review-passed]
    exit: [anchor-status-completed, ci-passed]
    artifacts: []
    skills: [wf-integrate]
    role: developer
    isolation: none
    returns: []
---

## Gate rules

Prose, not parsed.
"""


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A workspace with one valid definition under the default definitions_dir."""
    defs = tmp_path / ".devkit" / "workflows"
    defs.mkdir(parents=True)
    (defs / "direct-delivery.md").write_text(WORKFLOW, encoding="utf-8")
    return tmp_path


def write_config(root: Path, body: str) -> Path:
    path = root / ".devkit" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def write_unit(root: Path, rel: str, anchor: str = "task.md", status: str = "planned", extra: str = "") -> Path:
    unit = root / rel
    unit.mkdir(parents=True, exist_ok=True)
    (unit / anchor).write_text(f"---\nid: x\nstatus: {status}\n{extra}---\n# x\n", encoding="utf-8")
    return unit
