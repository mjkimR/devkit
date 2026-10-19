---
id: FB-envelope-answer-help-item-keys
title: envelope answer help does not name the keys of an --answers-file item
scope: repo
kind: suggestion
category: missing-capability
target: devkit workflow envelope answer --answers-file
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-envelope-answer-help-item-keys] envelope answer help does not name the keys of an --answers-file item

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: a planning worker that records the caller's answers runs
  `devkit workflow envelope answer --answers-to worker-NN.yaml --answers-file -`, as its contract says. The option's
  help text reads "YAML list of rewritten answers" and the `planning-worker` contract names only the content ("one
  choice and one decision sentence per question plus any new constraint"). The item keys (`question`, `choice`,
  `decision`, `constraints`) appear in `CAP-DLV-workflow-envelopes` and in the source, and a bare skeleton lists
  them, but neither the help text nor the contract names them.
- **Proposed Procedure**: name the keys in the `--answers-file` help, for example "YAML list of
  {question, choice, decision, constraints?}", and do the same for `--questions-file`
  ({id, title, prompt, context, options}).
- **Expected Benefit**: an agent can write the list from `--help` alone, with no lookup in a document or the source.
- **Cost & Risk**: one help string per option; nothing else changes.
- **Attempted**: in this run the keys came from `ANSWER_KEYS` in the envelope model before writing the envelope.
  The envelope it wrote passed validation on the first try.

## Diagnostic Details

- **Reproduction**: `devkit workflow envelope answer --help`; read the `--answers-file` line.
- **Expected / Actual**: expected the item keys or a pointer to them; actual is only "YAML list of rewritten answers".
- **Versions**: devkit 0.1.1, plan branch head `1a99c89`.
- **Conditions**: local-orchestrated Planning worker run on Claude Code, recording the user's answers to a
  `worker-01.yaml`.
- **Workarounds Attempted**: read `packages/devkit/src/devkit/workflow/unit/envelope/model.py` (`ANSWER_KEYS`,
  `parse_answer`); this worked.
- **Related Assets**: `packages/devkit/src/devkit/workflow/cli/envelope.py` (option help),
  `packages/devkit-spec/src/devkit_spec/bundle/subagents/planning-worker.md` (step 3), `CAP-DLV-workflow-envelopes`.

## Evidence

```text
$ devkit workflow envelope answer --help
  --answers-to TEXT          The worker-NN.yaml whose questions it answers
  --answers-file TEXT        YAML list of rewritten answers (path, or - for stdin)

model.py: ANSWER_KEYS = ("question", "choice", "decision", "constraints")
```
