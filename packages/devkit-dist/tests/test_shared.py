"""Shared artifact semantics and filesystem boundaries using isolated Git fixtures."""

from __future__ import annotations

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from devkit.shared import PutRequest
from devkit.shared.cli import cli
from devkit.shared.errors import AdapterError, ExclusionError, ExpiredError, InputError, MissingError, SharedError
from devkit.shared.local import LocalAdapter, discover
from devkit.shared.mcp import tools
from devkit.shared.service import adapter
from devkit_core.core.git import run_git


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    run_git(root, "init", "-b", "main")
    run_git(root, "config", "user.name", "Fixture")
    run_git(root, "config", "user.email", "fixture@example.test")
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text("schema = 1\n")
    run_git(root, "add", ".devkit/config.toml")
    run_git(root, "commit", "-m", "fixture")
    return root


@pytest.fixture
def request_data():
    return PutRequest("proposal-review", "example", "a" * 40, "en", "# Report\n")


def test_live_retry_expiry_and_cleanup(repository, request_data):
    now = datetime(2026, 1, 1, tzinfo=UTC)
    selected = LocalAdapter(discover(repository), clock=lambda: now)
    first = selected.put(request_data)
    assert first.local_path is not None
    assert selected.put(request_data) == first
    now += timedelta(days=7)
    before = Path(first.local_path).read_bytes()
    with pytest.raises(ExpiredError):
        selected.get(first.metadata.artifact_uri)
    assert selected.list("proposal-review", "example").entries == ()
    assert Path(first.local_path).read_bytes() == before
    assert selected.sweep().entries == (first.metadata.artifact_uri,)
    assert Path(first.local_path).exists()
    second = selected.put(request_data)
    assert second.metadata.artifact_uri != first.metadata.artifact_uri
    assert second.metadata.created_at != first.metadata.created_at
    selected.sweep(apply=True)
    with pytest.raises(MissingError):
        selected.get(first.metadata.artifact_uri)


def test_linked_cli_mcp_and_clone_isolation(repository, request_data, tmp_path):
    linked = tmp_path / "linked"
    run_git(repository, "worktree", "add", "-b", "worker", str(linked))
    result = CliRunner().invoke(
        cli,
        [
            "put",
            "--kind",
            request_data.kind,
            "--slug",
            request_data.slug,
            "--source-sha",
            request_data.source_sha,
            "--language",
            "en",
            "--workspace-root",
            str(linked),
            "--format",
            "json",
        ],
        input=request_data.content,
    )
    assert result.exit_code == 0, result.output
    value = json.loads(result.output)

    async def no_form(*args):
        raise AssertionError("no form allowed")

    tool = next(t for t in tools(repository) if t.name == "shared_get")

    async def invoke():
        return await tool.invoke({"artifact_uri": value["artifact_uri"]}, no_form)

    read = asyncio.run(invoke())
    assert read["metadata"] == value["metadata"]
    assert read["content"] == request_data.content
    assert run_git(repository, "status", "--porcelain", "--untracked-files=normal") == b""
    assert run_git(linked, "status", "--porcelain", "--untracked-files=normal") == b""
    assert (repository / ".git/info/exclude").read_text().count("/.devkit/.shared/") == 1
    clone = tmp_path / "clone"
    run_git(repository, "clone", str(repository), str(clone))
    other = adapter(clone)
    assert other.repository_namespace != value["repository_namespace"]
    with pytest.raises(InputError):
        other.get(value["artifact_uri"])


@pytest.mark.parametrize("case", ["visible", "tracked", "symlink"])
def test_exclusion_refuses_without_writes(repository, request_data, case, tmp_path):
    path = repository / ".devkit/.shared"
    if case == "symlink":
        path.symlink_to(tmp_path)
    else:
        path.mkdir()
        (path / "foreign").write_text("foreign")
        if case == "tracked":
            run_git(repository, "add", ".devkit/.shared/foreign")
    exclude = repository / ".git/info/exclude"
    before = exclude.read_bytes()
    with pytest.raises((ExclusionError, SharedError)):
        adapter(repository).put(request_data)
    assert exclude.read_bytes() == before
    assert not (repository / ".git/devkit-mcp.lock").exists()


def test_foreign_linked_content_refused(repository, request_data, tmp_path):
    linked = tmp_path / "linked"
    run_git(repository, "worktree", "add", "-b", "worker", str(linked))
    foreign = linked / ".devkit/.shared"
    foreign.mkdir()
    (foreign / "visible").write_text("keep visible")
    with pytest.raises(ExclusionError):
        adapter(repository).put(request_data)
    assert not (repository / ".devkit/.shared").exists()


def test_concurrent_identical_puts(repository, request_data):
    selected = adapter(repository)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: selected.put(request_data), range(16)))
    assert len({r.metadata.artifact_uri for r in results}) == 1
    assert len({r.metadata.created_at for r in results}) == 1
    other = selected.put(PutRequest("proposal-review", "example", "a" * 40, "en", "different"))
    assert other.metadata.artifact_uri != results[0].metadata.artifact_uri


def test_atomic_publication_failure(repository, request_data):
    selected = adapter(repository)
    with (
        patch("devkit.shared.local.os.replace", side_effect=OSError("injected publication interruption")),
        pytest.raises(SharedError),
    ):
        selected.put(request_data)
    assert selected.list("proposal-review", "example").entries == ()
    assert selected.put(request_data).content == request_data.content


def test_readonly_operations_and_registry_untouched(repository, request_data):
    selected = adapter(repository)
    first = selected.put(request_data)
    assert first.local_path is not None
    registry = repository / ".devkit/scope-fixture"
    registry.write_bytes(b"authority token revision journal")
    store = Path(first.local_path).parent
    for path in store.iterdir():
        path.chmod(0o400)
    store.chmod(0o500)
    try:
        assert selected.get(first.metadata.artifact_uri) == first
        assert len(selected.list("proposal-review", "example").entries) == 1
        assert selected.sweep().entries == ()
        assert registry.read_bytes() == b"authority token revision journal"
    finally:
        store.chmod(0o700)
        for path in store.iterdir():
            path.chmod(0o600)


def test_absent_reads_never_initialize(repository):
    selected = adapter(repository)
    before = (repository / ".git/info/exclude").read_bytes()
    assert selected.list("proposal-review", "example").entries == ()
    assert selected.sweep().entries == ()
    with pytest.raises(MissingError):
        selected.get(f"shared://{selected.repository_namespace}/" + "a" * 32)
    assert not (repository / ".devkit/.shared").exists()
    assert (repository / ".git/info/exclude").read_bytes() == before


def test_corruption_and_missing_lock_fail_closed(repository, request_data):
    selected = adapter(repository)
    value = selected.put(request_data)
    assert value.local_path is not None
    path = Path(value.local_path)
    path.write_text("broken")
    with pytest.raises(SharedError):
        selected.get(value.metadata.artifact_uri)
    with pytest.raises(SharedError):
        selected.list("proposal-review", "example")
    assert selected.sweep(apply=True).invalid == (path.name,)
    assert path.exists()
    (path.parent / ".lock").unlink()
    with pytest.raises(SharedError):
        selected.list("proposal-review", "example")


@pytest.mark.parametrize(
    "changes",
    [
        {"slug": "../escape"},
        {"source_sha": "main"},
        {"language": "fr"},
        {"kind": "scope"},
        {"content": "a" * (1024 * 1024 + 1)},
    ],
)
def test_invalid_put(repository, request_data, changes):
    from dataclasses import asdict

    with pytest.raises(InputError):
        adapter(repository).put(PutRequest(**{**asdict(request_data), **changes}))
    assert not (repository / ".devkit/.shared").exists()


def test_adapter_config_and_registration(repository, monkeypatch):
    (repository / ".devkit/config.local.toml").write_text('[shared]\nadapter="missing"\n')
    with pytest.raises(AdapterError):
        adapter(repository)
    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "local")
    assert adapter(repository).adapter_id == "local"

    class Entry:
        name = "local"

    monkeypatch.setattr("devkit.shared.service.metadata.entry_points", lambda **_: [Entry()])
    with pytest.raises(AdapterError):
        adapter(repository)


def test_pagination_and_sweep_bound(repository, request_data):
    now = datetime(2026, 1, 1, tzinfo=UTC)
    selected = LocalAdapter(discover(repository), clock=lambda: now)
    for i in range(103):
        selected.put(PutRequest("proposal-review", "example", "a" * 40, "en", str(i)))
    first = selected.list("proposal-review", "example")
    second = selected.list("proposal-review", "example", cursor=first.cursor)
    assert len(first.entries) == 100 and len(second.entries) == 3
    assert not set(first.entries) & set(second.entries)
    now += timedelta(days=7)
    sweep = selected.sweep(apply=True)
    assert len(sweep.entries) == 100 and sweep.cursor
    assert len(selected.sweep(apply=True, cursor=sweep.cursor).entries) == 3


def test_public_entry_point_conformance(repository, monkeypatch):
    from types import SimpleNamespace

    from devkit.shared.conformance import assert_conformance

    now = datetime(2026, 1, 1, tzinfo=UTC)

    class TestAdapter(LocalAdapter):
        adapter_id = "transactional-test"

        def __init__(self, context):
            super().__init__(context, clock=lambda: now)

    entry = SimpleNamespace(name="transactional-test", load=lambda: TestAdapter)
    monkeypatch.setattr("devkit.shared.service.metadata.entry_points", lambda **_: [entry])
    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "transactional-test")
    selected = adapter(repository)

    def advance(delta):
        nonlocal now
        now += delta

    assert_conformance(selected, advance)


@pytest.mark.parametrize("case", ["duplicate", "unloadable", "malformed"])
def test_invalid_adapter_registration(repository, monkeypatch, case):
    from types import SimpleNamespace

    def load():
        if case == "unloadable":
            raise ImportError("fixture")
        return lambda context: object()

    entry = SimpleNamespace(name="test", load=load)
    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "test")
    monkeypatch.setattr(
        "devkit.shared.service.metadata.entry_points", lambda **_: [entry, entry] if case == "duplicate" else [entry]
    )
    with pytest.raises(AdapterError):
        adapter(repository)


def test_timeout_and_access_codes(repository, request_data, monkeypatch):
    from devkit.shared.errors import AccessError, TimeoutError
    from devkit_core.core.deadline import Deadline

    selected = adapter(repository)
    first = selected.put(request_data)
    assert first.local_path is not None
    original_open = os.open

    def denied(path, *args, **kwargs):
        if str(path).endswith(".lock"):
            raise PermissionError("fixture")
        return original_open(path, *args, **kwargs)

    with patch("devkit.shared.local.os.open", side_effect=denied), pytest.raises(AccessError):
        selected.get(first.metadata.artifact_uri)
    monkeypatch.setattr("devkit.shared.local.deadline", lambda: Deadline(0, error=lambda *_: TimeoutError("fixture")))
    with pytest.raises(TimeoutError):
        selected.get(first.metadata.artifact_uri)


def test_sweep_invalid_names_continue(repository, request_data):
    selected = adapter(repository)
    artifact = selected.put(request_data)
    assert artifact.local_path is not None
    root = Path(artifact.local_path).parent
    for i in range(101):
        (root / f"bad-{i:03}").write_text("invalid")
    first = selected.sweep()
    assert first.cursor
    second = selected.sweep(cursor=first.cursor)
    assert len(first.invalid) + len(second.invalid) == 101


def test_scope_records_and_tokens_untouched_by_every_operation(repository, request_data):
    now = datetime(2026, 1, 1, tzinfo=UTC)
    common = repository / ".git"
    registry = common / "devkit-spec-scope"
    registry.mkdir()
    files = [registry / "records.json", registry / "journal.json", common / "devkit-spec-scope-token"]
    before = {}
    for i, path in enumerate(files):
        path.write_bytes(f"fixture-{i}\n".encode())
        before[path] = path.read_bytes()
    selected = LocalAdapter(discover(repository), clock=lambda: now)
    value = selected.put(request_data)
    selected.get(value.metadata.artifact_uri)
    selected.list("proposal-review", "example")
    now += timedelta(days=7)
    selected.sweep()
    selected.sweep(apply=True)
    assert {path: path.read_bytes() for path in files} == before


def test_real_lock_timeout(repository, request_data, monkeypatch):
    import fcntl

    from devkit.shared.errors import TimeoutError
    from devkit_core.core.deadline import Deadline

    selected = adapter(repository)
    value = selected.put(request_data)
    assert value.local_path is not None
    with (Path(value.local_path).parent / ".lock").open("rb") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        monkeypatch.setattr(
            "devkit.shared.local.deadline", lambda: Deadline(0.1, error=lambda *_: TimeoutError("lock fixture"))
        )
        with pytest.raises(TimeoutError):
            selected.get(value.metadata.artifact_uri)


@pytest.mark.parametrize("field", ["source_sha", "language"])
def test_required_put_fields_cannot_be_null(repository, request_data, field):
    from dataclasses import asdict

    request = PutRequest(**{**asdict(request_data), field: None})
    with pytest.raises(InputError):
        adapter(repository).put(request)
    assert not (repository / ".devkit/.shared").exists()


@pytest.mark.parametrize(
    "pattern",
    [
        "!/.devkit/.shared/",
        "!/.DEVKIT/.SHARED/",
        "!/.devkit/.sh[[:lower:]]red/",
        "!/.devkit/.sh[a[:lower:]]red/",
        "!**/.devkit/.shared/",
        "!/.devkit/**/.shared/",
        "!/.devkit/.shared/\n!/.devkit/.shared/artifacts/\n/.devkit/.shared/artifacts/*\n!/.devkit/.shared/artifacts/a*.md",
    ],
)
def test_negative_ignore_refuses_before_any_write(repository, request_data, pattern, monkeypatch):
    from types import SimpleNamespace

    run_git(repository, "config", "core.ignoreCase", "true")
    (repository / ".gitignore").write_text(pattern + "\n")
    before = (repository / ".git/info/exclude").read_bytes()
    monkeypatch.setattr("devkit.shared.local.uuid.uuid4", lambda: SimpleNamespace(hex="a" * 32))
    with pytest.raises(ExclusionError):
        adapter(repository).put(request_data)
    assert (repository / ".git/info/exclude").read_bytes() == before
    assert not (repository / ".git/devkit-mcp.lock").exists()
    assert not (repository / ".devkit/.shared").exists()


def test_concurrent_initialization_waits_for_stable_lock(repository, request_data, monkeypatch):
    import threading

    selected = adapter(repository)
    created, resume = threading.Event(), threading.Event()
    original_mkdir = Path.mkdir

    def paused(path, *args, **kwargs):
        result = original_mkdir(path, *args, **kwargs)
        if path.name == "artifacts" and not created.is_set():
            created.set()
            assert resume.wait(5)
        return result

    monkeypatch.setattr(Path, "mkdir", paused)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(selected.put, request_data)
        assert created.wait(5)
        second = pool.submit(selected.put, request_data)
        assert not second.done()
        resume.set()
        assert first.result().metadata == second.result().metadata


def test_distribution_accepts_shared_table(repository):
    from devkit.core.local_config import read_effective_config
    from devkit.distribution.installation.config import preview_config_template, read_config

    (repository / ".devkit/config.toml").write_text('schema=1\n[shared]\nadapter="local"\n')
    read_config(repository)
    assert read_effective_config(repository).values["shared"]["adapter"] == "local"
    assert preview_config_template(repository).state in ("updated", "unchanged")


@pytest.mark.parametrize("method", ["put", "get", "list", "sweep"])
def test_adapter_rejects_incompatible_signatures(repository, monkeypatch, method):
    from types import SimpleNamespace

    class Malformed(LocalAdapter):
        adapter_id = "fixture"

    setattr(Malformed, method, lambda self: None)
    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "fixture")
    monkeypatch.setattr(
        "devkit.shared.service.metadata.entry_points",
        lambda **_: [SimpleNamespace(name="fixture", load=lambda: Malformed)],
    )
    with pytest.raises(AdapterError):
        adapter(repository)


def test_adapter_rejects_malformed_result(repository, request_data, monkeypatch):
    from types import SimpleNamespace

    class Malformed(LocalAdapter):
        adapter_id = "fixture"

        def put(self, request):
            return {"not": "Artifact"}

    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "fixture")
    monkeypatch.setattr(
        "devkit.shared.service.metadata.entry_points",
        lambda **_: [SimpleNamespace(name="fixture", load=lambda: Malformed)],
    )
    with pytest.raises(AdapterError):
        adapter(repository).put(request_data)


def test_null_stored_metadata_is_corruption(repository, request_data):
    selected = adapter(repository)
    artifact = selected.put(request_data)
    assert artifact.local_path is not None
    path = Path(artifact.local_path)
    raw = path.read_bytes()
    header, body = raw[4:].split(b"\n---\n", 1)
    value = json.loads(header)
    value["source_sha"] = None
    path.write_bytes(b"---\n" + json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n---\n" + body)
    with pytest.raises(SharedError) as error:
        selected.get(artifact.metadata.artifact_uri)
    assert error.value.code == "SHARED_ARTIFACT_INVALID"
    assert selected.sweep(apply=True).invalid == (path.name,)


def test_unrelated_negative_ignore_does_not_block_shared_storage(repository, request_data):
    (repository / ".gitignore").write_text("!unrelated/\n")
    assert adapter(repository).put(request_data).content == request_data.content


def test_adapter_preserves_backend_input_error(repository, monkeypatch):
    from types import SimpleNamespace

    class Rejecting(LocalAdapter):
        adapter_id = "fixture"

        def list(self, kind, slug, *, source_sha=None, language=None, cursor=None, limit=100):
            raise InputError("cursor belongs to another query")

    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "fixture")
    monkeypatch.setattr(
        "devkit.shared.service.metadata.entry_points",
        lambda **_: [SimpleNamespace(name="fixture", load=lambda: Rejecting)],
    )
    with pytest.raises(InputError) as error:
        adapter(repository).list("proposal-review", "validation", cursor="backend-specific:query")
    assert error.value.code == "SHARED_INPUT_INVALID"
