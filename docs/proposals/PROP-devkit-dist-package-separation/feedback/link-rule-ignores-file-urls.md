---
id: FB-link-rule-ignores-file-urls
title: Markdown link rule accepts machine-local file URLs in documents
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit/src/devkit/rules/rules/markdown_link (RULE markdown-link)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-link-rule-ignores-file-urls] Markdown link rule accepts machine-local file URLs in documents

## 2. Suggestion / Change Request

- **Current Procedure**: The markdown link rule checks only relative links whose target file is missing. A link
  whose destination is an absolute `file:///` URL is treated like an external URL and never reported, so a
  proposal committed through the commit gate carried four capability links of the form
  `file:///<home>/<user>/projects/.../docs/capabilities/distribution/CAP-DIST-....md`. They point at another
  machine's checkout, are broken for every other reader, embed a local username, and break the
  `living-spec-writing` instruction, which says ID-bearing documents are referenced by full ID, never by path.
- **Proposed Procedure**: Report a Markdown link whose destination uses the `file:` scheme (or is an absolute
  filesystem path) in tracked documents as a violation, with a fix directive to use a relative link or, for an
  ID-bearing document, its full ID in backticks.
- **Expected Benefit**: Catches machine-local links at commit time instead of during a later Planning review; keeps
  local usernames out of committed documents.
- **Cost & Risk**: Low; a repository that intentionally documents `file:` URLs inside link syntax would need a
  per-path exclusion. Code spans and fenced blocks are not links and stay unaffected.
- **Attempted**: Hypothesis. This run replaced the four links by full IDs in the proposal by hand.

## Diagnostic Details

- **Reproduction**: `devkit rules check docs/proposals/PROP-devkit-dist-package-separation` on the proposal as
  recorded at plan-intent.
- **Expected / Actual**: Expected a finding for the four `file:///` links; actual `[SUMMARY: errors=0 warnings=0
  infos=0 fixed=0]`.
- **Versions**: devkit-agt 0.1.1 (workspace source at the plan-intent commit).
- **Conditions**: Planning worktree of the proposal; links written in an earlier session on another machine.
- **Workarounds Attempted**: Manual replacement during review.
- **Related Assets**: `markdown_link/rule.py` (`BrokenLink`: "A relative link whose file does not exist"),
  `living-spec-writing` instruction, `RULE-id-convention`.

## Evidence

```text
proposal.md section 3 (before this run):
  [CAP-DIST-manifest-spec](file:///<home>/<user>/projects/workbench/repos/devkit/docs/capabilities/distribution/CAP-DIST-manifest-spec.md)
  ... three more links of the same form
devkit rules check <proposal dir>  ->  [SUMMARY: errors=0 warnings=0 infos=0 fixed=0]
markdown_link/rule.py: "A relative link whose file does not exist, with its unique repair candidate if any."
```
