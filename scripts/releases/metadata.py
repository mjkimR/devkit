"""Formatting-preserving semantic generated edits and exact dependency propagation."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import tomlkit
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from .identity import require, requirements


def slots(text: str, manifest: bool = False) -> dict[str, str]:
    data = tomllib.loads(text)
    if manifest:
        return {"version": data["version"]}
    project = data["project"]
    result = {"project.version": project["version"]}
    groups = {
        "dependencies": project.get("dependencies", []),
        **{"optional-dependencies." + extra: reqs for extra, reqs in project.get("optional-dependencies", {}).items()},
    }
    for group, reqs in groups.items():
        for raw in reqs:
            req = Requirement(raw)
            key = "|".join([group, canonicalize_name(req.name), ",".join(sorted(req.extras)), str(req.marker or "")])
            require(key not in result, f"duplicate requirement slot: {key}")
            result[key] = raw
    return result


def replace(text: str, field: str, value: str, *, manifest: bool = False) -> str:
    doc = tomlkit.parse(text)
    if field == "version" and manifest:
        doc["version"] = value
    elif field == "project.version":
        doc["project"]["version"] = value
    else:
        current = slots(text)[field]
        group = field.split("|")[0]
        if group == "dependencies":
            array = doc["project"]["dependencies"]
        else:
            array = doc["project"]["optional-dependencies"][group.removeprefix("optional-dependencies.")]
        array[list(array).index(current)] = value
    return tomlkit.dumps(doc)


def unwind(root: Path, pending: dict | None) -> dict[str, str]:
    texts = {}
    for edit in pending.get("edits", []) if pending else []:
        relative = edit["path"]
        path = root / relative
        require(not Path(relative).is_absolute() and ".." not in Path(relative).parts, "unsafe generated edit path")
        if not path.exists():
            continue
        text = texts.get(relative, path.read_text())
        manifest = path.name == "bundle.toml"
        current = slots(text, manifest).get(edit["field"])
        if current is None or current == edit["before"]:
            continue  # Authored removal or explicit restoration survives.
        require(current == edit["after"], f"ambiguous generated edit: {relative} {edit['field']}")
        texts[relative] = replace(text, edit["field"], edit["before"], manifest=manifest)
    return texts


def selected(projects: dict, changed: set[str], release: str, baseline: dict) -> tuple[dict, dict]:
    reasons = {name: ["payload"] for name in changed}
    while True:
        versions = {name: release if name in changed else baseline[name]["version"] for name in projects}
        added = set()
        for name, project in projects.items():
            for raw in requirements(project):
                req = Requirement(raw)
                dep = canonicalize_name(req.name)
                if dep not in versions:
                    continue
                require(
                    not req.url
                    and (
                        not req.specifier
                        or (
                            len(req.specifier) == 1
                            and str(req.specifier).startswith("==")
                            and "*" not in str(req.specifier)
                        )
                    ),
                    f"unsupported internal requirement: {raw}",
                )
                if req.specifier and str(req.specifier) != "==" + versions[dep]:
                    added.add(name)
                    reasons.setdefault(name, []).append(dep)
        added -= changed
        if not added:
            return versions, {name: sorted(set(rs)) for name, rs in sorted(reasons.items())}
        changed |= added


def generated(root: Path, paths: dict, logical: dict, versions: dict, bundle_versions: dict) -> tuple[dict, list]:
    texts = dict(logical)
    edits = []
    for name, path in paths.items():
        relative = path.relative_to(root).as_posix()
        before = logical.get(relative, path.read_text())
        after = replace(before, "project.version", versions[name])
        for field, raw in slots(before).items():
            if "|" not in field:
                continue
            req = Requirement(raw)
            dep = canonicalize_name(req.name)
            if dep in versions and req.specifier:
                # Preserve authored spelling, extras and marker text around the exact specifier.
                updated = re.sub(
                    r"==([ \t]*)[^;\s]+", lambda m, version=versions[dep]: "==" + m[1] + version, raw, count=1
                )
                after = replace(after, field, updated)
        texts[relative] = after
        old, new = slots(before), slots(after)
        edits.extend(
            {"path": relative, "field": field, "before": value, "after": new[field]}
            for field, value in old.items()
            if value != new[field]
        )
    for relative, version in sorted(bundle_versions.items()):
        before = logical.get(relative, (root / relative).read_text())
        after = replace(before, "version", version, manifest=True)
        texts[relative] = after
        old = slots(before, True)["version"]
        if old != version:
            edits.append({"path": relative, "field": "version", "before": old, "after": version})
    return texts, edits
