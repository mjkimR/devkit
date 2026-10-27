"""Host collection exercises real Git sources and injected limits without worker publication."""

from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli
from spec_support.scope import git, write

from devkit_spec.features.scope import Deadline, auto_register, open_session, register
from devkit_spec.features.scope.models.observation import CollectionOptions
from devkit_spec.features.scope.repositories import collection_git
from devkit_spec.features.scope.repositories.collection_git import InputLimitError
from devkit_spec.features.scope.repositories.source import ReadBudget, ReaderPath, TreeReader
from devkit_spec.features.scope.services import collection
from devkit_spec.features.scope.services.collection import Collector
from devkit_spec.features.scope.services.declarations import from_spec
from devkit_spec.features.scope.usecases.collection import CollectScopesUseCase

UNIT = "specs/2026-10/20261025-a"


def base_repo(path: Path) -> Path:
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    write(path, ".devkit/config.toml", "")
    write(path, "src/shared.py", "shared = 1\n")
    git(path, "add", ".")
    git(path, "commit", "-qm", "base")
    return path


def task(path: Path, slug: str = "a") -> str:
    unit = f"specs/2026-10/20261025-{slug}"
    write(path, f"{unit}/spec.md", f"---\nid: SPEC-{slug}\nstatus: planned\n---\n")
    write(path, f"{unit}/tasks.md", "- [ ] **Task 1**: change\n  - **_Boundary**: `src/shared.py`\n")
    write(path, f"{unit}/reconcile.md", "---\ntargets: []\n---\n")
    git(path, "add", ".")
    git(path, "commit", "-qm", f"task {slug}")
    return unit


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = base_repo(tmp_path / "repo")
    git(root, "checkout", "-qb", "dev-a")
    task(root)
    return root


def collect(repo: Path, mode: str = "worktrees", **kwargs):
    return CollectScopesUseCase().execute(repo, CollectionOptions(mode=mode, **kwargs)).data


def invoke(repo: Path, *args: str):
    return CliRunner().invoke(cli, ["spec", "scope", "collect", *args, "-w", str(repo)])


def test_pinned_tree_uses_target_entrypoints_and_kinds_from_same_commit(repo: Path) -> None:
    write(repo, "docs/capabilities/x/CAP-X-a.md", "---\nentrypoints: [src/shared.py]\n---\n")
    write(repo, f"{UNIT}/tasks.md", "<!-- devkit:skeleton -->\n")
    write(repo, f"{UNIT}/reconcile.md", "---\ntargets:\n  - file: docs/capabilities/x/CAP-X-a.md\n---\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "targets")
    sha = git(repo, "rev-parse", "HEAD")
    write(repo, "docs/capabilities/x/CAP-X-a.md", "---\nentrypoints: [src/dirty.py]\n---\n")
    source = TreeReader(repo, sha, Deadline(5), ReadBudget())
    scope = from_spec(ReaderPath(source), UNIT)
    assert {p.path for p in scope.code} == {"src/shared.py"}
    assert str(scope.code[0].kind) == "file"


def test_modes_separate_snapshots_refs_and_live_dirty_paths(repo: Path) -> None:
    write(repo, "src/untracked.py", "new = 1\n")
    assert collect(repo, "snapshot")["observations"] == []
    refs = collect(repo, "refs", base="main")
    assert all("dirty" not in item["observed_layers"] for item in refs["observations"])
    live = collect(repo, base="main")
    worktree = next(o for o in live["observations"] if o["provenance"]["source"] == "worktree")
    assert "src/untracked.py" in {p["path"] for p in worktree["scope"]["observed"]}
    assert refs["coverage"]["status"] == "complete"
    assert not (repo / ".git/devkit-spec-scope").exists()


def test_staged_unstaged_and_renamed_paths_are_observed(repo: Path) -> None:
    git(repo, "mv", "src/shared.py", "src/moved.py")
    write(repo, "src/moved.py", "changed = 2\n")
    live = collect(repo, base="main")
    item = next(o for o in live["observations"] if o["provenance"]["source"] == "worktree")
    assert {"src/shared.py", "src/moved.py"} <= {p["path"] for p in item["scope"]["observed"]}


def test_token_and_registry_bytes_unchanged(repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev-b", str(linked), "main")
    unit = task(linked, "b")
    register(open_session(linked), unit)
    session = open_session(linked)
    directory = session.location.shared_path
    before = {p: p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    token = session.location.token_path.read_bytes()
    monkeypatch.setattr(
        "devkit_spec.features.scope.repositories.location.load_token", lambda *a, **kw: pytest.fail("token read")
    )
    result = collect(repo, base="main")
    assert len(result["observations"]) >= 2
    assert before == {p: p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    assert session.location.token_path.read_bytes() == token


def test_ref_aliases_deduplicate_only_equivalent_base_ranges(repo: Path) -> None:
    git(repo, "remote", "add", "cloud", str(repo.parent / "absent"))
    git(repo, "update-ref", "refs/remotes/cloud/dev-a", "HEAD")
    data = collect(repo, "refs", base="main")
    assert len(data["observations"]) == 1
    assert data["observations"][0]["aliases"]
    git(repo, "branch", "parent", "HEAD~1")
    # A distinct base SHA changes range provenance even if this fixture's path set is equal.
    git(repo, "update-ref", "refs/remotes/cloud/main", "main")
    git(repo, "symbolic-ref", "refs/remotes/cloud/HEAD", "refs/remotes/cloud/main")
    git(repo, "config", "branch.dev-a.devkitBase", "HEAD")
    data = collect(repo, "refs")
    assert len(data["observations"]) == 2


def test_diverged_refs_preserve_both_pinned_observations(repo: Path) -> None:
    git(repo, "remote", "add", "cloud", str(repo.parent / "absent"))
    old = git(repo, "rev-parse", "HEAD")
    git(repo, "update-ref", "refs/remotes/cloud/dev-a", old)
    write(repo, "src/local.py", "local = 1\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "local")
    data = collect(repo, "refs", base="main")
    assert len(data["observations"]) == 2
    assert len({o["provenance"]["sha"] for o in data["observations"]}) == 2


def test_terminal_worktree_dirty_changes_remain_visible(repo: Path) -> None:
    write(repo, f"{UNIT}/spec.md", "---\nid: SPEC-a\nstatus: completed\n---\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "completed")
    clean = collect(repo, base="main")
    assert clean["observations"] == []
    write(repo, "src/private.py", "private = 1\n")
    data = collect(repo, base="main")
    candidate = next(c for c in data["inventory"] if c["worktree"])
    assert candidate["activity"] == "unknown" and candidate["reason"] == "terminal-dirty"
    assert data["observations"]


def test_other_host_record_path_is_not_read(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    session = open_session(repo)
    record = register(session, UNIT).record
    adapter = collection.CollectionRegistry
    original = adapter.query

    def query(self, namespace, deadline):
        records, problems = original(self, namespace, deadline)
        return [
            r.with_(hostname=socket.gethostname() + "-elsewhere", worktree="/never/open") for r in records
        ], problems

    monkeypatch.setattr(adapter, "query", query)
    data = collect(repo, "snapshot")
    assert data["observations"][0]["provenance"]["worktree"] == "/never/open"
    assert data["observations"][0]["provenance"]["published_at"] == record.updated_at


@pytest.mark.parametrize(
    ("args", "targets"),
    [
        (("--mode", "snapshot", "--fetch", "origin"), ["--mode", "--fetch"]),
        (("--timeout", "0"), ["--timeout"]),
        (("--source-timeout", "301"), ["--source-timeout"]),
        (("--fetch", "unknown"), None),
    ],
)
def test_invalid_arguments_use_json_boundary(repo: Path, args: tuple[str, ...], targets: list[str] | None) -> None:
    result = invoke(repo, *args, "--format", "json")
    assert result.exit_code == 2
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "ARGUMENT_INVALID"
    if targets is not None:
        assert error["advisory"]["target_files"] == targets


def test_an_unknown_mode_is_a_usage_error(repo: Path) -> None:
    result = invoke(repo, "--mode", "bad", "--format", "json")
    assert result.exit_code == 2 and "snapshot" in result.output  # click lists the choices


def test_unknown_base_partial_strict_and_text_contract(repo: Path) -> None:
    normal = invoke(repo, "--mode", "refs", "--base", "missing", "--format", "json")
    strict = invoke(repo, "--mode", "refs", "--base", "missing", "--format", "json", "--strict")
    assert normal.exit_code == 0 and strict.exit_code == 1
    data = json.loads(normal.stdout)
    assert data["coverage"]["status"] == "partial"
    assert data["notices"][0]["code"] == "SPEC_SCOPE_COLLECTION_PARTIAL"
    result = invoke(repo, "--mode", "refs", "--base", "main")
    assert "[SCOPE_OBSERVATION:" in result.stdout and "[SUMMARY:" in result.stdout
    assert "SCOPE_ACK" not in result.stdout


def test_no_fetch_does_not_invoke_network_and_failed_fetch_keeps_cached_refs(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repo, "remote", "add", "cloud", str(repo.parent / "missing"))
    git(repo, "update-ref", "refs/remotes/cloud/dev-a", "HEAD")
    original = collection.git
    seen = []

    def checked(root, *args, **kwargs):
        seen.append(args)
        return original(root, *args, **kwargs)

    monkeypatch.setattr(collection, "git", checked)
    assert collect(repo, "refs", base="main")["observations"]
    assert not any(args[0] == "fetch" for args in seen)
    data = collect(repo, "refs", base="main", fetch=("cloud",))
    assert any(args[0] == "fetch" for args in seen)
    assert data["coverage"]["layers"]["fetch"][0]["status"] == "failed"
    assert data["observations"]


def test_git_output_and_declaration_inputs_are_bounded(repo: Path) -> None:
    with pytest.raises(InputLimitError):
        collection_git.git(repo, "show", f"HEAD:{UNIT}/tasks.md", deadline=Deadline(5), limit=8)
    write(repo, f"{UNIT}/tasks.md", "x" * (1024 * 1024 + 1))
    data = collect(repo, base="main")
    assert data["coverage"]["status"] == "partial"
    assert any(p["reason"] == "input-limit" for p in data["coverage"]["problems"])


def test_comparison_limit_retains_complete_pairs_and_explicit_gap(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked = tmp_path / "b"
    git(repo, "worktree", "add", "-qb", "dev-b", str(linked), "main")
    task(linked, "b")
    monkeypatch.setattr(collection, "MAX_EVIDENCE", 0)
    data = collect(repo, "refs", base="main")
    assert data["pairs"] == []
    assert data["coverage"]["comparisons_complete"] is False
    assert any(p["reason"] == "result-limit" for p in data["coverage"]["problems"])


def test_total_deadline_cannot_be_spent_inside_comparison(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = Collector.read_sources

    def expired(self):
        original(self)
        self.compute._end = 0

    monkeypatch.setattr(Collector, "read_sources", expired)
    data = collect(repo, base="main")
    assert data["coverage"]["comparisons_complete"] is False or data["coverage"]["pairs_total"] == 0


def test_update_hidden_but_direct_help_works() -> None:
    runner = CliRunner()
    assert "  update " not in runner.invoke(cli, ["spec", "scope", "--help"]).stdout
    assert runner.invoke(cli, ["spec", "scope", "update", "--help"]).exit_code == 0


def test_creation_failure_and_logging_failure_are_silent(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked = tmp_path / "b"
    git(repo, "worktree", "add", "-qb", "dev-b", str(linked))
    from devkit_spec.features.scope.usecases import flow

    def broken(*args, **kwargs):
        raise OSError("injected")

    monkeypatch.setattr(flow, "register", broken)
    assert auto_register(linked, UNIT, source="spec-new") == (None, [])
    with monkeypatch.context() as local:
        local.setattr(flow._log, "info", broken)
        result = auto_register(linked, UNIT, source="handoff")
    assert result == (None, [])


def test_unreadable_live_declaration_falls_back_to_pinned_scope(repo: Path) -> None:
    write(repo, f"{UNIT}/reconcile.md", "---\ntargets: malformed\n---\n")
    data = collect(repo, base="main")
    live = next(o for o in data["observations"] if o["provenance"]["source"] == "worktree")
    assert live["provenance"]["declarations_fallback"] is True
    assert "live-declarations" in live["missing_layers"]
    assert live["scope"]["code"][0]["path"] == "src/shared.py"


def test_successful_explicit_fetch_reads_published_ref_only(repo: Path, tmp_path: Path) -> None:
    remote = tmp_path / "remote.git"
    git(repo.parent, "clone", "--bare", str(repo), str(remote))
    git(repo, "remote", "add", "cloud", str(remote))
    data = collect(repo, "refs", fetch=("cloud",), base="main")
    assert data["coverage"]["layers"]["fetch"][0]["status"] == "complete"
    assert git(repo, "rev-parse", "refs/remotes/cloud/dev-a") == git(repo, "rev-parse", "dev-a")
    assert not (repo / ".git/devkit-spec-scope").exists()


def test_result_byte_cap_reports_partial_instead_of_serializing_unbounded_evidence(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(collection, "MAX_REPORT_BYTES", 8192)
    monkeypatch.setattr(collection, "RESERVED_BYTES", 4096)
    write(
        repo,
        f"{UNIT}/tasks.md",
        "- [ ] **Task 1**: change\n  - **_Boundary**: " + ", ".join(f"`src/p{i}.py`" for i in range(500)),
    )
    data = collect(repo, base="main")
    assert len(collection.encoded(data)) <= 8192
    assert data["coverage"]["status"] == "partial"
    assert any(p["reason"] == "result-limit" for p in data["coverage"]["problems"])


def test_source_timeout_retains_inventory_with_explicit_gap(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(self, candidate):
        raise collection.ScopeTimeoutError("injected source timeout")

    monkeypatch.setattr(Collector, "observe", timeout)
    data = collect(repo, "refs", base="main")
    assert data["inventory"] and not data["observations"]
    assert any(p["reason"] == "source-timeout" for p in data["coverage"]["problems"])


@pytest.mark.parametrize("folder", ["project", " project "])
def test_nested_workspace_observes_workspace_relative_paths(tmp_path: Path, folder: str) -> None:
    root = base_repo(tmp_path / "root")
    nested = root / folder
    nested.mkdir()
    write(nested, ".devkit/config.toml", "")
    write(nested, "src/shared.py", "nested = 1\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "nested base")
    git(root, "checkout", "-qb", "dev-a")
    task(nested)
    data = collect(nested, "refs", base="main")
    observation = data["observations"][0]
    assert observation["scope"]["code"][0]["path"] == "src/shared.py"
    assert all(not p["path"].startswith("project/") for p in observation["scope"]["observed"])


def test_stale_branch_unit_marker_does_not_attribute_changes_to_other_task(repo: Path) -> None:
    other = task(repo, "b")
    git(repo, "config", "branch.dev-a.devkitUnit", other)
    write(repo, "src/private.py", "private = 1\n")
    data = collect(repo, base="main")
    live = next(o for o in data["observations"] if o["provenance"]["source"] == "worktree")
    assert live["task_key"] is None
    assert "src/private.py" in {p["path"] for p in live["scope"]["observed"]}
    assert data["coverage"]["status"] == "partial"


def test_bounded_git_kills_slow_process_group(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    fake = tmp_path / "git"
    fake.write_text("#!/bin/sh\nsleep 10\n")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + ":/usr/bin:/bin")
    started = time.monotonic()
    with pytest.raises(collection.ScopeTimeoutError):
        collection_git.git(tmp_path, "status", deadline=Deadline(0.05))
    assert time.monotonic() - started < 2


def test_leading_and_trailing_whitespace_in_git_paths_is_preserved(repo: Path) -> None:
    paths = [" leading.py", "src/trailing .py", "src/name\nwith-newline.py"]
    for path in paths:
        write(repo, path, "changed = 1\n")
    git(repo, "add", ".")
    data = collect(repo, base="main")
    live = next(o for o in data["observations"] if o["provenance"]["source"] == "worktree")
    observed = {p["path"] for p in live["scope"]["observed"]}
    assert " leading.py" in observed and "src/trailing .py" in observed
    assert any(p["reason"] == "invalid-path" for p in live["scope"]["unresolved"])


def test_custom_registration_alias_reconciles_with_live_anchor_and_caps_refs(repo: Path, tmp_path: Path) -> None:
    linked = tmp_path / "linked"
    git(repo, "worktree", "add", "-qb", "dev-b", str(linked), "main")
    unit = task(linked, "b")
    write(linked, "src/pre.py", "before = 1\n")
    git(linked, "add", ".")
    git(linked, "commit", "-qm", "before registration")
    cap = git(linked, "rev-parse", "HEAD")
    register(open_session(linked), unit, task_id="custom-running-task")
    data = collect(repo, base="main")
    live = [
        o
        for o in data["observations"]
        if o["provenance"].get("unit") == unit and o["provenance"]["source"] != "snapshot"
    ]
    snapshot = next(
        o for o in data["observations"] if o["provenance"].get("registered_task_id") == "custom-running-task"
    )
    assert snapshot["task_key"] and all(o["task_key"] == snapshot["task_key"] for o in live)
    assert all(o["provenance"]["cap"] == cap for o in live)
    assert all("src/pre.py" not in {p["path"] for p in o["scope"]["observed"]} for o in live)
    assert snapshot["provenance"]["comparison_eligible"] is False
    snapshot_only = collect(repo, "snapshot")["observations"][0]
    assert snapshot_only["task_key"] is None
    assert snapshot_only["provenance"]["registered_task_id"] == "custom-running-task"


def test_timeout_kills_descendant_even_after_parent_exit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    fake = tmp_path / "git"
    marker = tmp_path / "survived"
    fake.write_text(f"#!/bin/sh\n(sleep 0.3; touch '{marker}') &\nexit 0\n")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + ":/usr/bin:/bin")
    with pytest.raises(collection.ScopeTimeoutError):
        collection_git.git(tmp_path, "status", deadline=Deadline(0.05))
    time.sleep(0.4)
    assert not marker.exists()


def test_registered_terminal_clean_snapshot_is_not_compared_with_active_task(repo: Path, tmp_path: Path) -> None:
    register(open_session(repo), UNIT)
    write(repo, f"{UNIT}/spec.md", "---\nid: SPEC-a\nstatus: completed\n---\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "finish a")
    linked = tmp_path / "b"
    git(repo, "worktree", "add", "-qb", "dev-b", str(linked), "main")
    task(linked, "b")
    data = collect(repo, base="main")
    snapshot = next(o for o in data["observations"] if o["provenance"]["source"] == "snapshot")
    assert snapshot["provenance"]["comparison_eligible"] is False
    assert all(p["a"] != snapshot["observation_id"] and p["b"] != snapshot["observation_id"] for p in data["pairs"])
    assert next(c for c in data["inventory"] if c["source_id"] == snapshot["observation_id"])["activity"] == "inactive"


def test_dense_text_with_long_observation_ids_respects_result_limit(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import io
    from contextlib import redirect_stdout

    from devkit_spec.features.scope.cli.collection_output import render
    from devkit_spec.features.scope.models.model import Granularity, ScopePath, ScopeSet, Source, Stage
    from devkit_spec.features.scope.models.observation import Observation

    limit = 64 * 1024
    monkeypatch.setattr(collection, "MAX_REPORT_BYTES", limit)
    monkeypatch.setattr(collection, "RESERVED_BYTES", 4096)
    observer = Collector(repo, CollectionOptions())
    prefix = "src/" + "nested/" * 8
    first = ScopeSet(
        "a", code=[ScopePath(prefix + str(i), Granularity.DIR, Source.DECLARED_CODE, Stage.SPEC) for i in range(10)]
    )
    second = ScopeSet(
        "b",
        code=[
            ScopePath(prefix + f"{i}/file{j}.py", Granularity.FILE, Source.DECLARED_CODE, Stage.SPEC)
            for i in range(10)
            for j in range(10)
        ],
    )
    one = Observation(
        "worktree:/" + "valid-nested/" * 60 + "a",
        json.dumps(["ns", "SPEC-a", "specs/a"]),
        first,
        {"source": "worktree"},
    )
    two = Observation(
        "worktree:/" + "valid-nested/" * 60 + "b",
        json.dumps(["ns", "SPEC-b", "specs/b"]),
        second,
        {"source": "worktree"},
    )

    def discover():
        observer.discovered_count = 2
        observer.observations = [one, two]

    monkeypatch.setattr(observer, "discover", discover)
    monkeypatch.setattr(observer, "read_sources", lambda: None)
    data = observer.execute().data
    output = io.StringIO()
    with redirect_stdout(output):
        render(data)
    assert len(output.getvalue().encode()) <= limit
    assert data["coverage"]["status"] == "partial" and not data["coverage"]["comparisons_complete"]


def test_ambiguous_dirty_worktree_prevents_terminal_snapshot_exclusion(repo: Path) -> None:
    register(open_session(repo), UNIT)
    write(repo, f"{UNIT}/spec.md", "---\nid: SPEC-a\nstatus: completed\n---\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "terminal")
    write(repo, f"{UNIT}/spec.md", "---\nstatus: malformed\n---\n")
    data = collect(repo, base="main")
    snapshot = next(o for o in data["observations"] if o["provenance"]["source"] == "snapshot")
    assert snapshot["provenance"].get("comparison_eligible", True)
    assert data["coverage"]["status"] == "partial"


def test_symlink_loop_is_partial_coverage_not_unexpected_failure(repo: Path) -> None:
    declaration = repo / UNIT / "tasks.md"
    declaration.unlink()
    declaration.symlink_to("tasks.md")
    data = collect(repo, base="main")
    assert data["coverage"]["status"] == "partial"
    assert data["observations"]


def test_text_names_sources_relative_and_a_dirty_base_checkout_is_no_gap(tmp_path: Path) -> None:
    root = base_repo(tmp_path / "repo")
    git(root, "checkout", "-qb", "dev-a")
    task(root)
    git(root, "checkout", "-q", "main")
    task(root, "b")  # the base holds a committed unit too
    write(root, "src/shared.py", "dirty = 1\n")  # and uncommitted changes
    linked = tmp_path / "wt-a"
    git(root, "worktree", "add", "-q", str(linked), "dev-a")
    result = invoke(root, "--format", "json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    ids = [item["source_id"] for item in data["inventory"]]
    assert "worktree:." in ids and "worktree:../wt-a" in ids
    base = next(item for item in data["inventory"] if item["source_id"] == "worktree:.")
    assert (base["activity"], base["reason"]) == ("inactive", "base-checkout")
    assert "SPEC_SCOPE_COLLECTION_PARTIAL" not in [notice["code"] for notice in data["notices"]]
    text = invoke(root).stdout
    assert "/" + str(tmp_path).strip("/") not in text  # no absolute path
    observation = next(line for line in text.splitlines() if line.startswith("[SCOPE_OBSERVATION:"))
    assert " task=SPEC-a unit=specs/2026-10/20261025-a " in observation and "[" not in observation[1:]


def test_partial_coverage_lists_each_gap_once_with_targets(repo: Path) -> None:
    collector = Collector(repo, CollectionOptions(mode="worktrees"))
    collector.problem("refs/heads/dev-a", "unknown-base")
    collector.problem("refs/heads/dev-a", "unknown-base")
    assert collector.problem_count == 1 and len(collector.problems) == 1
