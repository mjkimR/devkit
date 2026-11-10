"""Selective release contracts against original local wheels and clean consumers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from devkit.advisory import AdvisoryError

from scripts.releases import artifacts, identity, install, prepare
from scripts.releases.cli import main


def run(root: Path, *args: str) -> str:
    result = subprocess.run(args, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "VERSION").write_text("0.1.1\n")
    (root / ".gitignore").write_text("dist/\n.venv/\nuv.lock\n")
    (root / "pyproject.toml").write_text('[tool.uv.workspace]\nmembers = ["packages/*"]\n')
    recipe = root / "scripts/releases"
    recipe.mkdir(parents=True)
    for name in ("recipe.json", "build-constraints.txt"):
        shutil.copyfile(ROOT / "scripts/releases" / name, recipe / name)
    dependencies = {
        "devkit-advisory": [],
        "devkit-core": ["devkit-advisory==0.1.0"],
        "devkit-cli": ["devkit-advisory==0.1.0"],
        "devkit-dist": ["devkit-core==0.1.0", "devkit-cli==0.1.0"],
        "devkit-agt": ["devkit-dist==0.1.0"],
    }
    for name, reqs in dependencies.items():
        directory = root / "packages" / name
        module = directory / "src" / name.replace("-", "_")
        module.mkdir(parents=True)
        (module / "__init__.py").write_text('VALUE = "0.1.0 literal"\n')
        optional = ""
        if name == "devkit-agt":
            optional = '\n[project.optional-dependencies]\nsearch = ["devkit-dist[search]"]\ninactive = ["devkit-advisory==0.1.0; python_version > \'99\'"]\n'
        entry = ""
        if name == "devkit-dist":
            entry = '\n[project.scripts]\ndevkit = "devkit_dist:cli"\n[project.entry-points."devkit.bundles"]\ndemo = "devkit_dist"\n'
            (module / "__init__.py").write_text(
                'VALUE = "0.1.0 literal"\ndef cli():\n from importlib.metadata import version\n print(version("devkit-dist"))\n'
            )
            bundle = module / "bundle"
            bundle.mkdir()
            (bundle / "bundle.toml").write_text(
                'schema = 1\nname = "demo"\nversion = "0.1.0"\n[[assets]]\nid = "policy"\nkind = "document"\nsource = "policy.md"\n'
            )
            (bundle / "policy.md").write_text("Fixture policy.\n")
        (directory / "README.md").write_text("Fixture " + name + "\n")
        (directory / "pyproject.toml").write_text(
            '[project]\nname = "'
            + name
            + '"\nversion = "0.1.0"\nrequires-python = ">=3.12"\nreadme = "README.md"\n'
            + "dependencies = "
            + json.dumps(reqs)
            + "\n"
            + optional
            + entry
            + "\n[tool.uv.sources]\n"
            + "".join(f"{dep} = {{ workspace = true }}\n" for dep in dependencies if dep != name)
            + '\n[build-system]\nrequires = ["hatchling==1.27.0"]\nbuild-backend = "hatchling.build"\n'
            + '\n[tool.hatch.build.targets.wheel]\npackages = ["src/'
            + name.replace("-", "_")
            + '"]\n'
        )
    paths = identity.workspace(root)
    described, built = prepare.describe(root, paths, {})
    originals = tmp_path / "originals"
    originals.mkdir()
    for name, entry in described.items():
        path = originals / built[name].name
        shutil.copyfile(built[name], path)
        entry["artifact"] = {"filename": path.name, "url": path.as_uri(), "sha256": identity.sha(path)}
    baseline = root / "scripts/releases/baseline.json"
    identity.save(
        baseline,
        {
            "schema": 1,
            "kind": "completed",
            "release": "0.1.0",
            "source_sha": "a" * 40,
            "recipe": identity.RECIPE,
            "packages": described,
            "extras": {},
        },
    )
    return root, baseline, originals


def changed(plan):
    return {n for n, e in plan["packages"].items() if e["disposition"] == "changed"}


def change_policy(root):
    policy = root / "packages/devkit-dist/src/devkit_dist/bundle/policy.md"
    policy.write_text("Changed policy.\n")
    return policy


def finish(root, baseline, monkeypatch):
    # Fixture does not have the devkit sync command; exercise its failure/success boundary separately.
    actual = prepare.subprocess.run

    def invoke(args, **kwargs):
        if args in (["uv", "lock"], ["uv", "run", "--no-active", "devkit", "sync"]):
            return subprocess.CompletedProcess(args, 0)
        return actual(args, **kwargs)

    monkeypatch.setattr(prepare.subprocess, "run", invoke)
    return prepare.prepare(root, baseline)


def test_payload_change_closure_reprepare_and_count(repo, monkeypatch):
    root, baseline, _ = repo
    policy = change_policy(root)
    plan = finish(root, baseline, monkeypatch)
    assert changed(plan) == {"devkit-dist", "devkit-agt"}
    assert plan["packages"]["devkit-advisory"]["version"] == "0.1.0"
    assert plan["packages"]["devkit-dist"]["bundles"]["demo"]["version"] == "0.1.1"
    assert finish(root, baseline, monkeypatch) == plan
    assert prepare.prepare(root, baseline, check=True) == plan
    # The previous lockstep policy advanced all five fixture wheels; selective advances two.
    assert (len(plan["packages"]), len(changed(plan))) == (5, 2)
    policy.write_text("Fixture policy.\n")
    reverted = finish(root, baseline, monkeypatch)
    assert changed(reverted) == set()
    assert all(e["version"] == "0.1.0" for e in reverted["packages"].values())
    assert reverted["packages"]["devkit-dist"]["bundles"]["demo"]["version"] == "0.1.0"
    identity.consistent(reverted["packages"])


def test_advisory_closure_includes_inactive_optional_pins(repo):
    root, baseline, _ = repo
    path = root / "packages/devkit-advisory/src/devkit_advisory/__init__.py"
    path.write_text('VALUE = "changed literal"\n')
    plan, texts, _ = prepare.compute(root, baseline)
    assert changed(plan) == set(plan["packages"])
    agt = tomllib.loads(texts["packages/devkit-agt/pyproject.toml"])["project"]
    assert agt["optional-dependencies"]["inactive"] == ["devkit-advisory==0.1.1; python_version > '99'"]
    assert agt["optional-dependencies"]["search"] == ["devkit-dist[search]"]


@pytest.mark.parametrize("relative", ["README.md", "tests/test_only.py"])
def test_repository_only_changes_do_not_advance(repo, relative):
    root, baseline, _ = repo
    path = root / relative
    path.parent.mkdir(exist_ok=True)
    path.write_text("Repository-only edit.\n")
    assert changed(prepare.compute(root, baseline)[0]) == set()


def test_shipped_readme_literal_add_remove_and_modes_are_significant(repo):
    root, baseline, _ = repo
    path = root / "packages/devkit-advisory/README.md"
    path.write_text(path.read_text() + "Changed description.\n")
    assert "devkit-advisory" in changed(prepare.compute(root, baseline)[0])
    path.write_text("Fixture devkit-advisory\n")
    code = root / "packages/devkit-advisory/src/devkit_advisory/__init__.py"
    code.write_text('VALUE = "0.1.1 literal"\n')
    assert "devkit-advisory" in changed(prepare.compute(root, baseline)[0])
    code.write_text('VALUE = "0.1.0 literal"\n')
    code.chmod(0o755)
    assert "devkit-advisory" in changed(prepare.compute(root, baseline)[0])
    code.chmod(0o644)
    added = code.parent / "extra.txt"
    added.write_text("resource")
    assert "devkit-advisory" in changed(prepare.compute(root, baseline)[0])


def test_bundle_byproducts_and_owned_versions_normalize(repo):
    root, baseline, _ = repo
    bundle = root / "packages/devkit-dist/src/devkit_dist/bundle"
    (bundle / ".DS_Store").write_bytes(b"finder")
    (bundle / "__pycache__").mkdir()
    (bundle / "__pycache__/policy.pyc").write_bytes(b"bytecode")
    (bundle / "other.pyc").write_bytes(b"bytecode")
    assert changed(prepare.compute(root, baseline)[0]) == set()
    manifest = bundle / "bundle.toml"
    manifest.write_text(manifest.read_text().replace("0.1.0", "0.1.1"))
    assert changed(prepare.compute(root, baseline)[0]) == set()


def test_ambiguous_generated_edit_refuses_and_removed_requirement_survives(repo, monkeypatch):
    root, baseline, _ = repo
    change_policy(root)
    finish(root, baseline, monkeypatch)
    path = root / "packages/devkit-agt/pyproject.toml"
    after = path.read_text()
    path.write_text(after.replace("devkit-dist==0.1.1", "devkit-dist==0.9.0"))
    with pytest.raises(AdvisoryError, match="ambiguous generated edit"):
        prepare.compute(root, baseline)
    path.write_text(after.replace('"devkit-dist==0.1.1"', ""))
    plan, texts, _ = prepare.compute(root, baseline)
    assert tomllib.loads(texts["packages/devkit-agt/pyproject.toml"])["project"]["dependencies"] == []
    assert "devkit-agt" in changed(plan)  # Authored dependency removal is meaningful.


@pytest.mark.parametrize("failure", ["lock", "sync"])
def test_failed_preparation_is_incomplete_and_retryable(repo, monkeypatch, failure):
    root, baseline, _ = repo
    change_policy(root)
    actual = prepare.subprocess.run

    def invoke(args, **kwargs):
        if args == ["uv", "lock"]:
            if failure == "lock":
                raise subprocess.CalledProcessError(1, args)
            return subprocess.CompletedProcess(args, 0)
        if args == ["uv", "run", "--no-active", "devkit", "sync"]:
            raise subprocess.CalledProcessError(2, args)
        return actual(args, **kwargs)

    monkeypatch.setattr(prepare.subprocess, "run", invoke)
    with pytest.raises(subprocess.CalledProcessError):
        prepare.prepare(root, baseline)
    assert json.loads((root / "scripts/releases/pending.json").read_text())["state"] == "incomplete"
    with pytest.raises(AdvisoryError, match="incomplete"):
        prepare.prepare(root, baseline, check=True)


def test_baseline_corruption_wrong_schema_and_pending_baseline_refuse(repo, monkeypatch):
    root, baseline, _ = repo
    original = baseline.read_bytes()
    invalid = json.loads(original)
    invalid["release"] = "0.0.9"
    baseline.write_text(json.dumps(invalid))
    with pytest.raises(AdvisoryError, match="digest"):
        prepare.compute(root, baseline)
    invalid["schema"] = 99
    identity.save(baseline, invalid)
    with pytest.raises(AdvisoryError, match="schema"):
        prepare.compute(root, baseline)
    baseline.write_bytes(original)
    finish(root, baseline, monkeypatch)
    invalid = json.loads(original)
    invalid["source_sha"] = "b" * 40
    identity.save(baseline, invalid)
    with pytest.raises(AdvisoryError, match="baseline mismatch"):
        prepare.compute(root, baseline)


def test_canonical_container_fields_and_foreign_dist_info(repo, tmp_path):
    _, baseline, originals = repo
    entry = identity.inventory(baseline)["packages"]["devkit-advisory"]
    original = originals / entry["artifact"]["filename"]
    other = tmp_path / original.name
    with zipfile.ZipFile(original) as before, zipfile.ZipFile(other, "w", compression=zipfile.ZIP_STORED) as after:
        for info in reversed(before.infolist()):
            info.date_time = (2020, 1, 1, 0, 0, 0)
            after.writestr(info, b"derived" if info.filename.endswith("/RECORD") else before.read(info))
    assert identity.wheel(other, "devkit-advisory", "0.1.0", set())[0] == entry["fingerprint"]
    with zipfile.ZipFile(other, "a") as archive:
        archive.writestr("foreign-1.0.dist-info/METADATA", "Name: foreign")
    with pytest.raises(AdvisoryError, match="foreign"):
        identity.wheel(other, "devkit-advisory", "0.1.0", set())


def test_original_reuse_checksum_and_missing_refuse(repo, tmp_path):
    _, baseline, _ = repo
    artifact = identity.inventory(baseline)["packages"]["devkit-advisory"]["artifact"]
    assert identity.sha(artifacts.obtain(artifact, tmp_path / "cache")) == artifact["sha256"]
    (tmp_path / "cache" / artifact["filename"]).write_bytes(b"corrupt")
    with pytest.raises(AdvisoryError, match="checksum"):
        artifacts.obtain(artifact, tmp_path / "cache")
    with pytest.raises(OSError):
        artifacts.obtain({**artifact, "url": (tmp_path / "missing.whl").as_uri()}, tmp_path / "empty")


def test_command_variants_follow_original_urls_and_extras():
    packages = {}
    deps = {
        "devkit-advisory": [],
        "devkit-cli": ["devkit-advisory==0.1.0"],
        "devkit-core": ["devkit-advisory==0.1.0"],
        "devkit-dist": ["devkit-cli==0.1.0", "devkit-core==0.1.0", 'devkit-embed>=0.1; extra == "search"'],
        "devkit-agt": ["devkit-dist==0.1.1", 'devkit-dist[search]; extra == "search"'],
        "devkit-mcp": ["devkit-dist==0.1.1"],
        "devkit-docs": ["devkit-agt==0.1.1"],
        "devkit-spec": ["devkit-docs==0.1.1", "devkit-mcp==0.1.1"],
        "devkit-viewer": ["devkit-agt==0.1.1"],
    }
    for name, requires in deps.items():
        version = "0.1.0" if name in {"devkit-advisory", "devkit-core", "devkit-cli"} else "0.1.1"
        packages[name] = {
            "requires": requires,
            "version": version,
            "artifact": {"url": f"https://example/v{version}/{name}.whl"},
        }
    data = {"packages": packages, "extras": {"devkit-embed": {"artifact": {"url": "https://example/model/model.whl"}}}}
    commands = install.commands(data)
    assert set(commands) == set(install.VARIANTS)
    assert "v0.1.0/devkit-advisory" in commands["harness"]
    assert "devkit-embed" in commands["search"] and "devkit-dist[search]" in commands["search"]
    assert "devkit-mcp" not in commands["harness"] and "devkit-mcp" in commands["sdd"]
    assert commands["advisory"].count(" @ ") == 1
    assert commands["tool"].startswith('uv tool install "devkit-dist @ ')


def test_bootstrap_verifies_originals_and_source_tag(repo, tmp_path):
    root, _, originals = repo
    (root / "VERSION").write_text("0.1.0\n")
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
        "original source",
    )
    run(root, "git", "tag", "v0.1.0")
    (originals / "SHA256SUMS").write_text(
        "".join(f"{identity.sha(p)}  {p.name}\n" for p in sorted(originals.glob("*.whl")))
    )
    output = tmp_path / "baseline.json"
    data = artifacts.bootstrap(root, "v0.1.0", "HEAD", originals, output, "fixture/repo")
    assert (
        len(data["packages"]) == 5 and data["bootstrap"]["source_sha"] == run(root, "git", "rev-parse", "HEAD").strip()
    )
    wheel = next(originals.glob("*.whl"))
    wheel.write_bytes(b"corrupt")
    with pytest.raises(AdvisoryError, match="missing/corrupt"):
        artifacts.bootstrap(root, "v0.1.0", "HEAD", originals, tmp_path / "bad.json", "fixture/repo")


def test_missing_baseline_has_no_success(tmp_path, capsys):
    assert main([], root=tmp_path) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "RELEASE_BASELINE_REQUIRED" in captured.err and "--baseline" in captured.err


def test_clean_wheel_git_and_tool_consumers(repo, tmp_path, monkeypatch):
    root, baseline, _ = repo
    change_policy(root)
    plan = finish(root, baseline, monkeypatch)
    paths = identity.workspace(root)
    described, built = prepare.describe(root, paths, {})
    full = {**plan, "packages": described}
    originals = identity.inventory(baseline)["packages"]
    for name, entry in full["packages"].items():
        entry["artifact"] = (
            originals[name]["artifact"]
            if name not in changed(plan)
            else {"url": built[name].as_uri(), "filename": built[name].name, "sha256": identity.sha(built[name])}
        )
    requirements = install.closure(full, {"devkit-agt": {"search", "inactive"}})
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    env = consumer / ".venv"
    run(consumer, "uv", "venv", str(env), "--python", "3.12.8")
    run(consumer, "uv", "pip", "install", "--python", str(env / "bin/python"), "--no-index", *requirements)
    assert run(consumer, str(env / "bin/devkit")).strip() == "0.1.1"
    assert (
        run(
            consumer,
            str(env / "bin/python"),
            "-c",
            'from importlib.metadata import version; print(version("devkit-advisory"))',
        ).strip()
        == "0.1.0"
    )
    # A distribution-only tool receives no harness; install the inventory-selected exact closure.
    tool_env = {**os.environ, "UV_TOOL_DIR": str(tmp_path / "tools"), "UV_TOOL_BIN_DIR": str(tmp_path / "bin")}
    tool_reqs = install.closure(full, {"devkit-dist": set()})
    dist = next(r for r in tool_reqs if r.startswith("devkit-dist @"))
    subprocess.run(
        ["uv", "tool", "install", "--no-index", dist, *[a for r in tool_reqs if r != dist for a in ("--with", r)]],
        cwd=consumer,
        env=tool_env,
        check=True,
        capture_output=True,
    )
    tool_python = tmp_path / "tools/devkit-dist/bin/python"
    assert (
        run(
            consumer,
            str(tool_python),
            "-c",
            'import importlib.util; assert importlib.util.find_spec("devkit_agt") is None',
        )
        == ""
    )
    # Git resolution applies the top-level source's workspace sources at one commit.
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
        "prepared source",
    )
    commit = run(root, "git", "rev-parse", "HEAD").strip()
    git_consumer = tmp_path / "git-consumer"
    git_consumer.mkdir()
    (git_consumer / "pyproject.toml").write_text(
        '[project]\nname = "consumer"\nversion = "0.0.0"\nrequires-python = ">=3.12"\ndependencies = []\n'
    )
    run(
        git_consumer,
        "uv",
        "add",
        "--offline",
        f"devkit-agt[search,inactive] @ git+{root.as_uri()}@{commit}#subdirectory=packages/devkit-agt",
    )
    assert run(git_consumer, "uv", "run", "devkit").strip() == "0.1.1"
    lock = tomllib.loads((git_consumer / "uv.lock").read_text())
    sources = [p["source"]["git"] for p in lock["package"] if "git" in p["source"]]
    assert len(sources) == 5 and all(commit in source for source in sources)


def test_partial_upload_retry_checks_every_existing_asset_before_upload(repo, tmp_path, monkeypatch, capfd):
    root, baseline, originals = repo
    data = identity.inventory(baseline)
    data["release"] = "0.1.1"
    data["source_sha"] = "b" * 40
    directory = tmp_path / "release"
    directory.mkdir()
    for entry in data["packages"].values():
        entry["artifact"]["url"] = (
            "https://github.com/fixture/repo/releases/download/v0.1.1/" + entry["artifact"]["filename"]
        )
        shutil.copyfile(originals / entry["artifact"]["filename"], directory / entry["artifact"]["filename"])
    (directory / "SHA256SUMS").write_text(
        "".join(f"{e['artifact']['sha256']}  {e['artifact']['filename']}\n" for e in data["packages"].values())
    )
    identity.save(directory / "release-inventory.json", data)
    (directory.parent / "release-notes.md").write_text("Fixture notes")
    existing = {next(directory.glob("*.whl")).name: next(directory.glob("*.whl")).read_bytes()}
    uploads = []
    actual_run = artifacts.subprocess.run

    def invoke(args, **kwargs):
        if args[:3] == ["gh", "release", "view"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"assets": [{"name": n} for n in existing]}), "")
        if args[:3] in (["gh", "release", "upload"], ["gh", "release", "edit"]) or args[0] == "git":
            actual_run(
                [
                    sys.executable,
                    "-c",
                    'import sys; print("raw tool stdout"); print("raw tool stderr", file=sys.stderr)',
                ],
                cwd=kwargs["cwd"],
                capture_output=kwargs.get("capture_output", False),
                text=True,
                check=True,
            )
        if args[:3] == ["gh", "release", "upload"]:
            p = Path(args[4])
            uploads.append(p.name)
            existing[p.name] = p.read_bytes()
            return subprocess.CompletedProcess(args, 0)
        if args[:3] == ["gh", "release", "edit"] or args[0] == "git":
            return subprocess.CompletedProcess(args, 0)
        return actual_run(args, **kwargs)

    actual_check = artifacts.subprocess.check_output

    def output(args, **kwargs):
        if args[0] == "gh":
            actual_check(
                [sys.executable, "-c", 'import sys; print("raw download stderr", file=sys.stderr)'],
                cwd=kwargs["cwd"],
                stderr=kwargs.get("stderr"),
            )
            return existing[args[args.index("--pattern") + 1]]
        return actual_check(args, **kwargs)

    monkeypatch.setattr(artifacts, "git", lambda *_: "b" * 40)
    monkeypatch.setattr(artifacts.subprocess, "run", invoke)
    monkeypatch.setattr(artifacts.subprocess, "check_output", output)
    artifacts.publish(directory, "v0.1.1", root=root)
    assert uploads[-1] == "release-inventory.json"
    assert len(uploads) == len(list(directory.iterdir())) - 1
    uploads.clear()
    artifacts.publish(directory, "v0.1.1", root=root)
    assert uploads == []
    existing[next(iter(existing))] = b"mismatched published bytes"
    with pytest.raises(AdvisoryError, match="remote asset mismatch"):
        artifacts.publish(directory, "v0.1.1", root=root)
    assert uploads == []
    captured = capfd.readouterr()
    assert captured.out == captured.err == ""


def test_tagged_build_publishes_changed_wheels_and_reuses_originals(repo, monkeypatch, capfd):
    from scripts.releases.release import release

    root, baseline, _ = repo
    change_policy(root)
    plan = finish(root, baseline, monkeypatch)
    run(root, "git", "init", "-q")
    run(root, "git", "add", ".")
    run(root, "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "prepared")
    run(root, "git", "tag", "v0.1.1")
    actual = subprocess.run

    def invoke(args, **kwargs):
        if args == ["uv", "lock", "--check"] or "scripts/handbook.py" in args:
            return actual(
                [
                    sys.executable,
                    "-c",
                    'import sys; print("raw child result"); print("raw child diagnostic", file=sys.stderr)',
                ],
                cwd=kwargs["cwd"],
                capture_output=kwargs.get("capture_output", False),
                text=True,
                check=True,
            )
        return actual(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", invoke)
    data = release(root, "v0.1.1", baseline, "fixture/repo")
    names = {p.name for p in (root / "dist/release").glob("*.whl")}
    assert names == {"devkit_dist-0.1.1-py3-none-any.whl", "devkit_agt-0.1.1-py3-none-any.whl"}
    assert data["packages"]["devkit-advisory"]["artifact"] == plan["packages"]["devkit-advisory"]["artifact"]
    assert (
        identity.inventory(root / "dist/release/release-inventory.json")["source_sha"]
        == run(root, "git", "rev-parse", "HEAD").strip()
    )
    captured = capfd.readouterr()
    assert captured.out == captured.err == ""


def test_explicit_recipe_change_and_inconsistent_baseline(repo):
    root, baseline, _ = repo
    data = identity.inventory(baseline)
    data["recipe"] = {**identity.RECIPE, "uv": "0.12.7"}
    identity.save(baseline, data)
    assert changed(prepare.compute(root, baseline)[0]) == set(data["packages"])
    data["packages"]["devkit-core"]["requires"] = ['devkit-advisory==9.9.9; python_version > "99"']
    identity.save(baseline, data)
    with pytest.raises(AdvisoryError, match="actual version"):
        prepare.compute(root, baseline)


@pytest.mark.parametrize("mutation", ["missing", "wrong-name"])
def test_bootstrap_refuses_source_optional_metadata_mismatch(repo, tmp_path, mutation):
    import io

    root, _, originals = repo
    (root / "VERSION").write_text("0.1.0\n")
    run(root, "git", "init", "-q")
    run(root, "git", "add", ".")
    run(root, "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "original")
    run(root, "git", "tag", "v0.1.0")
    path = next(originals.glob("devkit_agt-*.whl"))
    buffer = io.BytesIO()
    with zipfile.ZipFile(path) as before, zipfile.ZipFile(buffer, "w") as after:
        for info in before.infolist():
            raw = before.read(info)
            if info.filename.endswith("/METADATA"):
                lines = raw.decode().splitlines(keepends=True)
                matching = [line for line in lines if line.startswith("Requires-Dist: devkit-dist[search]")]
                assert len(matching) == 1
                raw = "".join(
                    ("" if mutation == "missing" else line.replace("devkit-dist[search]", "wrong-helper[search]"))
                    if line in matching
                    else line
                    for line in lines
                ).encode()
            after.writestr(info, raw)
    path.write_bytes(buffer.getvalue())
    (originals / "SHA256SUMS").write_text(
        "".join(f"{identity.sha(p)}  {p.name}\n" for p in sorted(originals.glob("*.whl")))
    )
    with pytest.raises(AdvisoryError, match="complete dependency mismatch"):
        artifacts.bootstrap(root, "v0.1.0", "HEAD", originals, tmp_path / "invalid.json", "fixture/repo")
    assert not (tmp_path / "invalid.json").exists()


@pytest.mark.parametrize("content_changed", [False, True])
def test_moved_bundle_version_follows_content_not_distribution(repo, content_changed):
    root, baseline, _ = repo
    former = root / "packages/devkit-dist"
    metadata = former / "pyproject.toml"
    metadata.write_text(
        metadata.read_text().replace('[project.entry-points."devkit.bundles"]\ndemo = "devkit_dist"\n', "")
    )
    new = root / "packages/devkit-moved"
    module = new / "src/devkit_moved"
    module.mkdir(parents=True)
    (module / "__init__.py").write_text('"""Moved bundle fixture."""\n')
    shutil.move(former / "src/devkit_dist/bundle", module / "bundle")
    (new / "pyproject.toml").write_text(
        '[project]\nname = "devkit-moved"\nversion = "0.1.0"\nrequires-python = ">=3.12"\ndependencies = []\n'
        '[project.entry-points."devkit.bundles"]\ndemo = "devkit_moved"\n'
        '[build-system]\nrequires = ["hatchling==1.27.0"]\nbuild-backend = "hatchling.build"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["src/devkit_moved"]\n'
    )
    if content_changed:
        (module / "bundle/policy.md").write_text("Changed moved policy.\n")
    plan, _, _ = prepare.compute(root, baseline)
    moved = plan["packages"]["devkit-moved"]
    assert moved["version"] == "0.1.1"
    assert moved["bundles"]["demo"]["version"] == ("0.1.1" if content_changed else "0.1.0")
    assert plan["packages"]["devkit-dist"]["disposition"] == "changed"
    assert plan["packages"]["devkit-dist"]["bundles"] == {}
