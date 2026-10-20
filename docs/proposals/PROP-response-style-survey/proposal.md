---
id: PROP-response-style-survey
title: Survey reply-style practice to refine response-style
summary: "Selects established first-party prompt sources and official writing guides, then evaluates one portable response-style candidate with a bounded English/Korean pilot while retaining the 300-byte guidance contract."
status: reviewing
created_at: 2026-10-19
target_area: distribution/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - distribution/
    - packages/devkit-catalog/src/devkit_catalog/response_style/
    - packages/devkit-catalog/tests/test_bundles.py
    - scripts/smoke.sh
  excludes:
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-response-style-survey] Survey reply-style practice to refine response-style

## 1. Background & Hypothesis

The existing response-style has no recorded behavioral comparison. Popular prompt sources can identify useful
practices, but stars are a screening signal and do not prove that their instructions improve replies. The
previous single-source rewrite's origin is not independently audited or reused in this survey.

The selected direction is one portable style that preserves decision-relevant content, adapts length to the
request and avoids unnecessary framing. Its improvement over the current style remains a hypothesis until the
paired pilot runs. No source consensus, model-wide benefit or cross-host effectiveness is asserted in Planning.
The 300-UTF-8-byte guidance-fragment limit in `CAP-DIST-manifest-spec` remains in force. A once-read skill fading
in long sessions is unmeasured, and does not yet justify a shared distribution-contract change.

## 2. Technical Spike Conclusions

- **Q1 (Sources)**: Select OpenCode, Aider, Continue, gptme, Anthropic's official explanatory output-style plugin
  and Goose. All six meet the >=1,000-star, non-archived, <=180-day default-branch-commit screen, with pinned
  prompt/license sources. Add official Google, Microsoft and Toss writing guides as a separate evidence class.
  `MAT-response-style-source-selection` records current counts, source diversity, provenance limits, exclusions
  and the candidate-rule ledger. No majority vote treats unverified shared ancestry as independent evidence.
- **Q2 (Reuse)**: Keep per-source notes and original synthesis. Do not copy source wording, examples or structure;
  unresolved website terms are explicit. `PADR-response-style-source-selection` defines the screening and reuse
  direction without treating a license label as legal clearance.
- **Q3 (Measurement)**: Use twelve fixed English/Korean fixtures, no added bundle style/current/candidate arms,
  two fresh repetitions and at most 72 generation attempts per selected host. Preserve semantic obligations
  before optimizing form or length; publish raw synthetic outputs, blinded judgments and incomplete cells.
  `PADR-response-style-measurement` and `MAT-response-style-measurement-design` define the protocol. Execution
  host, isolation method and collection budget remain the single open Planning question. Existing interactive
  native subagents inherit style and are not valid no-style baselines.
- **Q4 (Always-on budget)**: Retain one <=300-byte pointer and the discoverable skill. No manifest exception,
  universal limit increase or fragment splitting. An optional <=16-generation synthetic position diagnostic
  cannot prove compaction behavior. An actual contract expansion needs a separately accepted design supported by
  observed host behavior; this proposal promises no such expansion (`PADR-response-style-guidance-budget`).
- **Q5 (Variants)**: Keep one style and existing `language` configuration. Presets, new variables and host-specific
  prompt variants add unsupported branches and are excluded.
- **Q6 (Precedence)**: User and workflow requirements determine necessary content and required formats. Style
  controls presentation within those obligations. A required table, risk, field or verification number survives
  concision; the pilot tests that interaction. No spec report-schema change is proposed.

## 3. Proposed Design & Impact

Planning writes the pinned survey notes, twelve-case evaluation design and three PADRs inside this proposal.
After the open execution decision and `plan-accept`, handoff promotes source materials and decisions through the
normal workflow; Development writes its spec, plan and tasks before editing the bundle.

Development freezes the baseline and fixtures, writes one original candidate and a small spec-local standard-library
import/scoring script, collects the selected host cohort and records the first results. Reject a candidate that
loses required facts or fails artifact/report obligations. Adopt it only when the predeclared paired criteria pass;
otherwise retain the current style and publish the negative result. Each retained rule is labelled as existing
local policy, source-supported hypothesis or measured bundle behavior; no per-rule causal claim is inferred.

The production change, if supported, is limited to the response-style bundle, its existing deployment tests and
smoke assertions. Reflect its current contract in `CAP-DIST-content-packages`. Preserve template/language behavior,
opt-in packaging and projection for Codex, Claude Code and Antigravity. Deployment coverage is not a live reply
quality measurement; unmeasured hosts stay visible in the results. Shared guidance validation and
`CAP-DIST-manifest-spec` remain unchanged. No report format or unrelated bundle changes.

Verification: complete and uncontaminated result matrix for the selected host; original-source provenance and
license-scope review; scorer rejection tests for missing/duplicate records and incomplete facts; existing language
and host-projection coverage; applicable lint/type checks, `just test-affected`, consumer smoke, repository rules
and independent medium Development review. No live model call or production change occurs during Planning.

## 4. Lifecycle & Retirement Criteria

Accept the direction only after the execution host and budget are selected and independent Planning criticism is
resolved. Record the user's `plan-accept` decision through the workflow. Development starts by normal handoff;
no generation method, merge, push or publication is authorized merely by this document. At completion keep the
first results and the selected/retained style rationale, with explicit limits on host and long-session claims.
Rejection follows the workflow with its reason and preserves any open feedback before retirement.
