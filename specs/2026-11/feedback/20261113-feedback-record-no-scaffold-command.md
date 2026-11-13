---
id: FB-feedback-record-no-scaffold-command
title: No command scaffolds a feedback record; each is copied by hand from the template
scope: repo
kind: suggestion
category: missing-capability
target: the spec-feedback skill (Recording procedure)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-feedback-record-no-scaffold-command] No command scaffolds a feedback record; each is copied by hand from the template

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The agent searches for duplicates, chooses the path by context (proposal, Unit or
  `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<name>.md`), copies the template block, fills twelve frontmatter fields and
  the H1, then runs `devkit rules check` and `devkit rules fix` to align the ID. A consumer Unit wrote three records
  this way; this repository's own sweep wrote ten.
- **Proposed Procedure**: `devkit spec feedback new <name> --kind ... --category ... --target ... [--unit <dir>]`
  that picks the location, writes valid frontmatter and H1 with the right sections for the kind, refuses a used
  name, and prints the duplicate-search command to run first.
- **Expected Benefit**: Fewer hand-edits and rule-fix round trips; consistent paths and IDs.
- **Cost & Risk**: Another command to keep in step with the template; the content still needs the agent's judgment.
- **Attempted**: Hypothesis.

## Diagnostic Details

- **Reproduction**: not applicable.
- **Expected / Actual**: Expected a scaffold command like `devkit spec proposal new`; actual template copy.
- **Versions**: devkit `569379a06`.
- **Conditions**: consumer Unit feedback and this repository's Backlog.
- **Workarounds Attempted**: manual template copy; `devkit rules check` passed afterwards.
- **Related Assets**: `spec-feedback` skill and `references/template.md`.

## Evidence

```text
spec-feedback step 3: "Write the file where the work is ..."; step 4: "Fill it from the feedback template".
No feedback subcommand under `devkit spec`.
```
