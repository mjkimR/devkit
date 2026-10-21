from __future__ import annotations

import base64
import http.client
import json
import re
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo, commit_files, git

from devkit_viewer.errors import PortInUseError
from devkit_viewer.repositories import register
from devkit_viewer.server import ViewerServer, static_root


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
    viewer = ViewerServer(register([tmp_path / "beta", alpha], [], tmp_path), 0)
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


def test_info_and_refs(server: ViewerServer) -> None:
    assert request(server, "/api/repos/alpha/info").json() == {"repo_id": "alpha", "default_branch": "main"}
    assert request(server, "/api/repos/alpha/refs").json() == {
        "default_branch": "main",
        "branches": ["main", "plan-x"],
    }


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


def test_blob_at_another_branch(server: ViewerServer) -> None:
    response = request(server, "/api/repos/alpha/blob?path=docs/a.md&ref=plan-x")
    assert response.status == 200
    assert response.json() == {
        "path": "docs/a.md",
        "encoding": "base64",
        "content": base64.b64encode(b"plan a\n").decode(),
        "size": 7,
    }
    default = request(server, "/api/repos/alpha/blob?path=docs/a.md").json()
    assert base64.b64decode(default["content"]) == b"main a\n"


@pytest.mark.parametrize(
    ("path", "status", "code"),
    [
        ("/api/repos/gamma/info", 404, "VIEWER_REPO_UNKNOWN"),
        ("/api/repos/alpha/tree?path=docs&ref=nope", 404, "VIEWER_REF_UNKNOWN"),
        ("/api/repos/alpha/tree?path=docs&ref=-x", 404, "VIEWER_REF_UNKNOWN"),
        ("/api/repos/alpha/blob?path=docs/a.md&ref=origin/z", 404, "VIEWER_REF_UNKNOWN"),
        ("/api/repos/alpha/blob?path=docs/a.md&ref=main~0", 404, "VIEWER_REF_UNKNOWN"),
        ("/api/repos/alpha/blob?path=docs/none.md&ref=main", 404, "VIEWER_PATH_NOT_FOUND"),
        ("/api/repos/alpha/blob?path=docs/../x&ref=main", 400, "VIEWER_PATH_INVALID"),
        ("/api/repos/alpha/tree?path=./docs&ref=main", 400, "VIEWER_PATH_INVALID"),
        ("/api/repos/alpha/blob?path=docs&ref=main", 404, "VIEWER_PATH_NOT_FOUND"),
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


@pytest.fixture
def review_artifact(server: ViewerServer, monkeypatch: pytest.MonkeyPatch):
    from devkit.shared.api import PutRequest
    from devkit.shared.local import LocalAdapter, discover

    monkeypatch.delenv("DEVKIT_SHARED_ADAPTER", raising=False)
    selected = LocalAdapter(discover(server.repositories["alpha"].root))
    artifact = selected.put(
        PutRequest(
            "proposal-review",
            "sample",
            "a" * 40,
            "en",
            "# Review\n<script>alert(1)</script>\n[bad](javascript:alert(1))",
        )
    )

    def forbidden(*args, **kwargs):
        pytest.fail("viewer must not enumerate or write shared artifacts")

    for method in ("put", "list", "sweep"):
        monkeypatch.setattr(LocalAdapter, method, forbidden)
    return selected, artifact


def test_exact_review_is_escaped_read_only(server: ViewerServer, review_artifact) -> None:
    selected, artifact = review_artifact
    before = {p.name: p.read_bytes() for p in selected.root.iterdir()}
    response = request(server, f"/review/alpha/{artifact.metadata.generation_id}")
    assert response.status == 200
    body = response.body.decode()
    assert "&lt;script&gt;" in body and "<script>" not in body
    assert "<a href=" not in body
    assert artifact.metadata.source_sha in body
    assert artifact.metadata.language in body
    assert artifact.metadata.expires_at in body
    assert response.headers["cache-control"] == "no-store"
    assert "default-src 'none'" in response.headers["content-security-policy"]
    assert "access-control-allow-origin" not in response.headers
    assert {p.name: p.read_bytes() for p in selected.root.iterdir()} == before
    assert request(server, f"/review/beta/{artifact.metadata.generation_id}").status == 404
    assert not (server.repositories["beta"].root / ".devkit/.shared").exists()


@pytest.mark.parametrize(
    "path",
    [
        "/review",
        "/review/alpha",
        "/review/alpha/",
        "/review/alpha/list",
        "/review/alpha/../x",
        "/review/alpha/%2e%2e%2fx",
        "/review/alpha/%2fetc%2fpasswd",
        "/review/alpha/https:%2f%2fexample.com",
        "/review/unknown/" + "a" * 32,
    ],
)
def test_review_rejects_non_exact_paths(server: ViewerServer, path: str) -> None:
    assert request(server, path).status in (400, 404)


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def test_review_get_only(server: ViewerServer, method: str) -> None:
    assert request(server, "/review/alpha/" + "a" * 32, method=method).status == 405


def test_review_host_protection(server: ViewerServer) -> None:
    assert request(server, "/review/alpha/" + "a" * 32, host="evil.example").status == 403


def test_review_refuses_remote_adapter(server: ViewerServer, monkeypatch: pytest.MonkeyPatch) -> None:
    import devkit_viewer.review as review

    monkeypatch.setenv("DEVKIT_SHARED_ADAPTER", "remote")
    monkeypatch.setattr(review, "discover", lambda *_: pytest.fail("must refuse before discovering storage"))
    response = request(server, "/review/alpha/" + "a" * 32)
    assert response.status == 404
    assert response.json()["error"]["code"] == "VIEWER_REVIEW_UNAVAILABLE"


@pytest.mark.parametrize("change", ["kind", "namespace", "digest", "expired"])
def test_review_refuses_invalid_or_expired_artifact(server: ViewerServer, review_artifact, change: str) -> None:
    from datetime import UTC, datetime, timedelta

    selected, artifact = review_artifact
    path = selected.root / (artifact.metadata.generation_id + ".md")
    header, content = path.read_bytes()[4:].split(b"\n---\n", 1)
    meta = json.loads(header)
    if change == "kind":
        meta["kind"] = "other"
    elif change == "namespace":
        meta["repository_namespace"] = "other"
    elif change == "digest":
        content += b"tampered"
    else:
        meta["created_at"] = (datetime.now(UTC) - timedelta(days=8)).isoformat()
        meta["expires_at"] = (datetime.fromisoformat(meta["created_at"]) + timedelta(days=7)).isoformat()
    path.write_bytes(b"---\n" + json.dumps(meta, sort_keys=True, separators=(",", ":")).encode() + b"\n---\n" + content)
    before = path.read_bytes()
    response = request(server, f"/review/alpha/{artifact.metadata.generation_id}")
    assert response.status == (410 if change == "expired" else 400)
    if change == "expired":
        assert "Ask the Host to regenerate" in response.body.decode()
        assert response.headers["content-type"].startswith("text/html")
        assert response.headers["cache-control"] == "no-store"
    assert path.read_bytes() == before


def test_missing_review_has_read_only_host_refresh_page(server: ViewerServer, review_artifact):
    selected, _artifact = review_artifact
    before = {p.name: p.read_bytes() for p in selected.root.iterdir()}
    response = request(server, "/review/alpha/" + "0" * 32)
    assert response.status == 404
    assert "Proposal review unavailable" in response.body.decode()
    assert "Ask the Host to regenerate" in response.body.decode()
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["cache-control"] == "no-store"
    assert "default-src 'none'" in response.headers["content-security-policy"]
    assert "access-control-allow-origin" not in response.headers
    assert {p.name: p.read_bytes() for p in selected.root.iterdir()} == before
