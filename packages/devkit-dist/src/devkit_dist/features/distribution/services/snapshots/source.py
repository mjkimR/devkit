"""Build an ordinary local wrapper from a statically supported content-provider checkout."""

from __future__ import annotations

import json
import keyword
import re
import tomllib
from pathlib import Path
from typing import Any

from devkit_dist.features.distribution.models.content import Content, json_content, sha256
from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.models.snapshots import (
    SnapshotCandidate,
    SnapshotInvalidError,
    SnapshotUnsupportedError,
)
from devkit_dist.features.distribution.repositories.snapshots import read_content, read_tree, source_commit
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.manifest import safe_source
from devkit_dist.features.distribution.services.snapshots.provenance import seal, validate_relative_inventory
from devkit_dist.features.distribution.services.snapshots.support import (
    check_declarations,
    check_python,
    inert_initializer,
)

PACKAGE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?\Z")
MODULE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def package_module(name: str) -> str:
    if not PACKAGE.fullmatch(name):
        raise SnapshotInvalidError("--package must be a distribution name")
    module = re.sub(r"[-_.]+", "_", name).lower()
    if not MODULE.fullmatch(module) or keyword.iskeyword(module):
        raise SnapshotUnsupportedError("the local package name must also form a valid distinct Python module")
    return module


def _project(source: Path) -> tuple[dict[str, Any], Content]:
    raw = read_content(source / "pyproject.toml")
    try:
        data = tomllib.loads(raw.data.decode())
    except (ValueError, UnicodeError) as exc:
        raise SnapshotInvalidError(f"invalid source pyproject.toml: {exc}") from exc
    project = data.get("project", {})
    if not isinstance(project, dict) or project.get("dynamic") or not isinstance(project.get("name"), str):
        raise SnapshotUnsupportedError("source requires static project name/version metadata")
    if (
        not PACKAGE.fullmatch(project["name"])
        or not isinstance(project.get("version"), str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.!+_-]*", project["version"])
    ):
        raise SnapshotUnsupportedError("source requires static distribution name/version strings")
    if project.get("dependencies") or project.get("optional-dependencies"):
        raise SnapshotUnsupportedError("source project runtime dependencies/optional-dependencies must be empty")
    groups = project.get("entry-points", {})
    if (
        not isinstance(groups, dict)
        or set(groups) != {"devkit.bundles"}
        or project.get("scripts")
        or project.get("gui-scripts")
    ):
        raise SnapshotUnsupportedError("source may declare only devkit.bundles entry points, no runtime commands")
    entries = groups["devkit.bundles"]
    if not isinstance(entries, dict) or not entries:
        raise SnapshotUnsupportedError("source must provide at least one bundle resource module")

    def table(value: Any, label: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise SnapshotUnsupportedError(f"{label} must be a static table")
        return value

    build = table(data.get("build-system", {}), "build-system")
    tool = table(data.get("tool", {}), "tool")
    hatch = table(table(tool.get("hatch", {}), "tool.hatch").get("build", {}), "tool.hatch.build")
    targets = table(hatch.get("targets", {}), "wheel targets")
    wheel = table(targets.get("wheel", {}), "wheel mapping")
    if (
        build.get("build-backend") != "hatchling.build"
        or build.get("backend-path")
        or set(hatch) - {"targets"}
        or set(targets) - {"wheel"}
        or set(wheel) - {"packages"}
    ):
        raise SnapshotUnsupportedError(
            "source requires the ordinary Hatch src package mapping without custom build hooks"
        )
    packages = wheel.get("packages")
    if (
        not isinstance(packages, list)
        or not packages
        or not all(isinstance(item, str) and item.startswith("src/") for item in packages)
    ):
        raise SnapshotUnsupportedError("source wheel packages must name ordinary src directories")
    return {**project, "_packages": packages}, raw


def _resource(source: Path, module: str, packages: list[str]) -> Path:
    parts = module.split(".")
    if not parts or any(not MODULE.fullmatch(part) or keyword.iskeyword(part) for part in parts):
        raise SnapshotUnsupportedError(
            f"entry point must name a resource module, without attributes or extras: {module}"
        )
    relative = "src/" + "/".join(parts)
    if not any(relative == item or relative.startswith(item.rstrip("/") + "/") for item in packages):
        raise SnapshotUnsupportedError(f"resource module is outside declared src package mapping: {module}")
    try:
        root = safe_source(source, relative)
        for index in range(1, len(parts) + 1):
            initializer = source / "src" / Path(*parts[:index]) / "__init__.py"
            if initializer.exists() or index == len(parts):
                inert_initializer(read_content(initializer).data, initializer.relative_to(source).as_posix())
        return safe_source(root, "bundle")
    except BundleError as exc:
        raise SnapshotUnsupportedError(f"incomplete resource module: {module}: {exc.message}") from exc


def _notices(source: Path, project: dict[str, Any]) -> dict[Path, Content]:
    names = project.get("license-files", [])
    if not isinstance(names, list) or not all(isinstance(item, str) for item in names):
        raise SnapshotUnsupportedError("license-files must name literal in-checkout files")
    license_value = project.get("license")
    if isinstance(license_value, dict) and "file" in license_value:
        names = [*names, license_value["file"]]
    if not isinstance(names, list) or not all(isinstance(item, str) for item in names):
        raise SnapshotUnsupportedError("license-files must name literal in-checkout files")
    found: dict[Path, Content] = {}
    for name in names:
        try:
            path = safe_source(source, name)
            found[path] = read_content(path)
        except BundleError as exc:
            raise SnapshotUnsupportedError(f"license/notice file is unavailable: {name}") from exc
    return found


def prepare_candidate(source: Path, package: str) -> SnapshotCandidate:
    """Read all source bytes once, validate them, then construct a path-free wrapper."""
    module = package_module(package)
    if source.is_symlink() or not source.is_dir():
        raise SnapshotInvalidError("source must be an accessible unlinked checkout directory")
    source = source.resolve()
    project, raw = _project(source)
    source_name = project["name"]
    if re.sub(r"[-_.]+", "-", package).lower() == re.sub(r"[-_.]+", "-", source_name).lower():
        raise SnapshotUnsupportedError("wrapper distribution name must differ from the upstream provider")
    files: dict[str, Content] = {f"src/{module}/__init__.py": Content(b"", 0o644)}
    originals = {source / "pyproject.toml": raw}
    bundles: dict[str, dict[str, str]] = {}
    entries: dict[str, str] = {}
    destinations: set[str] = set()
    for name, original_module in sorted(project["entry-points"]["devkit.bundles"].items()):
        if not isinstance(name, str) or not isinstance(original_module, str):
            raise SnapshotUnsupportedError("bundle entry points must be static resource-module strings")
        root = _resource(source, original_module, project["_packages"])
        try:
            bundle = load_bundle(root)
        except BundleError as exc:
            raise SnapshotInvalidError(f"invalid source bundle {name}: {exc.message}") from exc
        if bundle.name != name:
            raise SnapshotUnsupportedError(f"entry point {name} does not match bundle name {bundle.name}")
        local = name.replace("-", "_")
        if not MODULE.fullmatch(local) or keyword.iskeyword(local) or local in destinations:
            raise SnapshotUnsupportedError(f"bundle name has colliding/invalid normalized wrapper module: {name}")
        destinations.add(local)
        payload = read_tree(root, source=True)
        check_python(payload)
        check_declarations(bundle, payload)
        prefix = f"src/{module}/{local}"
        files[f"{prefix}/__init__.py"] = Content(b"", 0o644)
        for rel, content in payload.items():
            files[f"{prefix}/bundle/{rel}"] = content
            originals[root / rel] = content
        # Inert parent/resource initializers participate in commit provenance too.
        parent = root.parent
        while parent != source / "src":
            initializer = parent / "__init__.py"
            if initializer.exists():
                originals[initializer] = read_content(initializer)
            parent = parent.parent
        entries[name] = f"{module}.{local}"
        bundles[name] = {"version": bundle.version, "module": entries[name]}
    notices = _notices(source, project)
    for path, content in notices.items():
        files[f"notices/{path.relative_to(source).as_posix()}"] = content
        originals[path] = content
    requires_python = project.get("requires-python", ">=3.12")
    if not isinstance(requires_python, str):
        raise SnapshotUnsupportedError("source requires-python must be a static string")
    quote = json.dumps
    entry_lines = "\n".join(f"{quote(name)} = {quote(value)}" for name, value in entries.items())
    notice_paths = sorted(rel for rel in files if rel.startswith("notices/"))
    license_line = f"license-files = {quote(notice_paths)}\n" if notice_paths else ""
    packaging = (
        f'[project]\nname = {quote(package)}\nversion = "0.0.0"\nrequires-python = {quote(requires_python)}\n'
        f"{license_line}"
        'dependencies = []\n\n[project.entry-points."devkit.bundles"]\n'
        f'{entry_lines}\n\n[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        f'\n[tool.hatch.build.targets.wheel]\npackages = ["src/{module}"]\n'
    )
    files["pyproject.toml"] = Content(packaging.encode(), 0o644)
    validate_relative_inventory(files)
    record = seal(
        {
            "schema": 1,
            "package": package,
            "source": {
                "name": source_name,
                "version": project["version"],
                "commit": source_commit(source, originals),
                "requires_python": requires_python,
                "metadata_sha256": sha256(raw.data),
            },
            "bundles": bundles,
        },
        files,
    )
    return SnapshotCandidate({**files, "snapshot.json": json_content(record)}, record)
