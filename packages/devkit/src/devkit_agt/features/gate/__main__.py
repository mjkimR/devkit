"""``python -m devkit_agt.features.gate``: the gate CLI alone, which the hook wrappers exec.

Importing only the gate area (and what it depends on) keeps commits independent
of the other ``devkit`` command groups and keeps hook start-up short.
"""

from devkit_agt.features.gate.cli import cli

if __name__ == "__main__":
    cli(prog_name="devkit gate")
