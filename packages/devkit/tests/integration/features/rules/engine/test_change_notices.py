from __future__ import annotations

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_agt.features.rules import Phase, Severity, git_snapshot, run_project_rules
from devkit_agt.features.rules.cli.commands import cli
from devkit_agt.features.rules.models.errors import TargetError
from devkit_agt.features.rules.repositories.read_sessions import MAX_AGE, MAX_FINGERPRINTS, suppress
from devkit_agt.features.rules.usecases.context import ReadRuleContextUseCase

NOTICE = """import ast
from devkit_agt.features.rules import RuleContext, Violation, Severity
from devkit_agt.features.rules.services.builtins import BaseRule
class Consider(BaseRule):
    def __init__(self):
        super().__init__('RULE-consider', 'consider', 'fixture', severity=Severity.NOTICE, change_scope=True, inputs=('**/*.py',))
    def check(self, ctx):
        found = []
        for path, change in ctx.changes.items():
            if not change.available or not path.endswith('.py'):
                continue
            # Prefer after-side live constructs; deleted constructs use before evidence.
            sides = [('after', change.after)] if change.after else [('before', change.before)]
            for side, text in sides:
                for node in ast.walk(ast.parse(text)):
                    if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                        span = change.span(side, node.lineno, node.end_lineno + 1)
                        if change.affects(span):
                            found.append(Violation(self.id, path, node.lineno, 'Consider whether this fallback hides failure', change_span=span))
        return found
"""
BEFORE = (
    "def f():\n    try:\n        work()\n    except ValueError:\n        fallback()\n\ndef untouched():\n    return 1\n"
)
AFTER = BEFORE.replace("ValueError", "Exception")


def git(root: Path, *args: str, index: Path | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    return subprocess.run(
        ["git", "-C", str(root), *args], env=env, capture_output=True, text=True, check=True
    ).stdout.strip()


def workspace(tmp_path: Path) -> Path:
    root = tmp_path.resolve()
    git(root, "init", "-q")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Fixture")
    (root / "rules/notice").mkdir(parents=True)
    (root / "rules/notice/__init__.py").write_text(NOTICE)
    (root / "a.py").write_text(BEFORE)
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "baseline")
    return root


def notices(root: Path, **kwargs):
    return run_project_rules(root, rules_dir=root / "rules", **kwargs)


def test_relevant_unrelated_deleted_and_hygiene(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    (root / "a.py").write_text(AFTER)
    run = notices(root, targets=["a.py"])
    assert run.ok and len(run.result.violations) == 1 and run.result.violations[0].severity is Severity.NOTICE
    git(root, "add", "a.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "broad")
    (root / "a.py").write_text(AFTER.replace("return 1", "return 2"))
    assert notices(root).result.violations == []
    assert notices(root, phase=Phase.HYGIENE).result.violations == []
    (root / "a.py").unlink()
    run = notices(root)
    assert run.ok and run.result.violations[0].file == "a.py"
    assert run.result.violations[0].change_span is not None
    assert run.result.violations[0].change_span.side == "before"


def test_staged_ci_and_alternate_index_use_exact_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = workspace(tmp_path)
    base = git(root, "rev-parse", "HEAD")
    (root / "a.py").write_text(AFTER)
    git(root, "add", "a.py")
    snap = git_snapshot(root, staged=True)
    (root / "a.py").write_text(BEFORE)
    (root / "rules/notice/__init__.py").write_text("raise RuntimeError('unstaged must not execute')")
    run = notices(root, snapshot=snap)
    assert run.ok and len(run.result.violations) == 1
    alternate = root / "alternate-index"
    git(root, "read-tree", "HEAD", index=alternate)
    monkeypatch.setenv("GIT_INDEX_FILE", str(alternate))
    clean = git_snapshot(root, staged=True)
    assert notices(root, snapshot=clean).result.violations == []
    monkeypatch.delenv("GIT_INDEX_FILE")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "broad")
    ci = git_snapshot(root, staged=False, base=base)
    assert len(notices(root, snapshot=ci).result.violations) == 1


def test_read_context_always_returns_hunks_and_token_suppresses_messages(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    (root / "a.py").write_text(AFTER)
    usecase = ReadRuleContextUseCase()
    first = usecase.execute(root, "a.py", rules_dir=root / "rules", session="opaque-private-token")
    second = usecase.execute(root, "a.py", rules_dir=root / "rules", session="opaque-private-token")
    assert len(first.findings) == 1 and len(second.findings) == 0 and second.suppressed == 1
    assert first.hunks == second.hunks and first.hunks
    # An unrelated edit changes the file identity, not the relevant reminder fingerprint.
    (root / "a.py").write_text(AFTER.replace("return 1", "return 2"))
    assert usecase.execute(root, "a.py", rules_dir=root / "rules", session="opaque-private-token").suppressed == 1
    (root / "a.py").write_text(AFTER.replace("fallback()", "other()"))
    assert len(usecase.execute(root, "a.py", rules_dir=root / "rules", session="opaque-private-token").findings) == 1
    assert len(usecase.execute(root, "a.py", rules_dir=root / "rules").findings) == 1
    memo = next((root / ".devkit/transient/rules/read-notices").glob("*.json"))
    content = memo.read_text()
    assert "opaque-private-token" not in content and "fallback" not in content
    (root / "a.py").write_text(BEFORE)
    unchanged = usecase.execute(root, "a.py", rules_dir=root / "rules")
    assert unchanged.change["status"] == "unchanged" and not unchanged.hunks and not unchanged.findings


def test_read_context_deleted_unavailable_no_rules_and_invalid(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    (root / "a.py").unlink()
    result = ReadRuleContextUseCase().execute(root, "a.py")
    assert result.change["status"] == "deleted" and result.hunks and not result.findings
    (root / "binary.dat").write_bytes(b"\0")
    binary = ReadRuleContextUseCase().execute(root, "binary.dat")
    assert binary.change["status"] == "unavailable" and binary.notices[0].code == "RULE_CHANGE_EVIDENCE_UNAVAILABLE"
    with pytest.raises(TargetError):
        ReadRuleContextUseCase().execute(root, "does-not-exist.py")
    with pytest.raises(TargetError):
        ReadRuleContextUseCase().execute(root, "../outside.py")


def test_cli_notice_strict_and_legacy_warning_info_results(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    (root / "a.py").write_text(AFTER)
    runner = CliRunner()
    args = ["check", "-w", str(root), "--rules-dir", str(root / "rules"), "--strict", "a.py"]
    text = runner.invoke(cli, args)
    assert text.exit_code == 0, text.output
    assert "severity=notice" in text.stdout and "status=consider" in text.stdout and "notices=1" in text.stdout
    data = runner.invoke(cli, [*args[:-1], "--format", "json", "a.py"])
    assert data.exit_code == 0 and not data.stderr
    assert json.loads(data.stdout)["summary"]["notices"] == 1
    read = runner.invoke(cli, ["context", "-w", str(root), "a.py", "--format", "json"])
    assert read.exit_code == 0 and json.loads(read.stdout)["hunks"]
    for severity in ("warning", "info"):
        (root / ".devkit").mkdir(exist_ok=True)
        (root / ".devkit/config.toml").write_text(f'[rules.severity_overrides]\nRULE-consider = "{severity}"\n')
        legacy = runner.invoke(cli, args)
        assert legacy.exit_code == 0 and f"severity={severity}" in legacy.stdout


def test_session_expiry_corruption_cap_and_lock_failure(tmp_path: Path) -> None:
    fingerprint = "a" * 64
    assert suppress(tmp_path, "token", [fingerprint], now=0) == (set(), None)
    assert suppress(tmp_path, "token", [fingerprint], now=1) == ({fingerprint}, None)
    expired = suppress(tmp_path, "token", [fingerprint], now=MAX_AGE)[1]
    assert expired is not None and expired.code == "RULE_READ_SESSION_EXPIRED"
    path = next((tmp_path / ".devkit/transient/rules/read-notices").glob("*.json"))
    path.write_text("broken")
    duplicate, advisory = suppress(tmp_path, "token", [fingerprint], now=1)
    assert not duplicate and advisory is not None and advisory.code == "RULE_READ_SESSION_UNAVAILABLE"
    cap = [f"{i:064x}" for i in range(MAX_FINGERPRINTS + 1)]
    capped = suppress(tmp_path, "cap", cap)[1]
    assert capped is not None and capped.code == "RULE_READ_SESSION_EXPIRED"
    from devkit_core.core import file_lock

    with file_lock(tmp_path / ".devkit/transient/lock"):
        locked = suppress(tmp_path, "locked", [fingerprint])[1]
        assert locked is not None and locked.code == "RULE_READ_SESSION_UNAVAILABLE"


def test_session_concurrency_does_not_duplicate_successful_delivery(tmp_path: Path) -> None:
    # Unavailable lock updates are deliberately unsuppressed; two successful writes never both claim first delivery.
    def call(_):
        return suppress(tmp_path, "same", ["b" * 64])

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(call, range(2)))
    successful = [duplicate for duplicate, notice in results if notice is None]
    assert sum(not duplicate for duplicate in successful) == 1


@pytest.mark.parametrize("initial,final,expected", [(BEFORE, AFTER, 1), (AFTER, BEFORE, 0)])
def test_autofix_refreshes_after_evidence_against_original_base(
    tmp_path: Path, initial: str, final: str, expected: int
) -> None:
    root = workspace(tmp_path)
    # Baseline has the opposite handler, so the fix must introduce/remove an actual change.
    baseline = BEFORE if final == AFTER else AFTER
    (root / "a.py").write_text(baseline)
    git(root, "add", "a.py")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-qm", "handler baseline")
    (root / "a.py").write_text(initial)
    fixer = root / "rules/fixer"
    fixer.mkdir()
    fixer.joinpath("__init__.py").write_text(
        "from devkit_agt.features.rules.services.builtins import BaseRule\n"
        "class Repair(BaseRule):\n"
        "    def __init__(self): super().__init__('RULE-repair', 'repair', 'fixture')\n"
        "    def check(self, ctx): return []\n"
        f"    def fix(self, ctx):\n        ctx.cache.write_text('a.py', {final!r})\n        return ['a.py']\n"
    )
    run = notices(root, targets=["a.py"], fix=True)
    assert run.ok, [str(e) for e in run.errors]
    assert len([v for v in run.result.violations if v.severity is Severity.NOTICE]) == expected
    assert run.context is not None and run.context.before_text("a.py") == baseline


def test_failed_fixer_unknown_writes_recaptures_all_evidence(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    fixer = root / "rules/fixer"
    fixer.mkdir()
    fixer.joinpath("__init__.py").write_text(
        "from devkit_agt.features.rules.services.builtins import BaseRule\n"
        "class Repair(BaseRule):\n"
        "    def __init__(self): super().__init__('RULE-repair', 'repair', 'fixture')\n"
        "    def check(self, ctx): return []\n"
        f"    def fix(self, ctx):\n        ctx.cache.write_text('a.py', {AFTER!r})\n        raise RuntimeError('partial')\n"
    )
    run = notices(root, fix=True)
    assert [e.code for e in run.errors] == ["RULES_EXECUTION_FAILED"]
    assert len([v for v in run.result.violations if v.severity is Severity.NOTICE]) == 1


def test_unavailable_working_evidence_does_not_fail_independent_rules(tmp_path: Path) -> None:
    (tmp_path / "rules/notice").mkdir(parents=True)
    (tmp_path / "rules/notice/__init__.py").write_text(NOTICE)
    (tmp_path / "a.py").write_text(AFTER)
    (tmp_path / "a.md").write_text("[broken](missing.md)")
    run = notices(tmp_path)
    assert not run.errors and any(v.rule_id == "RULE-markdown-link" for v in run.result.violations)
    assert [n.code for n in run.notices] == ["RULE_CHANGE_EVIDENCE_UNAVAILABLE"]


def test_unborn_staged_rename_mode_and_exclusion(tmp_path: Path) -> None:
    root = tmp_path.resolve()
    git(root, "init", "-q")
    (root / "rules/notice").mkdir(parents=True)
    (root / "rules/notice/__init__.py").write_text(NOTICE)
    (root / "a.py").write_text(AFTER)
    git(root, "add", ".")
    initial = git_snapshot(root, staged=True)
    assert len(notices(root, snapshot=initial).result.violations) == 1
    git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-qm",
        "initial",
    )
    (root / "a.py").rename(root / "b.py")
    git(root, "add", ".")
    moved = notices(root, snapshot=git_snapshot(root, staged=True))
    assert {v.file for v in moved.result.violations} == {"a.py", "b.py"}
    git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-qm",
        "rename",
    )
    (root / "b.py").chmod(0o755)
    mode = notices(root, snapshot=git_snapshot(root, staged=True))
    assert mode.result.violations == []
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text('[rules]\nexclude = ["b.py"]\n')
    (root / "b.py").write_text(AFTER.replace("fallback()", "other()"))
    assert notices(root).result.violations == []


def test_gate_and_workflow_lint_clean_keep_considerations_nonblocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import devkit_agt.features.rules as rules_api
    from devkit.advisory import Level
    from devkit_agt.features.gate.usecases.gates.rules import RulesCheckGate
    from devkit_agt.features.workflow.usecases.lint import lint_with_rules
    from testsupport.gate import gate_ctx

    root = workspace(tmp_path)
    (root / "a.py").write_text(AFTER)
    git(root, "add", "a.py")
    original = rules_api.run_project_rules
    monkeypatch.setattr(
        rules_api, "run_project_rules", lambda root, **kw: original(root, rules_dir=root / "rules", **kw)
    )
    gate = RulesCheckGate().run(gate_ctx(root))
    assert [(n.code, n.level) for n in gate.notices] == [("GATE_RULES_NOTICES", Level.NOTICE)]
    assert lint_with_rules(root, ["a.py"]) == []


@pytest.mark.parametrize("fails", [False, True])
def test_autofix_refresh_admits_output_outside_original_targets(tmp_path: Path, fails: bool) -> None:
    root = workspace(tmp_path)
    (root / "focus.txt").write_text("target")
    (root / "b.py").write_text(BEFORE)
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "other input baseline")
    fixer = root / "rules/fixer"
    fixer.mkdir()
    ending = "raise RuntimeError('partial')" if fails else "return ['b.py']"
    fixer.joinpath("__init__.py").write_text(
        "from devkit_agt.features.rules.services.builtins import BaseRule\n"
        "class Repair(BaseRule):\n"
        "    def __init__(self): super().__init__('RULE-repair', 'repair', 'fixture')\n"
        "    def check(self, ctx): return []\n"
        f"    def fix(self, ctx):\n        ctx.cache.write_text('b.py', {AFTER!r})\n        {ending}\n"
    )
    run = notices(root, targets=["focus.txt"], fix=True)
    assert bool(run.errors) is fails
    considerations = [v for v in run.result.violations if v.severity is Severity.NOTICE]
    assert [v.file for v in considerations] == ["b.py"]
    assert run.context is not None and run.context.before_text("b.py") == BEFORE


def test_nested_workspace_untargeted_capture_uses_workspace_paths(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    inner = root / "inner"
    (inner / "rules/notice").mkdir(parents=True)
    (inner / "rules/notice/__init__.py").write_text(NOTICE)
    (inner / "a.py").write_text(BEFORE)
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "nested baseline")
    (inner / "a.py").write_text(AFTER)
    (root / "outside.py").write_text(AFTER)
    run = notices(inner)
    assert run.ok and [(v.file, v.line) for v in run.result.violations] == [("a.py", 4)]
    assert run.context is not None and set(run.context.changes) == {"a.py"}
    assert run.context.before_text("a.py") == BEFORE


@pytest.mark.parametrize(
    "kind",
    [
        "file",
        "dot_file",
        "parent_file",
        "abs_file",
        "abs_parent_file",
        "dir",
        "dot_dir",
        "abs_dir",
        "parent_root",
        "dot_root",
        "abs_root",
        "abs_parent_root",
        "alias_file",
        "alias_root",
    ],
)
def test_original_target_equivalent_spellings(tmp_path: Path, kind: str) -> None:
    root = workspace(tmp_path)
    (root / "sub").mkdir()
    (root / "sub/b.py").write_text(BEFORE)
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "directory baseline")
    (root / "a.py").write_text(AFTER)
    (root / "sub/b.py").write_text(AFTER)
    alias = tmp_path.parent / (tmp_path.name + "-alias")
    alias.symlink_to(root, target_is_directory=True)
    choices = {
        "file": ("a.py", ["a.py"]),
        "dot_file": ("./a.py", ["a.py"]),
        "parent_file": ("sub/../a.py", ["a.py"]),
        "abs_file": (str(root / "a.py"), ["a.py"]),
        "abs_parent_file": (str(root / "sub/../a.py"), ["a.py"]),
        "dir": ("sub", ["sub/b.py"]),
        "dot_dir": ("./sub", ["sub/b.py"]),
        "abs_dir": (str(root / "sub"), ["sub/b.py"]),
        "parent_root": ("sub/..", ["a.py", "sub/b.py"]),
        "dot_root": (".", ["a.py", "sub/b.py"]),
        "abs_root": (str(root), ["a.py", "sub/b.py"]),
        "abs_parent_root": (str(root / "sub/.."), ["a.py", "sub/b.py"]),
        "alias_file": (str(alias / "a.py"), ["a.py"]),
        "alias_root": (str(alias), ["a.py", "sub/b.py"]),
    }
    target, expected = choices[kind]
    run = notices(root, targets=[target])
    assert run.ok and sorted(v.file for v in run.result.violations) == expected
    if kind in ("file", "dot_file", "parent_file", "abs_file", "abs_parent_file", "alias_file"):
        read = ReadRuleContextUseCase().execute(root, target, rules_dir=root / "rules")
        assert read.file == "a.py" and len(read.findings) == 1


@pytest.mark.parametrize("kind", ["case", "unicode"])
def test_original_target_actual_filesystem_spelling_keeps_before_identity(tmp_path: Path, kind: str) -> None:
    import unicodedata

    root = workspace(tmp_path)
    original = "Capital.py" if kind == "case" else "café.py"
    target = "capital.py" if kind == "case" else unicodedata.normalize("NFD", original)
    (root / original).write_text(BEFORE)
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "name baseline")
    if not (root / target).is_file():
        pytest.skip("filesystem keeps alternate spellings distinct")
    (root / original).write_text(AFTER)
    run = notices(root, targets=[target])
    assert run.ok and len(run.result.violations) == 1
    finding = run.result.violations[0]
    assert run.context is not None and run.context.before_text(finding.file) == BEFORE
    read = ReadRuleContextUseCase().execute(root, target, rules_dir=root / "rules")
    assert len(read.findings) == 1 and read.change["before_id"] == run.context.changes[finding.file].before_id


def test_directory_with_only_deletions_still_checks_change_rules(tmp_path: Path) -> None:
    root = workspace(tmp_path)
    (root / "sub").mkdir()
    (root / "sub/only.py").write_text(AFTER)
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "deletion baseline")
    (root / "sub/only.py").unlink()
    normal = root / "rules/ordinary"
    normal.mkdir()
    normal.joinpath("__init__.py").write_text(
        "from devkit_agt.features.rules.services.builtins import BaseRule\n"
        "class Ordinary(BaseRule):\n"
        "    def __init__(self): super().__init__('RULE-ordinary', 'ordinary', 'fixture')\n"
        "    def check(self, ctx): raise AssertionError('empty present targets must not run ordinary rules')\n"
    )
    run = notices(root, targets=["sub/../sub"])
    assert run.ok and [v.file for v in run.result.violations] == ["sub/only.py"]
    (root / "empty").mkdir()
    no_change = notices(root, targets=["empty"])
    assert no_change.ok and no_change.result.violations == []
    assert "RULE-consider" in no_change.skipped
    ordinary_only = run_project_rules(root, targets=["empty"])
    assert ordinary_only.ok and ordinary_only.context is None and ordinary_only.result.violations == []
