from __future__ import annotations

import subprocess

from devkit_agt.features.worktree.repositories.gh import http_response, run_gh

SELECTOR = "github.example/owner/repo"


def test_runner_is_bounded_noninteractive_and_timeout_is_unknown(tmp_path, monkeypatch):
    def timeout(args, **kwargs):
        assert kwargs["timeout"] == 5 and kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["env"]["GH_PROMPT_DISABLED"] == "1" and "GH_REPO" not in kwargs["env"]
        raise subprocess.TimeoutExpired(args, 5)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert run_gh(tmp_path, ["pr", "view", "1", "-R", SELECTOR], timeout=5).returncode is None


def test_input_is_written_to_gh_instead_of_devnull(tmp_path, monkeypatch):
    def capture(args, **kwargs):
        assert kwargs["input"] == b"{}" and kwargs["stdin"] is None
        return subprocess.CompletedProcess(args, 0, b"out", b"")

    monkeypatch.setattr(subprocess, "run", capture)
    assert run_gh(None, ["api", "--input", "-", "x"], timeout=1, input=b"{}").stdout == "out"


def test_missing_gh_is_127(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    assert run_gh(tmp_path, ["auth", "status"], timeout=1).returncode == 127


def test_http_response_reads_the_last_block_status_headers_and_body():
    output = 'HTTP/1.1 100 Continue\r\n\r\nHTTP/2.0 403 Forbidden\r\nRetry-After: 10\r\n\r\n{"a": 1}\n'
    response = http_response(output)
    assert response is not None
    assert (response.status, response.headers, response.body) == (403, {"retry-after": "10"}, '{"a": 1}\n')


def test_http_response_is_none_without_an_http_block():
    for output in ("", "not http", "HTTP/2.0 200 OK", "HTTP/2.0 abc OK\n\nbody"):
        assert http_response(output) is None
