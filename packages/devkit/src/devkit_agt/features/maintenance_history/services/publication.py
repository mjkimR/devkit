"""Atomic, non-forced publication and immutable retry inspection."""

from __future__ import annotations

import base64
import json
import secrets
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..models.errors import (
    AuthorityMissing,
    BranchAbsent,
    BranchForeign,
    BranchMissing,
    Deferred,
    GhUnavailable,
    HistoryError,
    InputError,
    PublishFailed,
    PublishUnknown,
    RecordCollision,
    RepositoryEmpty,
    RunMissing,
)
from ..models.records import (
    IDENTITY,
    ROOT_COMMIT,
    ROOT_DATE,
    ROOT_README,
    HistoryResult,
    canonical,
    git_sha,
    published_record,
    run_parts,
    run_path,
    safe_file,
)
from ..repositories.github import Response, Runner, run_gh
from ..repositories.local import read_record, write_record
from .runs import check_secrets, evidence, now


class GitHubHistory:
    def __init__(self, repository: str, branch: str, runner: Runner = run_gh) -> None:
        self.prefix = f"repos/{repository}"
        self.branch = branch
        self.runner = runner
        self.attempts: list[dict[str, Any]] = []

    def request(
        self, method: str, path: str, payload: dict[str, Any] | None = None, *, reference: bool = False
    ) -> Response:
        timeout = 30.0 + (len(canonical(payload)) / 65536 if payload is not None else 0)
        try:
            response = self.runner(method, f"{self.prefix}/{path}", payload, timeout)
        except subprocess.TimeoutExpired as exc:
            self.attempts.append(
                {
                    "at": now(),
                    "request": f"{method} {path}",
                    "status_class": "timeout",
                    "result": "unknown" if reference else "deferred",
                }
            )
            if reference:
                raise PublishUnknown("History reference update response was lost") from exc
            raise Deferred("History request timed out before publication") from exc
        self.attempts.append(
            {
                "at": now(),
                "request": f"{method} {path}",
                "status_class": f"{response.status // 100}xx",
                "result": response.status,
            }
        )
        headers = {key.lower(): value for key, value in response.headers.items()}
        if response.status == 429 or (
            response.status == 403 and ("retry-after" in headers or headers.get("x-ratelimit-remaining") == "0")
        ):
            raise Deferred(
                "GitHub deferred history access",
                retry_after=headers.get("retry-after") or headers.get("x-ratelimit-reset") or "60s",
            )
        if response.status >= 500:
            if reference:
                raise PublishUnknown("GitHub reference update outcome is unknown")
            raise Deferred("GitHub history request is temporarily unavailable")
        return response

    def ok(self, method: str, path: str, payload: dict[str, Any] | None = None, *, reference: bool = False) -> Any:
        response = self.request(method, path, payload, reference=reference)
        if (
            response.status == 409
            and method == "POST"
            and path == "git/trees"
            and payload is not None
            and "base_tree" not in payload
        ):
            raise RepositoryEmpty("GitHub cannot create history objects in an empty repository")
        if response.status not in (200, 201):
            raise PublishFailed("GitHub refused history access", f"{method} {path}: HTTP {response.status}")
        return response.body

    def repository(self) -> None:
        self.ok("GET", "")

    def head(self) -> str | None:
        response = self.request("GET", "git/ref/heads/" + quote(self.branch, safe=""))
        if response.status == 404:
            return None
        if response.status != 200:
            raise PublishFailed("Cannot read history branch", f"HTTP {response.status}")
        return response.body["object"]["sha"]

    def validate(self, head: str) -> None:
        response = self.request("GET", f"compare/{ROOT_COMMIT}...{head}?per_page=1")
        if response.status == 404 or (
            response.status == 200 and response.body.get("status") not in ("identical", "ahead")
        ):
            raise BranchForeign("Destination branch does not descend from the frozen history root")
        if response.status != 200:
            raise PublishFailed("Cannot validate history root", f"HTTP {response.status}")

    def read_file(self, path: str, head: str) -> tuple[bytes, str] | None:
        response = self.request("GET", f"contents/{quote(path, safe='/')}?ref={quote(head, safe='')}")
        if response.status == 404:
            return None
        if response.status != 200 or not isinstance(response.body, dict) or response.body.get("encoding") != "base64":
            raise PublishFailed("Cannot read history file", f"{path}: HTTP {response.status}")
        try:
            data = base64.b64decode(response.body["content"])
            return data, response.body["sha"]
        except (ValueError, KeyError, TypeError) as exc:
            raise PublishFailed("Malformed history file response") from exc

    def commit_for(self, path: str) -> str:
        entries = self.ok("GET", f"commits?sha={quote(self.branch, safe='')}&path={quote(path, safe='')}&per_page=1")
        if not entries:
            raise PublishUnknown("History content matches but its publication commit cannot be located")
        return entries[0]["sha"]

    def initialize(self, authority: str) -> HistoryResult:
        require_authority(authority)
        self.repository()
        head = self.head()
        if head is None:
            tree = self.ok(
                "POST",
                "git/trees",
                {"tree": [{"path": "README.md", "mode": "100644", "type": "blob", "content": ROOT_README.decode()}]},
            )
            commit = self.ok(
                "POST",
                "git/commits",
                {
                    "message": "Initialize devkit maintenance history\n",
                    "tree": tree["sha"],
                    "parents": [],
                    "author": IDENTITY | {"date": ROOT_DATE},
                    "committer": IDENTITY | {"date": ROOT_DATE},
                },
            )
            if commit["sha"] != ROOT_COMMIT:
                raise PublishFailed("GitHub root differs from the frozen history root")
            response = self.request(
                "POST", "git/refs", {"ref": "refs/heads/" + self.branch, "sha": ROOT_COMMIT}, reference=True
            )
            if response.status in (409, 422):
                head = self.head()
                if head is None:
                    raise RepositoryEmpty("GitHub refused creating history in an empty or restricted repository")
            elif response.status != 201:
                raise PublishFailed("GitHub refused creating the history branch", f"HTTP {response.status}")
            else:
                head = ROOT_COMMIT
        self.validate(head)
        return HistoryResult(
            "HISTORY_BRANCH_READY", {"root_sha": ROOT_COMMIT, "head_sha": head, "authority": authority}
        )

    def publish_files(
        self,
        *,
        record: dict[str, Any],
        immutable: dict[str, bytes],
        identity_path: str,
        index_line: dict[str, Any],
        message: str,
        date: str,
    ) -> str:
        self.repository()
        for _ in range(3):
            head = self.head()
            if head is None:
                raise BranchMissing("History branch is absent; publication remains pending")
            self.validate(head)
            existing = self.read_file(identity_path, head)
            if existing:
                if existing[1] != git_sha("blob", immutable[identity_path]):
                    raise RecordCollision(
                        "History path already holds different immutable content", target_files=[identity_path]
                    )
                # Verify selected companion files as well: idempotency never hides a partial/foreign record.
                for path, data in immutable.items():
                    remote = self.read_file(path, head)
                    if remote is None or remote[1] != git_sha("blob", data):
                        raise RecordCollision("Published companion content differs", target_files=[path])
                return self.commit_for(identity_path)
            playbook, year = run_parts(record["run_id"])
            shard = f"index/{playbook}/{year}.jsonl"
            old_shard = self.read_file(shard, head)
            content = (old_shard[0] if old_shard else b"") + canonical(index_line)
            blobs = dict(immutable)
            blobs[shard] = content
            entries = []
            for path, data in blobs.items():
                blob = self.ok("POST", "git/blobs", {"encoding": "base64", "content": base64.b64encode(data).decode()})
                entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
            parent = self.ok("GET", "git/commits/" + head)
            tree = self.ok("POST", "git/trees", {"base_tree": parent["tree"]["sha"], "tree": entries})
            commit = self.ok(
                "POST",
                "git/commits",
                {
                    "message": message,
                    "tree": tree["sha"],
                    "parents": [head],
                    "author": IDENTITY | {"date": date},
                    "committer": IDENTITY | {"date": date},
                },
            )
            response = self.request(
                "PATCH", "git/refs/heads/" + quote(self.branch, safe=""), {"sha": commit["sha"]}, reference=True
            )
            if response.status == 200:
                return commit["sha"]
            if response.status not in (409, 422):
                raise PublishFailed("GitHub refused updating history reference", f"HTTP {response.status}")
            if self.head() == head:
                raise PublishFailed("History reference update was refused without a concurrent writer")
        raise Deferred("Concurrent history writers exhausted three publication attempts")

    def listing(
        self, playbook: str, source_sha: str | None, outcome: str | None, include_superseded: bool, limit: int
    ) -> HistoryResult:
        self.repository()
        head = self.head()
        if head is None:
            return HistoryResult("HISTORY_LIST", {"count": 0, "runs": []}, [BranchAbsent("History branch is absent")])
        self.validate(head)
        response = self.request("GET", f"contents/index/{quote(playbook, safe='')}?ref={quote(head, safe='')}")
        if response.status == 404:
            return HistoryResult("HISTORY_LIST", {"count": 0, "runs": []})
        if response.status != 200 or not isinstance(response.body, list):
            raise PublishFailed("Cannot list history index shards")
        merged: dict[str, dict[str, Any]] = {}
        # Read complete run-year shards newest first; amendments stay in the run ID year.
        for entry in sorted(response.body, key=lambda item: item.get("name", ""), reverse=True):
            if not entry.get("name", "").endswith(".jsonl"):
                continue
            shard = self.read_file(entry["path"], head)
            if shard is None:
                raise PublishFailed("History shard disappeared at a fixed head")
            try:
                for line in shard[0].splitlines():
                    item = json.loads(line)
                    previous = merged.get(item["run_id"])
                    if previous is None or item.get("updated_at", item["finished_at"]) >= previous.get(
                        "updated_at", previous["finished_at"]
                    ):
                        merged[item["run_id"]] = item
            except (ValueError, KeyError, TypeError) as exc:
                raise PublishFailed("Malformed history index shard") from exc
            superseded_so_far = {value for item in merged.values() for value in item["supersedes"]}
            eligible = [
                item
                for item in merged.values()
                if (include_superseded or item["run_id"] not in superseded_so_far)
                and (source_sha is None or item["source_sha"] == source_sha)
                and (outcome is None or item["outcome"] == outcome)
            ]
            if len(eligible) >= limit:
                break
        superseded = {value for item in merged.values() for value in item["supersedes"]}
        runs = [
            item
            for item in merged.values()
            if (include_superseded or item["run_id"] not in superseded)
            and (source_sha is None or item["source_sha"] == source_sha)
            and (outcome is None or item["outcome"] == outcome)
        ]
        runs.sort(key=lambda item: item["run_id"], reverse=True)
        runs = runs[:limit]
        return HistoryResult("HISTORY_LIST", {"count": len(runs), "runs": runs})

    def get(self, run_id: str, file: str) -> HistoryResult:
        self.repository()
        head = self.head()
        if head is None:
            raise RunMissing("History branch is absent")
        self.validate(head)
        path = f"{run_path(run_id)}/{safe_file(file)}"
        item = self.read_file(path, head)
        if item is None:
            raise RunMissing("History run file does not exist", target_files=[path])
        return HistoryResult(
            "HISTORY_FILE",
            {
                "run_id": run_id,
                "file": file,
                "encoding": "base64",
                "content": base64.b64encode(item[0]).decode(),
                "sha": item[1],
            },
        )


def require_authority(authority: str) -> None:
    if not authority.strip():
        raise AuthorityMissing("History mutation requires explicit destination authority")


def index_entry(record: dict[str, Any], path: str) -> dict[str, Any]:
    return {
        key: record[key] for key in ("run_id", "source_sha", "inspected_tree", "outcome", "result", "supersedes")
    } | {"kind": "run", "finished_at": record["finished_at"]["utc"], "path": path}


def publish(
    history: GitHubHistory, run: Path, authority: str, files: tuple[Path, ...], repository: str
) -> HistoryResult:
    require_authority(authority)
    record = read_record(run)
    selected = evidence(run, record, files)
    selected_names = sorted(selected)
    if record.get("published_files") is not None and record["published_files"] != selected_names:
        raise InputError("A publication retry must keep its original selected files")
    record["published_files"] = selected_names
    destination = f"{repository}#{history.branch}"
    if record["destination"] is not None and record["destination"] != destination:
        raise InputError("A publication retry must keep its original destination")
    record["destination"], record["authority"] = destination, authority
    prefix = run_path(record["run_id"])
    path = prefix + "/record.json"
    immutable = {prefix + "/" + relative: data for relative, data in selected.items()}
    immutable[path] = canonical(published_record(record))
    write_record(run, record)
    try:
        commit = history.publish_files(
            record=record,
            immutable=immutable,
            identity_path=path,
            index_line=index_entry(record, path),
            message=f"history: {record['playbook']} {record['run_id']}",
            date=record["finished_at"]["utc"],
        )
        record["publication"], record["history_commit"] = "published", commit
    except HistoryError as exc:
        record["publication"] = (
            "unknown"
            if isinstance(exc, PublishUnknown)
            else "pending"
            if isinstance(exc, (Deferred, GhUnavailable, BranchMissing))
            else "failed"
        )
        raise
    finally:
        record["attempts"].extend(history.attempts)
        write_record(run, record)
    return HistoryResult(
        "HISTORY_PUBLISHED", {"run_id": record["run_id"], "history_commit": commit, "publication": "published"}
    )


def update(
    history: GitHubHistory, run: Path, authority: str, integration_state: str, applied_commits: tuple[str, ...]
) -> HistoryResult:
    require_authority(authority)
    record = read_record(run)
    if record["publication"] != "published" or not integration_state.strip():
        raise InputError("An amendment requires a published run and nonempty integration state")
    changes = record["updates"]
    if changes and changes[-1]["state"] != "published":
        change = changes[-1]
        if change["content"]["integration_state"] != integration_state or change["content"]["applied_commits"] != list(
            applied_commits
        ):
            raise InputError("An amendment retry must keep its original content")
    else:
        at = now()
        name = at[:19].replace("-", "").replace(":", "") + "Z-" + secrets.token_hex(4) + ".json"
        content = {
            "run_id": record["run_id"],
            "updated_at": at,
            "integration_state": integration_state,
            "applied_commits": list(applied_commits),
            "authority": authority,
        }
        change = {
            "file": "updates/" + name,
            "state": "pending",
            "content": content,
            "attempts": [],
            "history_commit": None,
        }
        changes.append(change)
    check_secrets(run, {change["file"]: canonical(change["content"])})
    write_record(run, record)
    path = run_path(record["run_id"]) + "/" + change["file"]
    line = index_entry(record, path) | {
        "kind": "update",
        "updated_at": change["content"]["updated_at"],
        "integration_state": integration_state,
    }
    try:
        commit = history.publish_files(
            record=record,
            immutable={path: canonical(change["content"])},
            identity_path=path,
            index_line=line,
            message=f"history: update {record['run_id']}",
            date=change["content"]["updated_at"],
        )
        change["state"], change["history_commit"] = "published", commit
    except HistoryError as exc:
        change["state"] = (
            "unknown"
            if isinstance(exc, PublishUnknown)
            else "pending"
            if isinstance(exc, (Deferred, GhUnavailable, BranchMissing))
            else "failed"
        )
        raise
    finally:
        change["attempts"].extend(history.attempts)
        write_record(run, record)
    return HistoryResult(
        "HISTORY_RUN_UPDATED", {"run_id": record["run_id"], "history_commit": commit, "file": change["file"]}
    )
