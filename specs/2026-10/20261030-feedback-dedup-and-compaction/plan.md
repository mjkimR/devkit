---
id: PLAN-feedback-dedup-and-compaction
spec: SPEC-feedback-dedup-and-compaction
---

# Technical Plan: `SPEC-feedback-dedup-and-compaction` Feedback lookup before recording and compaction of closed feedback

## 1. Constitution & Invariant Review

None. The change implements `ADR-recording-looks-up-existing-feedback-of-every-status-first` and
`ADR-closed-feedback-compacts-into-per-area-records-with-aliases`, both accepted and refining `ADR-feedback-lifecycle`
without changing a status or its meaning. The compaction playbook follows the shape of `adr-compaction`
(`ADR-adr-compaction`, `ADR-immutable-decisions-editable-records`). No architecture `MUST` changes: no package,
command, document kind or model changes. Bundle assets stay self-contained (`agent-asset-writing`): they cite no
authoring-repository document ID.

## 2. Architecture Overview & Impact

Guidance-only change in the `spec` bundle of `devkit-spec`, plus its Living Spec reflection and tests.

| Component | Change |
| --- | --- |
| `skills/spec-feedback/SKILL.md` | New recording step 2 "Look up" before writing: the search command, the sameness judgment, the compact record entry rule and the per-status action table. Later steps renumber. |
| `skills/spec-feedback/references/sweep.md` | Procedure step 2 runs the lookup of the recording procedure per candidate with `--all-namespaces`; the equal-`target` deduplication against the open list is removed. |
| `playbooks/feedback-compaction/SKILL.md` (new) | Entry (invoked or confirmed, `session` depth, clean tree, base commit, outcome never changes), Step 1 collect and exclude, Step 2 group and show the map, Step 3 write or extend records from an embedded record template, Step 4 apply and verify (delete, `devkit rules fix`, status check, Response review), Step 5 ADR candidates, completion conditions. |
| `bundle.toml` | `[[assets]] id = "feedback-compaction" kind = "playbook" source = "playbooks/feedback-compaction"` and the id in `presets.core`. No version bump (asset additions did not bump it before). |
| `skills/spec/references/source-feedback.md` | One sentence: a terminal source may resolve to a compact record through its alias; the reference stays traceability. |
| `skills/spec/references/playbooks.md` | The confirmation sentence names `spec/feedback-compaction` beside `spec/adr-compaction` as authorizing its deletions at `session` depth. |
| `playbooks/feedback-hygiene/SKILL.md` | One line: terminal feedback is compacted by the separate `feedback-compaction` playbook, never in a hygiene session. |
| `CAP-HARN-agent-guidance` | Playbook asset row and 4.5 table add `feedback-compaction`; the feedback capture policy replaces open-backlog deduplication with the every-status lookup. |
| `CAP-DLV-delivery-workflows` | The "Source feedback at completion" lifecycle paragraph adds the lookup before recording and compaction of closed feedback, citing both ADRs. |
| `.devkit/installation.json`, `AGENTS.md` block | Written by `devkit sync` after the bundle source change. |

## 3. Component & Interface Design

The lookup command (normative, from the ADR):

```bash
devkit docs search "<symptom and asset words>" --kind feedback --history -n 5   # sweep: add --all-namespaces
```

The compact record (normative shape, embedded in the playbook as a fenced template):

```markdown
---
id: FB-compacted-<area>-<status>
title: <Area> feedback, <status>
summary: <the area's recurring symptoms, in one English sentence>
target: docs/capabilities/<area>/
status: <status>
created_at: <first run date>
aliases:
  - FB-<retired>
---

# [FB-compacted-<area>-<status>] <Area> feedback, <status>

## FB-<retired>

- **Symptom**: <the original title's words>
- **Response**: <outcome with its destination>
- **Reason**: <one line>
```

Record path: `specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md`, which `RULE-id-convention` already
maps to `FB-compacted-<area>-<status>`. A later run appends entries and aliases to the same file.

## 5. Error Handling & Edge Cases

- A file that fails `devkit rules check` or has an unknown status, an item cited by a current document, an item of an
  incomplete spec or live proposal, or an item an unmerged branch touches: left in place and reported with the reason.
- A fidelity mismatch (status differs, Response altered or untraceable): return to the writing step or take the item
  out of its group, as `adr-compaction` does.
- A `promoted` or `forwarded` lookup hit whose destination no longer resolves (`DOCS_ID_UNRESOLVED`): treated as
  ended, so a new item citing the ID is recorded.

## 6. Verification & Test Plan

- New `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_lookup_guidance.py`: AC-01 to AC-03 on the
  skill and the sweep reference (`assert_rule`, absent equal-`target` wording).
- New `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_compaction_guidance.py`: AC-04 (bundle
  registration), AC-05 to AC-07, AC-09 to AC-11 wording; AC-08 extracts the record template, fills it, writes it with
  a completed spec bundle citing a retired ID, loads `DocumentIndex` and runs the `id-convention`, `spec-format` and
  `document-reference` rules; AC-12 self-containment (no repository ID in the playbook).
- `test_playbook_discovery_guidance.py`: add the playbook to `PLAYBOOKS` (AC-12); `test_bundle_budgets.py` covers the
  new file automatically.
- AC-04 and the Living Spec reflection also by running `uv run devkit sync`, `uv run devkit sync --check`,
  `uv run devkit playbook get spec/feedback-compaction` and `uv run devkit rules check`.
- Commands: `just lint devkit-spec`, `just check devkit-spec` (Pyright on touched modules), `just test-affected`
  (keeping its `mode=full` fallback), `uv run devkit rules check`, `uv run devkit rules check --phase hygiene` on the
  changed assets for `RULE-agent-asset-wording`.
