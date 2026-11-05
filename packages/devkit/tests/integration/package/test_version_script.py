"""Release command boundaries preserve diagnostics and reject unprepared releases."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def test_release_rejects_wrong_tag_before_building():
    result = subprocess.run(["bash", "scripts/release.sh", "v99.0.0"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 2
    assert "RELEASE_TAG_MISMATCH" in result.stderr
    assert "does not match VERSION" in result.stderr
    assert result.stdout == ""


def test_version_check_requires_completed_baseline():
    result = subprocess.run(
        ["uv", "run", "python", "scripts/version.py", "--check"], cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "RELEASE_BASELINE_REQUIRED" in result.stderr
    assert "--baseline" in result.stderr
    assert result.stdout == ""


def test_invalid_cli_options_never_reach_release_effects(tmp_path, monkeypatch, capsys):
    import sys
    from unittest.mock import Mock

    sys.path.insert(0, str(ROOT))
    from scripts.releases import cli

    effects = {
        name: Mock(side_effect=AssertionError("unexpected effect"))
        for name in ("bootstrap", "publish", "release", "prepare")
    }
    for name, effect in effects.items():
        monkeypatch.setattr(cli, name, effect)
    for args in (
        ["publish", "v0.1.7", "--check"],
        ["build", "v0.1.7", "--check"],
        ["--bootstrap", "v0.1.6", "--check", "--output", str(tmp_path / "baseline.json")],
        ["publish", "v0.1.7", "--bootstrap", "v0.1.6"],
        ["--output", str(tmp_path / "baseline.json")],
    ):
        assert cli.main(args, root=tmp_path) == 2
        captured = capsys.readouterr()
        assert captured.out == "" and "RELEASE_OPTIONS_INVALID" in captured.err
    for args in (["--unknown-option"], ["--baseline"], ["bogus-operation"]):
        assert cli.main(args, root=tmp_path) == 2
        captured = capsys.readouterr()
        assert captured.out == "" and "ARGUMENT_INVALID" in captured.err and "Traceback" not in captured.err
    for effect in effects.values():
        effect.assert_not_called()
    assert not (tmp_path / "baseline.json").exists()


def test_just_release_build_passes_tag_once():
    result = subprocess.run(
        ["just", "release-build", "v99.0.0", "--baseline", "fixture.json"], cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "RELEASE_TAG_MISMATCH" in result.stderr
    assert "ARGUMENT_INVALID" not in result.stderr
    assert result.stdout == ""
