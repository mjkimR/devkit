---
id: FB-target-docs-not-scaffoldable-after-new
title: No command adds target-docs.md to a proposal bundle created without it
scope: repo
kind: friction
category: missing-capability
target: devkit spec proposal new
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-target-docs-not-scaffoldable-after-new] No command adds target-docs.md to a proposal bundle created without it

## 1. Friction / Question (friction, question)

- **Context**: First Planning turn of a draft that Backlog created with `devkit spec proposal new` without
  `--with-target-docs`; the turn drafts the Living Spec targets.
- **Expectation**: A command or a managed template gives the blueprint's frontmatter (`id: PROP-<slug>-target`,
  `proposal`, `targets`) and its five sections, as `.devkit/managed/spec/templates/proposal.md` does for
  `proposal.md`.
- **Actual**: `target-docs.md` is written only by `new --with-target-docs`. `devkit spec proposal --help` lists no
  command that adds it to an existing bundle, and `.devkit/managed/spec/templates/` holds no blueprint template.
- **Workaround (or Interpretation Chosen)**: Copied the shape from `_target_docs` in the scaffold source and from
  another proposal's `target-docs.md`, and filled `targets` by hand.
- **Suggestion**: Ship the blueprint as a managed template beside `proposal.md`, or let a command write
  `target-docs.md` into an existing bundle; name the route in the planning reference.

## Diagnostic Details

- **Reproduction**: `devkit spec proposal new <slug>` without `--with-target-docs`, then start Planning and draft the
  targets.
- **Expected / Actual**: expected a scaffold route for the blueprint; found none after `new`.
- **Versions**: the repository at `b3e4753d`.
- **Conditions**: any proposal created without `--with-target-docs`, the default.
- **Workarounds Attempted**: read `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`
  (`_target_docs`); succeeded.
- **Related Assets**: the `spec` skill's `references/planning.md`, `CAP-DLV-proposal-planning` section 4.4.

## Evidence

```text
devkit spec proposal --help: accept, check, handoff, new, padr, report
devkit spec proposal new --help: "--with-target-docs  Also scaffold target-docs.md, the Living Spec blueprint"
ls .devkit/managed/spec/templates/: proposal.md (no blueprint template)
```
