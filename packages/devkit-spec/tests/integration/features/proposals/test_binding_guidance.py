"""The fix of an unbound notice names exact commands, never a workflow placeholder."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from devkit_spec.features.proposals.usecases import binding


def test_several_workflows_give_one_exact_bind_command_each(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class _Workspace:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def definitions(self) -> list[SimpleNamespace]:
            return [SimpleNamespace(id=name) for name in ("sdd-spec-feature", "sdd-spec-bugfix", "other")]

    monkeypatch.setattr(binding, "Workspace", _Workspace)
    fix, details = binding.unbound_guidance(tmp_path, "specs/2026-10/20261027-x", "sdd-spec-feature")
    assert "<" not in fix and "[DETAIL]" in fix
    assert details == (
        "uv run devkit workflow bind --unit specs/2026-10/20261027-x --workflow other",
        "uv run devkit workflow bind --unit specs/2026-10/20261027-x --workflow sdd-spec-bugfix",
    )
