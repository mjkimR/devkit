"""The reading tab reads ``handbook/`` through the ordinary ``tree`` and ``blob`` endpoints, with their guards."""

from __future__ import annotations

import base64
import http.client
import json
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo

from devkit_viewer.features.browse.http.server import ViewerServer
from devkit_viewer.features.browse.usecases.register import RegisterRepositoriesUseCase

MANIFEST = '{"tag": "v0.1.4", "langs": ["en", "ko"], "generated": "2026-10-26"}\n'


@pytest.fixture
def server(make_repo: MakeRepo, tmp_path: Path) -> Iterator[ViewerServer]:
    repo = make_repo(
        "alpha",
        {
            "VERSION": "0.1.4\n",
            "handbook/manifest.json": MANIFEST,
            "handbook/en/README.md": "# devkit handbook\n",
            "handbook/ko/README.md": "# devkit 핸드북\n",
        },
    )
    (repo / "handbook/en/link.md").symlink_to(repo / "VERSION")
    viewer = ViewerServer(RegisterRepositoriesUseCase().execute([repo], [], tmp_path), 0)
    thread = threading.Thread(target=viewer.serve_forever, daemon=True)
    thread.start()
    yield viewer
    viewer.shutdown()
    viewer.server_close()


def get(server: ViewerServer, path: str) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    connection.request("GET", path)
    response = connection.getresponse()
    body = json.loads(response.read())
    connection.close()
    return response.status, body


def test_manifest_and_pages_read_through_blob(server: ViewerServer) -> None:
    status, body = get(server, "/api/repos/alpha/blob?path=handbook/manifest.json")
    assert status == 200
    assert base64.b64decode(body["content"]).decode() == MANIFEST
    status, body = get(server, "/api/repos/alpha/blob?path=handbook/ko/README.md")
    assert status == 200
    assert base64.b64decode(body["content"]).decode() == "# devkit 핸드북\n"


def test_listing_omits_symlinked_pages(server: ViewerServer) -> None:
    status, body = get(server, "/api/repos/alpha/tree?path=handbook/en")
    assert status == 200
    assert [item["path"] for item in body["items"]] == ["handbook/en/README.md"]


@pytest.mark.parametrize(
    ("path", "status", "code"),
    [
        ("handbook/en/link.md", 404, "VIEWER_PATH_NOT_FOUND"),
        ("handbook/en/missing.md", 404, "VIEWER_PATH_NOT_FOUND"),
        ("handbook/../VERSION", 400, "VIEWER_PATH_INVALID"),
        ("handbook/en/../../.git/config", 400, "VIEWER_PATH_INVALID"),
    ],
)
def test_handbook_reads_keep_the_working_tree_guards(server: ViewerServer, path: str, status: int, code: str) -> None:
    answered, body = get(server, f"/api/repos/alpha/blob?path={path}")
    assert (answered, body["error"]["code"]) == (status, code)
