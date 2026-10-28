"""The Host's decomposition procedure on a fixture Backlog (``SPEC-backlog-subagent-roles``): the existing commands and
moves the Backlog reference names apply a ``decomposer`` split without losing provenance, edges or feedback."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from click.testing import CliRunner, Result
from devkit_core.core.frontmatter import parse
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import TODAY
from spec_support.scope import git, write

from devkit_spec.features.proposals import create_proposal

FEEDBACK = """---
id: FB-wide-observation
title: An observation on the wide draft
scope: repo
kind: suggestion
category: missing-capability
target: docs/
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-20
---

# [FB-wide-observation] An observation on the wide draft

## Evidence

```text
observed
```
"""


def _docs(root: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["docs", *args, "-w", str(root)])


def _spec(root: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", *args, "-w", str(root)])


def _meta(path: Path) -> dict[str, object]:
    return parse(path.read_text(encoding="utf-8")).data or {}


def _repo(tmp_path: Path) -> Path:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, ".devkit/config.toml", "")
    create_proposal(root, "wide", today=TODAY)
    create_proposal(root, "taken", today=TODAY)
    later = root / create_proposal(root, "later", today=TODAY).path
    later.write_text(
        later.read_text(encoding="utf-8").replace("status: draft", "status: draft\ndepends_on: [PROP-wide]", 1),
        encoding="utf-8",
    )
    write(root, "docs/proposals/PROP-wide/feedback/wide-observation.md", FEEDBACK)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "backlog")
    return root


def test_a_split_keeps_provenance_rewires_the_edge_and_retires_the_feedback(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    assert _spec(root, "proposal", "check", "wide").exit_code == 0
    incoming = json.loads(_docs(root, "refs", "PROP-wide", "--direction", "in", "-n", "0", "--format", "json").stdout)
    assert "PROP-later" in json.dumps(incoming)

    taken = root / "docs/proposals/PROP-taken/proposal.md"
    before = taken.read_bytes()
    collision = _spec(root, "proposal", "new", "taken", "--decomposed-from", "PROP-wide", "--format", "json")
    assert collision.exit_code == 2 and json.loads(collision.stdout)["error"]["code"] == "SPEC_PROPOSAL_EXISTS"
    assert taken.read_bytes() == before

    for child in ("wide-core", "wide-viewer"):
        created = _spec(root, "proposal", "new", child, "--decomposed-from", "PROP-wide")
        assert created.exit_code == 0, created.output
        assert _meta(root / f"docs/proposals/PROP-{child}/proposal.md")["decomposed_from"] == "PROP-wide"

    # Edges to children are written after the children exist, in the same Backlog change.
    later = root / "docs/proposals/PROP-later/proposal.md"
    later.write_text(later.read_text(encoding="utf-8").replace("[PROP-wide]", "[PROP-wide-core]", 1), encoding="utf-8")
    # Feedback retirement: the open file moves whole, once, with its ID and status; the parent is deleted.
    source = root / "docs/proposals/PROP-wide/feedback/wide-observation.md"
    target = root / "specs/2026-10/feedback/20261026-wide-observation.md"
    target.parent.mkdir(parents=True)
    source.rename(target)
    git(root, "rm", "-q", "-r", "docs/proposals/PROP-wide")
    shutil.rmtree(root / "docs/proposals/PROP-wide")  # the emptied feedback/ directory

    assert _meta(later)["depends_on"] == ["PROP-wide-core"]
    assert _docs(root, "resolve", "PROP-wide-core").exit_code == 0
    moved = _meta(target)
    assert (moved["id"], moved["status"]) == ("FB-wide-observation", "open")
    assert not list((root / "docs/proposals").glob("PROP-wide-*/feedback/*.md"))
    resolved = _docs(root, "resolve", "FB-wide-observation")
    assert resolved.exit_code == 0 and "specs/2026-10/feedback/20261026-wide-observation.md" in resolved.stdout
    assert not (root / "docs/proposals/PROP-wide").exists()
    for child in ("wide-core", "wide-viewer"):  # provenance survives the parent's deletion
        assert _meta(root / f"docs/proposals/PROP-{child}/proposal.md")["decomposed_from"] == "PROP-wide"
