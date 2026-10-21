"""``RULE-secret-leak``: credential files and secret patterns in explicit targets, never in whole-workspace runs."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from devkit_agt.features.rules import RuleContext, git_snapshot, run_project_rules
from devkit_agt.features.rules.services.builtins.secret_leak import SecretLeakRule
from devkit_agt.features.rules.services.builtins.secret_leak.rule import credential_file
from devkit_agt.features.rules.services.testing import check, write_files


def _check(root: Path, files: dict[str, bytes]) -> list[tuple[str, int, str]]:
    return [(v.file, v.line, v.message) for v in check(SecretLeakRule(), root, files, targets=list(files))]


def test_secret_leak_detects_files_and_contents_among_targets(tmp_path: Path) -> None:
    files = {
        ".env": b"TOKEN=1\n",
        ".env.example": b"TOKEN=\n",
        "keys/id_ed25519": b"xx",
        "src/a.py": b'key = "AKIA' + b'ABCDEFGHIJKLMNOP"\n',
        "src/b.py": b"-----BEGIN " + b"RSA PRIVATE KEY-----\n",
        "src/c.py": b'tok = "ghp_' + b"a" * 36 + b'"\n',
        "src/ok.py": b"print('hi')\n",
    }
    found = {file: message for file, _, message in _check(tmp_path, files)}
    assert set(found) == {".env", "keys/id_ed25519", "src/a.py", "src/b.py", "src/c.py"}
    assert found[".env"] == ".env is a credential file"
    assert found["src/a.py"] == "Potential secret in file content (aws access key)"


def test_whole_workspace_runs_report_nothing(tmp_path: Path) -> None:
    write_files(tmp_path, {".env": b"TOKEN=1\n"})
    assert SecretLeakRule().check(RuleContext(workspace_root=tmp_path)) == []
    assert check(SecretLeakRule(), tmp_path) == []


@pytest.mark.parametrize(
    ("content", "kind"),
    [
        (b"-----BEGIN " + b"PRIVATE KEY-----", "private key"),
        (b"-----BEGIN " + b"ENCRYPTED PRIVATE KEY-----", "private key"),
        (b"-----BEGIN " + b"OPENSSH PRIVATE KEY-----", "private key"),
        (b"-----BEGIN " + b"PGP PRIVATE KEY BLOCK-----", "private key"),
        (b"ASIA" + b"ABCDEFGHIJKLMNOP", "aws access key"),
        (b"github_pat_" + b"A1" * 15, "github token"),
        (b"gho_" + b"b" * 36, "github token"),
        (b"sk-ant-" + b"c" * 30, "api key"),
        (b"sk_live_" + b"d" * 24, "stripe key"),
        (b"xoxb-" + b"1234567890-abcdef", "slack token"),
        (b"AIza" + b"e" * 35, "google api key"),
    ],
)
def test_secret_patterns(tmp_path: Path, content: bytes, kind: str) -> None:
    found = _check(tmp_path, {"src/x.txt": b"first line\n\nvalue = " + content + b"\n"})
    assert [(line, message) for _, line, message in found] == [(3, f"Potential secret in file content ({kind})")]


def test_secret_lines_are_reported_once_each(tmp_path: Path) -> None:
    key = b"AKIA" + b"ABCDEFGHIJKLMNOP"
    assert [line for _, line, _ in _check(tmp_path, {"a.txt": key + b" " + key + b"\nok\n" + key + b"\n"})] == [1, 3]


@pytest.mark.parametrize(
    ("name", "flagged"),
    [
        (".env", True),
        (".env.local", True),
        ("prod.env", True),
        ("server.key", True),
        ("store.p12", True),
        ("id_ed25519", True),
        (".env.example", False),
        (".env.production.example", False),
        ("prod.env.template", False),
        (".envrc", False),
        ("id_ed25519.pub", False),
    ],
)
def test_credential_file_names(name: str, flagged: bool) -> None:
    assert credential_file(name) is flagged


def test_plain_words_are_not_secrets(tmp_path: Path) -> None:
    assert _check(tmp_path, {"a.md": b"risk-assessment-framework-for-teams disk-partition-layout-guide\n"}) == []


def _git(root: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=env)


def test_staged_secret_in_a_backslash_file_name_is_found(tmp_path: Path) -> None:
    root = tmp_path.resolve() / "repo"
    write_files(root, {"README.md": "# Repo\n"})
    _git(root, "init", "-q", "-b", "main")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
    write_files(root, {"a\\b.txt": b"AKIA" + b"ABCDEFGHIJKLMNOP\n"})
    _git(root, "add", ".")
    run = run_project_rules(root, snapshot=git_snapshot(root, staged=True))
    assert [(v.rule_id, v.file) for v in run.result.violations] == [("RULE-secret-leak", "a\\b.txt")]
