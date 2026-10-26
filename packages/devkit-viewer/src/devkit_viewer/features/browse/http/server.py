"""The local HTTP server: the committed app build and a read-only JSON API over registered repositories.

The server binds to ``127.0.0.1`` only and answers ``GET`` only. A request whose ``Host`` header is not the
loopback address or ``localhost`` at the bound port is refused, so a page on another site cannot read repository
content through the browser by DNS rebinding; no response carries a CORS header. The API:

- ``/api/repos``: ``{"repos": [{"id", "default_branch"}]}``;
- ``/api/repos/<id>/info``: ``{"repo_id", "default_branch"}``;
- ``/api/repos/<id>/tree?path=``: ``{"items": [{"name", "path", "type", "size"?}]}`` from the working tree;
- ``/api/repos/<id>/blob?path=``: ``{"path", "encoding": "base64", "content", "size}`` from the working tree;
- ``/api/repos/<id>/dashboard-list?path=<section>``: ``{"items": [{"path", "content", "encoding"}], "errors"}``;
- ``/api/repos/<id>/planning-proposals``: ``{"sources", "items": [{"source", "path", "content", "encoding"}], "errors"}``;
- ``/api/repos/<id>/shared?generation=&kind=&slug=``: ``{"artifacts": [...]}`` or ``{"metadata", "content", "artifact_uri"}``.

``default_branch`` reports the checked-out branch or ``HEAD`` when detached. A legacy ``ref`` parameter is ignored.
``tree`` and ``blob`` accept ``source=<Planning source ID>`` for paths in that source's proposal directory; every other
endpoint ignores it. Errors are
``{"error": {"code", "message"}}`` with the status of the ``ReadError``. Any other path serves a file the bundled
``static/`` directory lists, looked up by its decoded path (``/`` is ``index.html``).
"""

from __future__ import annotations

import errno
import json
import mimetypes
from collections.abc import Mapping, Sequence
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from importlib.resources.abc import Traversable
from urllib.parse import parse_qs, unquote, urlsplit

from devkit_core.core.logs import get_logger

from devkit_viewer.features.browse.models.errors import PortInUseError, ReadError, repo_unknown
from devkit_viewer.features.browse.models.repository import Repository
from devkit_viewer.features.browse.usecases.read import list_repositories, read_repository
from devkit_viewer.features.browse.usecases.review import UNAVAILABLE_CODES, report_page, unavailable_page
from devkit_viewer.features.browse.usecases.shared import list_shared_artifacts, read_shared_artifact

HOST = "127.0.0.1"
# Under the devkit logger hierarchy, so `-v` prints one line per request.
_log = get_logger("devkit.viewer.server")

_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
}


def static_root() -> Traversable:
    """The bundled app build."""
    return files("devkit_viewer") / "static"


def bundle_files() -> dict[str, Traversable]:
    """Every file of the bundled app build by its ``/``-separated relative path: the only files the server serves."""
    found: dict[str, Traversable] = {}

    def walk(node: Traversable, prefix: str) -> None:
        for child in node.iterdir():
            if child.is_dir():
                walk(child, f"{prefix}{child.name}/")
            elif child.is_file():
                found[f"{prefix}{child.name}"] = child

    root = static_root()
    if root.is_dir():
        walk(root, "")
    return found


class ViewerServer(ThreadingHTTPServer):
    """A server for ``repositories`` on ``127.0.0.1:<port>`` (``0`` picks a free port)."""

    daemon_threads = True

    def __init__(self, repositories: Sequence[Repository], port: int) -> None:
        self.repositories = {repo.id: repo for repo in repositories}
        self.bundle = bundle_files()
        try:
            super().__init__((HOST, port), Handler)
        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                raise PortInUseError(f"port {port} is already in use on {HOST}") from exc
            raise

    @property
    def port(self) -> int:
        return int(self.server_address[1])

    @property
    def url(self) -> str:
        return f"http://{HOST}:{self.port}/"


class Handler(BaseHTTPRequestHandler):
    server: ViewerServer
    server_version = "devkit-viewer"
    sys_version = ""

    # -- plumbing ---------------------------------------------------------------------------------------------

    def log_message(self, format: str, *args: object) -> None:
        _log.debug("%s %s", self.address_string(), format % args)

    def _send(self, status: int, body: bytes, content_type: str, *, report: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if report:
            self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; sandbox")
        if report or content_type.startswith("application/json"):
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: Mapping[str, object]) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8", errors="backslashreplace")
        self._send(status, body, "application/json; charset=utf-8")

    def _error(self, error: ReadError) -> None:
        self._json(error.status, {"error": {"code": error.code, "message": error.message}})

    def _host_allowed(self) -> bool:
        port = self.server.port
        return self.headers.get("Host", "") in (f"{HOST}:{port}", f"localhost:{port}")

    def _refuse_method(self) -> None:
        self._error(ReadError(HTTPStatus.METHOD_NOT_ALLOWED, "VIEWER_METHOD_NOT_ALLOWED", "the viewer is read-only"))

    do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_HEAD = _refuse_method

    # -- routes -----------------------------------------------------------------------------------------------

    def do_GET(self) -> None:
        if not self._host_allowed():
            self._error(ReadError(HTTPStatus.FORBIDDEN, "VIEWER_HOST_REFUSED", "the Host header is not local"))
            return
        url = urlsplit(self.path)
        try:
            if url.path == "/api" or url.path.startswith("/api/"):
                self._json(HTTPStatus.OK, self._api(url.path, parse_qs(url.query, keep_blank_values=True)))
            elif url.path == "/review" or url.path.startswith("/review/"):
                self._review(url.path)
            else:
                self._static(url.path)
        except ReadError as error:
            self._error(error)

    def _api(self, path: str, query: Mapping[str, list[str]]) -> Mapping[str, object]:
        parts = [unquote(part) for part in path.split("/")[2:]]
        if parts == ["repos"]:
            return list_repositories(self.server.repositories.values())
        if len(parts) != 3 or parts[0] != "repos":
            raise ReadError(HTTPStatus.NOT_FOUND, "VIEWER_NOT_FOUND", f"no API endpoint {path!r}")
        repo = self.server.repositories.get(parts[1])
        if repo is None:
            raise repo_unknown(parts[1])
        if parts[2] == "shared":
            generation = query.get("generation", [""])[0]
            if generation:
                return read_shared_artifact(repo, generation)
            return list_shared_artifacts(
                repo,
                kind=query.get("kind", [""])[0] or None,
                slug=query.get("slug", [""])[0] or None,
            )
        return read_repository(
            repo,
            parts[2],
            query.get("path", [""])[0],
            recursive=query.get("recursive", [""])[0] == "true",
            source=query.get("source", [""])[0],
        )

    def _review(self, path: str) -> None:
        parts = [unquote(part) for part in path.split("/")[2:]]
        if len(parts) != 2:
            raise ReadError(HTTPStatus.NOT_FOUND, "VIEWER_NOT_FOUND", "expected one exact report")
        repo = self.server.repositories.get(parts[0])
        if repo is None:
            raise repo_unknown(parts[0])
        try:
            page = report_page(repo, parts[1])
        except ReadError as error:
            if error.code not in UNAVAILABLE_CODES:
                raise
            self._send(error.status, unavailable_page(error), "text/html; charset=utf-8", report=True)
            return
        self._send(HTTPStatus.OK, page, "text/html; charset=utf-8", report=True)

    def _static(self, path: str) -> None:
        # Only a file the bundle lists is served: the decoded path is a lookup key, never joined to a directory.
        name = unquote(path).lstrip("/") or "index.html"
        node = self.server.bundle.get(name)
        if node is None:
            raise ReadError(HTTPStatus.NOT_FOUND, "VIEWER_NOT_FOUND", f"no file {path!r}")
        suffix = name[name.rfind(".") :] if "." in name else ""
        content_type = _TYPES.get(suffix) or mimetypes.guess_type(name)[0] or "application/octet-stream"
        self._send(HTTPStatus.OK, node.read_bytes(), content_type)
