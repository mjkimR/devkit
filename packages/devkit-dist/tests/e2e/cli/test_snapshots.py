"""Installed runtime/wrapper consumers exercise private-origin-free source adoption and refresh."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from zipfile import ZipFile

from click.testing import CliRunner
from distsupport.distribution import cli
from distsupport.snapshots import content_source

ROOT = Path(__file__).resolve().parents[5]


def test_json_snapshot_and_refresh_errors_use_stable_codes(tmp_path: Path) -> None:
    source = content_source(tmp_path / "source")
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    runner = CliRunner()
    created = runner.invoke(
        cli, ["bundle", "snapshot", str(source), "--to", "tools/copy", "--package", "team-copy", "-w", str(consumer)]
    )
    assert created.exit_code == 0, created.output
    data = json.loads(created.stdout)
    assert data["code"] == "BUNDLE_SNAPSHOT_CREATED" and set(data["bundles"]) == {"alpha", "beta"}
    refresh = ["bundle", "refresh", "tools/copy", "--source", str(source), "-w", str(consumer)]
    preview = runner.invoke(cli, refresh)
    assert preview.exit_code == 0, preview.output
    previewed = json.loads(preview.stdout)
    assert previewed["status"] == "preview" and previewed["code"] == "BUNDLE_SNAPSHOT_PREVIEW"
    half = runner.invoke(cli, [*refresh, "--expect", previewed["current_digest"]])
    assert half.exit_code == 2
    half_error = json.loads(half.stdout)["error"]
    assert half_error["code"] == "ARGUMENT_INVALID" and half_error["advisory"]["target_files"] == ["--candidate"]
    stale = runner.invoke(cli, [*refresh, "--expect", "0" * 64, "--candidate", previewed["candidate_digest"]])
    assert stale.exit_code == 2
    assert json.loads(stale.stdout)["error"]["code"] == "BUNDLE_SNAPSHOT_CONFLICT"
    assert runner.invoke(cli, [*refresh, "--check"]).exit_code == 2
    assert "--check" not in runner.invoke(cli, ["bundle", "refresh", "--help"]).output


def test_built_wrapper_fresh_clone_refresh_reinstall_and_rule_execution(tmp_path: Path) -> None:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith(("DEVKIT_", "PYTHONPATH", "VIRTUAL_ENV"))
    }

    def run(*args: str, cwd: Path = tmp_path, code: int = 0) -> str:
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
        assert result.returncode == code, result.stdout + result.stderr
        return result.stdout

    wheels = tmp_path / "wheels"
    for package in ("devkit-advisory", "devkit-cli", "devkit-core", "devkit-dist", "devkit-agt"):
        run("uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels), cwd=ROOT)
    runtime = [path for path in wheels.glob("*.whl") if not path.name.startswith("devkit_agt-")]
    venv = tmp_path / "venv"
    run("uv", "venv", str(venv))
    python = str(venv / "bin/python")
    run("uv", "pip", "install", "--python", python, *map(str, runtime))
    source = content_source(tmp_path / "private-checkout", rule=True)
    adoption = tmp_path / "adoption"
    adoption.mkdir()
    run("git", "init", "-q", str(adoption))
    made = json.loads(
        run(
            python,
            "-m",
            "devkit_dist",
            "bundle",
            "snapshot",
            str(source),
            "--to",
            "tools/team-copy",
            "--package",
            "team-copy",
            "-w",
            str(adoption),
        )
    )
    assert made["code"] == "BUNDLE_SNAPSHOT_CREATED"
    copied = adoption / "tools/team-copy"
    wrapper_wheels = tmp_path / "wrapper-wheels"
    run("uv", "build", str(copied), "--wheel", "--out-dir", str(wrapper_wheels))
    wrapper_wheel = next(wrapper_wheels.glob("*.whl"))
    with ZipFile(wrapper_wheel) as archive:
        assert "team_copy/alpha/bundle/guide.md.jinja" in archive.namelist()
        assert any(name.endswith("notices/LICENSE") for name in archive.namelist())
    run("uv", "pip", "install", "--python", python, str(wrapper_wheel))
    run(
        python,
        "-c",
        "from importlib.metadata import requires, version; assert not requires('team-copy'); assert version('team-copy') == '0.0.0'",
    )
    run("git", "-C", str(adoption), "add", "tools")
    run(
        "git",
        "-C",
        str(adoption),
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-qm",
        "adopt snapshot",
    )
    clone = tmp_path / "consumer"
    run("git", "clone", "-q", str(adoption), str(clone))
    offline = tmp_path / "offline-source"
    source.rename(offline)

    def installed(*args: str, code: int = 0) -> str:
        return run(python, "-m", "devkit_dist", *args, "-w", str(clone), cwd=clone, code=code)

    installed("add", "alpha:core", "beta:core")
    installed("sync", "--locked")
    assert (clone / ".devkit/managed/alpha/guide.md").is_file()
    run(
        python,
        "-c",
        "from importlib.metadata import distributions; assert not {'private-content', 'devkit-agt'} & {d.metadata['Name'] for d in distributions()}",
    )
    assert not source.exists()

    # Switch to the committed editable wrapper using an ordinary consumer project.
    requirements = [f"{path.name.split('-')[0].replace('_', '-')} @ {path.as_uri()}" for path in runtime]
    (clone / "pyproject.toml").write_text(
        '[project]\nname = "snapshot-consumer"\nversion = "0.0.0"\nrequires-python = ">=3.12"\ndependencies = []\n'
        "\n[dependency-groups]\ndev = "
        + json.dumps(["team-copy", *requirements])
        + '\n\n[tool.uv.sources]\nteam-copy = {path = "tools/team-copy", editable = true}\n'
    )
    env["UV_PROJECT_ENVIRONMENT"] = str(venv)
    run("uv", "sync", "--project", str(clone))
    assert "private.invalid" not in (clone / "uv.lock").read_text()
    installed("sync", "--locked")
    unchanged = json.loads(installed("bundle", "refresh", "tools/team-copy", "--source", str(offline)))
    assert unchanged["changes"] == {"added": [], "modified": [], "removed": []}
    installed("override", "create", "alpha:guide")
    override = clone / ".devkit/overrides/alpha/guide.md.jinja"
    assert override.exists()
    override.write_text(override.read_text().replace("alpha body.", "consumer adaptation."))
    installed("sync")

    offline.rename(source)
    metadata = source / "pyproject.toml"
    metadata.write_text(metadata.read_text().replace('beta = "private_content.beta"', 'gamma = "private_content.beta"'))
    beta = source / "src/private_content/beta/bundle/bundle.toml"
    beta.write_text(beta.read_text().replace('name = "beta"', 'name = "gamma"'))
    alpha = source / "src/private_content/alpha/bundle/guide.md.jinja"
    alpha.write_text(alpha.read_text().replace("alpha body.", "upstream changed."))
    preview = json.loads(installed("bundle", "refresh", "tools/team-copy", "--source", str(source)))
    assert preview["removed_selected"] == ["beta"] and preview["packaging_changed"]
    config = clone / ".devkit/config.toml"
    receipt = clone / ".devkit/installation.json"
    before = config.read_bytes(), receipt.read_bytes(), override.read_bytes()
    applied = json.loads(
        installed(
            "bundle",
            "refresh",
            "tools/team-copy",
            "--source",
            str(source),
            "--expect",
            preview["current_digest"],
            "--candidate",
            preview["candidate_digest"],
        )
    )
    assert before == (config.read_bytes(), receipt.read_bytes(), override.read_bytes())
    assert {"code": "SNAPSHOT_REINSTALL_PACKAGE", "command": "uv sync --reinstall-package team-copy"} in applied[
        "actions"
    ]
    run("uv", "sync", "--project", str(clone), "--reinstall-package", "team-copy")
    installed("remove", "beta")
    synced = json.loads(installed("add", "gamma:core", "--format", "json"))
    assert "OVERRIDE_DRIFT" in {item["code"] for item in synced["notices"]}
    assert override.read_bytes() == before[2]
    assert b"consumer adaptation." in (clone / ".devkit/managed/alpha/guide.md").read_bytes()

    # Global provider ambiguity remains an error, even for the subset a consumer selects.
    run("uv", "pip", "install", "--python", python, "--no-deps", "--editable", str(source))
    duplicate = json.loads(installed("list", code=2))
    assert duplicate["error"]["code"] == "BUNDLE_PACKAGE_INVALID"
    run("uv", "pip", "uninstall", "--python", python, "private-content")

    # Harness is installed separately; the wrapper retains its own relative helper and public API imports.
    harness = next(wheels.glob("devkit_agt-*.whl"))
    run("uv", "pip", "install", "--python", python, str(harness))
    installed("add", "alpha:all")
    checked = json.loads(installed("rules", "check", "--format", "json"))
    assert any(
        item["rule_id"] == "RULE-snapshot-example" and item["message"] == "copied" for item in checked["violations"]
    )
