---
id: FB-proposal-report-template-discovery
title: Expose the required proposal report template to MCP callers
scope: repo
kind: friction
category: missing-capability
target: spec_proposal_report
skill: spec-review-proposal
agent: codex
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-21
---

# [FB-proposal-report-template-discovery] Expose the required proposal report template to MCP callers

## 1. Friction / Question

- **Context**: Publishing a current accepted-base proposal briefing through the owning MCP service before Development handoff.
- **Expectation**: The tool description and workflow skill expose enough information to construct the required body, or identify a callable template retrieval route.
- **Actual**: The tool exposes body as a string and promises a complete source-bound briefing, but does not disclose mandatory frontmatter, localized exact headings, nested decision fields and envelope coverage tokens. The first semantic briefing was rejected with PROPOSAL_REVIEW_INVALID. The fix names a report template without a retrieval command.
- **Workaround**: Read the domain implementation and invoke its read-only Python template function locally, then publish a correctly structured Korean report through MCP. Both report publications succeeded; exact-playbook-get handoff succeeded using its immutable URI. Shared list and publication namespace matched the local template namespace.
- **Suggestion**: Expose the domain-owned template through a discoverable MCP read operation or document its supported retrieval route in tool metadata and the review skill. Include the failed field class in diagnostics without weakening source, language or coverage checks.

## Diagnostic Details

- **Reproduction**: Call spec_proposal_report with accepted slug, current full source SHA and a complete prose briefing lacking schema frontmatter. It returns the identity mismatch. Inspect proposal_report.py and obtain template(root, slug, sha); fill its structure and call the same publication tool successfully.
- **Expected / Actual**: Discoverable authoring contract versus source inspection required for successful input construction.
- **Versions**: Base commit 6e964edd763bd29794301826dcb3a9e0b70c3062; installed package version not separately inspected.
- **Conditions**: Codex local orchestration, connected devkit MCP, local shared adapter, Korean approval language, clean accepted base. No cloud or cross-host sharing exercised.
- **Workarounds Attempted**: CLI report help exposed required body-file but no template option. Local read-only Python template inspection disclosed exact required structure. Publication remained on MCP; no CLI publication fallback was used.
- **Related Assets**: packages/devkit-spec/src/devkit_spec/proposal_report.py; spec-review-proposal skill; spec_proposal_report tool description.

## Evidence

```text
First publication: PROPOSAL_REVIEW_INVALID
message: report identity does not match repository, proposal, source or language
fix: Provide a complete report for the current clean committed proposal using the report template
Domain _check requires proposal, source_sha, language, repository_namespace;
localized section names, each PADR and all Planning envelope filenames.
After filling template: two immutable proposal-review artifacts published;
exact-playbook-get spec_handoff status=handed_off.
```

## Disposition

- **Disposition (resolved)**: `SPEC-feedback-guidance-fixes` adds `devkit spec proposal report <slug> --source-sha <sha> --template` and the
  read-only MCP tool `spec_proposal_report_template`, names them in the `spec_proposal_report` description and the
  `spec-review-proposal` skill, and prefixes each `PROPOSAL_REVIEW_INVALID` message with the failed field class whose
  `[FIX]` names both routes; every publication check is kept. Verified by
  `packages/devkit-spec/tests/integration/features/proposals/test_proposal_report.py` and `test_cloud_guidance.py`.
