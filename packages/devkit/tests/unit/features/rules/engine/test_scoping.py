"""Target scoping in ``evaluate_rules``: declared ``inputs`` skip a rule no explicit working-tree target can affect."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from devkit_agt.features.rules import (
    Phase,
    RuleContext,
    RuleDefinitionError,
    Severity,
    Snapshot,
    Violation,
    evaluate_rules,
)
from devkit_agt.features.rules.services.builtins import BaseRule

ROOT = Path("/scoping-workspace")


@dataclass
class Probe:
    """A protocol-only rule recording each check; ``inputs`` is whatever the test sets."""

    id: str
    inputs: Any = None
    name: str = "probe"
    description: str = "probe"
    phase: Phase = Phase.LINTER
    severity: Severity = Severity.ERROR
    calls: int = 0
    found: list[Violation] = field(default_factory=list)

    def check(self, ctx: RuleContext) -> list[Violation]:
        self.calls += 1
        return list(self.found)


@dataclass
class Writer(Probe):
    """An autofixable rule whose fix reports writing ``src/b.py``."""

    fixes: int = 0

    def fix(self, ctx: RuleContext) -> list[str]:
        self.fixes += 1
        return ["src/b.py"]


def _ctx(*targets: str, **options: Any) -> RuleContext:
    return RuleContext(workspace_root=ROOT, changed_files=list(targets), **options)


def _snapshot() -> Snapshot:
    return Snapshot(ROOT, "staged", "0" * 40, "1" * 40, ("docs/a.md",), (), ())


# --- the declaration (AC-01, AC-02) ---------------------------------------------


class Declared(BaseRule):
    def __init__(self, inputs: Any) -> None:
        super().__init__(id="RULE-declared", name="declared", description="declared", inputs=inputs)

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []


def test_base_rule_keeps_a_valid_declaration() -> None:
    assert Declared(None).inputs is None
    assert Declared(("**/*.py", ".devkit/architecture.toml")).inputs == ("**/*.py", ".devkit/architecture.toml")


@pytest.mark.parametrize(
    "inputs",
    [(), ["**/*.py"], "**/*.py", ("",), ("/abs.py",), ("a\\b.py",), ("c:/a.py",), ("./a.py",), ("../a.py",), ("a**",)],
)
def test_base_rule_rejects_a_malformed_declaration(inputs: Any) -> None:
    with pytest.raises(RuleDefinitionError) as raised:
        Declared(inputs)
    assert raised.value.code == "RULES_DEFINITION_INVALID" and raised.value.rule_id == "RULE-declared"


@pytest.mark.parametrize("inputs", ["**/*.py", ["**/*.py"], ()])
def test_a_protocol_rule_with_malformed_inputs_fails_before_any_rule_runs(inputs: Any) -> None:
    bad, good = Probe("RULE-bad", inputs=inputs), Probe("RULE-good")
    result = evaluate_rules(_ctx("docs/a.md"), [good, bad])
    assert [(e.code, e.rule_id) for e in result.errors] == [("RULES_DEFINITION_INVALID", "RULE-bad")]
    assert result.errors[0].target_files == (__file__,)
    assert (good.calls, bad.calls) == (0, 0) and result.violations == [] and not result.ok


# --- the skip (AC-03, AC-04) --------------------------------------------------------


def test_a_declared_rule_no_target_matches_is_skipped() -> None:
    declared, undeclared = Probe("RULE-python", inputs=("**/*.py",)), Probe("RULE-any")
    result = evaluate_rules(_ctx("docs/a.md"), [declared, undeclared])
    assert (declared.calls, undeclared.calls) == (0, 1)
    assert result.skipped == ["RULE-python"] and result.ok


@pytest.mark.parametrize(
    ("targets", "options"),
    [
        (("src/a.py",), {}),  # a matching target
        (("docs/a.md", "src/a.py"), {"exclude": ("src/**",)}),  # matched before [rules] exclude removes it
        (("docs/a.md", ".devkit/config.toml"), {}),  # project policy can change any rule's findings
        (("docs/a.md", ".devkit/installation.json"), {}),  # installation receipt changes loaded rules
        ((), {}),  # the whole workspace
        (
            ("src/a.py",),
            {"snapshot": Snapshot(ROOT, "staged", "0" * 40, "1" * 40, ("src/a.py",), (), ())},
        ),  # snapshot matching changed
        (
            (),
            {"snapshot": Snapshot(ROOT, "staged", "0" * 40, "1" * 40, (), ("src/old.py",), ())},
        ),  # snapshot matching deleted
        (
            (".devkit/config.toml",),
            {"snapshot": Snapshot(ROOT, "staged", "0" * 40, "1" * 40, (".devkit/config.toml",), (), ())},
        ),  # snapshot config
        (
            (".devkit/installation.json",),
            {"snapshot": Snapshot(ROOT, "staged", "0" * 40, "1" * 40, (".devkit/installation.json",), (), ())},
        ),  # snapshot receipt
    ],
    ids=[
        "matching",
        "excluded-matching",
        "config",
        "receipt",
        "whole-workspace",
        "snapshot-matching",
        "snapshot-deleted",
        "snapshot-config",
        "snapshot-receipt",
    ],
)
def test_every_other_run_evaluates_the_declared_rule(targets: tuple[str, ...], options: dict[str, Any]) -> None:
    declared, undeclared = Probe("RULE-python", inputs=("**/*.py",)), Probe("RULE-any")
    result = evaluate_rules(_ctx(*targets, **options), [declared, undeclared])
    assert (declared.calls, undeclared.calls) == (1, 1)
    assert result.skipped == []


def test_a_snapshot_run_no_diff_path_matches_is_skipped() -> None:
    declared, undeclared = Probe("RULE-python", inputs=("**/*.py",)), Probe("RULE-any")
    snapshot = Snapshot(ROOT, "staged", "0" * 40, "1" * 40, ("docs/a.md",), (), ())
    result = evaluate_rules(_ctx("docs/a.md", snapshot=snapshot), [declared, undeclared])
    assert (declared.calls, undeclared.calls) == (0, 1)
    assert result.skipped == ["RULE-python"] and result.ok


def test_snapshot_deleted_paths_are_not_in_targets() -> None:
    snapshot = Snapshot(ROOT, "staged", "0" * 40, "1" * 40, (), ("src/old.py",), ())
    ctx = _ctx(snapshot=snapshot)
    assert ctx.targets == () and ctx.changed_files == []
    assert not ctx.is_file_targeted("src/old.py")


def test_a_root_level_file_matches_a_double_star_pattern() -> None:
    declared = Probe("RULE-manifest", inputs=("**/pyproject.toml",))
    assert evaluate_rules(_ctx("pyproject.toml"), [declared]).skipped == [] and declared.calls == 1


def test_inactive_rules_are_not_listed_as_skipped() -> None:
    hygiene = Probe("RULE-hygiene", inputs=("**/*.py",), phase=Phase.HYGIENE)
    assert evaluate_rules(_ctx("docs/a.md"), [hygiene]).skipped == []


# --- fix and recheck (AC-05) --------------------------------------------------------


def test_the_recheck_evaluates_a_skipped_rule_whose_input_a_fix_wrote() -> None:
    finding = Violation("RULE-python", "src/b.py", 1, "written")
    declared = Writer("RULE-python", inputs=("**/*.py",), found=[finding])
    writer = Writer("RULE-writer")
    result = evaluate_rules(_ctx("docs/a.md", fix=True), [declared, writer])
    assert (declared.calls, declared.fixes) == (1, 0)  # the declared rule ran only in the recheck, without fixing
    assert (writer.calls, writer.fixes) == (2, 1)
    assert [(v.rule_id, v.file, v.fixed) for v in result.violations] == [("RULE-python", "src/b.py", False)]
    assert result.skipped == []


def test_a_skipped_rule_is_not_fixed_and_stays_skipped_when_fixes_miss_its_inputs() -> None:
    declared = Writer("RULE-docs", inputs=("docs/**/*.txt",))
    writer = Writer("RULE-writer")
    result = evaluate_rules(_ctx("docs/a.md", fix=True), [declared, writer])
    assert (declared.calls, declared.fixes, writer.calls) == (0, 0, 2)
    assert result.skipped == ["RULE-docs"]


def test_a_failed_fix_rechecks_every_active_rule() -> None:
    @dataclass
    class Failing(Probe):
        def fix(self, ctx: RuleContext) -> list[str]:
            raise RuntimeError("partial write")

    declared, failing = Probe("RULE-python", inputs=("**/*.py",)), Failing("RULE-failing")
    result = evaluate_rules(_ctx("docs/a.md", fix=True), [declared, failing])
    assert declared.calls == 1 and failing.calls == 2
    assert result.skipped == [] and [e.code for e in result.errors] == ["RULES_EXECUTION_FAILED"]


def test_context_keeps_targets_before_exclusion() -> None:
    ctx = _ctx("docs/a.md", f"{ROOT}/src/a.py", exclude=("src/**",))
    assert ctx.targets == ("docs/a.md", "src/a.py") and ctx.changed_files == ["docs/a.md"]
    assert ctx.relative_path(ROOT / "src/b.py") == "src/b.py" and ctx.relative_path("/elsewhere/c.py") is None
