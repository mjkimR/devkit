---
id: FB-answer-envelope-has-no-decider
title: Answer envelopes cannot record who decided each answer
scope: repo
kind: friction
category: missing-capability
target: devkit workflow envelope answer
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-answer-envelope-has-no-decider] Answer envelopes cannot record who decided each answer

## 1. Friction / Question (friction, question)

- **Context**: A Planning worker recorded answers to four questions of one `worker` envelope. The Host's payload
  marked three answers as the user's decisions and one as the Host's own sequencing decision, and asked that each be
  recorded "with `--by user`" or "`--by host`".
- **Expectation**: The spec constitution says records name `user` or `policy`, and `devkit workflow answer` and
  `devkit spec proposal accept` take `--by`. An answer record would carry its decider the same way.
- **Actual**: `devkit workflow envelope answer` has no `--by` option, and an answer entry holds only `question`,
  `choice`, `decision` and `constraints`. Worker records §2 does not say how to attribute an answer. A Host decision
  and a user decision in one envelope differ only in prose.
- **Workaround (or Interpretation Chosen)**: One answer envelope whose summary says which questions the user and the
  Host decided, and decision sentences that start "The user decided" or "The Host decided".
- **Suggestion**: Either add an optional per-answer `by` field (`user`, `host`, `policy`) to the answer envelope
  and its command, or state in worker records §2 and the `planning-worker` payload that attribution goes into the
  decision sentence, so Host payloads stop asking for a flag that does not exist.

## Diagnostic Details

- **Reproduction**: `uv run devkit workflow envelope answer --help` lists no `--by`; compare
  `uv run devkit workflow answer --help`.
- **Expected / Actual**: Expected a decider field or a documented convention; actual neither.
- **Versions**: worktree base `51894649`.
- **Conditions**: SDD proposal Planning in `local-orchestrated` mode on a `plan-` worktree.
- **Workarounds Attempted**: Attribution in the summary and decision text of historical Git `b27116846db71a45feacbaa7e60b05ac4d2c4d5e:docs/proposals/PROP-rename-incubation-to-adaptive-dev/envelopes/answer-01.yaml`; accepted by
  the command.
- **Related Assets**: `CAP-DLV-workflow-envelopes`, `CAP-DLV-cli-and-output`,
  `packages/devkit/src/devkit_agt/features/workflow/cli/run.py`, the `spec` skill's `references/worker-records.md`.

## Evidence

```text
devkit workflow envelope answer options: --unit --anchor --stage --summary --assume --unverified --effort
  --answers-to --answers-file --settle --format (no --by)
devkit_agt/features/workflow/cli/run.py:76 @click.option("--by", ... "Who answered (person or host)") on workflow answer
answer entry fields: {question, choice, decision, constraints?}
```
