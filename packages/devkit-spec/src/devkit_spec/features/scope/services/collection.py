"""Bounded Host observation, independent of worker publication and workflow evaluation."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError

from devkit_spec.base.errors import ScopeCollectionFailedError, ScopeCollectionPartialWarning, ScopeTimeoutError
from devkit_spec.features.entrypoints import covers
from devkit_spec.features.policy.services.config import read_spec_config
from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import Record, ScopeSet, now
from devkit_spec.features.scope.models.observation import Candidate, CollectionOptions, CollectionReport, Observation
from devkit_spec.features.scope.repositories.collection_git import InputLimitError, git, optional, text
from devkit_spec.features.scope.repositories.collection_registry import CollectionRegistry
from devkit_spec.features.scope.repositories.location import locate
from devkit_spec.features.scope.repositories.source import FilesystemReader, ReadBudget, TreeReader
from devkit_spec.features.scope.services import inventory
from devkit_spec.features.scope.services.observation import (
    add_paths,
    committed,
    declarations,
    dirty,
    fingerprint,
    identify,
    select_base,
    semantic_key,
    task_key,
)

MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_PAIRS = 10_000
MAX_EVIDENCE = 10_000
RESERVED_BYTES = 64 * 1024


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8", errors="backslashreplace")


class Collector:
    def __init__(self, root: Path, options: CollectionOptions) -> None:
        self.root, self.options = root, options
        self.deadline = Deadline(options.timeout)
        # Reserve bounded finalization time from computation, within the same total budget.
        self.compute = Deadline(max(0.001, options.timeout - min(0.5, options.timeout / 10)))
        self.budget = ReadBudget()
        self.started = now()
        self.records: list[Record] = []
        self.candidates: list[Candidate] = []
        self.observations: list[Observation] = []
        self.problems: list[dict[str, str]] = []
        self.problem_count = 0
        self.bytes_left = MAX_REPORT_BYTES - RESERVED_BYTES
        self.layers: dict[str, Any] = {}
        self.namespace = ""
        self.successful_inventory = 0
        self.comparisons_complete = True
        self.evidence_left = MAX_EVIDENCE
        self.inactive_keys: set[str] = set()
        self.last_pair: str | None = None
        self.pairs_attempted = 0
        self.pairs_total = 0

    def source_deadline(self) -> Deadline:
        self.compute.check("scope collection")
        return Deadline(max(0.001, min(self.options.source_timeout, self.compute.remaining())))

    def problem(self, source: str, reason: str) -> None:
        if dict(source_id=source[:512], reason=reason) in self.problems:
            return  # one gap per source and reason, however many stages meet it
        self.problem_count += 1
        if len(self.problems) < 32:
            self.problems.append(dict(source_id=source[:512], reason=reason))

    def retain(self, value: Any) -> bool:
        rendered = encoded(value)
        size = len(rendered) + rendered.count(b"\n") * 8 + 128
        if isinstance(value, dict) and "a" in value and "b" in value and "docs" in value and "code" in value:
            # Text repeats both IDs on every evidence line; cover that representation too.
            evidence_count = len(value["docs"]) + len(value["code"])
            size += evidence_count * (len(encoded(value["a"])) + len(encoded(value["b"])) + 256)
        if size > self.bytes_left:
            self.problem("report", "result-limit")
            return False
        self.bytes_left -= size
        return True

    @staticmethod
    def reason(exc: Exception) -> str:
        if isinstance(exc, ScopeTimeoutError):
            return "source-timeout"
        if isinstance(exc, InputLimitError):
            return "input-limit"
        if isinstance(exc, ValueError) and str(exc) == "identity-ambiguous":
            return "identity-ambiguous"
        return "source-unreadable"

    def registry(self) -> None:
        config = read_spec_config(self.root).scope  # invalid project config remains a primary error
        try:
            deadline = self.source_deadline()
            location = locate(self.root, config, deadline)
            self.namespace = location.namespace
            self.records, problems = CollectionRegistry(location.shared_path).query(location.namespace, deadline)
            self.successful_inventory += 1
            self.layers["registry"] = "partial" if problems else "complete"
            for problem in problems:
                self.problem(f"record:{problem.file}", problem.reason)
        except (AdvisoryError, OSError, ValueError) as exc:
            self.layers["registry"] = "failed"
            self.problem("registry", self.reason(exc))

    def refresh(self) -> None:
        if not self.options.fetch:
            self.layers["fetch"] = {"requested": [], "freshness": "unknown"}
            return
        remotes = text(self.root, "remote", deadline=self.source_deadline()).splitlines()
        if any(remote not in remotes for remote in self.options.fetch):
            raise ArgumentError("--fetch must name a configured remote", fix="Pass a configured remote name")
        outcomes = []
        for remote in dict.fromkeys(self.options.fetch):
            try:
                git(
                    self.root,
                    "fetch",
                    "--no-tags",
                    "--no-prune",
                    "--no-recurse-submodules",
                    "--no-write-fetch-head",
                    "--",
                    remote,
                    f"+refs/heads/*:refs/remotes/{remote}/*",
                    deadline=self.source_deadline(),
                )
                outcomes.append(dict(remote=remote, status="complete", refreshed_at=now()))
            except (AdvisoryError, OSError, InputLimitError):
                outcomes.append(dict(remote=remote, status="failed", refreshed_at=None))
                self.problem(f"fetch:{remote}", "fetch-failed")
        self.layers["fetch"] = outcomes

    def discover(self) -> None:
        self.registry()
        if self.options.mode != "snapshot":
            self.refresh()
            for name, function in (("refs", inventory.refs), ("worktrees", inventory.worktrees)):
                if name == "worktrees" and self.options.mode != "worktrees":
                    continue
                try:
                    found = function(self.root, self.source_deadline())
                    self.successful_inventory += 1
                    self.layers[name] = "complete"
                    self.candidates.extend(found)
                except (AdvisoryError, OSError, ValueError, InputLimitError) as exc:
                    self.layers[name] = "failed"
                    self.problem(name, self.reason(exc))
        self.candidates.extend(
            Candidate(source_id=f"snapshot:{record.task_id}", worktree=record.worktree, record=record)
            for record in self.records
        )
        self.candidates.sort(key=lambda candidate: candidate.source_id)
        if len(self.candidates) > inventory.MAX_SOURCES:
            self.problem("inventory", "result-limit")
        # Bound candidate metadata as well as observations. The skipped count remains explicit.
        self.discovered_count = len(self.candidates)
        self.candidates = self.candidates[: inventory.MAX_SOURCES]
        if not self.successful_inventory:
            failed = [problem["source_id"] for problem in self.problems]
            raise ScopeCollectionFailedError(
                "No selected inventory source could be read",
                *(f"{problem['source_id']}: {problem['reason']}" for problem in self.problems),
                target_files=failed or ["--mode"],
            )

    def snapshot(self, candidate: Candidate) -> Observation:
        assert candidate.record is not None
        record = candidate.record
        # task_id is a registration alias, not necessarily the anchor ID.
        key = None
        candidate.task_key = key
        candidate.reason = "snapshot-only"
        scope = record.to_set()
        return Observation(
            candidate.source_id,
            key,
            scope,
            dict(
                source="snapshot",
                registered_task_id=record.task_id,
                namespace=record.namespace,
                unit=record.spec,
                published_at=record.updated_at,
                observed_at=now(),
                revision=record.revision,
                host=record.hostname,
                worktree=record.worktree,
            ),
            ["snapshot"],
            ["live-declarations", "committed", "dirty"],
        )

    def observe(self, candidate: Candidate) -> Observation:
        deadline = self.source_deadline()
        root = Path(candidate.worktree) if candidate.worktree else self.root
        if candidate.worktree:
            # Only inventoried worktrees, never arbitrary remote record paths, reach this branch.
            common = text(root, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=deadline)
            expected = text(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=deadline)
            if Path(common).resolve() != Path(expected).resolve():
                raise ValueError("identity-ambiguous")
            local = [
                record
                for record in self.records
                if record.hostname == socket.gethostname() and Path(record.worktree) == root
            ]
            if len(local) == 1:
                candidate.record = local[0]
            candidate.sha = text(root, "rev-parse", "HEAD", deadline=deadline)
        before = fingerprint(root, deadline) if candidate.worktree else ""
        reader: TreeReader | FilesystemReader = (
            FilesystemReader(root, deadline, self.budget)
            if candidate.worktree
            else TreeReader(root, candidate.sha, deadline, self.budget)
        )
        dirty_paths = dirty(root, deadline) if candidate.worktree else []
        try:
            unit, meta = identify(candidate, reader, root, deadline)
            key = task_key(self.namespace, str(meta["id"]), unit)
            candidate.task_key = key
        except ScopeTimeoutError:
            raise
        except (AdvisoryError, ValueError, OSError):
            if not candidate.worktree:
                raise
            # Unknown shared/detached worktree changes remain separately attributable physical evidence.
            unbound = bool(candidate.branch) and not inventory.ACTIVITY.fullmatch(candidate.branch)
            # The base checkout (the main worktree off any activity branch) is never a task, dirty or not.
            base = unbound and text(
                root, "rev-parse", "--path-format=absolute", "--git-dir", deadline=deadline
            ) == text(root, "rev-parse", "--path-format=absolute", "--git-common-dir", deadline=deadline)
            clean_unbound = base or (unbound and not dirty_paths)
            candidate.activity = "inactive" if clean_unbound else "unknown"
            candidate.reason = "base-checkout" if base else "clean-unbound" if clean_unbound else "identity-ambiguous"
            scope = ScopeSet(candidate.source_id)
            add_paths(scope, dirty_paths, reader, deadline)
            if before != fingerprint(root, deadline) or (
                isinstance(reader, FilesystemReader) and not reader.unchanged()
            ):
                self.problem(candidate.source_id, "observation-changed")
            return Observation(
                candidate.source_id,
                None,
                scope,
                dict(source="worktree", worktree=str(root), sha=candidate.sha, observed_at=now()),
                ["dirty"],
                [] if clean_unbound else ["identity", "declarations", "committed"],
            )
        fallback = False
        try:
            scope = declarations(reader, unit)
        except ScopeTimeoutError:
            raise
        except (AdvisoryError, OSError, UnicodeError, InputLimitError) as exc:
            if not candidate.worktree:
                raise
            pinned = TreeReader(root, candidate.sha, deadline, self.budget)
            scope = declarations(pinned, unit)
            fallback = True
            self.problem(candidate.source_id, self.reason(exc))
        scope.id = candidate.source_id
        terminal = meta.get("status") in {"completed", "rejected"}
        candidate.activity = "unknown" if terminal and dirty_paths else "inactive" if terminal else "active-candidate"
        candidate.reason = (
            "terminal-dirty" if terminal and dirty_paths else "terminal" if terminal else "nonterminal-unit"
        )
        missing = ["live-declarations"] if fallback else []
        record = candidate.record
        if record is None:
            matches = [r for r in self.records if r.spec == unit and r.namespace == self.namespace]
            if len(matches) == 1:
                record = matches[0]
        base_ref, base_source = select_base(root, candidate, self.options.base, record, deadline)
        base_sha = (
            optional(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}", deadline=deadline) if base_ref else ""
        )
        if base_sha == candidate.sha or base_ref == candidate.ref:
            base_sha = ""
        cap = record.base_revision if record else ""
        paths, unresolved, start = committed(root, candidate.sha, base_sha, cap, deadline)
        scope.unresolved.extend(unresolved)
        if unresolved:
            missing.append("committed")
        add_paths(scope, paths, reader, deadline)
        if candidate.worktree:
            add_paths(scope, dirty_paths, reader, deadline)
            if before != fingerprint(root, deadline) or (
                isinstance(reader, FilesystemReader) and not reader.unchanged()
            ):
                self.problem(candidate.source_id, "observation-changed")
        if scope.unresolved:
            self.problem(candidate.source_id, "unknown-base" if unresolved else "unresolved-input")
        provenance = dict(
            source="worktree" if candidate.worktree else "ref",
            sha=candidate.sha,
            unit=unit,
            observed_at=now(),
            base_sha=base_sha,
            base_source=base_source,
            base_ref=base_ref,
            cap=cap,
            range_start=start,
            range_method="registered-cap" if record else "branch-relative",
            worktree=candidate.worktree,
            declaration_source=candidate.sha if fallback or not candidate.worktree else f"filesystem:{root}",
            declarations_fallback=fallback,
            ref=candidate.ref,
            freshness="unknown",
        )
        layers = ["declarations", *([] if unresolved else ["committed"]), *(["dirty"] if candidate.worktree else [])]
        return Observation(candidate.source_id, key, scope, provenance, layers, missing)

    def read_sources(self) -> None:
        keys: dict[str, Observation] = {}
        for candidate in self.candidates:
            try:
                self.compute.check("scope sources")
                observation = (
                    self.snapshot(candidate) if candidate.source_id.startswith("snapshot:") else self.observe(candidate)
                )
                if observation.missing_layers and observation.provenance["source"] != "snapshot":
                    self.problem(
                        candidate.source_id, "identity-ambiguous" if observation.task_key is None else "unknown-base"
                    )
                if candidate.activity == "inactive":
                    if observation.task_key:
                        self.inactive_keys.add(observation.task_key)
                    continue
                key = semantic_key(observation)
                if not candidate.worktree and key in keys and observation.provenance["source"] != "snapshot":
                    if self.retain(candidate.source_id):
                        keys[key].aliases.append(candidate.source_id)
                    candidate.reason = "equivalent-observation"
                    continue
                if not self.retain(observation.public()):
                    candidate.reason = "result-limit"
                    continue
                if candidate.activity != "inactive":
                    keys[key] = observation
                    self.observations.append(observation)
            except (AdvisoryError, OSError, ValueError, InputLimitError) as exc:
                candidate.reason = self.reason(exc)
                self.problem(candidate.source_id, candidate.reason)
        # Reconcile registration aliases only with a uniquely observed canonical anchor.
        live: dict[tuple[str, str], set[str]] = {}
        for observation in self.observations:
            if observation.task_key and observation.provenance["source"] != "snapshot":
                namespace, _, unit = json.loads(observation.task_key)
                live.setdefault((namespace, unit), set()).add(observation.task_key)
        for key in self.inactive_keys:
            namespace, _, unit = json.loads(key)
            live.setdefault((namespace, unit), set()).add(key)
        active_keys = {o.task_key for o in self.observations if o.provenance["source"] != "snapshot"}
        live_keys = {
            o.task_key for o in self.observations if o.provenance["source"] != "snapshot" and not o.missing_layers
        }
        uncertain_units = {
            (record.namespace, record.spec)
            for candidate in self.candidates
            if candidate.source_id.startswith("worktree:")
            and candidate.task_key is None
            and candidate.activity != "inactive"
            for record in self.records
            if record.hostname == socket.gethostname() and Path(record.worktree) == Path(candidate.worktree)
        }
        for observation in self.observations:
            if observation.provenance["source"] != "snapshot":
                continue
            binding = (observation.provenance["namespace"], observation.provenance["unit"])
            identities = live.get(binding, set())
            if len(identities) == 1:
                observation.task_key = next(iter(identities))
                for candidate in self.candidates:
                    if candidate.source_id == observation.observation_id:
                        candidate.task_key = observation.task_key
                terminal = (
                    observation.task_key in self.inactive_keys
                    and observation.task_key not in active_keys
                    and binding not in uncertain_units
                )
                if observation.task_key in live_keys or terminal:
                    observation.provenance["historical"] = True
                    observation.provenance["comparison_eligible"] = False
                    if terminal:
                        for candidate in self.candidates:
                            if candidate.source_id == observation.observation_id:
                                candidate.activity, candidate.reason = "inactive", "terminal-snapshot"

    def check_identities(self) -> None:
        units: dict[tuple[str, str], set[str]] = {}
        for observation in self.observations:
            if observation.task_key:
                namespace, identity, unit = json.loads(observation.task_key)
                units.setdefault((namespace, identity), set()).add(unit)
        duplicates = {key for key, paths in units.items() if len(paths) > 1}
        for observation in self.observations:
            if observation.task_key:
                namespace, identity, _ = json.loads(observation.task_key)
                if (namespace, identity) in duplicates:
                    observation.task_key = None
                    self.problem(observation.observation_id, "identity-ambiguous")
                    for candidate in self.candidates:
                        if candidate.source_id == observation.observation_id:
                            candidate.task_key = None
                            candidate.activity, candidate.reason = "unknown", "identity-ambiguous"

    def relations(self) -> None:
        try:
            for i, first in enumerate(self.observations):
                sha = first.provenance.get("sha")
                if not sha or not first.task_key:
                    continue
                for second in self.observations[i + 1 :]:
                    other = second.provenance.get("sha")
                    if not other or first.task_key != second.task_key or sha == other:
                        continue
                    common = optional(self.root, "merge-base", "--all", sha, other, deadline=self.source_deadline())
                    relation = (
                        "ancestor"
                        if common == sha
                        else "descendant"
                        if common == other
                        else "divergent"
                        if common
                        else "unknown"
                    )
                    item = dict(other=second.observation_id, relation=relation)
                    if not self.retain(item):
                        return
                    first.provenance.setdefault("relations", []).append(item)
        except (AdvisoryError, OSError, InputLimitError) as exc:
            self.problem("relations", self.reason(exc))

    def compare(self, first: Observation, second: Observation) -> dict[str, Any]:
        a, b = first.scope, second.scope
        evidence_docs: list[dict[str, Any]] = []
        evidence_code: list[dict[str, Any]] = []
        docs = {path.path: path for path in b.docs}
        for path in a.docs:
            self.compute.check("scope comparison")
            if path.path in docs:
                evidence_docs.append(
                    dict(
                        path=path.path,
                        kind="doc",
                        granularity=str(path.kind),
                        other=path.path,
                        source=str(path.source),
                        other_source=str(docs[path.path].source),
                    )
                )
                if len(evidence_docs) > self.evidence_left:
                    raise InputLimitError("result-limit")
        seen: set[tuple[str, str]] = set()
        for mine in [*a.code, *a.observed]:
            for theirs in [*b.code, *b.observed]:
                self.compute.check("scope comparison")
                key = (mine.path, theirs.path)
                if key in seen or not (covers(mine.path, theirs.path) or covers(theirs.path, mine.path)):
                    continue
                seen.add(key)
                evidence_code.append(
                    dict(
                        path=mine.path,
                        kind="code",
                        granularity=str(mine.kind),
                        other=theirs.path,
                        source=str(mine.source),
                        other_source=str(theirs.source),
                    )
                )
                if len(evidence_docs) + len(evidence_code) > self.evidence_left:
                    raise InputLimitError("result-limit")
        return dict(
            a=first.observation_id,
            b=second.observation_id,
            docs=evidence_docs,
            code=evidence_code,
            unresolved=len(a.unresolved) + len(b.unresolved),
        )

    def comparisons(self) -> list[dict[str, Any]]:
        result = []
        observations = [o for o in self.observations if o.provenance.get("comparison_eligible", True)]
        self.pairs_total = sum(
            1
            for i, a in enumerate(observations)
            for b in observations[i + 1 :]
            if not a.task_key or a.task_key != b.task_key
        )
        try:
            for i, first in enumerate(observations):
                for second in observations[i + 1 :]:
                    if first.task_key and first.task_key == second.task_key:
                        continue
                    self.compute.check("scope comparison")
                    if len(result) >= MAX_PAIRS:
                        raise InputLimitError("result-limit")
                    pair = self.compare(first, second)
                    if not self.retain(pair):
                        raise InputLimitError("result-limit")
                    result.append(pair)
                    self.evidence_left -= len(pair["docs"]) + len(pair["code"])
                    self.pairs_attempted += 1
                    self.last_pair = f"{pair['a']}|{pair['b']}"
        except (ScopeTimeoutError, InputLimitError) as exc:
            self.comparisons_complete = False
            self.problem("comparisons", "source-timeout" if isinstance(exc, ScopeTimeoutError) else "result-limit")
        return result

    def execute(self) -> CollectionReport:
        self.discover()
        self.read_sources()
        self.check_identities()
        self.relations()
        pairs = self.comparisons()
        inventory_data = []
        for candidate in self.candidates:
            item = candidate.public()
            if self.retain(item):
                inventory_data.append(item)
        observations = [item.public() for item in self.observations]
        notices: list[AdvisoryError] = []
        if self.problem_count:
            notices.append(
                ScopeCollectionPartialWarning(
                    f"Scope observation has {self.problem_count} coverage gap(s)",
                    *(f"{p['source_id']}: {p['reason']}" for p in self.problems),
                    target_files=list(dict.fromkeys(p["source_id"] for p in self.problems)),
                )
            )
        data: dict[str, Any] = dict(
            mode=self.options.mode,
            started_at=self.started,
            finished_at=now(),
            coverage=dict(
                status="partial" if self.problem_count else "complete",
                layers=self.layers,
                problems=self.problems,
                problems_total=self.problem_count,
                sources_discovered=self.discovered_count,
                sources_retained=len(inventory_data),
                comparisons_complete=self.comparisons_complete,
                pairs_total=self.pairs_total,
                pairs_completed=self.pairs_attempted,
                last_completed_pair=self.last_pair,
            ),
            inventory=inventory_data,
            observations=observations,
            pairs=pairs,
            summary=dict(
                candidates=len(inventory_data),
                observations=len(observations),
                pairs=len(pairs),
                overlapping=sum(bool(p["docs"] or p["code"]) for p in pairs),
            ),
            notices=[n.to_dict() for n in notices],
        )
        # All variable entries were charged with framing overhead; metadata uses the reserved space.
        if len(encoded(data)) > MAX_REPORT_BYTES:
            raise ScopeCollectionFailedError(
                "Report metadata exceeds collection result limit",
                input_error=False,
                fix="Report the limit; a narrower --mode (snapshot) collects fewer sources",
            )
        if self.deadline.expired():
            self.problem("finalization", "source-timeout")
            data["coverage"]["status"] = "partial"
            data["coverage"]["problems_total"] = self.problem_count
            notices = [ScopeCollectionPartialWarning("Scope result finalization reached its time budget")]
            data["notices"] = [notice.to_dict() for notice in notices]
        return CollectionReport(data, notices)
