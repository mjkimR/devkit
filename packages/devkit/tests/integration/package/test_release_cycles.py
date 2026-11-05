"""Release-cycle baseline provenance and authored-metadata preservation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from devkit.advisory import AdvisoryError

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from packages.devkit.tests.integration.package.test_selective_releases import change_policy, finish, run
from packages.devkit.tests.integration.package.test_selective_releases import repo as _repo_fixture
from scripts.releases import identity, prepare
from scripts.releases.release import release


@pytest.fixture
def release_repo(tmp_path):
    wrapped = getattr(_repo_fixture, "__wrapped__", None)
    assert callable(wrapped)
    return wrapped(tmp_path)


def test_older_baseline_refuses_before_overwriting_current_versions(release_repo):
    root, baseline, _ = release_repo
    (root / "VERSION").write_text("0.1.2\n")
    paths = identity.workspace(root)
    for path in paths.values():
        path.write_text(
            path.read_text().replace('version = "0.1.0"', 'version = "0.1.1"').replace("==0.1.0", "==0.1.1")
        )
    current, _ = prepare.describe(root, paths, {})
    identity.consistent(current)
    before = {path: path.read_bytes() for path in paths.values()}
    with pytest.raises(AdvisoryError, match=r"baseline.*version"):
        prepare.prepare(root, baseline)
    assert all(path.read_bytes() == raw for path, raw in before.items())
    assert not (root / "scripts/releases/pending.json").exists()


def test_completed_release_plan_rolls_forward_without_unwinding_published_versions(release_repo, monkeypatch):
    root, baseline, _ = release_repo
    change_policy(root)
    first = finish(root, baseline, monkeypatch)
    run(root, "git", "init", "-q")
    run(root, "git", "add", ".")
    run(
        root,
        "git",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-qm",
        "prepared release",
    )
    run(root, "git", "tag", "v0.1.1")
    actual = subprocess.run

    def invoke(args, **kwargs):
        if args == ["uv", "lock", "--check"] or "scripts/handbook.py" in args:
            return subprocess.CompletedProcess(args, 0)
        return actual(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", invoke)
    completed = release(root, "v0.1.1", baseline, "fixture/repo")
    (root / "VERSION").write_text("0.1.2\n")
    for field, value, message in [
        ("baseline_digest", "0" * 64, "prior plan origin"),
        ("source_sha", "b" * 40, "source does not prove"),
    ]:
        invalid = root / "dist" / (field + ".json")
        identity.save(invalid, {**completed, field: value})
        with pytest.raises(AdvisoryError, match=message):
            prepare.prepare(root, invalid)
    next_plan = prepare.prepare(root, root / "dist/release/release-inventory.json")
    assert next_plan["release"] == "0.1.2"
    assert next_plan["baseline_release"] == completed["release"]
    assert next_plan["edits"] == []
    assert all(e["disposition"] == "reused" for e in next_plan["packages"].values())
    assert {n: e["version"] for n, e in next_plan["packages"].items()} == {
        n: e["version"] for n, e in first["packages"].items()
    }


@pytest.mark.parametrize("edit_kind", ["comment-tool", "dependency"])
def test_builder_time_authored_metadata_edit_is_preserved(release_repo, monkeypatch, edit_kind):
    root, baseline, _ = release_repo
    path = root / "packages/devkit-advisory/pyproject.toml"
    marker = '# Authored during comparison; retain this comment.\n[tool.consumer]\nchoice = "retain"\n'
    authored = (
        path.read_text() + "\n" + marker
        if edit_kind == "comment-tool"
        else path.read_text().replace("dependencies = []", 'dependencies = ["outside-helper>=1"]')
    )
    calls = 0

    def builder(*args):
        nonlocal calls
        result = prepare.build(*args)
        calls += 1
        if calls == 2:
            path.write_text(authored)
        return result

    actual = subprocess.run

    def invoke(args, **kwargs):
        if args in (["uv", "lock"], ["uv", "run", "--no-active", "devkit", "sync"]):
            return subprocess.CompletedProcess(args, 0)
        return actual(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", invoke)
    with pytest.raises(AdvisoryError, match="changed during preparation"):
        try:
            prepare.prepare(root, baseline, builder=builder)
        finally:
            assert path.read_text() == authored
    assert not (root / "scripts/releases/pending.json").exists()


def test_unpublished_mismatched_plan_still_refuses(release_repo, monkeypatch):
    root, baseline, _ = release_repo
    change_policy(root)
    finish(root, baseline, monkeypatch)
    plan_path = root / "scripts/releases/pending.json"
    previous = plan_path.read_bytes()
    (root / "VERSION").write_text("0.1.2\n")
    with pytest.raises(AdvisoryError, match="unpublished plan"):
        prepare.prepare(root, baseline)
    assert plan_path.read_bytes() == previous


def test_new_workspace_package_is_allowed_with_consistent_existing_versions(release_repo):
    root, baseline, _ = release_repo
    path = root / "packages/new-content"
    (path / "src/new_content").mkdir(parents=True)
    (path / "src/new_content/__init__.py").write_text('VALUE = "new"\n')
    (path / "pyproject.toml").write_text(
        '[project]\nname = "new-content"\nversion = "0.0.0"\nrequires-python = ">=3.12"\n'
        '[build-system]\nrequires = ["hatchling==1.27.0"]\nbuild-backend = "hatchling.build"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["src/new_content"]\n'
    )
    plan, _, _ = prepare.compute(root, baseline)
    assert plan["packages"]["new-content"]["version"] == "0.1.1"
    assert plan["packages"]["new-content"]["disposition"] == "changed"
    assert all(e["disposition"] == "reused" for n, e in plan["packages"].items() if n != "new-content")
