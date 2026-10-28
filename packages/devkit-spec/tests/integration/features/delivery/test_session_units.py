"""A session task refuses only the spec bundle of its own slug, matched exactly as ``<YYYYMMDD>-<slug>``."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from spec_support.scope import write

from devkit_spec.features.delivery.usecases.integration import _check_session_task

CLAIMS = {"task_kind": "feature", "effort": "low", "review": True, "tests": True, "lint": True}


def _reasons(workspace: Path, branch: str) -> list[str]:
    context = SimpleNamespace(
        finish=SimpleNamespace(branch=branch, source_sha="a" * 40, target_sha="b" * 40),
        task=SimpleNamespace(claims_json=json.dumps(CLAIMS)),
    )
    snapshot = SimpleNamespace(changed=(), deleted=())
    _evidence, reasons = _check_session_task(cast(Any, context), cast(Any, snapshot), workspace)
    return reasons


def test_a_neighbouring_bundle_ending_with_the_slug_is_not_the_session_unit(tmp_path: Path) -> None:
    write(tmp_path, "specs/2026-10/20261001-hook-cleanup/spec.md", "---\nid: SPEC-hook-cleanup\n---\n")
    assert not any("has spec unit" in reason for reason in _reasons(tmp_path, "dev-cleanup"))


def test_the_bundle_of_the_session_slug_is_refused(tmp_path: Path) -> None:
    write(tmp_path, "specs/2026-10/20261002-cleanup/spec.md", "---\nid: SPEC-cleanup\n---\n")
    write(tmp_path, "specs/2026-10/20261001-hook-cleanup/spec.md", "---\nid: SPEC-hook-cleanup\n---\n")
    assert [reason for reason in _reasons(tmp_path, "dev-cleanup") if "has spec unit" in reason] == [
        "branch dev-cleanup has spec unit specs/2026-10/20261002-cleanup;"
        " integrate it as a unit task, not a session task"
    ]


def test_missing_claims_emit_coded_input_recovery(tmp_path: Path) -> None:
    context = SimpleNamespace(
        finish=SimpleNamespace(branch="dev-session", source_sha="a" * 40, target_sha="b" * 40),
        task=SimpleNamespace(claims_json="{}"),
    )
    snapshot = SimpleNamespace(changed=(), deleted=())
    evidence, reasons = _check_session_task(cast(Any, context), cast(Any, snapshot), tmp_path)
    assert reasons
    assert [(item.code, item.value) for item in evidence if item.code == "SESSION_CLAIMS_INVALID"] == [
        ("SESSION_CLAIMS_INVALID", "--claims")
    ]
