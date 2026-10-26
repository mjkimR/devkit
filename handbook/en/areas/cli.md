---
sources:
  ARCH-05-3-command-plugins: ec76f9e3d68a8d43196eb96180530ecaff83900a
  ARCH-08-1-agent-output: 30466db492161e034b6d5c1e076d0e9f5432f514
  CAP-ADV-agent-advisory-protocol: bc9cd491e33c6cd4db4cdf12f714062d8487d98b
  CAP-CLI-agent-cli-toolkit: aaddc88dd7e643c5dbbf7f7d61ddfcb68bc1809f
title: Agent-first CLI toolkit
---

# Agent-first CLI toolkit

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `ae01161143be`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Advisories](advisory.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The command-line tools in your repositories are increasingly run by AI agents on your behalf. `devkit-cli`
(`devkit_cli`) gives any click tool the same output contract `devkit` itself follows, and the opt-in `cli-tool`
bundle of `devkit-catalog` tells your agent how to structure such a tool and checks the structure with five rules.
The contract is the one of `ARCH-08-1-agent-output`; errors and warnings are advisories
([Advisories](advisory.md)). For the idea of agent-first output in context, see [Concepts](../concepts.md).

## The contract your tool gets

| Channel | Carries |
| --- | --- |
| stdout | The result: one-line `[KIND: ...]` sentinels, or exactly one JSON object under `--format json` |
| stderr | Advisory blocks, plus `[INFO]` log lines under `-v` |
| exit code | `0` success, `1` negative result (or a warning under `--strict`), `2` could not run |

No colour, tables, progress bars or prompts: nothing depends on a terminal. stdout and stderr are UTF-8 whatever
the locale, and a reader that closes stdout early ends the command with exit `2` and no noise.

## Wrap a click command

```python
import click
from devkit_cli import FORMAT_OPTION, Boundary, echo_json, echo_notices, is_json

boundary = Boundary("mytool")          # reads MYTOOL_QUIET, MYTOOL_VERBOSE, MYTOOL_STRICT

@click.command()
@FORMAT_OPTION
@boundary                              # below the click decorators; adds -q, -v and --strict
def scan(output_format: str) -> None:
    result, notices = run_scan()
    if is_json(output_format):
        echo_json({"result": result, "notices": [n.to_dict() for n in notices]})
    else:
        click.echo(f"[SCAN: files={result.count}]")
        echo_notices(notices)
```

The boundary does the rest:

- An `ERROR` advisory raised by the command is rendered once and sets the exit code; in JSON mode it becomes
  `{"error": {...}}` on stdout with nothing on stderr.
- Anything else that escapes (a bug, a `SystemExit`) becomes `UNEXPECTED_ERROR` with exit `2`, its traceback logged
  for `-v`.
- A flag wins over the environment; a variable counts as on only when it is exactly `1`; `-q` with `-v` is
  `ARGUMENT_INVALID`.
- Raise `devkit.advisory.ArgumentError` for a semantic argument check.

Other helpers: `exit_on_warnings` (exit `1` under `--strict` after a warning), `exit_on_problems` and
`report_exit_code` for commands that report collected problems, `LazyGroup` to import subcommand modules only when
they run, and `devkit_cli.testing.invoke` with `Outcome.json()` and `Outcome.codes()` for tests.

`devkit` itself is built this way: `devkit_dist.adapters.cli` binds `Boundary("devkit")` (`DEVKIT_QUIET`,
`DEVKIT_VERBOSE`, `DEVKIT_STRICT`), and the root group is a `LazyGroup` extended with `devkit.commands` plugins
(`ARCH-05-3-command-plugins`), which is how `devkit spec` and `devkit run` mount
([Harness](harness.md)).

## Keep a tool's structure healthy

Select the `cli-tool` bundle with `devkit add cli-tool`. Its default preset deploys the `cli-tool-structure`
instruction and five rules; the `guide` preset deploys the instruction only. The rules check:

| Rule | Keeps |
| --- | --- |
| `RULE-cli-tool-layout` | modules sit in a feature layout (`features/<feature>/cli`, `usecases`, `services`, `repositories`, `models`, ...), not a flat package |
| `RULE-cli-tool-layers` | only CLI modules import `click` or `devkit_cli`; feature layers import only their own rank or lower; the root `cli` stays lazy |
| `RULE-cli-tool-command-boundary` | every click command carries the boundary decorator |
| `RULE-cli-tool-library-output` | no `print`, and no `click.echo` or `sys.stdout.write` outside CLI modules |
| `RULE-cli-tool-heavy-imports` | CLI modules do not import heavy modules at import time |

Each rule takes `include` and `exclude` patterns and documents its other settings in its guide
(`devkit rules explain RULE-cli-tool-layers`). Tune them in `[rules]` like any rule
([Governance rules](governance.md)).

## Versioning

`devkit-cli` depends only on `click` and `devkit-advisory`, and importing it loads nothing else. Because other
repositories already consume it, it is a semver contract released in lockstep with `devkit-dist`, `devkit-agt` and
`devkit-advisory`: within `0.x`, removing or renaming a public name bumps the minor version.

## Sources

- [CAP-CLI-agent-cli-toolkit](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md):
  the boundary, helpers, test helper and the `cli-tool` rules.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-1-agent-output.md):
  the output contract the toolkit implements.
- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  the advisories it renders.
- [ARCH-05-3-command-plugins](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-05-3-command-plugins.md):
  how `devkit` mounts command plugins.
