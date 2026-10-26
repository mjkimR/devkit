from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from spec_support.types import Write

CAP = "docs/capabilities/x/CAP-X-one.md"
USECASE = "docs/usecases/x/UC-two.md"


def _derive(workspace: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", "entrypoints", "derive", *args, "-w", str(workspace)])


def _code(result: Result) -> str:
    return json.loads(result.stdout)["error"]["code"]


@pytest.fixture
def bundles(workspace: Path, write: Write) -> Path:
    write(CAP, "---\nid: CAP-X-one\nstatus: active\n---\n")
    write(USECASE, "---\nid: UC-two\nstatus: active\n---\n")
    write("src/pkg/b.go", "package b\n")
    write("src/other/c.go", "package c\n")

    def bundle(directory: str, spec_id: str, status: str, boundary: str, target: str) -> None:
        write(f"{directory}/spec.md", f"---\nid: {spec_id}\nstatus: {status}\n---\n")
        write(
            f"{directory}/tasks.md", f"- [x] **Task 1**: t\n  - **_Boundary**: {boundary}\n  - _Requirements: AC-01_\n"
        )
        write(
            f"{directory}/reconcile.md",
            f"---\nreconcile_id: REC-x\nstatus: resolved\ntargets:\n  - file: {target}\n    resolution: modified\n---\n",
        )

    bundle("specs/2026-10/20261001-one", "SPEC-one", "completed", "`src/pkg/`, N/A", CAP)
    bundle("specs/2026-10/20261002-two", "SPEC-two", "completed", "`src/pkg/`, `src/other/`", CAP)
    bundle("specs/2026-10/20261003-three", "SPEC-three", "draft", "`src/other/`", USECASE)
    write("specs/2026-10/20261004-four/spec.md", "---\nid: SPEC-four\nstatus: completed\n---\n")
    return workspace


def test_single_bundle(bundles: Path) -> None:
    result = _derive(bundles, "--spec", "specs/2026-10/20261001-one")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[CANDIDATES: CAP-X-one path=docs/capabilities/x/CAP-X-one.md new=src/pkg missing=- folded=- declared=-]",
        "[SKIPPED: N/A kind=boundary spec=SPEC-one task=1 reason=not-a-path]",
        "[SUMMARY: pairs=1 new=1 declared=0 skipped=1 applied=0]",
    ]
    assert "entrypoints" not in (bundles / CAP).read_text()
    absolute = _derive(bundles, "--spec", str(bundles / "specs/2026-10/20261001-one"))
    assert absolute.stdout == result.stdout


def test_input_and_option_errors(bundles: Path, write: Write) -> None:
    result = _derive(bundles, "--spec", "specs/2026-10/20261004-four", "--format", "json")
    assert result.exit_code == 2
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "SPEC_ENTRYPOINTS_INPUT_MISSING"
    assert error["advisory"]["target_files"] == ["specs/2026-10/20261004-four/tasks.md"]
    for args in (
        [],
        ["--spec", "x", "--all"],
        ["--spec", "x", "--min-count", "2"],
        ["--spec", "x", "--status", "draft"],
        ["--all", "--min-count", "0"],
        ["--all", "--target", "CAP-X-one"],
        ["--spec", "../outside"],
    ):
        assert _code(_derive(bundles, *args, "--format", "json")) == "ARGUMENT_INVALID", args
    write("specs/2026-10/20261005-five/tasks.md", "- [ ] t\n")
    write("specs/2026-10/20261005-five/reconcile.md", "not yaml\n")
    result = _derive(bundles, "--spec", "specs/2026-10/20261005-five")
    assert result.exit_code == 2 and "(SPEC_ENTRYPOINTS_INPUT_INVALID)" in result.stderr


def test_all_aggregates_and_skips_bundles(bundles: Path) -> None:
    result = _derive(bundles, "--all")
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert (
        "[CANDIDATES: CAP-X-one path=docs/capabilities/x/CAP-X-one.md new=src/other(1),src/pkg(2) missing=- folded=- declared=-]"
        in lines
    )
    assert "UC-two" not in result.stdout
    assert "[SKIPPED: specs/2026-10/20261004-four kind=bundle spec=SPEC-four reason=input-missing]" in lines

    payload = json.loads(_derive(bundles, "--all", "--min-count", "2", "--format", "json").stdout)
    assert [pair["code"] for pair in payload["pairs"]] == ["src/pkg"]
    assert payload["summary"]["pairs"] == 1
    assert payload["errors"] == [] and payload["notices"] == []

    result = _derive(bundles, "--all", "--status", "Draft")
    assert "[CANDIDATES: UC-two path=docs/usecases/x/UC-two.md new=src/other(1) missing=- folded=- declared=-]" in (
        result.stdout.splitlines()
    )


def test_apply_with_targets(bundles: Path) -> None:
    assert _code(_derive(bundles, "--all", "--apply", "--target", "UC-nope", "--format", "json")) == (
        "SPEC_ENTRYPOINTS_TARGET_UNKNOWN"
    )
    assert _code(_derive(bundles, "--all", "--apply", "--target", USECASE, "--format", "json")) == (
        "SPEC_ENTRYPOINTS_TARGET_UNKNOWN"
    )
    result = _derive(bundles, "--all", "--apply", "--target", "CAP-X-one")
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert f"[APPLIED: CAP-X-one path={CAP} added=src/other/,src/pkg/]" in lines
    assert lines[-1] == "[SUMMARY: pairs=2 new=2 declared=0 skipped=2 applied=1]"
    assert (bundles / CAP).read_text() == (
        "---\nid: CAP-X-one\nstatus: active\nentrypoints:\n  - src/other/\n  - src/pkg/\n---\n"
    )
    result = _derive(bundles, "--all", "--apply", "--target", f"./{CAP}")
    assert "declared=src/other(1),src/pkg(2)]" in result.stdout and result.stdout.endswith("applied=0]\n")


def test_code_and_exclude_filters(bundles: Path) -> None:
    result = _derive(bundles, "--all", "--code", "src/other")
    assert "new=src/other(1) " in result.stdout
    result = _derive(bundles, "--all", "--exclude", "src/other/")
    assert "[SKIPPED: src/other kind=boundary reason=excluded]" in result.stdout.splitlines()
    assert "src/pkg(2)" in result.stdout
    assert _code(_derive(bundles, "--all", "--code", "../x", "--format", "json")) == "SPEC_ENTRYPOINTS_PATH_INVALID"


def test_unmatched_code_is_refused_before_writing(bundles: Path) -> None:
    result = _derive(
        bundles,
        "--all",
        "--apply",
        "--target",
        "CAP-X-one",
        "--code",
        "src/nowhere",
        "--code",
        "src/pkg",
        "--format",
        "json",
    )
    assert result.exit_code == 2
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "SPEC_ENTRYPOINTS_CODE_UNMATCHED"
    assert error["advisory"]["target_files"] == ["src/nowhere"]
    assert "entrypoints" not in (bundles / CAP).read_text()
    text = _derive(bundles, "--all", "--code", "src/nowhere")
    assert text.exit_code == 2 and text.stdout == ""
    assert "(SPEC_ENTRYPOINTS_CODE_UNMATCHED)" in text.stderr and "[TARGET] src/nowhere" in text.stderr
    assert _code(
        _derive(bundles, "--spec", "specs/2026-10/20261001-one", "--code", "src/other", "--format", "json")
    ) == ("SPEC_ENTRYPOINTS_CODE_UNMATCHED")
    # A code that only another document's candidates match is unmatched for the targeted document.
    both = ("--all", "--status", "completed,draft", "--apply", "--format", "json")
    assert _code(_derive(bundles, *both, "--target", "UC-two", "--code", "src/pkg/b.go")) == (
        "SPEC_ENTRYPOINTS_CODE_UNMATCHED"
    )
    assert "entrypoints" not in (bundles / USECASE).read_text()


def test_file_code_under_a_directory_candidate_is_applied(bundles: Path) -> None:
    args = ("--spec", "specs/2026-10/20261001-one", "--apply", "--target", "CAP-X-one", "--code", "src/pkg/b.go")
    result = _derive(bundles, *args)
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[CANDIDATES: CAP-X-one path=docs/capabilities/x/CAP-X-one.md new=src/pkg/b.go missing=- folded=- declared=-]",
        "[SKIPPED: N/A kind=boundary spec=SPEC-one task=1 reason=not-a-path]",
        f"[APPLIED: CAP-X-one path={CAP} added=src/pkg/b.go]",
        "[SUMMARY: pairs=1 new=1 declared=0 skipped=1 applied=1]",
    ]
    assert (bundles / CAP).read_text() == "---\nid: CAP-X-one\nstatus: active\nentrypoints:\n  - src/pkg/b.go\n---\n"
    rerun = _derive(bundles, *args)
    assert rerun.stdout.splitlines()[-1] == "[SUMMARY: pairs=1 new=0 declared=1 skipped=1 applied=0]"
    aggregated = _derive(bundles, "--all", "--code", "src/pkg/b.go", "--code", "src/other/c.go")
    assert "new=src/other/c.go(1) missing=- folded=- declared=src/pkg/b.go(2)]" in aggregated.stdout


def test_selected_folded_candidate_is_applied(bundles: Path, write: Write) -> None:
    write("specs/2026-10/20261011-nested/spec.md", "---\nid: SPEC-nested\nstatus: completed\n---\n")
    write(
        "specs/2026-10/20261011-nested/tasks.md",
        "- [x] **Task 1**: pkg\n  - **_Boundary**: src/pkg/, src/pkg/b.go\n  - _Requirements: AC-01_\n",
    )
    write(
        "specs/2026-10/20261011-nested/reconcile.md",
        f"---\nreconcile_id: REC-nested\nstatus: resolved\ntargets:\n  - file: {CAP}\n    resolution: modified\n---\n",
    )
    result = _derive(
        bundles, "--spec", "specs/2026-10/20261011-nested", "--apply", "--target", "CAP-X-one", "--code", "src/pkg/b.go"
    )
    assert result.exit_code == 0, result.output
    assert f"[APPLIED: CAP-X-one path={CAP} added=src/pkg/b.go]" in result.stdout.splitlines()
    assert "reason=folded" not in result.stdout


def test_apply_failure_is_reported_after_the_result(bundles: Path, write: Write) -> None:
    (bundles / CAP).chmod(0o444)
    (bundles / CAP).parent.chmod(0o555)
    try:
        result = _derive(bundles, "--all", "--apply", "--format", "json")
    finally:
        (bundles / CAP).parent.chmod(0o755)
        (bundles / CAP).chmod(0o644)
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert [error["code"] for error in payload["errors"]] == ["SPEC_ENTRYPOINTS_APPLY_FAILED"]
    assert payload["errors"][0]["advisory"]["target_files"] == [CAP]
    assert payload["summary"]["applied"] == 0


def test_invalid_documents_are_warnings(bundles: Path, write: Write) -> None:
    write("docs/usecases/x/UC-broken.md", "---\nid: [\n---\n")
    result = _derive(bundles, "--spec", "specs/2026-10/20261001-one")
    assert result.exit_code == 0
    assert "(SPEC_DOCUMENT_INVALID)" in result.stderr


def test_candidates_group_each_document_by_state() -> None:
    from devkit_spec.features.entrypoints import Pair, State
    from devkit_spec.features.entrypoints.cli.commands import _candidates

    pairs = [
        Pair("CAP-A", "a.md", "src/a", State.NEW, True, "SPEC-x", 1),
        Pair("CAP-A", "a.md", "src/a/b.py", State.NEW, True, "SPEC-x", 1, folded_into="src/a"),
        Pair("CAP-A", "a.md", "src/gone.py", State.NEW, False, "SPEC-x", 2),
        Pair("CAP-A", "a.md", "src/old", State.DECLARED, True, "SPEC-x", 2),
        Pair("UC-b", "b.md", "src/a", State.NEW, True, "SPEC-x", 1),
    ]
    assert _candidates(pairs) == [
        (
            "CAP-A",
            "a.md",
            {"new": ["src/a"], "missing": ["src/gone.py"], "folded": ["src/a/b.py"], "declared": ["src/old"]},
        ),
        ("UC-b", "b.md", {"new": ["src/a"], "missing": [], "folded": [], "declared": []}),
    ]


def test_apply_target_named_by_an_alias(bundles: Path, write: Write) -> None:
    write(CAP, "---\nid: CAP-X-one\nstatus: active\naliases: [CAP-X-first]\n---\n")
    result = _derive(bundles, "--all", "--apply", "--target", "CAP-X-first")
    assert result.exit_code == 0, result.output
    assert f"[APPLIED: CAP-X-one path={CAP} added=src/other/,src/pkg/]" in result.stdout.splitlines()


def test_derive_directory_code_folds_and_applies(bundles: Path, write: Write) -> None:
    write("src/sub/one.go", "package sub\n")
    write("src/sub/two.go", "package sub\n")
    write("specs/2026-10/20261010-files/spec.md", "---\nid: SPEC-files\nstatus: completed\n---\n")
    write(
        "specs/2026-10/20261010-files/tasks.md",
        "- [x] **Task 1**: sub\n  - **_Boundary**: src/sub/one.go, src/sub/two.go\n  - _Requirements: AC-01_\n",
    )
    write(
        "specs/2026-10/20261010-files/reconcile.md",
        f"---\nreconcile_id: REC-files\nstatus: resolved\ntargets:\n  - file: {CAP}\n    resolution: modified\n---\n",
    )

    bare_res = _derive(bundles, "--spec", "specs/2026-10/20261010-files", "--code", "src/sub")
    assert bare_res.exit_code == 0
    assert (
        "[CANDIDATES: CAP-X-one path=docs/capabilities/x/CAP-X-one.md new=src/sub/one.go,src/sub/two.go missing=- folded=- declared=-]"
        in bare_res.stdout
    )

    dir_res = _derive(bundles, "--spec", "specs/2026-10/20261010-files", "--code", "src/sub/")
    assert dir_res.exit_code == 0
    assert (
        "[CANDIDATES: CAP-X-one path=docs/capabilities/x/CAP-X-one.md new=src/sub missing=- folded=src/sub/one.go,src/sub/two.go declared=-]"
        in dir_res.stdout
    )

    apply_res = _derive(
        bundles, "--spec", "specs/2026-10/20261010-files", "--apply", "--target", "CAP-X-one", "--code", "src/sub/"
    )
    assert apply_res.exit_code == 0
    assert f"[APPLIED: CAP-X-one path={CAP} added=src/sub/]" in apply_res.stdout
    cap_text = (bundles / CAP).read_text()
    assert "src/sub/" in cap_text
    assert "src/sub/one.go" not in cap_text

    missing_res = _derive(bundles, "--spec", "specs/2026-10/20261010-files", "--code", "src/nonexistent/")
    assert missing_res.exit_code == 2
