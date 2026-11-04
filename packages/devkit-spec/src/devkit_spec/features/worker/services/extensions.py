"""Structural extension evidence; project ownership and necessity remain reviewer judgments."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from devkit_agt.features.workflow.services.envelope import Envelopes
from devkit_core.core.frontmatter import parse

from devkit_spec.base.errors import WorkerScopeUnresolvedError
from devkit_spec.features.entrypoints.repositories.bundle import parse_acceptance_ids, parse_boundaries


def protected(path: str) -> bool:
    """Only recognizable protected trees/classes, independent of a project's custom protected paths."""
    parts = PurePosixPath(path).parts
    return (
        parts[0] in {".devkit", ".agents", ".claude", ".codex", ".github", "specs"}
        or path.startswith(("docs/proposals/", "docs/architecture/"))
        or "rules" in parts
        or parts[-1] in {"AGENTS.md", "CLAUDE.md", "pyproject.toml", "uv.lock", "package-lock.json"}
    )


def inspect_extensions(
    tasks_text: str, spec_text: str, loaded: Envelopes, files: set[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compare retained task annotations with all committed worker records, latest sequence winning per path."""
    tasks = parse_boundaries(tasks_text)
    annotations: dict[str, tuple[int, str, set[str]]] = {}
    for task in tasks:
        if task.annotation_errors:
            raise WorkerScopeUnresolvedError(f"Task {task.index}: {'; '.join(task.annotation_errors)}")
        for extension in task.extensions:
            path = extension.path
            pure = PurePosixPath(path)
            if (
                task.index < 1
                or path not in files
                or path != pure.as_posix()
                or pure.is_absolute()
                or ".." in pure.parts
                or any(c in path for c in "*?[]\\\x00")
            ):
                raise WorkerScopeUnresolvedError(
                    f"Task {task.index}: extension must name an exact repository file: {path}"
                )
            if path in annotations:
                raise WorkerScopeUnresolvedError(f"Duplicate extension annotation: {path}")
            annotations[path] = task.index, extension.reason, set(task.requirements)
    known_acs = parse_acceptance_ids(spec_text)
    workflow = (parse(spec_text).data or {}).get("workflow", "")
    latest = {
        e.path: (e, worker.name)
        for worker in sorted(loaded.by_kind.get("worker", []), key=lambda w: w.seq)
        if not worker.workflow or worker.workflow == workflow
        for e in worker.scope_extensions
    }
    evidence = []
    issues = []
    for path in sorted(annotations.keys() | latest.keys()):
        annotation = annotations.get(path)
        record = latest.get(path)
        if record:
            extension, source = record
            evidence.append({**extension.to_dict(), "source": source})
        if annotation is None or record is None:
            issues.append({"path": path, "cause": "Matching task annotation and worker record are required"})
            continue
        extension, _ = record
        task, reason, requirements = annotation
        if (
            extension.task != task
            or extension.reason != reason
            or not set(extension.requirements) <= requirements
            or not set(extension.requirements) <= known_acs
        ):
            issues.append({"path": path, "cause": "Task, reason or AC ownership differs from the record"})
        if protected(path):
            issues.append({"path": path, "cause": "Extension lies in a protected tree or class"})
    return evidence, {"status": "fail" if issues else "pass", **({"issues": issues} if issues else {})}
