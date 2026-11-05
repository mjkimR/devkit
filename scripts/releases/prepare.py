"""Prepare deterministic release plans against verified completed inventories."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename

from .errors import StalePlanError
from .identity import RECIPE, VERSION, bundles, consistent, inventory, require, save, seal, sha, wheel, workspace
from .metadata import generated, selected, unwind


def recipe(root: Path) -> dict:
    value = json.loads((root / "scripts/releases/recipe.json").read_text())
    require(value == RECIPE, "unsupported build recipe; update tooling and recipe together")
    require(sys.version.split()[0] == value["python"], "run with recipe Python " + value["python"])
    actual = subprocess.check_output(["uv", "--version"], cwd=root, text=True).split()[1]
    require(actual == value["uv"], "run with recipe uv " + value["uv"])
    return value


def build(root: Path, paths: dict, texts: dict) -> dict:
    """Build disposable source snapshots, keeping the candidate worktree untouched."""
    location = root / "dist/selective-probes" / uuid.uuid4().hex
    location.mkdir(parents=True)
    result = {}
    for name, metadata in sorted(paths.items()):
        target = location / name
        # Backend source trees need no editing byproducts; use the manifest's exclusions.
        from devkit_dist.features.distribution.services.bundles.manifest import IGNORED_NAMES, IGNORED_SUFFIXES

        shutil.copytree(
            metadata.parent,
            target,
            ignore=lambda _, names: [
                n for n in names if n in IGNORED_NAMES or n.endswith(IGNORED_SUFFIXES) or n in {".venv", ".git", "dist"}
            ],
        )
        for relative, text in texts.items():
            original = root / relative
            if original.is_relative_to(metadata.parent):
                (target / original.relative_to(metadata.parent)).write_text(text)
        out = location / (name + "-wheels")
        subprocess.run(
            [
                "uv",
                "build",
                str(target),
                "--wheel",
                "--no-sources",
                "--python",
                RECIPE["python"],
                "--build-constraints",
                str(root / "scripts/releases/build-constraints.txt"),
                "--out-dir",
                str(out),
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        artifacts = list(out.glob("*.whl"))
        require(len(artifacts) == 1, f"{name}: expected one built wheel")
        result[name] = artifacts[0]
    return result


def describe(root: Path, paths: dict, texts: dict, builder=build) -> tuple[dict, dict]:
    built = builder(root, paths, texts)
    result = {}
    for name, path in sorted(paths.items()):
        relative = path.relative_to(root).as_posix()
        project = tomllib.loads(texts.get(relative, path.read_text()))["project"]
        # Manifest reader must see the logical snapshot, never pending generated values.
        snapshot = built[name].parent.parent / name / "pyproject.toml"
        bundle_data = bundles(snapshot if snapshot.exists() else path)
        for bundle in bundle_data.values():
            manifest = (path.parent / bundle["manifest"]).relative_to(root).as_posix()
            if manifest in texts and not snapshot.exists():
                # Custom fixture builders can expose logical versions without building a copy.
                bundle["version"] = tomllib.loads(texts[manifest])["version"]
        manifests = {b["manifest"].removeprefix("src/") for b in bundle_data.values()}
        fingerprint, requires = wheel(built[name], name, project["version"], manifests)
        result[name] = {
            "path": path.parent.relative_to(root).as_posix(),
            "version": project["version"],
            "fingerprint": fingerprint,
            "requires": requires,
            "bundles": bundle_data,
        }
    return result, built


def pending(root: Path, baseline: dict, release: str) -> dict | None:
    path = root / "scripts/releases/pending.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    require(
        data["schema"] == 1 and data["kind"] == "pending" and data["digest"] == seal(data)["digest"],
        "invalid pending plan",
    )
    require(
        data["baseline_digest"] == baseline["digest"] and data["release"] == release,
        "pending release/baseline mismatch; resolve the existing plan before preparing another release",
    )
    return data


def model_extras(root: Path, baseline: dict, release: str) -> dict:
    """The committed model keeps its independent version and original bytes."""
    extras = dict(baseline["extras"])
    sources = tomllib.loads((root / "pyproject.toml").read_text()).get("tool", {}).get("uv", {}).get("sources", {})
    for name, source in sources.items():
        if not isinstance(source, dict) or not str(source.get("path", "")).endswith(".whl"):
            continue
        relative = source["path"]
        require(relative.startswith("models/") and ".." not in Path(relative).parts, "unsupported extra wheel source")
        path = root / relative
        dist, version, _, _ = parse_wheel_filename(path.name)
        require(dist == canonicalize_name(name), "extra source identity mismatch")
        checksum = sha(path)
        previous = extras.get(dist)
        if previous and previous["version"] == str(version):
            require(previous["artifact"]["sha256"] == checksum, "published model identity has different bytes")
        else:
            extras[dist] = {
                "version": str(version),
                "source_path": relative,
                "artifact": {"filename": path.name, "sha256": checksum, "url": "<release-url>/" + path.name},
            }
    return extras


def compute(root: Path, baseline_path: Path, *, builder=build) -> tuple[dict, dict, dict]:
    baseline = inventory(baseline_path)
    release = (root / "VERSION").read_text().strip()
    require(VERSION.fullmatch(release), "VERSION must contain X.Y.Z without leading zeroes")
    require(
        tuple(map(int, release.split("."))) > tuple(map(int, baseline["release"].split("."))),
        "release must be newer than completed baseline",
    )
    build_recipe = recipe(root)
    paths = workspace(root)
    old_plan = pending(root, baseline, release)
    logical = unwind(root, old_plan)
    candidate, _ = describe(root, paths, logical, builder)
    changed = {
        name
        for name, entry in candidate.items()
        if name not in baseline["packages"]
        or entry["fingerprint"] != baseline["packages"][name]["fingerprint"]
        or build_recipe != baseline["recipe"]
    }
    projects = {
        name: tomllib.loads(logical.get(path.relative_to(root).as_posix(), path.read_text()))["project"]
        for name, path in paths.items()
    }
    for project in projects.values():
        from .identity import requirements

        for raw in requirements(project):
            dep = canonicalize_name(Requirement(raw).name)
            require(
                dep not in baseline["packages"] or dep in projects,
                "removed internal dependency is still required: " + dep,
            )
    versions, reasons = selected(projects, changed, release, baseline["packages"])
    bundle_versions = {}
    for name, entry in candidate.items():
        for bundle_name, bundle in entry["bundles"].items():
            previous = baseline["packages"].get(name, {}).get("bundles", {}).get(bundle_name)
            version = (
                release if previous is None or previous["fingerprint"] != bundle["fingerprint"] else previous["version"]
            )
            bundle_versions[(paths[name].parent / bundle["manifest"]).relative_to(root).as_posix()] = version
    texts, edits = generated(root, paths, logical, versions, bundle_versions)
    final, built = describe(root, paths, texts, builder)
    extras = model_extras(root, baseline, release)
    consistent(final, extras)
    for name, entry in final.items():
        if name not in changed:
            require(
                entry["fingerprint"] == baseline["packages"][name]["fingerprint"],
                f"{name}: unexpected final payload drift",
            )
        entry["disposition"] = "changed" if name in changed else "reused"
        if name not in changed:
            entry["artifact"] = baseline["packages"][name]["artifact"]
    plan = {
        "schema": 1,
        "kind": "pending",
        "release": release,
        "state": "complete",
        "baseline_digest": baseline["digest"],
        "baseline_release": baseline["release"],
        "baseline": baseline,
        "recipe": build_recipe,
        "packages": final,
        "extras": extras,
        "closure": reasons,
        "edits": edits,
    }
    return seal(plan), texts, built


def prepare(root: Path, baseline_path: Path, *, check: bool = False, builder=build) -> dict:
    plan, texts, _ = compute(root, baseline_path, builder=builder)
    plan_path = root / "scripts/releases/pending.json"
    if check:
        if not plan_path.exists() or json.loads(plan_path.read_text()) != plan:
            raise StalePlanError("release plan stale, missing or incomplete")
        if not all((root / relative).read_text() == text for relative, text in texts.items()):
            raise StalePlanError("generated metadata stale")
        return plan
    save(plan_path, {**plan, "state": "incomplete"})
    for relative, text in texts.items():
        if (root / relative).read_text() != text:
            (root / relative).write_text(text)
    subprocess.run(["uv", "lock"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(["uv", "run", "--no-active", "devkit", "sync"], cwd=root, check=True, capture_output=True, text=True)
    save(plan_path, plan)
    return plan
