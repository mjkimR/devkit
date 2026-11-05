---
id: PROP-justfile-standard-templates-target
title: Target Living Spec Structure for PROP-justfile-standard-templates
status: draft
proposal: SPEC-justfile-standard-templates
created_at: 2026-11-04
targets: []
---

# [Blueprint] PROP-justfile-standard-templates

## 1. Retained Onboarding Changes

- Update `guides/install/existing-repository.md` and `guides/install/new-repository.md` with concrete examples of
  existing command reuse, optional justfile recipes and native non-Python verification commands.
- Preserve CAP-GATE-commit-gates: the project explicitly supplies fast commands; a justfile's presence does not
  select a gate command. No new scaffolding command or runtime inference is planned.

## 2. Catalog Instruction Candidate

If retained in Planning, describe an opt-in catalog bundle for creating and extending justfile, CLI and MCP
interfaces in CAP-DIST-content-packages and its own capability/use case where needed. Update catalog and
installation recommendation tables to identify when the bundle helps.

The instruction selects useful operations before creating entry points, reuses suitable existing commands,
and keeps detailed guidance conditional. It does not mirror all CLI commands into MCP or require a task runner.
It does not duplicate the Python implementation guidance owned by `cli-tool`. Existing-interface cleanup stays
with the `maintenance` review-refactor playbook. Bundle naming and asset layout remain Planning questions.

## 3. Verification

Walk through existing-command and new-interface setup, plus one actual non-Python pilot case. If the catalog
candidate is retained, check its opt-in manifest and review creation scenarios across all three interfaces.
No CLI architecture change or automatic command-removal mechanism is planned.
