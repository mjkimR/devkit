"""Exact, non-executing retrieval of a synchronized playbook, by asset ID or by a declared alias."""

from __future__ import annotations

import hashlib
from pathlib import Path

from devkit.advisory import ExitCode
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.distribution.models.errors import PlaybookAliasAmbiguousError, SelectionError
from devkit_dist.features.distribution.models.results import PlaybookResult
from devkit_dist.features.distribution.services.bundles.common import SLUG, read_frontmatter
from devkit_dist.features.distribution.services.bundles.playbooks import PlaybookHeader, read_playbook_header
from devkit_dist.features.distribution.services.installation.local_render import LocalRenderStaleError
from devkit_dist.features.distribution.services.installation.overrides import override_rel
from devkit_dist.features.distribution.services.installation.reading import (
    read_owned,
    read_synchronized,
    synchronized_project_root,
)
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION, devkit_command
from devkit_dist.features.project.models.receipt import AssetRecord, Receipt
from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, RECEIPT_PATH


def validate_playbook_id(selector: str) -> tuple[str, str]:
    """Validate the exact selector before any workspace resolution, including at CLI boundaries."""
    parts = selector.split("/")
    if len(parts) != 2 or not all(SLUG.fullmatch(part) for part in parts):
        raise ArgumentError(
            f"playbook: expected <bundle>/<playbook> lowercase slugs, not {selector!r}",
            target_files=["PLAYBOOK_ID"],
            fix=devkit_command("list"),
        )
    return parts[0], parts[1]


class GetPlaybook(BaseUseCase):
    """Execute the get playbook application operation."""

    def execute(self, start: Path, selector: str) -> PlaybookResult:
        """Return effective bytes as validated metadata and complete body, without following the procedure.

        An exact asset ID always wins. Otherwise the selector is an alias: it resolves only when exactly one effective
        playbook header of the bundle (overrides included) declares it, and the result names the canonical ``id`` and
        the ``alias`` used; several declarers raise ``PLAYBOOK_ALIAS_AMBIGUOUS``.
        """
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
                raise SelectionError(
                    f"bundle is not synchronized: {bundle}", fix=devkit_command("list"), target_files=["PLAYBOOK_ID"]
                )
            playbooks = [asset for asset in receipt.assets("playbook") if asset.bundle == bundle]
            matches = [asset for asset in playbooks if asset.id == asset_id]
            alias: str | None = None
            if not matches:
                # The alias path reads every effective header of the bundle; an exact ID is served without it.
                declared = [
                    asset for asset in playbooks if asset_id in _header(root, receipt, asset, bundle)[1].aliases
                ]
                if len(declared) > 1:
                    names = ", ".join(f"{bundle}/{asset.id}" for asset in declared)
                    raise PlaybookAliasAmbiguousError(
                        f"playbook alias {selector} is declared by {len(declared)} playbooks: {names}",
                        target_files=[f"{bundle}/{asset.id}" for asset in declared],
                        fix="Name the playbook by its exact asset ID, or keep the alias on one playbook "
                        f"(edit the override or the bundle source, then `{AGENT_INVOCATION} sync`)",
                    )
                if not declared:
                    raise SelectionError(
                        f"playbook is not synchronized: {selector}",
                        "Inspect explicit bundle and preset selection",
                        fix=devkit_command("list"),
                        target_files=["PLAYBOOK_ID"],
                    )
                matches, alias = declared, asset_id
            if len(matches) != 1:
                raise ReceiptError(f"{RECEIPT_PATH}: expected exactly one playbook entrypoint for {selector}")
            asset = matches[0]
            name, metadata, data = _header(root, receipt, asset, bundle)
            text, block, _ = read_frontmatter(data, name, "playbook")
            return PlaybookResult(
                bundle,
                asset.id,
                metadata.name,
                metadata.description,
                list(metadata.aliases),
                text[block.end :],
                str(root / name),
                hashlib.sha256(data).hexdigest(),
                alias,
            )


def _header(root: Path, receipt: Receipt, asset: AssetRecord, bundle: str) -> tuple[str, PlaybookHeader, bytes]:
    """The effective entrypoint of a playbook asset, its validated header and its bytes."""
    selector = f"{bundle}/{asset.id}"
    if len(asset.entrypoints) != 1:
        raise ReceiptError(f"{RECEIPT_PATH}: expected exactly one playbook entrypoint for {selector}")
    name = asset.entrypoints[0]
    if name not in asset.paths or not name.startswith((f"{MANAGED_PATH}/{bundle}/", override_rel(bundle, ""))):
        raise ReceiptError(f"{RECEIPT_PATH}: invalid playbook entrypoint: {name}")
    data = read_owned(root, receipt, name)
    return name, read_playbook_header(data, name), data
