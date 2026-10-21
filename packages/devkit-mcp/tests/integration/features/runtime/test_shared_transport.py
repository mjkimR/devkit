"""Exercise the real SDK handler with fixed execution classes and owning workspace."""

import asyncio

import pytest
from devkit_core.core.git import run_git
from devkit_dist.features.project.repositories.invocation import ExecutionBinding
from devkit_dist.features.shared.mcp import tools
from devkit_mcp.features.runtime.mcp.server import build_server
from mcp import types


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    run_git(root, "init", "-b", "main")
    run_git(root, "config", "user.name", "Fixture")
    run_git(root, "config", "user.email", "fixture@example.test")
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text("schema = 1\n")
    run_git(root, "add", ".devkit")
    run_git(root, "commit", "-m", "fixture")
    return root


def call(server, name, arguments):
    result = asyncio.run(
        server.request_handlers[types.CallToolRequest](
            types.CallToolRequest(
                method="tools/call", params=types.CallToolRequestParams(name=name, arguments=arguments)
            )
        )
    )
    return result.root


def test_local_put_never_elicits_and_cloud_hides_and_refuses(project):
    declared = {tool.name: tool for tool in tools(project)}
    server = build_server(declared, ExecutionBinding(project, project))
    args = dict(kind="proposal-review", slug="test", source_sha="a" * 40, language="en", content="# Test")
    # No request context/session exists: any form elicitation would fail this call.
    result = call(server, "shared_put", args)
    assert not result.isError, result
    assert result.structuredContent["metadata"]["source_sha"] == "a" * 40
    cloud = build_server(declared, ExecutionBinding(project, project), profile="read-only")

    async def list_tools():
        return await cloud.request_handlers[types.ListToolsRequest](types.ListToolsRequest(method="tools/list"))

    listing = asyncio.run(list_tools())
    assert isinstance(listing.root, types.ListToolsResult)
    assert {t.name for t in listing.root.tools} == {"shared_get", "shared_list", "shared_sweep"}
    assert call(cloud, "shared_put", args).isError
    assert call(cloud, "shared_sweep_apply", {}).isError
    assert call(cloud, "shared_sweep", {"apply": True}).isError
    (project / ".devkit/config.local.toml").write_text('[execution]\nenvironment="cloud"\n')
    assert call(server, "shared_put", args).isError
    assert not call(server, "shared_get", {"artifact_uri": result.structuredContent["artifact_uri"]}).isError


def test_read_and_write_use_owning_configuration(project, tmp_path):
    linked = tmp_path / "linked"
    run_git(project, "worktree", "add", "-b", "worker", str(linked))
    (project / ".devkit/config.local.toml").write_text('[shared]\nadapter="missing"\n')
    server = build_server({t.name: t for t in tools(project)}, ExecutionBinding(linked, project))
    result = call(server, "shared_list", {"kind": "proposal-review", "slug": "test"})
    assert not result.isError, result
    (linked / ".devkit/config.local.toml").write_text('[shared]\nadapter="missing"\n')
    result = call(server, "shared_list", {"kind": "proposal-review", "slug": "test"})
    assert result.structuredContent["error"]["code"] == "SHARED_ADAPTER_UNAVAILABLE"
