---
sources:
  ARCH-08-1-agent-output: 30466db492161e034b6d5c1e076d0e9f5432f514
  CAP-ADV-agent-advisory-protocol: bc9cd491e33c6cd4db4cdf12f714062d8487d98b
title: Advisories
---

# Advisories

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
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
- [Agent-first CLI toolkit](cli.md)
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

Every error, warning and notice a `devkit` command reports is an advisory: a short block on stderr (or the same
envelope in JSON) that says what happened and, in its `[ACTION]` line, what the agent does next. The point is to
stop the two classic agent failures: retrying an identical command in a loop, and improvising a destructive
workaround such as inventing `--force` or editing a rule until it passes. The protocol is also available as the
`devkit.advisory` library for your own tools. For where advisories sit in devkit's overall output model, see
[Concepts](../concepts.md) and `ARCH-08-1-agent-output`.

## Read an advisory

```text
[ERROR]  (RULES_CONFIG_INVALID) config rules.phase_overrides.RULE-x: 'linter' is not 'hygiene'; set it to 'hygiene' or remove the entry to keep the rule's default phase
[ACTION] INPUT_ERROR — Do not retry with identical input. Retrying unchanged will
         fail identically. Correct the flag, argument, or input file before rerunning.
[TARGET] .devkit/config.toml
[FIX]    Correct the [rules] table in .devkit/config.toml
```

- The headline carries the level and a stable `UPPER_SNAKE` code. Branch on the code, never on the message.
- `[ACTION]` names the mode and its fixed directive.
- `[TARGET]` is what to open, `[FIX]` an exact command or edit, `[REPORT]` what to tell the user, `[DETAIL]`
  diagnostics. Empty lines are left out; a block never contains a blank line and never uses colour.

## Did the command fail?

The level answers that, independently of the mode:

| Level | Headline | Meaning | Exit code |
| --- | --- | --- | --- |
| `ERROR` | `[ERROR]` | The command did not do its job, or a check found a negative result | `1` or `2` |
| `WARNING` | `[WARN]` | It succeeded, but the user needs to learn or decide something | unchanged (`--strict` turns `0` into `1`) |
| `NOTICE` | `[NOTICE]` | It succeeded; something is worth knowing | unchanged |

Exit `1` means a negative result (violations, a refused commit), `2` means the command could not run. A refusal is
always an error, never a warning. Plain diagnostics are not advisories at all: they are `[INFO]` log lines you see
with `-v`. `-q` hides notices, never warnings or errors.

## What to do about it

For an error, the mode tells the agent its next step:

| Mode | Situation | What the agent does |
| --- | --- | --- |
| `INPUT_ERROR` | A flag, argument or input file is wrong | Correct the `[TARGET]` and rerun |
| `AUTO` | A safe deterministic fix exists | Run `[FIX]` once, retry once, stop either way |
| `BLOCKED` | A deliberate guardrail refused (a commit gate, a workflow rule) | Report and stop; changing the rule is the user's call |
| `INTERACTION` | A human decision or permission is needed | Ask the user; `[FIX]` is for after they agree |
| `MAINTENANCE` | A defect in the code or tool | Report and stop; repairing it is a separate task |
| `HALT` | Continuing could corrupt state | Report what was left half-done; do not retry or finish by hand |
| `DEFER` | Nothing is broken; try later | Report the cause and when to retry |

Warnings always carry `CONTINUE` and notices `NOTE`: the operation already succeeded, so the agent tells the user
and runs `[FIX]` only when asked. `AUTO` is the only mode that authorizes a retry.

As a person you rarely act on advisories yourself; you see them relayed by your agent. When the agent asks you
something, it is usually an `INTERACTION` error's `[REPORT]` question or a `CONTINUE` warning the user has to know
about.

## Machine channels

- `--format json` prints one object on stdout. A failure is `{"error": {...}}` with `code`, `level`, `message`,
  `exit_code` and an `advisory` object holding the mode, the action text and every non-empty field; warnings and
  notices of a successful result sit under `notices`. Nothing is printed on stderr, so an agent host that merges
  the channels never reads an advisory twice.
- MCP tools return the rendered block as the error text, or append warning and notice blocks after the result.
- HTTP services can use the same envelope in an RFC 7807 problem document.

No transport or consumer runs `[FIX]` on the agent's behalf.

## Write advisories in your own tool

Use `devkit.advisory` (the `devkit-advisory` package; a semver contract other repositories already depend on):

1. Pick the level first: failed or refused is `ERROR`, succeeded with something to learn is `WARNING`, succeeded
   with something worth knowing is `NOTICE`, and nothing to act on is a log line.
2. For an error, set the fields (`actor`, `retry`, `guardrail`, `input_error`) and check that the derived mode is
   the directive you want. The mode is never set directly. `AUTO` requires a `fix`.
3. Make `[TARGET]` a file, flag or `path:line:col`, `[FIX]` an exact runnable command without placeholders, and
   word everything deterministically: no "likely" or "might".
4. Return warnings and notices with the result instead of raising them, and report one advisory per condition.

The `advisory` bundle ships the `agent-advisory` and `agent-advisory-python` instructions, consumer-facing mirrors of
this contract, and `RULE-advisory-unique-code`, which refuses two unrelated Python classes declaring the same code.
To give a click tool this output contract for free, see [Agent-first CLI toolkit](cli.md).

## Sources

- [CAP-ADV-agent-advisory-protocol](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md):
  levels, block format, fields, mode derivation, the canonical action texts and the authoring checklist.
- [ARCH-08-1-agent-output](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/architecture/ARCH-08-1-agent-output.md):
  how advisories sit among a command's stdout, stderr and exit codes.
- [Advisory reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/advisory.md): the
  `devkit.advisory` Python API.
