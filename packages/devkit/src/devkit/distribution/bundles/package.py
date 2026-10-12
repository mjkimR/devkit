"""``devkit bundle build``: a deterministic ZIP archive of a bundle source with a hashed inventory."""

from __future__ import annotations

import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path

from devkit.core.errors import ArgumentError
from devkit.distribution.bundles.manifest import Bundle, source_files
from devkit.distribution.content import Content, json_content, normal_mode, sha256
from devkit.distribution.errors import BundleError

INVENTORY = "inventory.json"


@dataclass(frozen=True)
class BuildResult:
    """The archive written: its path, SHA-256 and number of files (the inventory included)."""

    path: Path
    sha256: str
    files: int

    def to_dict(self) -> dict[str, object]:
        return {"path": str(self.path), "sha256": self.sha256, "files": self.files}


def _payload(bundle: Bundle) -> dict[str, Content]:
    """Archive path -> content (normalized mode) for the manifest, constitution and every source file."""
    payload = {"bundle.toml": Content((bundle.root / "bundle.toml").read_bytes(), 0o644)}
    if bundle.constitution is not None:
        payload["AGENTS.md"] = Content(bundle.constitution.read_bytes(), 0o644)
    for asset in bundle.assets:
        for _, source in asset.sources:
            for path in source_files(bundle.root, source):
                payload[path.relative_to(bundle.root).as_posix()] = Content(
                    path.read_bytes(), normal_mode(path.stat().st_mode)
                )
    return payload


def build_bundle(bundle: Bundle, output: Path) -> BuildResult:
    output = output.absolute()
    # An output inside the source can become part of a future skill payload.
    if output.resolve().is_relative_to(bundle.root):
        raise ArgumentError(
            "archive output must be outside the bundle source",
            target_files=["--output"],
            fix="Pass an --output path outside the bundle directory",
        )
    payload = _payload(bundle)
    if INVENTORY in payload:
        raise BundleError(f"{INVENTORY} is reserved for archive metadata")
    inventory = {
        name: {"sha256": sha256(content.data), "mode": content.mode} for name, content in sorted(payload.items())
    }
    payload[INVENTORY] = json_content(inventory)
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
            for name, content in sorted(payload.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | content.mode) << 16
                archive.writestr(info, content.data)
    except BaseException:
        # A partial archive would block the next build (exclusive creation); it was never complete.
        output.unlink(missing_ok=True)
        raise
    return BuildResult(output, sha256(output.read_bytes()), len(payload))
