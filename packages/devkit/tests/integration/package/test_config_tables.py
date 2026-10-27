"""The templates devkit-agt registers for its reserved tables (``devkit.config_tables``), rendered by devkit-dist.

With devkit-agt installed, ``devkit config template`` writes exactly what it wrote when these templates were
hard-coded in distribution: the tables, their text and their place (before the ``[tool.<name>]`` tables).
"""

from __future__ import annotations

import tomllib
from importlib.metadata import entry_points
from pathlib import Path

from devkit_agt.features.workflow.repositories.project.config import WorkflowConfig, parse_workflow_config
from devkit_agt.features.worktree.models.config import WorktreeConfig
from devkit_agt.features.worktree.repositories.config import read_worktree_config
from devkit_dist.features.distribution.services.installation.config import (
    RESERVED_TABLES,
    preview_config_template,
    refresh_config_template,
)
from devkit_dist.features.distribution.services.installation.config_template import RESERVED_GROUP
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH
from devkit_dist.features.project.services.config_template import uncomment

# The harness part of a fresh template before the split, byte for byte.
HARNESS_TABLES = (
    "## Workflow approval gates: ask waits for approval, auto satisfies the gate, off skips its stage. Names come from\n"
    "## workflow definitions; the gate below is an example, and a methodology package may fix some gates to a person (see\n"
    "## its policy command). Unset gates use ask.\n"
    "# [workflow.approvals]\n"
    '#   integration = "ask"  # "ask" | "auto" | "off"; approve integrating the change into the base\n'
    "\n"
    "## Workflow stages: policies apply by stage id across workflows. The id below is an example; unset stages use on. Stage\n"
    "## off takes precedence over approval policy.\n"
    "# [workflow.stages]\n"
    '#   collect-feedback = "on"  # "on" | "off"; set off to skip feedback collection\n'
    "\n"
    "## Git worktree behavior: integration policy, branch cleanup, setup for new worktrees and stale branches.\n"
    "# [worktree]\n"
    '#   pull_request = "auto"  # "auto" | "required"; auto: a pull request or worktree finish --merge, as the task'
    " needs; required refuses --merge\n"
    "#   delete_branch = true  # boolean; worktree finish deletes the merged branch with git branch -d\n"
    '#   merge = "no-ff"  # "no-ff" | "ff-only"; no-ff: a merge commit per task; ff-only: fast-forward only, wins in'
    " either policy\n"
    '#   setup = "uv sync"  # example; string; shell command run in a newly created worktree; unset: no setup command\n'
    '#   stale_after = "14d"  # "<N>d" | "<N>w"; idle plan-*/dev-* branches are reported by devkit worktree status --stale and'
    " hygiene runs\n"
)


def _agt_entries() -> dict[str, str]:
    return {
        entry.name: entry.value
        for entry in entry_points(group=RESERVED_GROUP)
        if entry.dist is not None and entry.dist.name == "devkit-agt"
    }


def test_devkit_agt_registers_the_gates_workflow_and_worktree_templates() -> None:
    assert _agt_entries() == {
        "gates": "devkit_agt.features.gate.usecases.hooks.local_config:config_tables",
        "workflow": "devkit_agt.features.workflow.repositories.project.config:config_tables",
        "worktree": "devkit_agt.features.worktree.repositories.config:config_tables",
    }
    assert set(_agt_entries()) <= set(RESERVED_TABLES)


def test_the_template_text_and_place_are_unchanged(tmp_path: Path) -> None:
    text = preview_config_template(tmp_path).text or ""
    start = text.index("## Workflow approval gates")
    assert text[start : start + len(HARNESS_TABLES)] == HARNESS_TABLES
    assert text.index('# override_drift = "warn"') < start
    assert text.index("# [gates.settings.verify-commands]") < start  # the gate engine's tables precede workflow
    tool = text.find("## [tool.")
    assert tool == -1 or tool == start + len(HARNESS_TABLES) + 1  # one blank line, then the tool tables


def test_the_tables_read_back_with_the_engines_default_policies(tmp_path: Path) -> None:
    refresh_config_template(tmp_path)
    text = (tmp_path / CONFIG_PATH).read_text()
    assert parse_workflow_config(tomllib.loads(text)) == WorkflowConfig()
    assert read_worktree_config(tmp_path) == WorktreeConfig()
    expanded = uncomment(text)
    workflow = parse_workflow_config(tomllib.loads(expanded))
    for gate in ("integration", "custom-gate"):
        assert workflow.policy(gate) == WorkflowConfig().policy(gate)
    assert workflow.stage_policy("collect-feedback") == WorkflowConfig().stage_policy("collect-feedback")
    (tmp_path / CONFIG_PATH).write_text(expanded)
    assert read_worktree_config(tmp_path) == WorktreeConfig(setup="uv sync")
