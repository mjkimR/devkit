"""Observe one pinned source, with explicit identity, base and missing-layer evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from devkit_core.core import GitError
from devkit_core.core.frontmatter import parse

from devkit_spec.base.errors import EntrypointsPathError
from devkit_spec.features.entrypoints import normalize
from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import (
    Granularity,
    Record,
    ScopePath,
    ScopeSet,
    Source,
    Stage,
    Unresolved,
)
from devkit_spec.features.scope.models.observation import Candidate, Observation
from devkit_spec.features.scope.repositories.collection_git import optional, text
from devkit_spec.features.scope.repositories.source import FilesystemReader, ReaderPath, TreeReader
from devkit_spec.features.scope.services.declarations import from_proposal, from_spec
from devkit_spec.features.scope.services.inventory import ACTIVITY

ACTIVE = {"planned", "draft", "reviewing", "accepted", "active", "in-progress", "in_progress"}


def task_key(namespace: str, identity: str, unit: str) -> str:
    return json.dumps([namespace, identity, unit], separators=(",", ":"))


def identify(
    candidate: Candidate, reader: TreeReader | FilesystemReader, root: Path, deadline: Deadline
) -> tuple[str, dict[str, Any]]:
    unit = ""
    if candidate.branch and candidate.ref.startswith("refs/heads/"):
        marker = optional(root, "config", "--get", f"branch.{candidate.branch}.devkitUnit", deadline=deadline)
        if marker:
            # A stale marker cannot silently fall back to another unit.
            unit = normalize(marker)
    if not unit and candidate.record is not None:
        unit = normalize(candidate.record.spec)
    if not unit:
        match = ACTIVITY.fullmatch(candidate.branch)
        if not match:
            raise ValueError("identity-ambiguous")
        slug = match[1]
        # Exact ``<date>-<slug>`` only: ``dev-cleanup`` never claims ``20261001-hook-cleanup``.
        name = re.compile(rf"\d{{8}}-{re.escape(slug)}")
        if isinstance(reader, TreeReader):
            paths = list(reader.entries)
        else:
            paths = []
            # Only exact slug candidates; do not scan every historical spec in a shared checkout.
            for prefix in ("specs",):
                directory = reader.root / prefix
                if directory.is_dir():
                    for path in directory.glob(f"*/*-{slug}/spec.md"):
                        deadline.check("scope unit discovery")
                        if name.fullmatch(path.parent.name):
                            paths.append(path.relative_to(reader.root).as_posix())
            paths.append(f"docs/proposals/PROP-{slug}/proposal.md")
        specs = [
            p.rsplit("/", 1)[0]
            for p in paths
            if p.endswith("/spec.md") and name.fullmatch(PurePosixPath(p).parent.name)
        ]
        proposals = (
            [f"docs/proposals/PROP-{slug}"]
            if reader.kind(f"docs/proposals/PROP-{slug}/proposal.md") is Granularity.FILE
            else []
        )
        units = sorted(set(specs or proposals))
        if len(units) != 1:
            raise ValueError("identity-ambiguous")
        unit = units[0]
    anchor = f"{unit}/{'proposal.md' if unit.startswith('docs/proposals/') else 'spec.md'}"
    meta = parse(reader.read(anchor)).data or {}
    identity = meta.get("id")
    if not isinstance(identity, str) or not identity or meta.get("status") not in ACTIVE | {"completed", "rejected"}:
        raise ValueError("identity-ambiguous")
    match = ACTIVITY.fullmatch(candidate.branch)
    if match:
        proposal = unit.startswith("docs/proposals/")
        expected = f"{'PROP' if proposal else 'SPEC'}-{match[1]}"
        exact = re.fullmatch(rf"\d{{8}}-{re.escape(match[1])}", PurePosixPath(unit).name)
        if identity != expected or (not proposal and not exact):
            raise ValueError("identity-ambiguous")
        if candidate.branch.startswith("plan-") and not proposal:
            raise ValueError("identity-ambiguous")
    if candidate.record is not None and candidate.record.spec != unit:
        raise ValueError("identity-ambiguous")
    return unit, meta


def declarations(reader: TreeReader | FilesystemReader, unit: str) -> ScopeSet:
    path = ReaderPath(reader)
    if unit.startswith("docs/proposals/PROP-"):
        return from_proposal(path, unit.rsplit("PROP-", 1)[1])
    return from_spec(path, unit)


def select_base(
    root: Path, candidate: Candidate, explicit: str | None, record: Record | None, deadline: Deadline
) -> tuple[str, str]:
    if explicit:
        return explicit, "explicit"
    if candidate.ref.startswith("refs/heads/"):
        marked = optional(root, "config", "--get", f"branch.{candidate.branch}.devkitBase", deadline=deadline)
        if marked:
            return marked, "branch.devkitBase"
    if record is not None and record.base_ref:
        return record.base_ref, "registration"
    hints: set[str] = set()
    if candidate.ref.startswith("refs/remotes/"):
        remote = candidate.ref.split("/", 3)[2]
        head = optional(root, "symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD", deadline=deadline)
        if head:
            hints.add(head)
    # The main worktree HEAD lives in the common directory even when invoked in a linked checkout.
    common = text(root, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=deadline)
    main = optional(Path(common), "symbolic-ref", "--quiet", "HEAD", deadline=deadline)
    if main and not ACTIVITY.fullmatch(main.removeprefix("refs/heads/")):
        hints.add(main)
    resolved = {optional(root, "rev-parse", "--verify", f"{h}^{{commit}}", deadline=deadline): h for h in hints}
    resolved.pop("", None)
    if len(resolved) != 1:
        return "", "unknown"
    return next(iter(resolved.values())), "integration-hint"


def committed(root: Path, tip: str, base: str, cap: str, deadline: Deadline) -> tuple[list[str], list[Unresolved], str]:
    issues: list[Unresolved] = []
    fork = ""
    if base:
        forks = optional(root, "merge-base", "--all", base, tip, deadline=deadline).splitlines()
        if len(forks) == 1:
            fork = forks[0]
    if not fork:
        issues.append(Unresolved(base, "unknown-base", Source.OBSERVED))
    if not cap:
        start = fork
    else:
        start = cap
        if fork and optional(root, "merge-base", cap, fork, deadline=deadline) == cap:
            start = fork
    if not start:
        return [], issues, ""
    try:
        changed = text(
            root, "diff", "--name-only", "--no-renames", "--relative", "-z", start, tip, deadline=deadline
        ).split("\0")
        if cap and fork and optional(root, "merge-base", fork, cap, deadline=deadline) != fork and start == cap:
            other = set(
                text(
                    root, "diff", "--name-only", "--no-renames", "--relative", "-z", fork, tip, deadline=deadline
                ).split("\0")
            )
            changed = [p for p in changed if p in other]
    except GitError:
        return [], [*issues, Unresolved(start, "unknown-base", Source.OBSERVED)], start
    return [p for p in changed if p], issues, start


def add_paths(scope: ScopeSet, paths: list[str], reader: TreeReader | FilesystemReader, deadline: Deadline) -> None:
    seen = {p.path for p in scope.observed}
    for path in paths:
        deadline.check("scope observed paths")
        try:
            path = normalize(path)
        except EntrypointsPathError:
            scope.unresolved.append(Unresolved(path, "invalid-path", Source.OBSERVED))
            continue
        if path not in seen:
            seen.add(path)
            try:
                kind = reader.kind(path)
            except OSError:
                # A changed path that escapes the worktree or is not a regular file or directory is still observed.
                kind = Granularity.UNKNOWN
            scope.observed.append(ScopePath(path, kind, Source.OBSERVED, Stage.BUILD))


def dirty(root: Path, deadline: Deadline) -> list[str]:
    paths: list[str] = []
    for args in (
        ("diff", "--name-only", "--no-renames", "--relative", "-z", "--cached"),
        ("diff", "--name-only", "--no-renames", "--relative", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        paths.extend(p for p in text(root, *args, deadline=deadline).split("\0") if p)
    return paths


def fingerprint(root: Path, deadline: Deadline) -> str:
    raw = text(root, "rev-parse", "HEAD", deadline=deadline) + text(
        root, "status", "--porcelain=v1", "-z", deadline=deadline
    )
    return hashlib.sha256(raw.encode("utf-8", errors="surrogateescape")).hexdigest()


def semantic_key(observation: Observation) -> str:
    p = observation.provenance
    scope = observation.scope.to_dict()
    scope.pop("id", None)
    return json.dumps(
        [
            observation.task_key,
            p.get("sha"),
            p.get("base_sha"),
            p.get("cap"),
            p.get("range_method"),
            scope,
            observation.missing_layers,
        ],
        sort_keys=True,
    )
