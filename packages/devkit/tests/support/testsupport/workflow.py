"""Workflow engine test helpers: a valid definition, a one-stage workspace, workspace writers and the CLI runner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from click.testing import CliRunner, Result

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


# A one-stage definition: ``SIMPLE.format(id=..., check=...)``.
SIMPLE = "---\nid: {id}\nschema_version: 1\nstages:\n  - id: s\n    exit: [{check}]\n---\n"
# The unit ``new u`` creates under the default layout.
SIMPLE_UNIT = ".devkit/transient/work/u"


def run_cli(*args: str) -> Result:
    """Invoke ``devkit workflow`` with ``args``."""
    from devkit_agt.features.workflow.cli import cli

    return CliRunner().invoke(cli, list(args))


def simple_workspace(root: Path, check: str = "anchor-exists") -> Path:
    """``root`` with the one-stage workflow ``w`` (exit ``check``) as ``[workflow].default``."""
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True, exist_ok=True)
    (defs / "w.md").write_text(SIMPLE.format(id="w", check=check))
    write_config(root, '[workflow]\ndefault = "w"\n')
    return root


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


def write_receipt(root: Path, assets: list[dict[str, Any]], *, hashed: tuple[str, ...] = ()) -> Path:
    """Write a valid installation receipt with ``assets`` (each needs ``kind`` and ``id``).

    ``paths`` defaults to the asset's ``entrypoints``; ``bundle`` defaults to ``team``.
    ``hashed`` paths get a ``files`` record with the SHA-256 of their current content.
    """
    records = []
    for asset in assets:
        record = {"bundle": asset.get("bundle", "team"), "id": asset["id"], "kind": asset["kind"]}
        record["paths"] = list(asset.get("paths", asset.get("entrypoints", [])))
        if "entrypoints" in asset:
            record["entrypoints"] = list(asset["entrypoints"])
        records.append(record)
    files = {rel: {"sha256": hashlib.sha256((root / rel).read_bytes()).hexdigest(), "mode": 0o644} for rel in hashed}
    data = {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": records, "files": files}
    path = root / ".devkit" / "installation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_record(unit: Path, name: str, **data: Any) -> Path:
    """Write ``decisions/<name>`` with the given keys as a host would (``at`` defaults to a fixed timestamp)."""
    data.setdefault("at", "2026-10-12T09:30:00Z")
    path = unit / "decisions" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path
