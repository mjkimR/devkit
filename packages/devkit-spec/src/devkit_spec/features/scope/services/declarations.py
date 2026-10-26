"""Shared scope declaration parsing, independent of filesystem or pinned-tree storage."""

from __future__ import annotations

from typing import Any

from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import parse

from devkit_spec.base.errors import (
    EntrypointsPathError,
    ProposalNotFoundError,
    ScopeInputInvalidError,
    ScopeSpecNotFoundError,
)
from devkit_spec.features.entrypoints import (
    Reason,
    classify_boundary,
    covers,
    entrypoint_bearing,
    feedback_file,
    normalize,
    parse_boundaries,
)
from devkit_spec.features.scope.models.model import Diff, Granularity, ScopePath, ScopeSet, Source, Stage, Unresolved
from devkit_spec.features.scope.models.source import InputPath

PROPOSAL_FILE = "proposal.md"
PROPOSALS = "docs/proposals"
TARGET_DOCS = "target-docs.md"
SKELETON_MARKER = "<!-- devkit:skeleton -->"
RECONCILE = "reconcile.md"
TASKS = "tasks.md"
SPEC = "spec.md"
WAIVED = "waived"


def _is_placeholder(raw: str) -> bool:
    stripped = raw.strip()
    return len(stripped) >= 2 and stripped.startswith("<") and stripped.endswith(">")


def kind_of(root: InputPath, path: str) -> Granularity:
    """Whether the workspace-relative ``path`` is a file or a directory of the working tree, else ``unknown``."""
    target = root / path
    if target.is_dir():
        return Granularity.DIR
    if target.is_file():
        return Granularity.FILE
    return Granularity.UNKNOWN


def _frontmatter(path: InputPath, relative: str) -> dict[str, Any] | None:
    """The frontmatter of ``path``; ``None`` when it has none; ``ScopeInputInvalidError`` when unreadable."""
    try:
        return parse(path.read_text(encoding="utf-8")).data
    except (OSError, UnicodeDecodeError) as exc:
        raise ScopeInputInvalidError(f"cannot read {relative}: {exc}", target_files=[relative]) from exc
    except FrontmatterError as exc:
        raise ScopeInputInvalidError(f"cannot read {relative}: {exc.message}", target_files=[relative]) from exc


def _declared_id(path: InputPath) -> str:
    """The ``id`` of a document's frontmatter, ``""`` when it has none or cannot be read."""
    try:
        data = parse(path.read_text(encoding="utf-8")).data or {}
    except (OSError, UnicodeDecodeError, FrontmatterError):
        return ""
    value = data.get("id")
    return value.strip() if isinstance(value, str) else ""


def _targets(path: InputPath, relative: str) -> list[tuple[str, str]] | None:
    """``(file, resolution)`` of each target; ``None`` when the file does not exist or declares no ``targets``."""
    if not path.is_file():
        return None
    data = _frontmatter(path, relative) or {}
    if "targets" not in data:
        return None
    value = data["targets"] or []
    if not isinstance(value, list):
        raise ScopeInputInvalidError(f"cannot read {relative}: targets must be a list", target_files=[relative])
    targets = []
    for position, entry in enumerate(value, 1):
        if not isinstance(entry, dict) or not isinstance(entry.get("file", ""), str):
            raise ScopeInputInvalidError(
                f"cannot read {relative}: targets[{position}] must be a mapping with a string file",
                target_files=[relative],
            )
        resolution = entry.get("resolution")
        targets.append((entry.get("file", "").strip(), resolution.strip() if isinstance(resolution, str) else ""))
    return targets


def _entrypoints(root: InputPath, file: str) -> list[str]:
    try:
        data = parse((root / file).read_text(encoding="utf-8")).data or {}
    except (OSError, UnicodeDecodeError, FrontmatterError):
        return []
    value = data.get("entrypoints")
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _add_doc_targets(
    root: InputPath, scope: ScopeSet, targets: list[tuple[str, str]], stage: Stage, *, candidates: bool = True
) -> None:
    """Record document targets and, with ``candidates``, the code candidates their entrypoints provide.

    A waived target, an invalid path, a planned document (not in the working tree; it still counts as a document,
    so a shared planned path overlaps) and a capability or use case without entrypoints are unresolved, also without
    ``candidates``.
    """
    seen_docs = {path.path for path in scope.docs}
    seen_code = {path.path for path in scope.code}
    for raw, resolution in targets:
        if not raw:
            continue
        if resolution.lower() == WAIVED:
            scope.unresolved.append(Unresolved(raw, "waived", Source.DECLARED_DOC))
            continue
        try:
            file = normalize(raw)
        except EntrypointsPathError:
            scope.unresolved.append(Unresolved(raw, "invalid-path", Source.DECLARED_DOC))
            continue
        if file in seen_docs:
            continue
        seen_docs.add(file)
        kind = kind_of(root, file)
        scope.docs.append(ScopePath(file, kind, Source.DECLARED_DOC, stage))
        if kind is Granularity.UNKNOWN:
            scope.unresolved.append(Unresolved(file, "planned-doc", Source.DECLARED_DOC))
            continue
        if not entrypoint_bearing(file):
            continue
        entries = _entrypoints(root, file)
        if not entries:
            scope.unresolved.append(Unresolved(file, "no-entrypoints", Source.CANDIDATE))
            continue
        if not candidates:
            continue
        for entry in entries:
            try:
                code = normalize(entry)
            except EntrypointsPathError:
                continue
            if code not in seen_code:
                seen_code.add(code)
                scope.code.append(ScopePath(code, kind_of(root, code), Source.CANDIDATE, stage))
    scope.docs.sort(key=lambda path: path.path)
    scope.code.sort(key=lambda path: path.path)


def _diff(blueprint: list[tuple[str, str]], reconcile: list[tuple[str, str]]) -> list[Diff]:
    def paths(targets: list[tuple[str, str]]) -> set[str]:
        found = set()
        for raw, resolution in targets:
            if resolution.lower() == WAIVED:
                continue
            try:
                found.add(normalize(raw))
            except EntrypointsPathError:
                continue
        return found

    planned, reconciled = paths(blueprint), paths(reconcile)
    diff = [Diff(path, "target-docs") for path in planned - reconciled]
    diff += [Diff(path, "reconcile") for path in reconciled - planned]
    return sorted(diff, key=lambda item: (item.path, item.side))


def from_proposal(root: InputPath, slug: str) -> ScopeSet:
    """The ``prop``-stage scope of proposal ``slug`` (a ``PROP-`` prefix is accepted).

    Raises ``ProposalNotFoundError`` when no bundle or single-file proposal has the slug.
    """
    clean = slug
    bundle = root / PROPOSALS / f"PROP-{clean}"
    single = root / PROPOSALS / f"PROP-{clean}.md"
    if (bundle / PROPOSAL_FILE).is_file():
        anchor = bundle / PROPOSAL_FILE
    elif single.is_file():
        anchor = single
    else:
        raise ProposalNotFoundError(f"no proposal has the slug {clean!r}", target_files=[f"{PROPOSALS}/PROP-{clean}"])
    scope = ScopeSet(id=_declared_id(anchor) or f"PROP-{clean}")
    relative = f"{PROPOSALS}/PROP-{clean}/{TARGET_DOCS}"
    blueprint = bundle / TARGET_DOCS
    targets = _targets(blueprint, relative)
    if targets is None:
        reason = "no-targets" if blueprint.is_file() else "missing-target-docs"
        scope.unresolved.append(Unresolved(TARGET_DOCS, reason, Source.DECLARED_DOC))
        return scope
    _add_doc_targets(root, scope, targets, Stage.PROP)
    return scope


def _external_feedback(root: InputPath, spec_dir: str, raw: str) -> str | None:
    """The normalized ``raw`` when it names a feedback file of a spec bundle other than ``spec_dir`` and is no
    directory of the working tree, else ``None``."""
    try:
        path, unit = normalize(raw.strip()), normalize(spec_dir)
    except EntrypointsPathError:
        return None
    if not feedback_file(path) or covers(unit, path) or kind_of(root, path) is Granularity.DIR:
        return None
    return path


def from_spec(root: InputPath, spec_dir: str) -> ScopeSet:
    """The ``spec``-stage scope of the bundle at the workspace-relative ``spec_dir`` (declarations only).

    Declared code paths of ``tasks.md`` replace the targets' entrypoint candidates; without any, the candidates stay.
    A declared feedback file of another bundle is declared code too, but never replaces the candidates.

    Raises ``ScopeSpecNotFoundError`` when it is not a directory and ``ScopeInputInvalidError`` when an input
    cannot be read.
    """
    base = root / spec_dir
    if not base.is_dir():
        raise ScopeSpecNotFoundError(f"spec bundle not found: {spec_dir}", target_files=[spec_dir])
    scope = ScopeSet(id=_declared_id(base / SPEC) or base.name)
    declares_code = False
    tasks_path = base / TASKS
    if not tasks_path.is_file():
        scope.unresolved.append(Unresolved(TASKS, "missing-tasks", Source.DECLARED_CODE))
    else:
        try:
            text = tasks_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            relative = f"{spec_dir}/{TASKS}"
            raise ScopeInputInvalidError(f"cannot read {relative}: {exc}", target_files=[relative]) from exc
        if SKELETON_MARKER in text:
            scope.unresolved.append(Unresolved(TASKS, "missing-tasks", Source.DECLARED_CODE))
        else:
            seen: set[str] = set()
            for task in parse_boundaries(text):
                for raw in task.values:
                    if _is_placeholder(raw):
                        scope.unresolved.append(Unresolved(raw, "not-a-path", Source.DECLARED_CODE))
                        continue
                    code, reason = classify_boundary(raw)
                    if code is None and reason is Reason.EXCLUDED_TREE:
                        code = _external_feedback(root, spec_dir, raw)
                    elif code is not None:
                        declares_code = True
                    if code is None:
                        scope.unresolved.append(Unresolved(raw, str(reason), Source.DECLARED_CODE))
                    elif code not in seen:
                        seen.add(code)
                        scope.code.append(ScopePath(code, kind_of(root, code), Source.DECLARED_CODE, Stage.SPEC))
    candidates = not declares_code  # declared code paths replace the entrypoint candidates; feedback files do not
    reconcile = _targets(base / RECONCILE, f"{spec_dir}/{RECONCILE}")
    blueprint = _targets(base / TARGET_DOCS, f"{spec_dir}/{TARGET_DOCS}")
    if reconcile is not None:
        _add_doc_targets(root, scope, reconcile, Stage.SPEC, candidates=candidates)
        if blueprint is not None:
            scope.diff = _diff(blueprint, reconcile)
    else:
        scope.unresolved.append(Unresolved(RECONCILE, "missing-reconcile", Source.DECLARED_DOC))
        if blueprint is not None:
            _add_doc_targets(root, scope, blueprint, Stage.PROP, candidates=candidates)
    scope.code.sort(key=lambda path: path.path)
    return scope
