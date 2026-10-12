from __future__ import annotations

from pathlib import Path

from agent_rule_engine import RuleContext
from agent_rule_engine.rules import CleanArtifactsRule, SecretLeakRule


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
    assert found["src/a.py"] == "Potential secret in file content"


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
