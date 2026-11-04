---
id: FB-padr-default-slug-from-long-title
title: Planning guidance omits --slug, so a descriptive PADR title yields an unwieldy ADR ID
scope: repo
kind: suggestion
category: redundant-step
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-padr-default-slug-from-long-title] Planning guidance omits --slug, so a descriptive PADR title yields an unwieldy ADR ID

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the Planning reference (step 2) says to create a PADR with
  `devkit spec proposal padr <slug> "<title>" --summary "<Y-statement>"`. The command derives the PADR slug from the
  whole title unless `--slug` is passed, so a title written as a sentence ("Per-namespace milestones under the
  namespace docs root") produces a nine-word PADR ID (the whole title as a slug), which handoff promotes to an ADR
  ID of the same length. The agent deletes the scaffold and reruns with `--slug`.
- **Proposed Procedure**: the Planning reference names `--slug <short-slug>` in its example and says the ADR keeps
  the PADR slug, so the agent chooses the ID once; alternatively the `padr` command's text output could print the
  derived ID with a hint when the slug exceeds a few words.
- **Expected Benefit**: one scaffold run instead of two per PADR, and ADR IDs that read like the existing ones
  (`ADR-ux-screens`, `ADR-document-system`).
- **Cost & Risk**: one more flag in an example; no behavior change.
- **Attempted**: hypothesis; the rerun with `--slug namespace-milestone-roots` worked in this session.

## Diagnostic Details

- **Reproduction**: `uv run devkit spec proposal padr namespace-roadmap "Per-namespace milestones under the namespace docs root" --summary "..."`, then rerun with `--slug namespace-milestone-roots` after deleting the first file.
- **Expected / Actual**: expected a short ID or a hint; actual: the nine-word ID was scaffolded, as the `--help` text
  says.
- **Versions**: the `plan-namespace-roadmap` worktree at the Planning head.
- **Conditions**: Planning in direct mode, first PADR of the proposal.
- **Workarounds Attempted**: delete and rerun with `--slug`; succeeded.
- **Related Assets**: `devkit spec proposal padr --help`; the `spec` skill `references/planning.md` step 2.

## Evidence

```text
[PADR: <the title slugified, nine words> path=docs/proposals/PROP-namespace-roadmap/decisions/<same>.md proposal=PROP-namespace-roadmap]
--slug TEXT  Slug of the PADR ID and file name; its first word needs a letter [default: the title's slug]
planning.md step 2: Create it with `devkit spec proposal padr <slug> "<title>" --summary "<Y-statement>"` and read the scaffold before writing its body.
```
