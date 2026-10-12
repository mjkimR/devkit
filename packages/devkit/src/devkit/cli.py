"""The ``devkit`` command line: distribution commands at the top level, one group per engine.

``devkit sync``, ``add``, ``remove``, ``list``, ``status`` and the other
distribution commands sit at the top level, as does ``devkit run`` (compact
command output); ``devkit rules``, ``devkit workflow`` and ``devkit gate`` are
the rule engine, workflow engine and commit gate groups.
"""

from __future__ import annotations

import click

from devkit.compact.cli import run_cmd
from devkit.distribution.cli import register as register_distribution
from devkit.gate.cli import cli as gate_cli
from devkit.rules.cli import cli as rules_cli
from devkit.workflow.cli import cli as workflow_cli


@click.group(name="devkit")
@click.version_option(package_name="devkit")
def cli() -> None:
    """Devkit: agent asset distribution, repository rules, delivery workflows, commit gates and compact command output."""


register_distribution(cli)
cli.add_command(run_cmd, "run")
cli.add_command(rules_cli, "rules")
cli.add_command(workflow_cli, "workflow")
cli.add_command(gate_cli, "gate")
