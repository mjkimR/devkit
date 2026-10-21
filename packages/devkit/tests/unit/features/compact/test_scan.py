"""``devkit_agt.features.compact.services.scan``: recognized summaries and warnings, relayed advisory blocks, the excerpt, the budgets."""

from __future__ import annotations

import importlib
import io
import re
import time

import pytest
from devkit.advisory import AdvisoryError, Level
from devkit_agt.features.compact.services.scan import (
    ADVISORY_BUDGET,
    FAILURE_BUDGET,
    HEAD,
    LAST_BUDGET,
    LAST_LINES,
    MAX_LINE,
    SUMMARY_BUDGET,
    TAIL,
    WARNING_BUDGET,
    WARNING_MESSAGE,
    Failure,
    Scan,
    ToolWarning,
    scan,
)

scan_module = importlib.import_module(
    "devkit_agt.features.compact.services.scan"
)  # the package exports the function under this name


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
        "Found 3 errors.",
        "Found 1 error in src/index.ts:3",
        "Found 3 errors in 2 files.",
        "Found 3 errors in the same file, starting at: src/index.ts:1",
        "Found 0 errors. Watching for file changes.",
        "Found 5 errors in 2 files (checked 10 source files)",
        "Success: no issues found in 5 source files",
        "Tests:       1 failed, 3 passed, 4 total",
        "Test Suites: 2 passed, 2 total",
        "test result: ok. 15 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s",
        "test result: FAILED. 1 passed; 1 failed; 0 ignored",
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


_MARKER = re.compile(r"\[\.\.\. (?P<chars>\d+) characters omitted, log lines (?P<first>\d+)-(?P<last>\d+) \.\.\.\]\n")


def test_large_output_keeps_head_and_tail_with_a_marker() -> None:
    text = "".join(f"line {i:05d} {'x' * 60}\n" for i in range(1000)) + "FAILED tests/test_a.py::test_last\n"
    result = _scan(text)
    head, chars, first, last, tail = _MARKER.split(result.output)
    assert int(chars) == result.omitted.output
    assert text.startswith(head) and text.endswith(tail)
    assert len(head) <= HEAD and len(tail) <= TAIL
    assert len(head) + result.omitted.output + len(tail) == len(text)
    assert tail.endswith("FAILED tests/test_a.py::test_last\n")
    # The marker names exactly the log lines it stands for: `sed -n 'FIRST,LASTp' <log>` reads them.
    assert "".join(text.splitlines(keepends=True)[int(first) - 1 : int(last)]) == text[len(head) : -len(tail)]


def test_the_marker_counts_log_lines_including_filtered_lines_and_advisory_blocks() -> None:
    block = _block(Level.WARNING, "OVERRIDE_DRIFT", "drift")
    lines = [
        "tests/test_a.py ..... [ 10%]",
        *block.splitlines(),
        *(f"line {i:05d} {'x' * 60}" for i in range(400)),
    ]
    result = _scan("".join(f"{line}\n" for line in lines))
    match = _MARKER.search(result.output)
    assert match
    first, last = int(match["first"]), int(match["last"])
    head = result.output[: match.start()].splitlines()
    tail = result.output[match.end() :].splitlines()
    assert lines[first - 2] == head[-1] and lines[last] == tail[0]


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
    filler = "".join(f"{i:03d} {'y' * 80}\n" for i in range(200))
    result = _scan(filler + error + "\n" + filler)
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
        "....................................................................sx [100%]",
        "........................................................................ [ 54%]",
        "tests/test_mix.py ..s.. [ 12/130]",
        "tests/test_mix.py::test_many[0] PASSED                                         [  0%]",
        "tests/test_mix.py::test_param[a b] SKIPPED (no db)                             [ 50%]",
        "tests/test_mix.py::test_xf XFAIL                                               [ 99%]",
        "[gw0] [ 12%] PASSED tests/test_mix.py::test_many[3]",
        "[gw3] [ 40%] SKIPPED tests/test_mix.py::test_skip",
        "tests/test_mix.py::test_many[3] ",  # pytest-xdist -v, as the test starts
        "tests/test_mix.py::test_param[a b] ",
        "                                                                         [100%]",
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
        "tests/test_mix.py ..F.. [ 45%]",
        "..E..sx [100%]",
        "tests/test_mix.py::test_many[3]",  # a --collect-only listing
        "4 workers [125 items]",
        "[gw1] node down: Not properly terminated",
        "replacing crashed worker gw1",
        "worker 'gw1' crashed while running 'tests/test_mix.py::test_crash'",
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
        "created: 8/8 workers",
        "bringing up nodes...",
        "scheduling tests via WorkStealingScheduling",
        "[gw3] darwin -- Python 3.12.8 /work/project/.venv/bin/python",
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


def test_an_empty_line_inside_an_advisory_value_keeps_the_block_whole() -> None:
    block = AdvisoryError("broken", "Traceback:\n\n  File x", code="X_FAILED").render()
    result = _scan(f"{block}\nafter\n")
    assert [a.text for a in result.advisories] == [block]
    assert result.output == "after\n"


def test_an_empty_line_ends_an_advisory_block() -> None:
    # A rendered block has no empty lines: indented tool output after one is not part of the block.
    block = _block(Level.ERROR, "X_FAILED", "nested failed")
    indented = "         line of a deeply indented traceback\n"
    result = _scan(f"{block}\n\n{indented}tests/x.py:3: AssertionError\n")
    assert [a.text for a in result.advisories] == [block]
    assert result.output == f"\n{indented}tests/x.py:3: AssertionError\n"


def test_a_block_longer_than_its_budget_stays_in_the_excerpt_and_is_counted() -> None:
    lines = "".join(f"         code {i}\n" for i in range(300))  # 5,400 characters: over the budget, not the excerpt's
    result = _scan(f"[WARN]   (X_DRIFT) w\n{lines}FAILED tests/x.py::t - boom\n")
    assert result.advisories == () and result.omitted.advisories == 1
    assert result.output.startswith("[WARN]   (X_DRIFT) w\n         code 0\n")
    assert result.output.endswith("         code 299\nFAILED tests/x.py::t - boom\n")
    assert result.omitted.output == 0


def test_a_block_that_does_not_fit_what_is_left_of_the_budget_stays_in_the_excerpt() -> None:
    block = _block(Level.WARNING, "ORPHAN_LEFT", "z" * 1_500)
    result = _scan(f"{block}\n" * 3)
    assert [a.text for a in result.advisories] == [block, block] and result.omitted.advisories == 1
    assert result.output == f"{block}\n"


def test_errors_have_a_budget_of_their_own() -> None:
    notice = _block(Level.NOTICE, "BUNDLE_UNSELECTED", "n" * 900)
    error = _block(Level.ERROR, "CONFIG_INVALID", "decisive")
    result = _scan(f"{notice}\n" * 5 + f"{error}\n" + f"{notice}\n")
    assert [a.level for a in result.advisories][-1] is Level.ERROR
    assert result.omitted.advisories == 6 - sum(a.level is Level.NOTICE for a in result.advisories)


def test_an_over_long_line_keeps_its_start_and_end_and_marks_the_cut() -> None:
    result = _scan("Error: the real cause " + "y" * 200_000 + " the end\n")
    first, marker, last = result.output.splitlines()
    assert first.startswith("Error: the real cause") and len(first) == MAX_LINE
    assert last.endswith(" the end") and len(last) == MAX_LINE
    assert marker == f"[... {result.omitted.output} characters of log line 1 omitted ...]"
    assert len(first) + result.omitted.output + len(last) == len("Error: the real cause ") + 200_000 + len(" the end")


def test_last_lines_are_the_last_non_blank_lines_of_the_excerpt() -> None:
    notice = _block(Level.NOTICE, "BUNDLE_UNSELECTED", "extras")
    result = _scan(
        "".join(f"step {i}\n" for i in range(10))
        + "  Success: built 3 targets  \n\n"
        + "Installed 3 packages in 2ms\n"  # filtered noise is not a last line
        + f"{notice}\n\n"
    )
    assert result.last_lines == ("step 6", "step 7", "step 8", "step 9", "Success: built 3 targets")
    assert len(result.last_lines) == LAST_LINES


def test_last_lines_keep_to_their_budget_and_cut_only_an_over_long_last_line() -> None:
    lines = [f"{i} {'y' * 148}" for i in range(10)]
    result = _scan("".join(f"{line}\n" for line in lines))
    assert result.last_lines == tuple(lines[-3:])
    assert sum(len(text) + 1 for text in result.last_lines) <= LAST_BUDGET
    (last,) = _scan("short\n" + "z" * (MAX_LINE * 3) + "\n").last_lines
    assert last.endswith("...") and len(last) + 1 <= LAST_BUDGET


def test_last_lines_come_from_the_tail_when_the_output_is_cut() -> None:
    result = _scan("".join(f"line {i:05d} {'x' * 60}\n" for i in range(1000)))
    assert result.last_lines[-1] == f"line 00999 {'x' * 60}"
    assert _scan("").last_lines == ()


def _filler(name: str, size: int) -> str:
    """Distinct lines of about ``size`` characters, so none of them collapses into a repeat."""
    return "".join(f"{name} {i:05d} {'.' * 60}\n" for i in range(size // 72 + 1))


def _cut_out(text: str) -> str:
    """``text`` between enough output that the excerpt's head and tail leave it out."""
    return _filler("before", HEAD + 500) + text + _filler("after", TAIL + 500)


@pytest.mark.parametrize(
    "line,expected",
    [
        (
            "FAILED tests/test_a.py::test_x - AssertionError: assert 1 == 2",
            Failure("tests/test_a.py::test_x", "failed", "AssertionError: assert 1 == 2"),
        ),
        (
            "FAILED tests/test_a.py::TestCase::test_param[a b-1]",
            Failure("tests/test_a.py::TestCase::test_param[a b-1]", "failed"),
        ),
        (
            "ERROR tests/test_a.py::test_db - RuntimeError: database is not reachable",
            Failure("tests/test_a.py::test_db", "error", "RuntimeError: database is not reachable"),
        ),
        (
            "ERROR tests/test_broken.py - ImportError: no module",
            Failure("tests/test_broken.py", "error", "ImportError: no module"),
        ),
        ("[gw1] [ 59%] FAILED tests/test_a.py::test_x", Failure("tests/test_a.py::test_x", "failed")),
        (
            "tests/test_a.py::test_x FAILED                                            [ 59%]",
            Failure("tests/test_a.py::test_x", "failed"),
        ),
    ],
)
def test_failed_tests_the_excerpt_cuts_out_are_listed(line: str, expected: Failure) -> None:
    result = _scan(_cut_out(f"{line}\n"))
    assert line not in result.output
    assert result.failures == (expected,)


def test_failed_tests_the_excerpt_shows_are_not_repeated() -> None:
    assert _scan("FAILED tests/test_a.py::test_x - assert 1 == 2\n").failures == ()
    # Named by its -v line in the head, the test is in the excerpt although its short summary line is cut.
    result = _scan(
        "tests/test_a.py::test_x FAILED [ 50%]\n" + _cut_out("FAILED tests/test_a.py::test_x - assert 1 == 2\n")
    )
    assert result.failures == ()


def test_a_failure_takes_the_message_its_short_summary_gives() -> None:
    result = _scan(_cut_out("tests/test_a.py::test_x FAILED [ 50%]\nFAILED tests/test_a.py::test_x - assert 1 == 2\n"))
    assert result.failures == (Failure("tests/test_a.py::test_x", "failed", "assert 1 == 2"),)


@pytest.mark.parametrize(
    "line",
    [
        "FAILED",
        "Build FAILED.",
        "ERROR: Could not find a version that satisfies the requirement nope",
        "FAIL src/b.test.js",
        "FAILED (errors=2)",
    ],
)
def test_other_failure_lines_are_not_tests(line: str) -> None:
    assert _scan(_cut_out(f"{line}\n")).failures == ()


def test_failures_have_a_budget_and_each_left_out_test_is_counted_once() -> None:
    progress = "".join(f"tests/test_a.py::test_{i:03d} FAILED [ 1%]\n" for i in range(300))
    summary = "".join(f"FAILED tests/test_a.py::test_{i:03d} - AssertionError: value {i}\n" for i in range(300))
    result = _scan(_cut_out(progress + summary))
    named = {failure.test for failure in result.failures}
    assert sum(len(f.test) + len(f.message) + 1 for f in result.failures) <= FAILURE_BUDGET
    assert len(named) + result.omitted.failures + sum(f"::test_{i:03d} " in result.output for i in range(300)) == 300


def test_identical_lines_keep_the_first_and_a_count_with_their_log_lines() -> None:
    line = "connect ECONNREFUSED 127.0.0.1:5432, retrying in 1s"
    text = "start\n" + f"{line}\n" * 100 + "Error: gave up\n"
    result = _scan(text)
    assert result.output.splitlines() == [
        "start",
        line,
        "[... previous line repeated 99 more times, log lines 3-101 ...]",
        "Error: gave up",
    ]
    assert result.filtered == 99


def test_a_count_is_used_only_when_it_is_shorter() -> None:
    result = _scan("ok\nok\nok\nend\n")
    assert result.output == "ok\nok\nok\nend\n" and result.filtered == 0


def test_repeats_at_the_end_of_the_output_are_counted_too() -> None:
    line = "x" * 80
    result = _scan(f"{line}\n" * 3)
    assert result.output == f"{line}\n[... previous line repeated 2 more times, log lines 2-3 ...]\n"


def test_only_consecutive_lines_of_the_excerpt_collapse() -> None:
    line = "y" * 80
    assert _scan(f"{line}\n\n{line}\n").output == f"{line}\n\n{line}\n"
    # A filtered line between them leaves them consecutive in the excerpt.
    result = _scan(f"{line}\ntests/test_a.py .... [ 50%]\n{line}\n")
    assert result.output == f"{line}\n[... previous line repeated 1 more time, log line 3 ...]\n"


def test_read_counts_every_character_of_the_output() -> None:
    text = "a\r\nb\x1b[31mred\x1b[0m\n" + "z" * 200_000 + "\n"
    assert _scan(text).read == len(text)


@pytest.mark.parametrize(
    "line",
    ["FAILED x.py" + "::a" * 40 + " !", "x.py" + "::a" * 40 + " FAILED oops", "x.py" + "::a" * 40 + "  "],
)
def test_a_long_run_of_node_id_separators_is_scanned_in_linear_time(line: str) -> None:
    # Each "::" once split two ways, so 40 of them took longer than any run; now it is milliseconds.
    started = time.monotonic()
    _scan(f"{line}\n" * 20)
    assert time.monotonic() - started < 5


def test_a_warnings_summary_without_its_closing_line_ends_at_output_that_is_not_part_of_it() -> None:
    result = _scan(
        "============================= warnings summary =============================\n"
        "tests/test_a.py::test_x\n"
        "tests/test_a.py: 12 warnings\n"
        "../lib/compat.py:41\n"
        "  /abs/tests/test_a.py:5: UserWarning: boom\n"
        "    warnings.warn('boom')\n"
        "\n"
        "FAILED tests/test_a.py::test_y - assert 1 == 2\n"
        "error: Recipe `test` failed on line 3 with exit code 1\n"
    )
    assert (
        result.output
        == "FAILED tests/test_a.py::test_y - assert 1 == 2\nerror: Recipe `test` failed on line 3 with exit code 1\n"
    )
    assert result.warnings == (ToolWarning("UserWarning: boom", "/abs/tests/test_a.py:5"),)


def test_a_line_that_names_a_failure_is_never_filtered_inside_the_warnings_summary() -> None:
    result = _scan(
        "============================= warnings summary =============================\n"
        "tests/test_a.py::test_x\n"
        "  FAILED tests/test_a.py::test_y - assert 1 == 2\n"
        "-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n"
    )
    assert result.output == "  FAILED tests/test_a.py::test_y - assert 1 == 2\n"


def test_a_repeat_marker_cut_from_the_excerpt_names_every_line_it_stood_for() -> None:
    # The head ends just before the marker, which is the first piece the tail drops.
    lines = ["a" * 999, "b" * 999, "c" * 940, *["r" * 30] * 6, *(f"t{i:03d} {'z' * 50}" for i in range(200))]
    result = _scan("".join(f"{line}\n" for line in lines))
    assert re.search(r"\[\.\.\. \d+ characters omitted, log lines 5-\d+ \.\.\.\]", result.output)


def test_failed_tests_past_those_remembered_are_counted_once_and_not_when_shown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scan_module, "FAILURES_KEPT", 3)
    tests = [f"tests/test_a.py::test_{i:02d}" for i in range(10)]
    verbose = "".join(f"{test} FAILED [ 50%]\n" for test in tests)
    summary = "".join(f"FAILED {test} - AssertionError\n" for test in tests[:8])
    result = _scan(_cut_out(verbose + summary) + "".join(f"FAILED {test} - AssertionError\n" for test in tests[8:]))
    shown = {test for test in tests if f"{test} " in result.output}
    assert shown == set(tests[8:])
    assert len(result.failures) == 3 and result.omitted.failures == 5


def test_last_lines_are_never_a_marker_line() -> None:
    line = "x" * 80
    assert _scan(f"done\n{line}\n{line}\n{line}\n").last_lines == ("done", line)
    assert _scan(f"done\n{line}\n{line}\n{line}\nlast\n").last_lines == ("done", line, "last")


def test_hyperlinks_and_charset_selections_are_not_output() -> None:
    link = "\x1b]8;;file:///work/a.py\x1b\\a.py\x1b]8;;\x1b\\"
    result = _scan(f"\x1b(B{link}:3: UserWarning: old\n\x1b]0;title\x07Found 1 error.\n")
    assert result.warnings == (ToolWarning("UserWarning: old", "a.py:3"),)
    assert result.summaries == ("Found 1 error.",)
