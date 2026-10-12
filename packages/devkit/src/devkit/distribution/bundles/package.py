from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path

from ..errors import ArgumentError, BundleError
from .manifest import Bundle, source_files


def _payload(bundle: Bundle) -> dict[str, tuple[bytes, int]]:
    """Archive path -> (bytes, normalized mode) for the manifest, constitution and every source file."""
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
        raise ArgumentError(
            "archive output must be outside the bundle source",
            target_files=["--output"],
            fix="Pass an --output path outside the bundle directory",
        )
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
    try:
        stream = output.open("xb")
    except FileExistsError as exc:
        raise ArgumentError(
            f"archive already exists: {output}",
            target_files=["--output"],
            fix="Pass a new --output path; devkit never replaces an existing archive",
        ) from exc
    try:
        with stream, zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, (data, mode) in sorted(payload.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | mode) << 16
                archive.writestr(info, data)
    except BaseException:
        # A partial archive would block the next build (exclusive creation); it was never complete.
        output.unlink(missing_ok=True)
        raise
    return {"path": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "files": len(payload)}
