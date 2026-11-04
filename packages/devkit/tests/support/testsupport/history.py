"""In-memory Git Database model for maintenance history integration tests."""

from __future__ import annotations

import base64
import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from devkit_agt.features.maintenance_history.models.records import ROOT_COMMIT, ROOT_README, canonical, git_sha
from devkit_agt.features.maintenance_history.repositories.github import Response


class FakeGitHub:
    def __init__(self) -> None:
        self.head: str | None = None
        self.blobs: dict[str, bytes] = {}
        self.trees: dict[str, dict[str, bytes]] = {}
        self.commits: dict[str, dict[str, Any]] = {}
        self.calls: list[tuple[str, str, dict[str, Any] | None, float]] = []
        self.hook: Callable[[str, str, dict[str, Any] | None], Response | None] | None = None

    def __call__(self, method: str, endpoint: str, payload: dict[str, Any] | None, timeout: float) -> Response:
        self.calls.append((method, endpoint, payload, timeout))
        url = urlsplit(endpoint)
        path = unquote(url.path.removeprefix("repos/owner/repo")).lstrip("/")
        query = parse_qs(url.query)
        if self.hook:
            answer = self.hook(method, path, payload)
            if answer is not None:
                return answer
        if url.path == "repos/owner/repo/":
            return Response(404, {}, {})
        if url.path == "repos/owner/repo":
            return Response(200, {}, {"full_name": "owner/repo"})
        if method == "GET" and path.startswith("git/ref/heads/"):
            return Response(200, {}, {"object": {"sha": self.head}}) if self.head else Response(404, {}, {})
        if method == "GET" and path.startswith("compare/"):
            wanted = path.split("...")[-1]
            cursor = wanted
            while cursor in self.commits:
                if cursor == ROOT_COMMIT:
                    return Response(200, {}, {"status": "identical" if wanted == ROOT_COMMIT else "ahead"})
                parents = self.commits[cursor]["parents"]
                if not parents:
                    break
                cursor = parents[0]
            return Response(404, {}, {})
        if method == "POST" and path == "git/blobs":
            assert payload is not None
            content = base64.b64decode(payload["content"])
            sha = git_sha("blob", content)
            self.blobs[sha] = content
            return Response(201, {}, {"sha": sha})
        if method == "POST" and path == "git/trees":
            assert payload is not None
            files = dict(self.trees.get(payload.get("base_tree", ""), {}))
            for entry in payload["tree"]:
                files[entry["path"]] = entry["content"].encode() if "content" in entry else self.blobs[entry["sha"]]
            sha = git_sha("tree", canonical({name: data.hex() for name, data in files.items()}))
            self.trees[sha] = files
            return Response(201, {}, {"sha": sha})
        if method == "POST" and path == "git/commits":
            assert payload is not None
            files = self.trees[payload["tree"]]
            sha = (
                ROOT_COMMIT
                if not payload["parents"] and files == {"README.md": ROOT_README}
                else git_sha("commit", canonical(payload))
            )
            self.commits[sha] = dict(payload)
            return Response(201, {}, {"sha": sha})
        if method == "POST" and path == "git/refs":
            assert payload is not None
            if self.head:
                return Response(422, {}, {})
            self.head = payload["sha"]
            return Response(201, {}, {})
        if method == "PATCH" and path.startswith("git/refs/heads/"):
            assert payload is not None
            assert not payload.get("force")
            new = payload["sha"]
            if self.head not in self.commits[new]["parents"] and new != self.head:
                return Response(422, {}, {})
            self.head = new
            return Response(200, {}, {})
        if method == "GET" and path.startswith("git/commits/"):
            commit = self.commits[path.rsplit("/", 1)[-1]]
            return Response(200, {}, commit | {"tree": {"sha": commit["tree"]}})
        if method == "GET" and path.startswith("contents/"):
            name = path.removeprefix("contents/")
            head = query.get("ref", [self.head])[0]
            if head is None or head not in self.commits:
                return Response(404, {}, {})
            files = self.trees[self.commits[head]["tree"]]
            if name in files:
                data = files[name]
                return Response(
                    200,
                    {},
                    {"content": base64.b64encode(data).decode(), "encoding": "base64", "sha": git_sha("blob", data)},
                )
            children = [key for key in files if key.startswith(name + "/") and "/" not in key[len(name) + 1 :]]
            if children:
                return Response(200, {}, [{"name": child.rsplit("/", 1)[-1], "path": child} for child in children])
            return Response(404, {}, {})
        if method == "GET" and path == "commits":
            head = self.head
            name = query["path"][0]
            while head:
                commit = self.commits[head]
                if name in self.trees[commit["tree"]]:
                    return Response(200, {}, [{"sha": head}])
                head = commit["parents"][0] if commit["parents"] else None
            return Response(200, {}, [])
        raise AssertionError((method, endpoint, payload))

    def files(self) -> dict[str, bytes]:
        assert self.head
        return self.trees[self.commits[self.head]["tree"]]

    def indexes(self) -> list[dict[str, Any]]:
        return [
            json.loads(line)
            for path, data in self.files().items()
            if path.startswith("index/")
            for line in data.splitlines()
        ]
