---
id: FB-compacted-governance-promoted
title: Governance feedback, promoted
summary: Repository governance rules and architectural constraints.
target: docs/capabilities/governance/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-authoring-preset-not-selected
  - FB-link-rule-ignores-file-urls
  - FB-new-seed-sync-output-outside-boundaries
  - FB-reference-to-draft-added-on-base
---

# [FB-compacted-governance-promoted] Governance feedback, promoted

## FB-authoring-preset-not-selected

- **Symptom**: The skill-authoring playbook and size rule are not selected in a repository that authors skills
- **Response**: `.devkit/config.toml` (s-lane)
- **Reason**: `authoring = "skill-authoring"` selected; `devkit rules check --phase hygiene` reports 0 warnings, since the rule measures bundle sources and skips receipt-owned projections.

## FB-link-rule-ignores-file-urls

- **Symptom**: Markdown link rule accepts machine-local file URLs in documents
- **Response**: RULE-markdown-link
- **Reason**: a file: destination is reported as a machine-local link

## FB-new-seed-sync-output-outside-boundaries

- **Symptom**: A new docs-skeleton seed writes a repository path no boundary names
- **Response**: Promoted outcome
- **Reason**: Promoted on the user's decision to the draft `SPEC-seeded-paths-in-boundaries`, which records this ID under `Source feedback`.

## FB-reference-to-draft-added-on-base

- **Symptom**: A Planning branch cannot cite a draft proposal added to the base after it branched
- **Response**: `src/devkit_spec/bundle/skills/spec/references/branches.md` §3
- **Reason**: a document added to the base after the branch started is cited by ID after merging the base, otherwise by slug in prose; the rule is unchanged.
