"""A handoff whose PADR partially supersedes an accepted ADR passes ``RULE-decision-supersession`` on the result
(SPEC-proposal-scaffold-and-handoff-pointers): the pointer the rule needs is written and staged with the transaction."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from spec_support.proposals import accept, record_acceptance

OLD = "docs/decisions/2026-09/20260901-old.md"


def _devkit(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("DEVKIT_")}
    return subprocess.run(
        [sys.executable, "-m", "devkit_dist", *args, "-w", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def _git(root: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@x",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@x",
    }
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True, env=env).stdout


def test_the_handoff_result_passes_the_supersession_rule(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q", "-b", "dev-partial")
    assert _devkit(tmp_path, "sync").returncode == 0
    old = tmp_path / OLD
    old.parent.mkdir(parents=True)
    old.write_text(
        '---\nid: ADR-old\ntitle: Old\nsummary: "The old decision about parsers."\nstatus: accepted\n'
        "created_at: 2026-09-01\n---\n\n# [ADR-old] Old\n\n## Decision Outcome\n\nParse with regexes.\n",
        encoding="utf-8",
    )
    assert _devkit(tmp_path, "spec", "proposal", "new", "partial", "--summary", "Pick a parser.").returncode == 0
    created = _devkit(
        tmp_path,
        "spec",
        "proposal",
        "padr",
        "partial",
        "Pick AST",
        "--summary",
        "For parsers, we pick the AST parser, to parse faster, accepting a rewrite.",
        "--format",
        "json",
    )
    assert created.returncode == 0, created.stdout + created.stderr
    padr = tmp_path / json.loads(created.stdout)["path"]
    text = padr.read_text(encoding="utf-8")
    placeholder = next(line for line in text.splitlines() if line.startswith("# supersedes:"))
    padr.write_text(text.replace(placeholder, "supersedes: [ADR-old]"), encoding="utf-8")
    proposal = tmp_path / "docs/proposals/PROP-partial/proposal.md"
    accept(proposal)
    record_acceptance(proposal)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "accepted proposal")

    result = _devkit(tmp_path, "spec", "proposal", "handoff", "partial", "--format", "json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    new = payload["decisions"][0]["path"]
    assert payload["pointers"] == [{"adr": "ADR-old", "path": OLD, "line": 11, "by": "ADR-pick-ast"}]
    # The edited ADR is part of the handoff delta the composed handoff stages with ``git add -A``.
    status = _git(tmp_path, "status", "--porcelain", "--untracked-files=all")
    assert f" M {OLD}" in status and f"?? {new}" in status
    check = _devkit(tmp_path, "rules", "check", OLD, new)
    assert check.returncode == 0, check.stdout + check.stderr
    assert "RULE-decision-supersession" not in check.stdout
