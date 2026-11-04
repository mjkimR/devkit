"""Run only with explicit authority for an existing throwaway GitHub repository/branch.

Creates and retains a dedicated test history branch; never deletes a remote resource.
Output contains status/SHAs and fixture IDs only, never credentials or real project content.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote

from devkit_agt.features.maintenance_history.models.records import IDENTITY, ROOT_COMMIT, ROOT_DATE, ROOT_README
from devkit_agt.features.maintenance_history.repositories.config import destination
from devkit_agt.features.maintenance_history.services.publication import GitHubHistory, publish, update
from devkit_agt.features.maintenance_history.services.runs import finish, start


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--authority", required=True)
    args = parser.parse_args()
    if not args.branch.startswith("devkit-history-exercise-") or not args.authority.strip():
        parser.error("Use an explicitly authorized devkit-history-exercise-* branch")
    observations: dict[str, object] = {
        "kind": "live GitHub exercise",
        "repository": args.repository,
        "branch": args.branch,
    }
    scratch = Path(__file__).resolve().parents[4] / "tmp"
    scratch.mkdir(exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="devkit-history-live-", dir=scratch))
    for command in (
        ["init", "-q"],
        ["config", "user.name", "devkit history exercise"],
        ["config", "user.email", "exercise@devkit.invalid"],
    ):
        subprocess.run(["git", "-C", str(root), *command], capture_output=True, check=True)
    (root / "fixture.txt").write_text("sanitized live exercise fixture\n")
    subprocess.run(["git", "-C", str(root), "add", "fixture.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "sanitized fixture"], check=True)
    repository, branch = destination(root, args.repository, args.branch)
    client = GitHubHistory(repository, branch)
    initialized = client.initialize(args.authority)
    observations["root_sha"] = initialized.data["root_sha"]
    blob_payload = {"encoding": "base64", "content": base64.b64encode(b"sanitized repeated object\n").decode()}
    first = client.ok("POST", "git/blobs", blob_payload)
    second = client.ok("POST", "git/blobs", blob_payload)
    assert first["sha"] == second["sha"]
    observations["repeated_blob_post_same_sha"] = True
    tree_payload = {
        "tree": [{"path": "README.md", "mode": "100644", "type": "blob", "content": ROOT_README.decode()}]
    }
    tree_one = client.ok("POST", "git/trees", tree_payload)
    tree_two = client.ok("POST", "git/trees", tree_payload)
    assert tree_one["sha"] == tree_two["sha"]
    observations["repeated_tree_post_same_sha"] = True
    commit_payload = {
        "message": "Initialize devkit maintenance history\n",
        "tree": tree_one["sha"],
        "parents": [],
        "author": IDENTITY | {"date": ROOT_DATE},
        "committer": IDENTITY | {"date": ROOT_DATE},
    }
    commit_one = client.ok("POST", "git/commits", commit_payload)
    commit_two = client.ok("POST", "git/commits", commit_payload)
    assert commit_one["sha"] == commit_two["sha"] == ROOT_COMMIT
    observations["repeated_commit_post_same_sha"] = True
    report = root / "report.md"
    started = start(
        root,
        repository=repository,
        playbook="weekly-report",
        scope="sanitized live exercise",
        into=root / "runs",
        report=report,
        zone="UTC",
        supersedes=(),
        prior_runs=(),
    )
    run = Path(started.data["path"])
    report.write_text("# Sanitized live history exercise\nNo real project content or credentials.\n")
    finish(run, outcome="completed", result="live fixture", report=None, applied_commits=(), follow_ups=())
    result = publish(client, run, args.authority, (), repository)
    duplicate = publish(GitHubHistory(repository, branch), run, args.authority, (), repository)
    assert result.data["history_commit"] == duplicate.data["history_commit"]
    observations["duplicate_publication_same_commit"] = True
    update(GitHubHistory(repository, branch), run, args.authority, "fixture integrated", ())
    head = client.head()
    assert head
    same = client.request("PATCH", "git/refs/heads/" + quote(branch, safe=""), {"sha": head}, reference=True)
    observations["same_sha_ref_status"] = same.status
    assert same.status == 200
    stale = client.request(
        "PATCH", "git/refs/heads/" + quote(branch, safe=""), {"sha": ROOT_COMMIT}, reference=True
    )
    observations["non_fast_forward_ref_status"] = stale.status
    assert stale.status in (409, 422)
    assert client.head() == head
    missing = client.request("GET", "contents/nonexistent-fixture?ref=" + head)
    observations["missing_file_status"] = missing.status
    assert missing.status == 404
    absent_ref = client.request("GET", "git/ref/heads/" + quote(branch + "-absent", safe=""))
    observations["missing_ref_status"] = absent_ref.status
    assert absent_ref.status == 404
    assert client.listing("weekly-report", None, None, False, 20).data["count"] >= 1
    fetched = client.get(run.name, "report.md")
    assert base64.b64decode(fetched.data["content"]) == report.read_bytes()
    observations["run_id"] = run.name
    observations["head_sha"] = head
    observations["retrieval_and_amendment"] = "passed"
    observations["cleanup"] = "branch retained; no deletion authorized or performed"
    # A readable repository's missing file/ref is confirmed above. An inaccessible/private repository
    # response must be observed with separately supplied access credentials; this fixture cannot infer it.
    observations["unverified"] = ["private repository without read permission", "rate-limit service responses"]
    print(json.dumps(observations, sort_keys=True))


if __name__ == "__main__":
    main()
