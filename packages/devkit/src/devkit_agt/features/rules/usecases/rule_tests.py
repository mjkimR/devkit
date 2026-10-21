"""Run the tests that live in each rule's folder (``devkit rules test``).

Every rule is one directory: a built-in rule is a package module of
``devkit_agt.features.rules.services.builtins``, a distributed or custom rule a plugin package. Its
tests sit beside the code in ``<rule folder>/tests/`` and are never imported
by devkit's loaders (``devkit_core.core.plugins``). ``rule_folder`` finds the folder
of a loaded rule: the directory of the module defining its class, or for a
plugin package the package's root in the tree that module came from (a
project override's copy when the class is defined there, else the managed
copy or the ``--rules-dir`` package).

``run_rule_tests`` runs ``python -m pytest <tests> --import-mode=importlib
-p no:cacheprovider`` once per tests directory, in a subprocess of the
interpreter running devkit, from the workspace root, with
``PYTHONDONTWRITEBYTECODE=1``: neither a bytecode cache nor a pytest cache is
written next to the tests, so a run leaves nothing in ``.devkit/managed/``.
The run goes through ``devkit_agt.features.compact.run_command`` (full output in a log
file, bounded view in the result); compact is imported only when tests run,
so importing ``devkit_agt.features.rules`` stays free of it.
"""

from __future__ import annotations

import importlib.util
import inspect
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from devkit.advisory import AdvisoryError
from devkit_core.core.plugins import TESTS_DIRECTORY

from devkit_agt.features.rules.models.contracts import Rule
from devkit_agt.features.rules.models.errors import RulesTestUnavailableError
from devkit_agt.features.rules.services.builtins.base import managed_counterpart
from devkit_agt.features.rules.services.registry import PLUGIN_NAMESPACE

if TYPE_CHECKING:
    from devkit_agt.features.compact import CommandRun

PYTEST_OPTIONS = ("--import-mode=importlib", "-p", "no:cacheprovider")
NO_TESTS_COLLECTED = 5  # pytest's exit code when it collected no test


class RuleTestResult(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    NO_TESTS = "no-tests"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class RuleTestRun:
    """The outcome of one rule's tests.

    ``tests`` is the rule's tests directory (it may not exist; ``None`` when the
    rule class has no source file). ``run`` is the pytest run, ``None`` when
    there was no tests directory to run. Rules defined in one package share
    one run.
    """

    rule_id: str
    tests: Path | None
    result: RuleTestResult
    run: CommandRun | None = None

    @property
    def exit_code(self) -> int | None:
        return self.run.exit_code if self.run is not None else None

    @property
    def failed(self) -> bool:
        return self.result is RuleTestResult.FAILED


class RuleTestsInterrupted(SystemExit):
    """A run was interrupted (Ctrl-C, ``SIGTERM``, ``SIGHUP``): ``results`` holds the rules run so far, the last
    one ``interrupted``. Left uncaught it exits ``128 + N``, as the signal would have."""

    def __init__(self, results: list[RuleTestRun], code: int) -> None:
        super().__init__(code)
        self.results = results


def rule_folder(rule: Rule) -> Path | None:
    """The directory a rule lives in, or ``None`` when its class has no source file.

    For a built-in (or any importable) rule, the directory of the module that
    defines the class. For a rule loaded from a plugin package, the package
    root in the tree of that module: ``sub/rule.py`` of a package is two
    levels below it.
    """
    cls = type(rule)
    try:
        file = Path(inspect.getfile(cls)).resolve()
    except (TypeError, OSError):
        return None
    top, _, dotted = cls.__module__.partition(".")
    folder = file.parent
    if not top.startswith(f"{PLUGIN_NAMESPACE}_") or not dotted:
        return folder
    depth = len(dotted.split(".")) - (0 if file.name == "__init__.py" else 1)
    for _ in range(depth):
        folder = folder.parent
    return folder


def tests_directory(rule: Rule) -> Path | None:
    """``<rule folder>/tests``, whether or not it exists; ``None`` when the rule has no folder.

    For a rule whose module a project override replaced, an override without ``tests/`` uses the managed copy's;
    their ``load_rule`` applies the override (``devkit_agt.features.rules.services.testing``), so they test the overridden modules.
    """
    folder = rule_folder(rule)
    if folder is None:
        return None
    tests = folder / TESTS_DIRECTORY
    managed = managed_counterpart(folder)
    if not tests.is_dir() and managed is not None and (managed / TESTS_DIRECTORY).is_dir():
        return managed / TESTS_DIRECTORY
    return tests


def pytest_available() -> bool:
    """Whether the interpreter running devkit can import pytest."""
    return importlib.util.find_spec("pytest") is not None


def run_rule_tests(root: Path, rules: Sequence[Rule], pytest_args: Sequence[str] = ()) -> list[RuleTestRun]:
    """Run each rule's tests, in the given order, and return one ``RuleTestRun`` per rule.

    ``root`` is the workspace root pytest runs from. Each run is isolated from the
    project: no configuration file is read (``-c os.devnull``) and the rule folder
    is the root and the conftest boundary, so the project's ``addopts``,
    ``filterwarnings`` and ``conftest.py`` files never apply; a rule's tests depend
    on its folder alone. ``pytest_args`` are appended to every run.
    A rule without a tests directory, or whose tests collect nothing (pytest
    exit code 5), is ``no-tests``; any other nonzero exit code is ``failed``.
    Raises ``RulesTestUnavailableError`` (``RULES_TEST_UNAVAILABLE``) when
    pytest is not importable, the compact errors when a run cannot start or
    log, and ``RuleTestsInterrupted`` with the results so far when a run is
    interrupted.
    """
    if not pytest_available():
        raise RulesTestUnavailableError(
            f"pytest is not importable by {sys.executable}, which runs devkit; rule tests need it",
            target_files=["pyproject.toml"],
        )
    from devkit_agt.features.compact import CommandInterrupted, run_command

    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    runs: dict[Path, CommandRun] = {}
    results: list[RuleTestRun] = []
    for rule in rules:
        tests = tests_directory(rule)
        if tests is None or not tests.is_dir():
            results.append(RuleTestRun(rule.id, tests, RuleTestResult.NO_TESTS))
            continue
        if tests not in runs:
            folder = str(tests.parent)
            isolation = ("-c", os.devnull, "--rootdir", folder, "--confcutdir", folder)
            argv = [sys.executable, "-m", "pytest", str(tests), *PYTEST_OPTIONS, *isolation, *pytest_args]
            try:
                runs[tests] = run_command(argv, cwd=root, env=env, slow_after=0)
            except CommandInterrupted as stopped:
                results.append(RuleTestRun(rule.id, tests, RuleTestResult.INTERRUPTED, stopped.run))
                raise RuleTestsInterrupted(results, stopped.code if isinstance(stopped.code, int) else 130) from stopped
        run = runs[tests]
        if run.exit_code == 0:
            result = RuleTestResult.PASSED
        elif run.exit_code == NO_TESTS_COLLECTED:
            result = RuleTestResult.NO_TESTS
        else:
            result = RuleTestResult.FAILED
        results.append(RuleTestRun(rule.id, tests, result, run))
    return results


def run_notices(results: Sequence[RuleTestRun]) -> list[AdvisoryError]:
    """The advisories of the pytest runs (compact's), once per run shared by several rules."""
    seen: set[int] = set()
    notices: list[AdvisoryError] = []
    for item in results:
        if item.run is not None and id(item.run) not in seen:
            seen.add(id(item.run))
            notices.extend(item.run.notices)
    return notices


def summary(results: Sequence[RuleTestRun]) -> dict[str, Any]:
    """Counts per result: ``rules``, ``passed``, ``failed``, ``no_tests``, ``interrupted``."""
    return {
        "rules": len(results),
        "passed": sum(r.result is RuleTestResult.PASSED for r in results),
        "failed": sum(r.result is RuleTestResult.FAILED for r in results),
        "no_tests": sum(r.result is RuleTestResult.NO_TESTS for r in results),
        "interrupted": sum(r.result is RuleTestResult.INTERRUPTED for r in results),
    }
