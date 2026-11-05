"""Release identities: strict inventories, canonical wheels and registered bundle content."""

from __future__ import annotations

import email.parser
import hashlib
import json
import re
import tomllib
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename

from .errors import ReleaseError

VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
RECIPE = {"python": "3.12.8", "uv": "0.12.8", "hatchling": "1.27.0", "canonical": 1}


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(value: dict) -> dict:
    return {**value, "digest": digest({k: v for k, v in value.items() if k != "digest"})}


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(seal(value)))


def requirements(project: dict) -> list[str]:
    return [
        *project.get("dependencies", []),
        *(r for rs in project.get("optional-dependencies", {}).values() for r in rs),
    ]


def consistent(packages: dict, extras: dict | None = None) -> None:
    for name, package in packages.items():
        for text in package["requires"]:
            req = Requirement(text)
            dep = canonicalize_name(req.name)
            if extras and dep in extras:
                require(
                    not req.url and (not req.specifier or req.specifier.contains(extras[dep]["version"])),
                    f"{name}: extra artifact version does not satisfy requirement: {text}",
                )
            if dep in packages and req.specifier:
                require(
                    str(req.specifier) == "==" + packages[dep]["version"] and not req.url,
                    f"{name}: internal requirement must pin actual version: {text}",
                )


def inventory(path: Path) -> dict:
    data = json.loads(path.read_text())
    require(data["schema"] == 1 and data["kind"] == "completed", "expected schema 1 completed inventory")
    require(data["digest"] == seal(data)["digest"], "inventory digest mismatch")
    require(
        VERSION.fullmatch(data["release"]) and re.fullmatch("[0-9a-f]{40}", data["source_sha"]),
        "invalid release/source identity",
    )
    require(isinstance(data["recipe"], dict) and data["packages"], "missing recipe/packages")
    for name, entry in {**data["packages"], **data["extras"]}.items():
        require(name == canonicalize_name(name) and VERSION.fullmatch(entry["version"]), "invalid package identity")
        artifact = entry["artifact"]
        dist, version, _, _ = parse_wheel_filename(artifact["filename"])
        require(dist == name and str(version) == entry["version"], "artifact filename identity mismatch")
        require(re.fullmatch("[0-9a-f]{64}", artifact["sha256"]), "invalid artifact digest")
        require(artifact["url"].endswith("/" + artifact["filename"]), "artifact URL identity mismatch")
        if name in data["packages"]:
            require(re.fullmatch("[0-9a-f]{64}", entry["fingerprint"]), "invalid payload fingerprint")
            require(
                not PurePosixPath(entry["path"]).is_absolute() and ".." not in PurePosixPath(entry["path"]).parts,
                "invalid package path",
            )
            require(
                isinstance(entry["bundles"], dict) and isinstance(entry["requires"], list), "invalid package metadata"
            )
    consistent(data["packages"], data["extras"])
    return data


def workspace(root: Path) -> dict[str, Path]:
    config = tomllib.loads((root / "pyproject.toml").read_text())["tool"]["uv"]["workspace"]
    excluded = {p for pattern in config.get("exclude", []) for p in root.glob(pattern)}
    result = {}
    for directory in sorted({p for pattern in config["members"] for p in root.glob(pattern)} - excluded):
        path = directory / "pyproject.toml"
        project = tomllib.loads(path.read_text())["project"]
        name = canonicalize_name(project["name"])
        require(name not in result and VERSION.fullmatch(project["version"]), f"invalid/duplicate package: {name}")
        result[name] = path
    require(result, "empty workspace")
    return result


def normalized_manifest(raw: bytes) -> bytes:
    text = raw.decode()
    header, separator, rest = text.partition("\n[")
    header, count = re.subn(r'(?m)^(version\s*=\s*)(["\'])[^"\'\r\n]*\2', r'\1"<version>"', header)
    require(count == 1, "unsupported bundle version shape")
    return (header + separator + rest).encode()


def bundles(metadata: Path) -> dict:
    from devkit_dist.features.distribution.services.bundles.manifest import load_bundle, source_files

    project = tomllib.loads(metadata.read_text())["project"]
    result = {}
    for name, module in project.get("entry-points", {}).get("devkit.bundles", {}).items():
        require(":" not in module, "unsupported bundle entrypoint")
        root = metadata.parent / "src" / module.replace(".", "/") / "bundle"
        bundle = load_bundle(root)
        files = {root / "bundle.toml"}
        if bundle.constitution:
            files.add(bundle.constitution)
        for asset in bundle.assets:
            for _, source in asset.sources:
                files.update(source_files(root, source))
        records = []
        for path in sorted(files):
            raw = path.read_bytes()
            if path.name == "bundle.toml" and path.parent == root:
                raw = normalized_manifest(raw)
            records.append(
                [path.relative_to(root).as_posix(), hashlib.sha256(raw).hexdigest(), bool(path.stat().st_mode & 0o111)]
            )
        result[name] = {
            "version": bundle.version,
            "fingerprint": digest(records),
            "manifest": (root / "bundle.toml").relative_to(metadata.parent).as_posix(),
        }
    return result


def wheel(path: Path, name: str, version: str, manifests: set[str]) -> tuple[str, list[str]]:
    dist, parsed_version, _, _ = parse_wheel_filename(path.name)
    require(dist == name and str(parsed_version) == version, "wheel filename identity mismatch")
    records = []
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        require(len({m.filename for m in members}) == len(members), "duplicate wheel member")
        owned = name.replace("-", "_") + "-" + version + ".dist-info/"
        metadata_path = owned + "METADATA"
        require(metadata_path in archive.namelist(), "unsupported wheel dist-info shape")
        require(manifests <= set(archive.namelist()), "registered bundle manifest missing from wheel")
        metadata = archive.read(metadata_path).decode()
        parsed = email.parser.Parser().parsestr(metadata)
        require(
            canonicalize_name(parsed["Name"]) == name and parsed.get_all("Version") == [version],
            "wheel metadata identity mismatch",
        )
        require(parsed.get("Metadata-Version") in {"2.1", "2.2", "2.3", "2.4"}, "unsupported metadata version")
        for member in members:
            p = PurePosixPath(member.filename)
            require(not p.is_absolute() and ".." not in p.parts, "unsafe wheel member")
            require(
                not any(part.endswith(".dist-info") for part in p.parts) or member.filename.startswith(owned),
                "foreign dist-info",
            )
            if member.is_dir() or member.filename == owned + "RECORD":
                continue
            raw = archive.read(member)
            if member.filename == metadata_path:
                raw, count = re.subn(rb"(?m)^Version: [^\r\n]+", b"Version: <version>", raw)
                require(count == 1, "unsupported METADATA Version shape")
            if member.filename in manifests:
                raw = normalized_manifest(raw)
            canonical = (
                member.filename.replace(owned, "<dist-info>/", 1)
                if member.filename.startswith(owned)
                else member.filename
            )
            records.append([canonical, hashlib.sha256(raw).hexdigest(), bool((member.external_attr >> 16) & 0o111)])
    return digest(sorted(records)), parsed.get_all("Requires-Dist", [])
