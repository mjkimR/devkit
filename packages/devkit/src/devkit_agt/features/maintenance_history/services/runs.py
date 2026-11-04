"""Capture and close immutable maintenance run evidence."""

from __future__ import annotations

import os
import secrets
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from devkit.advisory import AdvisoryError

from ..models.errors import EvidenceChanged, InputError, ReportMismatch, RunDrifted, SecretFound
from ..models.records import PLAYBOOKS, HistoryResult, canonical, digest, published_record
from ..repositories.local import read_record, write_record
from ..repositories.snapshot import capture


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def stamp(zone: str | None) -> tuple[dict[str, str], dict[str, str]]:
    current = datetime.now(UTC)
    source = "explicit" if zone else "system"
    if not zone:
        zone = os.environ.get("TZ")
        if not zone:
            localtime = str(Path("/etc/localtime").resolve())
            zone = localtime.split("/zoneinfo/", 1)[-1] if "/zoneinfo/" in localtime else "UTC"
    try:
        tz = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InputError("Use a valid IANA timezone") from exc
    return {"utc": current.isoformat().replace("+00:00", "Z"), "local": current.astimezone(tz).isoformat()}, {
        "name": zone,
        "source": source,
    }


def exclusions(root: Path, run: Path, report: Path) -> list[str]:
    result = []
    for path in (run, report):
        if path.is_relative_to(root):
            relative = path.relative_to(root).as_posix()
            if relative == ".":
                raise InputError("The run or report path cannot be the repository root")
            result.append(relative)
    return result


def check_secrets(run: Path, files: dict[str, bytes]) -> None:
    from devkit_agt.features.rules import RuleContext
    from devkit_agt.features.rules.services.builtins import SecretLeakRule

    with tempfile.TemporaryDirectory(prefix=".secret-check-", dir=run) as name:
        scan = Path(name)
        for relative, data in files.items():
            path = scan / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        findings = SecretLeakRule().check(RuleContext(scan, changed_files=list(files), exclude=()))
        if findings:
            first = findings[0]
            raise SecretFound(
                "History evidence contains a potential secret", f"{first.file}:{first.line}", target_files=[first.file]
            )


def start(
    root: Path,
    *,
    repository: str,
    playbook: str,
    scope: str,
    into: Path,
    report: Path,
    zone: str | None,
    supersedes: tuple[str, ...],
    prior_runs: tuple[str, ...],
) -> HistoryResult:
    if playbook not in PLAYBOOKS or not scope.strip():
        raise InputError("Name one supported maintenance playbook and a nonempty scope")
    started, timezone_info = stamp(zone)
    run_id = f"{playbook}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}"
    run = into.resolve() / run_id
    report = report.resolve()
    excluded = exclusions(root, run, report)
    snapshot, diff = capture(root, excluded)
    record: dict[str, Any] = {
        "schema": 1,
        "run_id": run_id,
        "playbook": playbook,
        "repository": repository,
        "scope": scope,
        "timezone": timezone_info,
        "started_at": started,
        "finished_at": None,
        "supersedes": list(supersedes),
        "prior_runs": list(prior_runs),
        **snapshot,
        "comparison": {"root": str(root), "excluded": excluded},
        "outcome": None,
        "result": None,
        "counts": {},
        "report": {"path": str(report), "sha256": None},
        "files": [],
        "applied_commits": [],
        "follow_ups": [],
        "destination": None,
        "authority": None,
        "attempts": [],
        "publication": "pending",
        "history_commit": None,
        "updates": [],
        "published_files": None,
        "record_digest": None,
    }
    run.mkdir(parents=True, exist_ok=False)
    if diff is not None:
        (run / "inspected.diff").write_bytes(diff)
    write_record(run, record)
    return HistoryResult("HISTORY_RUN_STARTED", {"run_id": run_id, "path": str(run), "record": record})


def finish(
    run: Path,
    *,
    outcome: str,
    result: str | None,
    report: Path | None,
    applied_commits: tuple[str, ...],
    follow_ups: tuple[str, ...],
    files: tuple[Path, ...] = (),
) -> HistoryResult:
    record = read_record(run)
    if record.get("finished_at"):
        raise InputError("Run already finished; use update for integration state")
    report_path = Path(record["report"]["path"])
    if report is not None and report.resolve() != report_path:
        raise ReportMismatch("finish --report differs from the intake report")
    if outcome not in ("completed", "failed", "interrupted"):
        raise InputError("Invalid run outcome")
    try:
        snapshot, _ = capture(Path(record["comparison"]["root"]), record["comparison"]["excluded"])
        report_bytes = report_path.read_bytes()
    except OSError as exc:
        raise InputError("Cannot read run evidence", type(exc).__name__) from exc
    record["outcome"], record["result"] = outcome, result
    record["applied_commits"], record["follow_ups"] = list(applied_commits), list(follow_ups)
    record["finished_at"], _ = stamp(record["timezone"]["name"])
    record["drifted_at_finish"] = any(snapshot[key] != record[key] for key in ("source_sha", "inspected_tree"))
    frozen = []
    sources = {"record.json": canonical(record), "report/" + report_path.name: report_bytes}
    names: set[str] = set()
    for file in files:
        file = file.resolve()
        relative = file.relative_to(run).as_posix() if file.is_relative_to(run) else file.name
        if relative in names or relative in ("record.json", "report.md") or relative.startswith("updates/"):
            raise InputError("Selected evidence filename is duplicate or reserved")
        names.add(relative)
        try:
            content = file.read_bytes()
        except OSError as exc:
            raise InputError("Cannot freeze selected evidence", target_files=[str(file)]) from exc
        sources["files/" + relative] = content
        frozen.append({"path": relative, "source": str(file), "sha256": digest(content)})
    record["files"] = frozen
    sources["record.json"] = canonical(record)
    check_secrets(run, sources)
    record["report"]["sha256"] = digest(report_bytes)
    record["record_digest"] = digest(canonical(published_record(record)))
    write_record(run, record)
    notices: list[AdvisoryError] = (
        [RunDrifted("Inspected content changed before finish")] if record["drifted_at_finish"] else []
    )
    return HistoryResult(
        "HISTORY_RUN_FINISHED", {"run_id": record["run_id"], "path": str(run), "record": record}, notices
    )


def verify_record(record: dict[str, Any]) -> None:
    if record.get("record_digest") != digest(canonical(published_record(record))):
        raise EvidenceChanged("Canonical run record differs from its finish digest")


def evidence(run: Path, record: dict[str, Any], selected: tuple[Path, ...]) -> dict[str, bytes]:
    if not record.get("finished_at"):
        raise InputError("Finish the run before publication")
    verify_record(record)
    report = Path(record["report"]["path"])
    try:
        report_bytes = report.read_bytes()
        if digest(report_bytes) != record["report"]["sha256"]:
            raise EvidenceChanged("The report differs from its frozen digest", target_files=[str(report)])
        files = {"report.md": report_bytes}
        existing = {item["path"]: item for item in record["files"]}
        for path in selected:
            path = path.resolve()
            candidates = [item for item in existing.values() if item["source"] == str(path)]
            if not candidates:
                raise InputError("Declare selected evidence with finish --file before publication")
            item = candidates[0]
            data = path.read_bytes()
            if digest(data) != item["sha256"]:
                raise EvidenceChanged("Selected evidence changed", target_files=[str(path)])
            files[item["path"]] = data
    except OSError as exc:
        raise InputError("Cannot read selected evidence", type(exc).__name__) from exc
    check_secrets(run, {name: data for name, data in files.items() if name != "report.md"})
    return files
