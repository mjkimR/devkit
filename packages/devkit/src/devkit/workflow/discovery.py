"""Finding workflow definitions: the project's ``definitions_dir`` plus synchronized workflow assets."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from devkit.core.receipt import Receipt, load_receipt
from devkit.workflow.definition import DefinitionError, WorkflowDocument, load

WORKFLOW_KIND = "workflow"


def _load_paths(paths: Iterable[Path]) -> tuple[list[WorkflowDocument], list[str]]:
    docs: list[WorkflowDocument] = []
    errors: list[str] = []
    for path in paths:
        try:
            docs.append(load(path))
        except DefinitionError as exc:
            errors.append(str(exc))
    return docs, errors


def load_all(definitions_dir: Path) -> tuple[list[WorkflowDocument], list[str]]:
    """Load every ``*.md`` definition in a directory; unreadable files are returned as error strings."""
    if not definitions_dir.is_dir():
        return [], []
    return _load_paths(sorted(definitions_dir.glob("*.md")))


def managed_definition_paths(workspace_root: Path, receipt: Receipt | None) -> tuple[list[Path], list[str]]:
    """Workflow assets recorded in the installation receipt, and the recorded files missing from disk.

    ``entrypoints`` name the definition files; an asset without them
    contributes every ``.md`` path.
    """
    paths: set[Path] = set()
    errors: list[str] = []
    for asset in receipt.assets(WORKFLOW_KIND) if receipt is not None else ():
        chosen = [r for r in asset.entrypoints if r.endswith(".md")] or list(asset.files(".md"))
        for rel in chosen:
            path = workspace_root / rel
            if path.is_file():
                paths.add(path)
            else:
                errors.append(f"synchronized workflow {rel} is missing from the working tree (run devkit sync)")
    return sorted(paths), errors


def discover(
    workspace_root: Path, definitions_dir: Path, receipt: Receipt | None = None
) -> tuple[list[WorkflowDocument], list[str]]:
    """Project definitions plus workflow assets synchronized by devkit.

    A project definition shadows a synchronized one with the same id, so a
    repository can adapt a distributed workflow without editing managed files.
    ``receipt`` defaults to the workspace's installation receipt; a malformed
    receipt raises ``devkit.core.errors.ReceiptError``.
    """
    if receipt is None:
        receipt = load_receipt(workspace_root)
    local, errors = load_all(definitions_dir)
    managed_paths, missing = managed_definition_paths(workspace_root, receipt)
    managed, managed_errors = _load_paths(managed_paths)
    local_ids = {d.id for d in local}
    docs = local + [d for d in managed if d.id not in local_ids]
    return docs, errors + missing + managed_errors


def select(docs: Iterable[WorkflowDocument], workflow_id: str, errors: Iterable[str], where: str) -> WorkflowDocument:
    """The single document whose id matches; zero or several matches are errors."""
    matches = [d for d in docs if d.id == workflow_id]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        errors = list(errors)
        hint = f" ({'; '.join(errors)})" if errors else ""
        raise DefinitionError(f"no workflow with id {workflow_id!r} under {where}{hint}")
    paths = ", ".join(d.path.as_posix() for d in matches if d.path)
    raise DefinitionError(f"workflow id {workflow_id!r} is defined more than once: {paths}")


def find(definitions_dir: Path, workflow_id: str, workspace_root: Path | None = None) -> WorkflowDocument:
    """The single definition whose id matches, from ``definitions_dir`` (plus the receipt with ``workspace_root``)."""
    docs, errors = discover(workspace_root, definitions_dir) if workspace_root else load_all(definitions_dir)
    where = definitions_dir.as_posix() + (" or the devkit installation receipt" if workspace_root else "")
    return select(docs, workflow_id, errors, where)


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


def resolve(definitions_dir: Path, ref: str, workspace_root: Path | None = None) -> WorkflowDocument:
    """``ref`` is a workflow id, or a path to a definition file (relative to ``workspace_root`` when given)."""
    path = definition_path(ref, workspace_root)
    if path is not None:
        if not path.is_file():
            raise DefinitionError(f"no definition file {ref}")
        return load(path)
    return find(definitions_dir, ref, workspace_root)
