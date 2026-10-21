"""Finding workflow definitions: the project's ``definitions_dir`` plus synchronized workflow assets.

Definitions that cannot be loaded are collected as ``WorkflowError``
instances (``DefinitionError``, ``WorkflowAssetMissingError``) next to the
loaded documents, never raised.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from devkit_dist.features.project.repositories.receipt import Receipt, load_receipt

from devkit_agt.features.workflow.models.definition import WorkflowDocument, parse_definition
from devkit_agt.features.workflow.models.errors import (
    DefinitionError,
    WorkflowAssetMissingError,
    WorkflowError,
    WorkflowNotFoundError,
)

WORKFLOW_KIND = "workflow"


def load_definition(path: Path) -> WorkflowDocument:
    """Read and parse the definition file at ``path``; raises ``DefinitionError`` targeting it."""
    try:
        text = path.read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        raise DefinitionError(f"{path}: {exc}", target_files=[path.as_posix()]) from exc
    try:
        return parse_definition(text, path)
    except DefinitionError as exc:
        raise DefinitionError(f"{path}: {exc}", target_files=[path.as_posix()]) from exc


def _load_paths(paths: Iterable[Path]) -> tuple[list[WorkflowDocument], list[WorkflowError]]:
    docs: list[WorkflowDocument] = []
    errors: list[WorkflowError] = []
    for path in paths:
        try:
            docs.append(load_definition(path))
        except DefinitionError as exc:
            errors.append(exc)
    return docs, errors


def load_definition_dir(definitions_dir: Path) -> tuple[list[WorkflowDocument], list[WorkflowError]]:
    """Load every ``*.md`` definition in a directory; unreadable files are returned as ``DefinitionError``s."""
    if not definitions_dir.is_dir():
        return [], []
    return _load_paths(sorted(definitions_dir.glob("*.md")))


def managed_definition_paths(workspace_root: Path, receipt: Receipt | None) -> tuple[list[Path], list[WorkflowError]]:
    """Workflow assets recorded in the installation receipt, and the recorded files missing from disk.

    ``entrypoints`` name the definition files; an asset without them
    contributes every ``.md`` path.
    """
    paths: set[Path] = set()
    errors: list[WorkflowError] = []
    for asset in receipt.assets(WORKFLOW_KIND) if receipt is not None else ():
        chosen = [r for r in asset.entrypoints if r.endswith(".md")] or list(asset.files(".md"))
        for rel in chosen:
            path = workspace_root / rel
            if path.is_file():
                paths.add(path)
            else:
                errors.append(
                    WorkflowAssetMissingError(
                        f"synchronized workflow {rel} is missing from the working tree", target_files=[rel]
                    )
                )
    return sorted(paths), errors


def discover_definitions(
    workspace_root: Path, definitions_dir: Path, receipt: Receipt | None = None
) -> tuple[list[WorkflowDocument], list[WorkflowError]]:
    """Project definitions plus workflow assets synchronized by devkit.

    A project definition shadows a synchronized one with the same id, so a
    repository can adapt a distributed workflow without editing managed files.
    ``receipt`` defaults to the workspace's installation receipt; a malformed
    receipt raises ``devkit_dist.base.errors.ReceiptError``.
    """
    if receipt is None:
        receipt = load_receipt(workspace_root)
    local, errors = load_definition_dir(definitions_dir)
    managed_paths, missing = managed_definition_paths(workspace_root, receipt)
    managed, managed_errors = _load_paths(managed_paths)
    local_ids = {d.id for d in local}
    docs = local + [d for d in managed if d.id not in local_ids]
    return docs, errors + missing + managed_errors


def select_definition(
    docs: Iterable[WorkflowDocument],
    workflow_id: str,
    errors: Iterable[WorkflowError],
    where: str,
    fix: str | None = None,
) -> WorkflowDocument:
    """The single document whose id matches.

    No match raises ``WorkflowNotFoundError`` (with ``fix`` and the load
    problems as details); several matches raise ``DefinitionError``.
    """
    matches = [d for d in docs if d.id == workflow_id]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise WorkflowNotFoundError(f"no workflow with id {workflow_id!r} under {where}", *errors, fix=fix)
    paths = ", ".join(d.path.as_posix() for d in matches if d.path)
    raise DefinitionError(f"workflow id {workflow_id!r} is defined more than once: {paths}")


def definition_path(ref: str, workspace_root: Path | None = None) -> Path | None:
    """The definition file ``ref`` names, or ``None`` when ``ref`` is an id.

    A ``.md`` reference is a path; a relative one is resolved against
    ``workspace_root`` when given.
    """
    candidate = Path(ref)
    if candidate.suffix != ".md":
        return None
    if not candidate.is_absolute() and workspace_root is not None:
        candidate = workspace_root / candidate
    return candidate


def load_definition_file(path: Path, ref: str, fix: str | None = None) -> WorkflowDocument:
    """The definition at ``path`` (named ``ref`` by the caller); a missing file is ``WorkflowNotFoundError``."""
    if not path.is_file():
        raise WorkflowNotFoundError(f"no definition file {ref}", fix=fix)
    return load_definition(path)


def resolve_definition(definitions_dir: Path, ref: str, workspace_root: Path | None = None) -> WorkflowDocument:
    """``ref`` is a workflow id, or a path to a definition file (relative to ``workspace_root`` when given).

    Ids are looked up in ``definitions_dir`` plus, with ``workspace_root``, the
    workflow assets of its installation receipt.
    """
    path = definition_path(ref, workspace_root)
    if path is not None:
        return load_definition_file(path, ref)
    if workspace_root is not None:
        docs, errors = discover_definitions(workspace_root, definitions_dir)
    else:
        docs, errors = load_definition_dir(definitions_dir)
    where = definitions_dir.as_posix() + (" or the devkit installation receipt" if workspace_root else "")
    return select_definition(docs, ref, errors, where)
