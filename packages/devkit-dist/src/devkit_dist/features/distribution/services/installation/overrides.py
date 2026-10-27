"""Project overrides: which file a deployment reads, and how drift behind an override is tracked.

An override is a project-owned replacement for upstream asset files under
``.devkit/overrides/<bundle>/<path in the bundle>``. Tracking is per asset and
covers every upstream file of it: the receipt records a digest over all of
them (``asset_digest``) when the override is first seen, and a later sync
whose upstream digest differs reports drift, whichever file changed. The
commands that create, review, accept and remove overrides are in
``override_commands``.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from devkit_dist.features.distribution.models.content import sha256
from devkit_dist.features.distribution.models.drift import Drift
from devkit_dist.features.distribution.services.bundles.manifest import Asset, Bundle, source_files
from devkit_dist.features.distribution.services.bundles.templates import output_path
from devkit_dist.features.distribution.services.installation.workspace import BASELINE, checked_path
from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, OVERRIDES_PATH, OverrideRecord


def override_rel(bundle: str, rel: str) -> str:
    """Workspace-relative override path of a file at ``rel`` in ``bundle``."""
    return f"{OVERRIDES_PATH}/{bundle}/{rel}"


def baseline_rel(bundle: str, rel: str) -> str:
    return f"{BASELINE}/{bundle}/{rel}"


def has_override(root: Path | None, bundle: str, rel: str) -> bool:
    """Whether the project overrides ``rel`` of ``bundle``.

    A symlink anywhere on the override path (``.devkit/overrides`` itself, the
    bundle directory, the file) is ``UnsafeWorkspaceError``: an override is
    project content and is never read from outside the project.
    """
    if root is None:
        return False
    return checked_path(root, override_rel(bundle, rel)).is_file()


def resolve_source(root: Path | None, bundle: Bundle, rel: str) -> tuple[Path, str]:
    """The file a deployment reads for ``rel`` and the workspace path it cites: the override, or the managed copy."""
    if has_override(root, bundle.name, rel):
        assert root is not None
        return root / override_rel(bundle.name, rel), override_rel(bundle.name, rel)
    return bundle.root / rel, f"{MANAGED_PATH}/{bundle.name}/{rel}"


def consumer_path(root: Path | None, bundle: Bundle, rel: str) -> str:
    if rel.endswith(".md.jinja"):
        return f"{MANAGED_PATH}/{bundle.name}/{output_path(rel)}"
    return resolve_source(root, bundle, rel)[1]


def asset_files(bundle: Bundle, asset: Asset) -> list[str]:
    """Bundle-relative paths of every upstream file of ``asset``, sorted and unique."""
    return sorted(
        {
            path.relative_to(bundle.root).as_posix()
            for _, source in asset.sources
            for path in source_files(bundle.root, source)
        }
    )


def primary_path(bundle: Bundle, asset: Asset) -> str:
    """The path that names an asset in reports: ``SKILL.md`` of a skill directory, else its first source."""
    source = asset.sources[0][1]
    for name in ("SKILL.md", "SKILL.md.jinja"):
        if (bundle.root / source / name).is_file():
            return f"{source}/{name}"
    return source


def asset_digest(files: Iterable[tuple[str, bytes]]) -> str:
    """SHA-256 over ``path NUL sha256`` lines of every file, sorted by path."""
    lines = sorted(f"{rel}\0{sha256(data)}\n" for rel, data in files)
    return sha256("".join(lines).encode())


def upstream_digest(bundle: Bundle, asset: Asset) -> str:
    return asset_digest((rel, (bundle.root / rel).read_bytes()) for rel in asset_files(bundle, asset))


def record_source(record: OverrideRecord) -> str | None:
    """The bundle-relative source a record names: a skill's directory for its ``SKILL.md``, else the path itself;
    ``None`` when that is the bundle root, which holds every override of the bundle.

    It locates the override of an asset the installed bundle no longer has, whose upstream files are unknown.
    """
    path = PurePosixPath(record.relative_path)
    source = path.parent.as_posix() if path.name in ("SKILL.md", "SKILL.md.jinja") else record.relative_path
    return None if source in ("", ".") else source


def record_overridden(root: Path, bundle: str, record: OverrideRecord) -> bool:
    """Whether any file remains under the override path of ``record`` (see ``record_source``); for a record at the
    bundle root, under the bundle's override directory."""
    source = record_source(record)
    path = root / (override_rel(bundle, source) if source is not None else f"{OVERRIDES_PATH}/{bundle}")
    return path.is_file() or (path.is_dir() and any(p.is_file() for p in path.rglob("*")))


def overridden_files(root: Path | None, bundle: Bundle, asset: Asset) -> list[str]:
    return [rel for rel in asset_files(bundle, asset) if has_override(root, bundle.name, rel)]


def track_override(
    root: Path | None, bundle: Bundle, asset: Asset, previous: OverrideRecord | None
) -> tuple[OverrideRecord | None, Drift | None]:
    """The receipt record for an overridden asset (``None`` when nothing is overridden) and its drift.

    The baseline is carried over from ``previous``; a first sighting takes the
    current upstream digest as the baseline.
    """
    if root is None or asset.seeded:
        return None, None
    overridden = overridden_files(root, bundle, asset)
    if not overridden:
        return None, None
    current = upstream_digest(bundle, asset)
    baseline = previous.baseline_upstream_sha256 if previous is not None else current
    record = OverrideRecord(
        kind=asset.kind,
        relative_path=primary_path(bundle, asset),
        baseline_upstream_sha256=baseline,
        override_sha256=asset_digest((rel, (root / override_rel(bundle.name, rel)).read_bytes()) for rel in overridden),
    )
    drift = Drift(bundle.name, asset.id, record.relative_path) if current != baseline else None
    return record, drift
