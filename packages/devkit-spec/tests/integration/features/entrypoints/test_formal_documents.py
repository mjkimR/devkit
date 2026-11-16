"""Actual derivation and explicit CLI selection use the delivered core kind policy."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli
from devkit_docs.features.documents import DocumentIndex

from devkit_spec.features.entrypoints import derive, load_bundle


@pytest.mark.parametrize("docs_root", ["docs", "docs/packages/api"])
def test_design_alias_selection_apply_body_and_ineligible_targets(tmp_path: Path, docs_root: str) -> None:
    def write(path: str, text: str) -> Path:
        result = tmp_path / path
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(text)
        return result

    write(".devkit/config.toml", '[[tool.docs.namespaces]]\nname="api"\npath="packages/api"\n')
    body = "# [DESIGN-mechanism] Mechanism\n\nRetained body with two spaces.  \n"
    path = write(
        f"{docs_root}/designs/DESIGN-mechanism.md",
        '---\nid: DESIGN-mechanism\ntitle: Mechanism\nsummary: "Local mechanism."\nstatus: active\naliases: [DESIGN-former]\n---\n'
        + body,
    )
    write("src/model.py", "MODE = 1\n")
    targets = [path.relative_to(tmp_path).as_posix()]
    for directory, name in [("domain", "DOMAIN-concept"), ("operations", "OPS-diagnosis")]:
        targets.append(
            write(f"{docs_root}/{directory}/{name}.md", f"---\nid: {name}\n---\n").relative_to(tmp_path).as_posix()
        )
    targets.append(write(f"{docs_root}/designs/README.md", "# Designs\n").relative_to(tmp_path).as_posix())
    targets.append(
        write(f"{docs_root}/designs/DESIGN-mechanism/artifacts/example.md", "# Example\nDESIGN-mechanism\n")
        .relative_to(tmp_path)
        .as_posix()
    )
    bundle = "specs/2026-11/20261116-formal"
    write(f"{bundle}/spec.md", "---\nid: SPEC-formal\nstatus: in-progress\n---\n")
    write(f"{bundle}/tasks.md", "- [x] **Task 1**: mechanism\n  - **_Boundary**: `src/`\n  - _Requirements: AC-01_\n")
    write(
        f"{bundle}/reconcile.md",
        "---\nreconcile_id: REC-formal\nstatus: pending\ntargets:\n"
        + "".join(f"  - file: {target}\n    resolution: modified\n" for target in targets)
        + "---\n",
    )
    documents = {d.path: d for d in DocumentIndex.load(tmp_path).documents}
    pairs, skipped = derive(tmp_path, load_bundle(tmp_path, bundle), documents)
    assert {(p.doc, p.code) for p in pairs} == {("DESIGN-mechanism", "src")}
    assert {s.value for s in skipped if str(s.reason) == "not-entrypoint-bearing"} == set(targets[1:])
    args = [
        "spec",
        "entrypoints",
        "derive",
        "--spec",
        bundle,
        "--apply",
        "--target",
        "DESIGN-former",
        "--code",
        "src/model.py",
        "--format",
        "json",
        "-w",
        str(tmp_path),
    ]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["summary"]["applied"] == 1
    assert path.read_text().split("---\n", 2)[2] == body
    assert "  - src/model.py\n" in path.read_text()
    before = path.read_bytes()
    rerun = CliRunner().invoke(cli, args)
    assert rerun.exit_code == 0 and json.loads(rerun.stdout)["summary"]["applied"] == 0
    assert path.read_bytes() == before
    bad_args = args.copy()
    bad_args[bad_args.index("src/model.py")] = "elsewhere/missing.py"
    bad = CliRunner().invoke(cli, bad_args)
    assert bad.exit_code == 2 and json.loads(bad.stdout)["error"]["code"] == "SPEC_ENTRYPOINTS_CODE_UNMATCHED"
    assert path.read_bytes() == before
