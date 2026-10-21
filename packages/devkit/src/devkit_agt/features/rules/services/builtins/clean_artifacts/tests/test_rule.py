"""``RULE-clean-artifacts``: binaries, databases and big logs in explicit targets, never in whole-workspace runs."""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules.services.builtins.clean_artifacts import CleanArtifactsRule
from devkit_agt.features.rules.services.testing import check


def _flagged(root: Path, files: dict[str, bytes]) -> list[str]:
    return sorted(v.file for v in check(CleanArtifactsRule(), root, files, targets=list(files)))


def test_detects_binaries_databases_and_big_logs(tmp_path: Path) -> None:
    files = {
        "bin/tool": b"\x7fELF" + b"\0" * 8,
        "bin/tool.exe": b"MZ" + b"\0" * 8,
        "bin/mac": b"\xcf\xfa\xed\xfe" + b"\0" * 8,
        "data/app.sqlite3": b"x",
        "logs/big.log": b"x" * (1024 * 1024 + 1),
        "logs/small.log": b"x",
        "src/ok.py": b"print('hi')\n",
    }
    assert _flagged(tmp_path, files) == ["bin/mac", "bin/tool", "bin/tool.exe", "data/app.sqlite3", "logs/big.log"]


def test_boundaries(tmp_path: Path) -> None:
    files = {
        "logs/exact.log": b"x" * (1024 * 1024),
        "bin/mac32": b"\xce\xfa\xed\xfe",
        "bin/universal": b"\xca\xfe\xba\xbe",
        "data/APP.DB": b"x",
    }
    assert _flagged(tmp_path, files) == ["bin/mac32", "bin/universal", "data/APP.DB"]


def test_whole_workspace_runs_report_nothing(tmp_path: Path) -> None:
    assert check(CleanArtifactsRule(), tmp_path, {"app.db": b"sqlite"}) == []
