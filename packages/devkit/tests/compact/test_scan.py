"""``devkit.compact.scan``: recognized summaries and warnings, relayed advisory blocks, the excerpt, the budgets."""

from __future__ import annotations

import io

import pytest
from devkit.advisory import AdvisoryError, Level
from devkit.compact.scan import (
    ADVISORY_BUDGET,
    HEAD,
    MAX_LINE,
    SUMMARY_BUDGET,
    TAIL,
    WARNING_BUDGET,
    WARNING_MESSAGE,
    Scan,
    ToolWarning,
    scan,
)


def _scan(text: str, *, notices: bool = True, base: list[str] | None = None) -> Scan:
    return scan(io.StringIO(text), notices=notices, base=base or ())


@pytest.mark.parametrize(
    "line",
    [
        "===== 42 passed, 2 skipped, 3 deselected, 1 xfailed, 4 warnings in 1.23s =====",
        "42 passed, 1 xpassed, 2 rerun in 65.20s (0:01:05)",
        "no tests ran in 0.01s",
        " Test Files  2 passed | 1 skipped (3)",
        "      Tests  12 passed | 2 skipped | 1 todo (15)",
        "  12 passed (1.2m)",
        "  2 flaky",
        "  3 did not run",
        "12 files already formatted",
        "1 file reformatted, 12 files left unchanged",
        "All checks passed!",
        "Found 3 errors (3 fixed, 0 remaining).",
        "0 errors, 2 warnings, 0 informations",
        "svelte-check found 0 errors and 2 warnings in 1 file",
        "✖ 2 problems (0 errors, 2 warnings)",
        "All matched files use Prettier code style!",
        "[SUMMARY: errors=0 warnings=2 infos=0 fixed=0]",
    ],
)
def test_recognizes_terminal_summaries_with_color_and_crlf(line: str) -> None:
    result = _scan(f"uninteresting output\n\x1b[32m{line}\x1b[0m\r\n")
    assert result.summaries == (line.strip().strip("=").strip(),)


@pytest.mark.parametrize("line", ["TOTAL   100  10  90%", "TOTAL   100  10  20  2  88.5%"])
def test_coverage_total_has_context(line: str) -> None:
    assert _scan(line).summaries == (f"Coverage: {line}",)


def test_does_not_infer_results_from_progress_or_arbitrary_messages() -> None:
    result = _scan(
        "tests/test_sample.py::test_ok PASSED\n"
        "collected 42 items\n"
        "test example: 42 passed\n"
        "Tests 12 passed (13) extra text\n"
        "verbose success output\n"
    )
    assert result.summaries == () and result.warnings == ()


def test_summary_budget_and_long_lines_are_bounded() -> None:
    result = _scan("x" * (MAX_LINE * 100) + "42 passed\n" + "12 passed in 0.10s\n" * SUMMARY_BUDGET)
    assert result.summaries[0] == "12 passed in 0.10s"
    assert sum(len(line) + 1 for line in result.summaries) <= SUMMARY_BUDGET
    assert result.omitted.summaries == SUMMARY_BUDGET - len(result.summaries)


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "lib/db.py:12: UserWarning: In-memory database",
            ToolWarning("UserWarning: In-memory database", "lib/db.py:12"),
        ),
        (
            "src/app.py:2:3 - warning: Unused import (reportUnusedImport)",
            ToolWarning("Unused import (reportUnusedImport)", "src/app.py:2:3"),
        ),
        (
            "(node:123) [DEP0040] DeprecationWarning: Deprecated module",
            ToolWarning("[DEP0040] DeprecationWarning: Deprecated module"),
        ),
        ("warning: Deprecated configuration", ToolWarning("Deprecated configuration")),
        (
            "src/App.svelte:2:3\nWarn: Missing label (svelte)",
            ToolWarning("Missing label (svelte)", "src/App.svelte:2:3"),
        ),
        (
            "/project/src/app.ts\n  2:3  warning  Unused variable  no-unused-vars",
            ToolWarning("Unused variable no-unused-vars", "/project/src/app.ts:2:3"),
        ),
    ],
)
def test_warnings_carry_their_location_without_source_excerpts(text: str, expected: ToolWarning) -> None:
    assert _scan(f"\x1b[33m{text}\x1b[0m\n  unrelated source excerpt\n").warnings == (expected,)


def test_repeated_warnings_are_reported_once() -> None:
    result = _scan("a.py:1: UserWarning: same\nb.py:2: UserWarning: same\n")
    assert result.warnings == (ToolWarning("UserWarning: same", "a.py:1"),)


def test_warning_budget_does_not_hide_test_results() -> None:
    result = _scan("".join(f"warning: issue {i}\n" for i in range(500)) + "12 passed, 500 warnings in 0.10s\n")
    assert sum(len(w.message) + len(w.location) + 1 for w in result.warnings) <= WARNING_BUDGET
    assert result.omitted.warnings == 500 - len(result.warnings)
    assert result.summaries == ("12 passed, 500 warnings in 0.10s",)


@pytest.mark.parametrize("length", [700, MAX_LINE * 100])
def test_long_warning_message_keeps_category_and_location(length: int) -> None:
    (warning,) = _scan("lib/db.py:12: UserWarning: " + "x" * length).warnings
    assert warning.message.startswith("UserWarning: ") and warning.message.endswith("...")
    assert warning.location == "lib/db.py:12"
    assert len(warning.message) <= WARNING_MESSAGE + 3


def test_suppressed_warning_details_are_not_invented() -> None:
    result = _scan("2 passed, 1 warning in 0.10s\n")
    assert result.summaries == ("2 passed, 1 warning in 0.10s",) and result.warnings == ()


def test_small_output_is_kept_whole() -> None:
    text = "first\nsecond\n"
    result = _scan(text)
    assert result.output == text and not result.omitted


def test_large_output_keeps_head_and_tail_with_a_marker() -> None:
    text = "".join(f"line {i:05d} {'x' * 60}\n" for i in range(1000)) + "FAILED tests/test_a.py::test_last\n"
    result = _scan(text)
    head, tail = result.output.split(f"[... {result.omitted.output} characters omitted ...]\n")
    assert text.startswith(head) and text.endswith(tail)
    assert len(head) <= HEAD and len(tail) <= TAIL
    assert len(head) + result.omitted.output + len(tail) == len(text)
    assert tail.endswith("FAILED tests/test_a.py::test_last\n")


def _block(level: Level, code: str, message: str) -> str:
    return AdvisoryError(message, code=code, level=level, fix="devkit sync").render()


def test_advisory_blocks_are_relayed_whole_and_left_out_of_the_excerpt() -> None:
    warning = _block(Level.WARNING, "OVERRIDE_DRIFT", "upstream drift")
    error = _block(Level.ERROR, "CONFIG_INVALID", "broken\nsecond line")
    result = _scan(f"before\n{warning}\nbetween\n{error}\nafter\n")
    assert [(a.level, a.text) for a in result.advisories] == [(Level.WARNING, warning), (Level.ERROR, error)]
    assert result.output == "before\nbetween\nafter\n"


def test_an_advisory_survives_when_the_output_around_it_is_cut() -> None:
    error = _block(Level.ERROR, "RULES_CONFIG_INVALID", "bad table")
    filler = "y" * 80 + "\n"
    result = _scan(filler * 200 + error + "\n" + filler * 200)
    assert [a.text for a in result.advisories] == [error]
    assert result.omitted.output > 0 and "RULES_CONFIG_INVALID" not in result.output


def test_relayed_notices_can_be_dropped() -> None:
    notice = _block(Level.NOTICE, "BUNDLE_UNSELECTED", "extras")
    warning = _block(Level.WARNING, "ORPHAN_LEFT", "left")
    result = _scan(f"{notice}\n{warning}\n", notices=False)
    assert [a.level for a in result.advisories] == [Level.WARNING]
    assert result.output == ""


def test_advisory_budget_counts_what_is_left_out() -> None:
    block = _block(Level.WARNING, "ORPHAN_LEFT", "z" * 500)
    result = _scan(f"{block}\n" * 20)
    assert sum(len(a.text) + 1 for a in result.advisories) <= ADVISORY_BUDGET
    assert result.omitted.advisories == 20 - len(result.advisories) > 0


def test_lines_that_only_look_like_continuations_stay_in_the_excerpt() -> None:
    result = _scan("         indented code\n[ACTION] stray field\n")
    assert result.advisories == ()
    assert result.output == "         indented code\n[ACTION] stray field\n"


@pytest.mark.parametrize(
    "line",
    [
        "tests/test_mix.py ............................................................ [ 45%]",
        ".................F....................................................sx [100%]",
        "........................................................................ [ 54%]",
        "tests/test_mix.py ..E.. [ 12/130]",
        "tests/test_mix.py::test_many[0] PASSED                                         [  0%]",
        "tests/test_mix.py::test_param[a b] SKIPPED (no db)                             [ 50%]",
        "tests/test_mix.py::test_xf XFAIL                                               [ 99%]",
        "[gw0] [ 12%] PASSED tests/test_mix.py::test_many[3]",
        "[gw3] [ 40%] SKIPPED tests/test_mix.py::test_skip",
        "PASSED tests/test_mix.py::test_many[1]",
        " ✓ src/a.test.ts (3 tests) 5ms",
        "  ✓  1 [chromium] › a.spec.ts:3:5 › has title (1.1s)",  # noqa: RUF001
        "PASS src/a.test.js (5.2 s)",
        "··········",
    ],
)
def test_progress_lines_are_filtered_and_counted(line: str) -> None:
    result = _scan(f"before\n{line}\nafter\n")
    assert result.output == "before\nafter\n" and result.filtered == 1


@pytest.mark.parametrize(
    "line",
    [
        "tests/test_mix.py::test_many[77] FAILED                                        [ 59%]",
        "tests/test_mix.py::test_db ERROR                                               [ 60%]",
        "[gw1] [ 59%] FAILED tests/test_mix.py::test_many[77]",
        "FAILED tests/test_mix.py::test_many[77] - assert 77 != 77",
        "E       assert 77 != 77",
        "tests/test_mix.py:3: AssertionError",
        "collected 132 items",
        " ❯ src/b.test.ts (2 tests | 1 failed) 5ms",  # noqa: RUF001
        "   × adds numbers 3ms",  # noqa: RUF001
        "FAIL src/b.test.js",
        "SKIPPED [1] tests/test_mix.py:4: needs a database",
        "··F··",
    ],
)
def test_lines_that_name_a_failure_or_carry_content_are_kept(line: str) -> None:
    result = _scan(f"{line}\n")
    assert result.output == f"{line}\n" and result.filtered == 0


def test_a_carriage_return_leaves_only_what_a_terminal_shows() -> None:
    result = _scan("Downloading 10%\rDownloading 50%\rDownloading 100%\r\nreal line\r\n")
    assert result.output == "Downloading 100%\nreal line\n"
    assert result.filtered == 2


def test_a_long_progress_bar_without_newlines_keeps_its_final_state() -> None:
    bar = "".join(f"\r[{'#' * (i // 10):<100}] {i}%" for i in range(1001))
    result = _scan(bar + "\nError: build failed\n")
    assert result.output.splitlines() == [f"[{'#' * 100}] 1000%", "Error: build failed"]
    assert result.filtered >= 1000 and not result.omitted


@pytest.mark.parametrize(
    "line",
    [
        "============================= test session starts ==============================",
        "platform darwin -- Python 3.12.8, pytest-9.1.1, pluggy-1.6.0",
        "rootdir: /work/project",
        "configfile: pyproject.toml",
        "cachedir: .pytest_cache",
        "plugins: cov-7.1.0, xdist-3.6.1",
        "Resolved 120 packages in 1ms",
        "Installed 1 package in 1ms",
        "Audited 118 packages in 0.52ms",
        "   Building devkit @ file:///work/project/packages/devkit",
        "      Built devkit @ file:///work/project/packages/devkit",
        "Downloading numpy (5.1MiB)",
        " + requests==2.32.3",
        " - urllib3==1.26.0",
        " ~ devkit==0.1.0 (from file:///work/project/packages/devkit)",
    ],
)
def test_lines_without_anything_to_act_on_are_filtered(line: str) -> None:
    result = _scan(f"before\n{line}\nafter\n")
    assert result.output == "before\nafter\n" and result.filtered == 1


@pytest.mark.parametrize(
    "line",
    [
        "collected 132 items",
        "error: Failed to prepare distributions",
        "  × No solution found when resolving dependencies:",  # noqa: RUF001
        "+ added line in a diff",
        "- removed line",
        "===== 1 failed, 3 passed in 0.10s =====",
    ],
)
def test_lines_that_look_alike_but_carry_content_are_kept(line: str) -> None:
    result = _scan(f"{line}\n")
    assert result.output == f"{line}\n" and result.filtered == 0


def test_a_run_of_blank_lines_keeps_one_also_around_filtered_lines() -> None:
    result = _scan("a\n\n\n \nb\n\ntests/test_a.py .... [100%]\n\nc\n")
    assert result.output == "a\n\nb\n\nc\n"
    assert result.filtered == 4  # two blanks after a, the progress line, the blank after it


def test_the_pytest_warnings_summary_is_filtered_but_its_warnings_are_reported() -> None:
    result = _scan(
        "=================================== FAILURES ===================================\n"
        "E   assert 3 != 3\n"
        "=============================== warnings summary ===============================\n"
        "tests/test_w.py::test_w[0]\n"
        "  /work/project/tests/test_w.py:4: DeprecationWarning: old api\n"
        "    warnings.warn('old api', DeprecationWarning)\n"
        "\n"
        "-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n"
        "=========================== short test summary info ============================\n"
        "FAILED tests/test_w.py::test_w[3] - assert 3 != 3\n"
        "==================== 1 failed, 4 passed, 5 warnings in 0.01s ====================\n",
        base=["/work/project"],
    )
    assert result.output.splitlines() == [
        "=================================== FAILURES ===================================",
        "E   assert 3 != 3",
        "=========================== short test summary info ============================",
        "FAILED tests/test_w.py::test_w[3] - assert 3 != 3",
        "==================== 1 failed, 4 passed, 5 warnings in 0.01s ====================",
    ]
    assert result.filtered == 6  # banner, test id, warning, source line, blank, docs link
    assert result.warnings == (ToolWarning("DeprecationWarning: old api", "tests/test_w.py:4"),)
    assert result.summaries == ("1 failed, 4 passed, 5 warnings in 0.01s",)


@pytest.mark.parametrize("closing", ["-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n", ""])
def test_the_warnings_summary_ends_without_a_banner_under_quiet(closing: str) -> None:
    # pytest -q prints its final summary without a banner; what a recipe runs next must stay visible.
    result = _scan(
        "============================== warnings summary ===============================\n"
        "tests/test_ok.py::test_ok\n"
        "  /work/tests/test_ok.py:2: DeprecationWarning: old\n"
        "\n"
        f"{closing}"
        "1 passed, 1 warning in 0.01s\n"
        "src/app.py:3:1 - error: Cannot access attribute\n"
        "1 error, 0 warnings, 0 informations\n"
    )
    assert result.output.splitlines() == [
        "1 passed, 1 warning in 0.01s",
        "src/app.py:3:1 - error: Cannot access attribute",
        "1 error, 0 warnings, 0 informations",
    ]
    assert result.summaries == ("1 passed, 1 warning in 0.01s", "1 error, 0 warnings, 0 informations")


def test_only_an_unindented_complete_line_ends_the_warnings_summary() -> None:
    result = _scan(
        "=============================== warnings summary ===============================\n"
        "tests/test_a.py::test_a\n"
        "  /work/tests/test_a.py:2: UserWarning: counts\n"
        "    3 warnings\n"
        "  " + "x" * (MAX_LINE + 10) + " 2 passed\n"
        "  more warning detail\n"
        "-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n"
        "after\n"
    )
    assert result.output == "after\n"


def test_warning_locations_outside_the_base_stay_absolute() -> None:
    result = _scan("/elsewhere/lib.py:3: UserWarning: x\n/work/app.py:1: UserWarning: y\n", base=["/work/"])
    assert [w.location for w in result.warnings] == ["/elsewhere/lib.py:3", "app.py:1"]
