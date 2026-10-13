from __future__ import annotations

from pathlib import Path

import pytest
from devkit.rules import RuleContext
from devkit.rules.rules import CleanArtifactsRule, SecretLeakRule
from devkit.rules.rules.secret_leak.rule import credential_file


def _write(root: Path, rel: str, data: bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def test_secret_leak_detects_files_and_contents_among_targets(tmp_path: Path) -> None:
    _write(tmp_path, ".env", b"TOKEN=1\n")
    _write(tmp_path, ".env.example", b"TOKEN=\n")
    _write(tmp_path, "keys/id_ed25519", b"xx")
    _write(tmp_path, "src/a.py", b'key = "AKIAABCDEFGHIJKLMNOP"\n')
    _write(tmp_path, "src/b.py", b"-----BEGIN RSA PRIVATE KEY-----\n")
    _write(tmp_path, "src/c.py", b'tok = "ghp_' + b"a" * 36 + b'"\n')
    _write(tmp_path, "src/ok.py", b"print('hi')\n")
    targets = [".env", ".env.example", "keys/id_ed25519", "src/a.py", "src/b.py", "src/c.py", "src/ok.py"]
    ctx = RuleContext(workspace_root=tmp_path, changed_files=targets)
    found = {v.file: v.message for v in SecretLeakRule().check(ctx)}
    assert set(found) == {".env", "keys/id_ed25519", "src/a.py", "src/b.py", "src/c.py"}
    assert found[".env"] == ".env is a credential file"
    assert found["src/a.py"] == "Potential secret in file content (aws access key)"


def test_safety_rules_skip_whole_workspace_runs(tmp_path: Path) -> None:
    _write(tmp_path, ".env", b"TOKEN=1\n")
    _write(tmp_path, "app.db", b"sqlite")
    ctx = RuleContext(workspace_root=tmp_path)
    assert SecretLeakRule().check(ctx) == []
    assert CleanArtifactsRule().check(ctx) == []


def test_clean_artifacts_detects_binaries_databases_and_big_logs(tmp_path: Path) -> None:
    _write(tmp_path, "bin/tool", b"\x7fELF" + b"\0" * 8)
    _write(tmp_path, "bin/tool.exe", b"MZ" + b"\0" * 8)
    _write(tmp_path, "bin/mac", b"\xcf\xfa\xed\xfe" + b"\0" * 8)
    _write(tmp_path, "data/app.sqlite3", b"x")
    _write(tmp_path, "logs/big.log", b"x" * (1024 * 1024 + 1))
    _write(tmp_path, "logs/small.log", b"x")
    _write(tmp_path, "src/ok.py", b"print('hi')\n")
    targets = ["bin/tool", "bin/tool.exe", "bin/mac", "data/app.sqlite3", "logs/big.log", "logs/small.log", "src/ok.py"]
    ctx = RuleContext(workspace_root=tmp_path, changed_files=targets)
    found = {v.file for v in CleanArtifactsRule().check(ctx)}
    assert found == {"bin/tool", "bin/tool.exe", "bin/mac", "data/app.sqlite3", "logs/big.log"}


@pytest.mark.parametrize(
    ("content", "kind"),
    [
        (b"-----BEGIN PRIVATE KEY-----", "private key"),
        (b"-----BEGIN ENCRYPTED PRIVATE KEY-----", "private key"),
        (b"-----BEGIN OPENSSH PRIVATE KEY-----", "private key"),
        (b"-----BEGIN PGP PRIVATE KEY BLOCK-----", "private key"),
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
    _write(tmp_path, "src/x.txt", b"first line\n\nvalue = " + content + b"\n")
    ctx = RuleContext(workspace_root=tmp_path, changed_files=["src/x.txt"])
    assert [(v.line, v.message) for v in SecretLeakRule().check(ctx)] == [
        (3, f"Potential secret in file content ({kind})")
    ]


def test_secret_lines_are_reported_once_each(tmp_path: Path) -> None:
    key = b"AKIA" + b"ABCDEFGHIJKLMNOP"
    _write(tmp_path, "a.txt", key + b" " + key + b"\nok\n" + key + b"\n")
    ctx = RuleContext(workspace_root=tmp_path, changed_files=["a.txt"])
    assert [v.line for v in SecretLeakRule().check(ctx)] == [1, 3]


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
    _write(tmp_path, "a.md", b"risk-assessment-framework-for-teams disk-partition-layout-guide\n")
    ctx = RuleContext(workspace_root=tmp_path, changed_files=["a.md"])
    assert SecretLeakRule().check(ctx) == []


def test_staged_secret_in_a_backslash_file_name_is_found(tmp_path: Path) -> None:
    from devkit.rules import git_snapshot, run_project_rules
    from testsupport.rules import git, init_repo

    root = init_repo(tmp_path / "repo").resolve()
    _write(root, "a\\b.txt", b"AKIA" + b"ABCDEFGHIJKLMNOP\n")
    git(root, "add", ".")
    run = run_project_rules(root, snapshot=git_snapshot(root, staged=True))
    assert [(v.rule_id, v.file) for v in run.result.violations] == [("RULE-secret-leak", "a\\b.txt")]


def test_clean_artifacts_boundaries(tmp_path: Path) -> None:
    _write(tmp_path, "logs/exact.log", b"x" * (1024 * 1024))
    _write(tmp_path, "bin/mac32", b"\xce\xfa\xed\xfe")
    _write(tmp_path, "bin/universal", b"\xca\xfe\xba\xbe")
    _write(tmp_path, "data/APP.DB", b"x")
    targets = ["logs/exact.log", "bin/mac32", "bin/universal", "data/APP.DB"]
    ctx = RuleContext(workspace_root=tmp_path, changed_files=targets)
    assert sorted(v.file for v in CleanArtifactsRule().check(ctx)) == ["bin/mac32", "bin/universal", "data/APP.DB"]
