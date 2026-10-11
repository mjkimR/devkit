from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path

from .guidance import prepend_context
from .manifest import Bundle, BundleError, source_files


def _payload(bundle: Bundle) -> dict[str, tuple[bytes, int]]:
    payload = {"bundle.toml": ((bundle.root / "bundle.toml").read_bytes(), 0o644)}
    if bundle.constitution is not None:
        payload["AGENTS.md"] = (bundle.constitution.read_bytes(), 0o644)
    for asset in bundle.assets:
        for _, source in asset.sources:
            for path in source_files(bundle.root, source):
                payload[path.relative_to(bundle.root).as_posix()] = (
                    path.read_bytes(),
                    0o755 if path.stat().st_mode & 0o111 else 0o644,
                )
    return payload


def build_bundle(bundle: Bundle, output: Path) -> dict[str, str | int]:
    output = output.absolute()
    # An output inside the source can become part of a future skill payload.
    if output.resolve().is_relative_to(bundle.root):
        raise BundleError("archive output must be outside the bundle source")
    payload = _payload(bundle)
    if "inventory.json" in payload:
        raise BundleError("inventory.json is reserved for archive metadata")
    inventory = {
        name: {"sha256": hashlib.sha256(data).hexdigest(), "mode": mode}
        for name, (data, mode) in sorted(payload.items())
    }
    payload["inventory.json"] = ((json.dumps(inventory, sort_keys=True, indent=2) + "\n").encode(), 0o644)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing artifacts from accidental replacement.
    with output.open("xb") as stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, (data, mode) in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            archive.writestr(info, data)
    return {"path": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "files": len(payload)}


def plan_bundle(bundle: Bundle, preset: str | None = None) -> dict[str, object]:
    if preset is not None and preset not in bundle.presets:
        raise BundleError(f"unknown preset: {preset}")
    selected = set(bundle.presets[preset]) if preset else {asset.id for asset in bundle.assets}
    payload = _payload(bundle)
    files = set()
    if bundle.constitution is not None:
        files.add("AGENTS.md")
    if bundle.constitution is not None or any(
        asset.kind == "instruction" and asset.id in selected for asset in bundle.assets
    ):
        skill_files = {
            f"{source}/SKILL.md"
            for asset in bundle.assets
            if asset.kind == "skill" and asset.id in selected
            for _, source in asset.sources
        }
        for name in skill_files:
            data, mode = payload[name]
            payload[name] = (prepend_context(data, bundle.name), mode)
    assets = []
    for asset in bundle.assets:
        if asset.id not in selected:
            continue
        assets.append({"id": asset.id, "kind": asset.kind, "variants": [target for target, _ in asset.sources]})
        for _, source in asset.sources:
            files.update(path.relative_to(bundle.root).as_posix() for path in source_files(bundle.root, source))
    return {
        "bundle": bundle.name,
        "version": bundle.version,
        "preset": preset,
        "scope": "managed inventory only; native projection and installation are not implemented",
        "assets": assets,
        "files": [
            {
                "source": name,
                "destination": f".devkit/managed/{bundle.name}/{name}",
                "sha256": hashlib.sha256(payload[name][0]).hexdigest(),
                "mode": payload[name][1],
            }
            for name in sorted(files)
        ],
    }
