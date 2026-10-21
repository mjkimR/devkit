"""Exact, non-executing retrieval of a synchronized playbook."""

from __future__ import annotations

import hashlib
from pathlib import Path

from devkit.advisory import ExitCode
from devkit_core.base.errors import ArgumentError

from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.distribution.models.errors import SelectionError
from devkit_dist.features.distribution.models.results import PlaybookResult
from devkit_dist.features.distribution.services.bundles.common import SLUG, read_frontmatter
from devkit_dist.features.distribution.services.bundles.playbooks import read_playbook_header
from devkit_dist.features.distribution.services.installation.local_render import LocalRenderStaleError
from devkit_dist.features.distribution.services.installation.overrides import override_rel
from devkit_dist.features.distribution.services.installation.reading import (
    read_owned,
    read_synchronized,
    synchronized_project_root,
)
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, RECEIPT_PATH


def validate_playbook_id(selector: str) -> tuple[str, str]:
    """Validate the exact selector before any workspace resolution, including at CLI boundaries."""
    parts = selector.split("/")
    if len(parts) != 2 or not all(SLUG.fullmatch(part) for part in parts):
        raise ArgumentError(
            f"playbook: expected <bundle>/<playbook> lowercase slugs, not {selector!r}",
            target_files=["PLAYBOOK_ID"],
            fix="Use an exact <bundle>/<playbook> selector",
        )
    return parts[0], parts[1]


def get_playbook(start: Path, selector: str) -> PlaybookResult:
    """Return effective bytes as validated metadata and complete body, without following the procedure."""
    bundle, asset_id = validate_playbook_id(selector)
    root = synchronized_project_root(start)
    with project_lock(root, shared=True):
        try:
            receipt = read_synchronized(root)
        except LocalRenderStaleError as exc:
            # Exact retrieval could not run; retain the shared code and recovery advisory.
            exc.exit_code = ExitCode.ERROR
            raise
        prefix = f"{MANAGED_PATH}/{bundle}/"
        if receipt.file(prefix + "bundle.toml") is None:
            raise SelectionError(f"bundle is not synchronized: {bundle}", fix="devkit list")
        matches = [asset for asset in receipt.assets("playbook") if asset.bundle == bundle and asset.id == asset_id]
        if not matches:
            raise SelectionError(
                f"playbook is not synchronized: {selector}",
                "Inspect explicit bundle and preset selection",
                fix="devkit list",
            )
        if len(matches) != 1 or len(matches[0].entrypoints) != 1:
            raise ReceiptError(f"{RECEIPT_PATH}: expected exactly one playbook entrypoint for {selector}")
        asset = matches[0]
        name = asset.entrypoints[0]
        if name not in asset.paths or not name.startswith((prefix, override_rel(bundle, ""))):
            raise ReceiptError(f"{RECEIPT_PATH}: invalid playbook entrypoint: {name}")
        data = read_owned(root, receipt, name)
        metadata = read_playbook_header(data, name)
        text, block, _ = read_frontmatter(data, name, "playbook")
        return PlaybookResult(
            bundle,
            asset_id,
            metadata.name,
            metadata.description,
            list(metadata.aliases),
            text[block.end :],
            str(root / name),
            hashlib.sha256(data).hexdigest(),
        )
