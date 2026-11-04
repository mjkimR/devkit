"""``devkit get-context``: a bundle's constitution and instruction header catalog."""

from __future__ import annotations

from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_dist.base.errors import ReceiptError
from devkit_dist.features.distribution.models.errors import BundleError, SelectionError
from devkit_dist.features.distribution.models.results import (
    ContextDocument,
    ContextElsewhere,
    ContextResult,
    Instruction,
)
from devkit_dist.features.distribution.models.settings import SLUG
from devkit_dist.features.distribution.services.bundles.context_documents import (
    count_documents,
    declared_directory,
    list_documents,
    provided_directories,
)
from devkit_dist.features.distribution.services.bundles.instructions import read_instruction_header
from devkit_dist.features.distribution.services.installation.discovery import discover_bundles
from devkit_dist.features.distribution.services.installation.overrides import override_rel
from devkit_dist.features.distribution.services.installation.reading import (
    read_owned,
    read_synchronized,
    synchronized_project_root,
)
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.project.models.invocation import devkit_command
from devkit_dist.features.project.repositories.receipt import MANAGED_PATH, RECEIPT_PATH


def _select_command(bundle: str) -> str:
    """The command that makes ``bundle`` synchronized: ``add`` for an installed bundle with a default preset, else
    ``list``, which tells a typo from a bundle whose preset has to be named.

    Discovery runs on this error path only; a successful read uses the receipt alone.
    """
    try:
        with discover_bundles() as installed:
            item = next((item for item in installed if item.bundle.name == bundle), None)
    except AdvisoryError:  # an unusable package must not replace the selection error
        item = None
    if item is not None and item.bundle.default_preset is not None:
        return devkit_command(f"add {bundle}")
    return devkit_command("list")


def _working_directory(root: Path, working: Path | None) -> Path:
    """``working`` resolved, an existing directory that is ``root`` or under it; ``root`` for ``None``.

    Checked before the project lock is taken, so a bad ``--for`` never waits for a sync.
    """
    if working is None:
        return root
    fix = "Pass an existing directory inside the project to --for"
    try:
        path = working.resolve()
        is_dir = path.is_dir()
    except (RuntimeError, OSError) as exc:  # Python 3.12 raises RuntimeError for a symlink loop
        raise ArgumentError(f"--for {working}: cannot be resolved: {exc}", target_files=["--for"], fix=fix) from exc
    if not is_dir:
        raise ArgumentError(f"--for {working}: not an existing directory", target_files=["--for"], fix=fix)
    base = root.resolve()
    if path != base and base not in path.parents:
        raise ArgumentError(f"--for {working}: not inside the project {root}", target_files=["--for"], fix=fix)
    return path


def _context_documents(
    root: Path, working: Path, directory: str | None
) -> tuple[list[ContextDocument], list[ContextElsewhere], list[AdvisoryError]]:
    """The documents of the declared ``directory`` merged with those the providers list for ``working``, the
    directories they only mention, and the providers' warnings; nothing runs without a declared directory."""
    if directory is None:
        return [], [], []
    provided, notices = provided_directories(root, working, directory)
    listed = {directory, *provided.listed}
    by_path = {item.path: item for rel in listed for item in list_documents(root, rel)}
    documents = [by_path[path] for path in sorted(by_path)]
    elsewhere: list[ContextElsewhere] = []
    for rel in sorted(set(provided.mentioned) - listed):
        count = count_documents(root, rel)
        if count is not None:
            elsewhere.append(ContextElsewhere(str(root / rel), count))
    return documents, sorted(elsewhere, key=lambda item: item.path), notices


class GetContext(BaseUseCase):
    """Execute the get context application operation."""

    def execute(self, start: Path, bundle: str, working: Path | None = None) -> ContextResult:
        """Read the synchronized constitution and instruction headers of the project containing ``start``, and the
        titles and summaries of the context documents the bundle's manifest declares and the installed providers
        list for ``working`` (an existing directory inside the project; the root when ``None``), with the
        directories they only mention and their warnings.

        Bodies are never returned.
        """
        if not SLUG.fullmatch(bundle):
            raise ArgumentError(f"bundle: expected a lowercase slug, not {bundle!r}", target_files=["BUNDLE_NAME"])
        root = synchronized_project_root(start)
        working = _working_directory(root, working)
        with project_lock(root, shared=True):
            receipt = read_synchronized(root)
            prefix = f"{MANAGED_PATH}/{bundle}/"
            if receipt.file(prefix + "bundle.toml") is None:
                synchronized = sorted({package.bundle for package in receipt.packages})
                raise SelectionError(
                    f"bundle is not synchronized: {bundle}",
                    f"synchronized bundles: {', '.join(synchronized) or 'none'}",
                    fix=_select_command(bundle),
                    target_files=["BUNDLE_NAME"],
                )
            constitution_path = prefix + "AGENTS.md"
            constitution = None
            if receipt.file(constitution_path) is not None:
                try:
                    constitution = read_owned(root, receipt, constitution_path).decode("utf-8")
                except UnicodeError as exc:
                    raise BundleError(
                        f"context file must be UTF-8: {constitution_path}", target_files=[constitution_path]
                    ) from exc
            paths = {name for asset in receipt.assets("instruction") if asset.bundle == bundle for name in asset.paths}
            instructions: list[Instruction] = []
            for name in sorted(paths):
                if not (name.startswith(prefix) or name.startswith(override_rel(bundle, ""))):
                    raise ReceiptError(f"{RECEIPT_PATH}: instruction outside bundle {bundle}: {name}")
                header = read_instruction_header(read_owned(root, receipt, name), name)
                instructions.append(Instruction(str(root / name), header))
            manifest_path = prefix + "bundle.toml"
            directory = declared_directory(read_owned(root, receipt, manifest_path), manifest_path)
            documents, elsewhere, notices = _context_documents(root, working, directory)
            return ContextResult(bundle, constitution, instructions, documents, elsewhere, notices)
