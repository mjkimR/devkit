from __future__ import annotations

import base64
import http.client
import json
import re
import socket
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo, commit_files, git

from devkit_viewer.features.browse.http.server import ViewerServer, static_root
from devkit_viewer.features.browse.models.errors import PortInUseError
from devkit_viewer.features.browse.usecases.register import RegisterRepositoriesUseCase


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> dict:
        return json.loads(self.body)


@pytest.fixture
def server(make_repo: MakeRepo, tmp_path: Path) -> Iterator[ViewerServer]:
    alpha = make_repo("alpha", {"docs/a.md": "main a\n", "docs/sub/b.md": "b\n"})
    git(alpha, "switch", "-q", "-c", "plan-x")
    commit_files(alpha, {"docs/a.md": "plan a\n"})
    git(alpha, "switch", "-q", "main")
    git(alpha, "update-ref", "refs/remotes/origin/z", "HEAD")
    make_repo("beta")
    viewer = ViewerServer(RegisterRepositoriesUseCase().execute([tmp_path / "beta", alpha], [], tmp_path), 0)
    thread = threading.Thread(target=viewer.serve_forever, daemon=True)
    thread.start()
    yield viewer
    viewer.shutdown()
    viewer.server_close()


def request(server: ViewerServer, path: str, *, method: str = "GET", host: str | None = None) -> Response:
    connection = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    headers = {} if host is None else {"Host": host}
    connection.request(method, path, headers=headers)
    response = connection.getresponse()
    result = Response(response.status, {k.lower(): v for k, v in response.getheaders()}, response.read())
    connection.close()
    return result


def test_binds_loopback_only(server: ViewerServer) -> None:
    assert server.server_address[0] == "127.0.0.1"
    assert server.url == f"http://127.0.0.1:{server.port}/"


def test_repos(server: ViewerServer) -> None:
    response = request(server, "/api/repos")
    assert response.status == 200
    assert response.json() == {
        "repos": [{"id": "alpha", "default_branch": "main"}, {"id": "beta", "default_branch": "main"}]
    }
    assert response.headers["cache-control"] == "no-store"


def test_info_reports_current_branch_and_branch_list_is_not_exposed(server: ViewerServer) -> None:
    assert request(server, "/api/repos/alpha/info").json() == {"repo_id": "alpha", "default_branch": "main"}
    assert request(server, "/api/repos/alpha/refs").status == 404


def test_tree(server: ViewerServer) -> None:
    response = request(server, "/api/repos/alpha/tree?path=docs&ref=main")
    assert response.status == 200
    assert response.json() == {
        "items": [
            {"name": "sub", "path": "docs/sub", "type": "tree"},
            {"name": "a.md", "path": "docs/a.md", "type": "blob", "size": 7},
        ]
    }
    root = request(server, "/api/repos/alpha/tree?path=&ref=main").json()
    assert [item["path"] for item in root["items"]] == [".devkit", "docs"]


def test_blob_reads_the_checked_out_working_tree_and_ignores_legacy_ref(server: ViewerServer) -> None:
    (server.repositories["alpha"].root / "docs/a.md").write_text("saved edit\n")
    response = request(server, "/api/repos/alpha/blob?path=docs/a.md&ref=plan-x")
    assert response.status == 200
    assert response.json() == {
        "path": "docs/a.md",
        "encoding": "base64",
        "content": base64.b64encode(b"saved edit\n").decode(),
        "size": 11,
    }


def test_tree_includes_untracked_files(server: ViewerServer) -> None:
    root = server.repositories["alpha"].root
    (root / "docs/new").mkdir()
    (root / "docs/new/note.md").write_text("untracked\n")
    response = request(server, "/api/repos/alpha/tree?path=docs&ref=plan-x")
    assert response.status == 200
    assert {item["path"] for item in response.json()["items"]} == {
        "docs/a.md",
        "docs/new",
        "docs/sub",
    }


def test_symlinks_are_hidden_and_cannot_be_read(server: ViewerServer, tmp_path: Path) -> None:
    root = server.repositories["alpha"].root
    secret = tmp_path / "secret.md"
    secret.write_text("outside\n")
    (root / "docs/secret.md").symlink_to(secret)
    tree = request(server, "/api/repos/alpha/tree?path=docs").json()
    assert "docs/secret.md" not in {item["path"] for item in tree["items"]}
    response = request(server, "/api/repos/alpha/blob?path=docs/secret.md")
    assert response.status == 404
    assert response.json()["error"]["code"] == "VIEWER_PATH_NOT_FOUND"


@pytest.mark.parametrize(
    ("path", "status", "code"),
    [
        ("/api/repos/gamma/info", 404, "VIEWER_REPO_UNKNOWN"),
        ("/api/repos/alpha/blob?path=docs/none.md", 404, "VIEWER_PATH_NOT_FOUND"),
        ("/api/repos/alpha/blob?path=docs/../x&ref=main", 400, "VIEWER_PATH_INVALID"),
        ("/api/repos/alpha/tree?path=./docs&ref=main", 400, "VIEWER_PATH_INVALID"),
        ("/api/repos/alpha/blob?path=docs", 404, "VIEWER_PATH_NOT_FOUND"),
        ("/api/repos/alpha/other", 404, "VIEWER_NOT_FOUND"),
        ("/api/nothing", 404, "VIEWER_NOT_FOUND"),
    ],
)
def test_read_errors(server: ViewerServer, path: str, status: int, code: str) -> None:
    response = request(server, path)
    assert response.status == status
    assert response.json()["error"]["code"] == code


@pytest.mark.parametrize("host", ["evil.example", "evil.example:{port}", "127.0.0.1:1", "localhost"])
def test_foreign_host_is_refused(server: ViewerServer, host: str) -> None:
    response = request(server, "/api/repos", host=host.format(port=server.port))
    assert response.status == 403
    assert response.json()["error"]["code"] == "VIEWER_HOST_REFUSED"


def test_localhost_host_is_allowed(server: ViewerServer) -> None:
    assert request(server, "/api/repos", host=f"localhost:{server.port}").status == 200


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
@pytest.mark.parametrize("path", ["/", "/api/repos", "/api/repos/alpha/blob?path=docs/a.md"])
def test_only_get_is_answered(server: ViewerServer, method: str, path: str) -> None:
    assert request(server, path, method=method).status == 405


def test_no_cors_header(server: ViewerServer) -> None:
    for path in ("/", "/api/repos", "/api/repos/alpha/tree?path=docs", "/api/repos/gamma/info", "/missing"):
        assert "access-control-allow-origin" not in request(server, path).headers


def test_bundled_page_and_asset(server: ViewerServer) -> None:
    index = request(server, "/")
    assert index.status == 200
    assert index.headers["content-type"].startswith("text/html")
    assets = re.findall(r'(?:src|href)="\.?/?([^"]+\.(?:js|css))"', index.body.decode())
    assert assets, "index.html references no script or stylesheet"
    for asset in assets:
        response = request(server, f"/{asset}")
        assert response.status == 200
        assert response.headers["content-type"].split(";")[0] in ("text/javascript", "text/css")
        assert (static_root() / asset).is_file()


@pytest.mark.parametrize(
    "path",
    [
        "/missing.js",
        "/../pyproject.toml",
        "/%2e%2e/cli.py",
        "/assets/",
        "/assets",
        "/..%2Fserver.py",
        "/assets/..%2F..%2Fcli.py",
        "/%2Fetc%2Fhosts",
        "/%2e%2e%2f%2e%2e%2fpyproject.toml",
        "/assets/..%5C..%5Ccli.py",
    ],
)
def test_files_outside_the_bundle_are_not_found(server: ViewerServer, path: str) -> None:
    assert request(server, path).status == 404


def test_port_in_use_is_refused(server: ViewerServer) -> None:
    with pytest.raises(PortInUseError) as caught:
        ViewerServer([], server.port)
    assert caught.value.code == "VIEWER_PORT_IN_USE"


def test_port_held_on_the_wildcard_address_is_refused() -> None:
    # Address reuse would let 127.0.0.1:<port> bind beside another process's 0.0.0.0:<port> listener on macOS.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as holder:
        holder.bind(("0.0.0.0", 0))
        holder.listen()
        with pytest.raises(PortInUseError):
            ViewerServer([], holder.getsockname()[1]).server_close()


def test_port_is_reusable_after_close() -> None:
    first = ViewerServer([], 0)
    port = first.port
    first.server_close()
    ViewerServer([], port).server_close()


def test_port_is_reusable_right_after_serving_a_request() -> None:
    # The server closes each HTTP/1.0 connection first, leaving it in TIME_WAIT on the port.
    first = ViewerServer([], 0)
    port = first.port
    thread = threading.Thread(target=first.serve_forever, daemon=True)
    thread.start()
    try:
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        connection.request("GET", "/api/repos")
        response = connection.getresponse()
        response.read()  # to the server's close
        assert response.status == 200
        connection.close()
    finally:
        first.shutdown()
        first.server_close()
        thread.join()
    ViewerServer([], port).server_close()


@pytest.mark.parametrize(
    "path",
    ["/review/alpha/" + "a" * 32, "/api/repos/alpha/shared", "/api/repos/alpha/shared?generation=" + "a" * 32],
)
def test_removed_review_and_shared_paths_are_not_found(server: ViewerServer, path: str) -> None:
    response = request(server, path)
    assert response.status == 404
    assert response.json()["error"]["code"] == "VIEWER_NOT_FOUND"


def test_recursive_metadata_endpoint_includes_descendants(server: ViewerServer) -> None:
    root = server.repositories["alpha"].root
    (root / "docs/sub/nested.md").write_text("saved")
    response = request(server, "/api/repos/alpha/tree?path=docs&recursive=true")
    assert response.status == 200
    items = response.json()["items"]
    assert "docs/sub/nested.md" in {item["path"] for item in items}
    assert all("content" not in item for item in items)
    assert "docs/sub/nested.md" not in {
        item["path"] for item in request(server, "/api/repos/alpha/tree?path=docs").json()["items"]
    }
    assert request(server, "/api/repos/alpha/tree?path=../&recursive=true").status == 400


def test_dashboard_metadata_endpoint(server: ViewerServer) -> None:
    repo = server.repositories["alpha"].root
    folder = repo / "docs/roadmap"
    folder.mkdir()
    (folder / "MS-a.md").write_text("---\nid: MS-a\nstatus: active\n---\nprivate body\n")
    response = request(server, "/api/repos/alpha/dashboard-list?path=milestones")
    assert response.status == 200
    assert response.json() == {
        "items": [
            {"path": "docs/roadmap/MS-a.md", "content": "---\nid: MS-a\nstatus: active\n---\n", "encoding": "utf-8"}
        ],
        "errors": [],
    }
    assert request(server, "/api/repos/alpha/dashboard-list?path=invalid").status == 400


@pytest.mark.parametrize(("prefix", "directory"), [("DESIGN", "designs"), ("DOMAIN", "domain"), ("OPS", "operations")])
@pytest.mark.parametrize("docs_root", ["docs", "docs/packages/registered"])
def test_http_formal_documents_and_artifacts_preserve_bytes_and_missing_paths(
    server: ViewerServer, prefix: str, directory: str, docs_root: str
) -> None:
    from urllib.parse import quote

    root = server.repositories["alpha"].root
    if docs_root != "docs":
        (root / "packages/registered").mkdir(parents=True, exist_ok=True)
        registry = root / ".devkit/config.toml"
        registry.write_text(
            registry.read_text() + '\n[[tool.docs.namespaces]]\nname = "registered"\npath = "packages/registered"\n'
        )
    area_root = f"{docs_root}/{directory}/distribution" if prefix != "OPS" else f"{docs_root}/{directory}"
    parent = f"{area_root}/{prefix}-http/design.md" if prefix == "DESIGN" else f"{area_root}/{prefix}-http.md"
    support = f"{area_root}/{prefix}-http/examples" if prefix == "DESIGN" else f"{area_root}/{prefix}-http/artifacts"
    files = {
        parent: f"---\nid: {prefix}-http\n---\n# HTTP\n".encode(),
        f"{support}/data sheet.csv": b"a,b\n1,2\n",
        f"{support}/chart.png": bytes([137, 80, 78, 71, 255]),
    }
    for path, data in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        response = request(server, f"/api/repos/alpha/blob?path={quote(path)}")
        assert response.status == 200
        assert base64.b64decode(response.json()["content"]) == data
    tree = request(server, f"/api/repos/alpha/tree?path={quote(docs_root)}&recursive=true")
    assert set(files) <= {item["path"] for item in tree.json()["items"]}
    missing = request(server, f"/api/repos/alpha/blob?path={quote(parent + '.missing')}")
    assert missing.status == 404
    assert missing.json()["error"]["code"] == "VIEWER_PATH_NOT_FOUND"
