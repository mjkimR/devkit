---
id: FB-proposal-new-target-area-placeholder
title: devkit spec proposal new leaves target_area and boundaries as placeholders
scope: repo
kind: suggestion
category: missing-capability
target: devkit spec proposal new
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-proposal-new-target-area-placeholder] devkit spec proposal new leaves target_area and boundaries as placeholders

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `devkit spec proposal new <slug>` writes `target_area: capabilities/<area>/` and
  `boundaries.owns: [capabilities/<area>/]` literally; the command has no option for either, so every draft needs a
  hand edit of the frontmatter after scaffolding. Whether a rule flags a
  remaining placeholder was not checked.
- **Proposed Procedure**: add `--target-area <path>` (filling both `target_area` and `boundaries.owns`), or have a
  rule report the literal `<area>` placeholder in a proposal leaving `draft`.
- **Expected Benefit**: one command produces a complete draft; a forgotten placeholder is caught before Planning.
- **Cost & Risk**: one more CLI option or rule; none for existing proposals.
- **Attempted**: two drafts scaffolded in this session; both frontmatters edited by hand.

## Evidence

- Scaffolded frontmatter excerpt: `target_area: capabilities/<area>/` and `owns: - capabilities/<area>/`.
- `devkit spec proposal new --help` lists `--task-kind`, `--planning-effort`, `--dev-effort`, `--namespace`,
  `--summary`, `--supersedes`, `--decomposed-from`, `--needs-decompose`, `--with-target-docs`; no target-area option.
