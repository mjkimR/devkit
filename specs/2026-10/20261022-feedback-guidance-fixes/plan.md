---
id: PLAN-feedback-guidance-fixes
spec: SPEC-feedback-guidance-fixes
---

# Technical Plan: `SPEC-feedback-guidance-fixes` Feedback Guidance Fixes

## 1. Architecture Overview & Impact
- Target Area: `devkit-spec` proposals feature (report use case, report MCP tools, handoff body carrying), the
  `devkit spec proposal` CLI group in the delivery feature, the `spec` bundle skill sources, and the `devkit-agt`
  workflow envelope authoring service.
- No schema, envelope format or approval-policy change. Publication keeps every existing check; only messages and
  the `[FIX]` text of `PROPOSAL_REVIEW_INVALID` and `ENVELOPE_FROM_INVALID` change.

## 2. Component Breakdown & Interface Contracts

### Report template route (AC-01 to AC-05)
- `features/proposals/usecases/report.py`: add `ReportTemplateUseCase(BaseUseCase).execute(root, slug, sha) -> str`
  that resolves the source checkout like `PublishWorkspaceProposalReportUseCase` (the Planning worktree when the
  retained base HEAD is not the source) and returns `template(...)`. Shared selection moves to a private helper.
- `_check` and `source` messages start with a field class (`identity:`, `title:`, `sections:`, `decisions:`,
  `decision fields:`, `coverage:`, `dev_effort:`, `size:`, `source:`) and name the mismatched keys, headings, PADR
  IDs or tokens. `ReportInvalidError.fix` names `devkit spec proposal report <slug> --source-sha <sha> --template`
  and `spec_proposal_report_template`.
- `features/delivery/cli/proposals.py`: `report` gains `--template` (flag); `--body-file` becomes optional; exactly
  one of them is required (`ArgumentError`, `ARGUMENT_INVALID`). Text output is the template Markdown; JSON is
  `{"proposal", "source_sha", "template"}`.
- `features/proposals/mcp/report.py`: add tool `spec_proposal_report_template` (`execution="read_only"`,
  `read_only=True`) returning `{"proposal", "source_sha", "template"}`; the `spec_proposal_report` description names
  it and the CLI flag.
- Skill `spec-review-proposal/SKILL.md.jinja`: step 5 names the template route before publication.

### Reverify fix (AC-06)
- `devkit_agt/features/workflow/services/envelope/authoring.py` `carried_findings`: when the `--from` envelope kind is
  `reconcile-check`, the `[FIX]` says a reconcile finding is closed by a new reconcile-check envelope
  (`devkit workflow envelope new --unit <dir> --kind reconcile-check --stage living-spec-draft ...`) or by calling the
  reconcile-reviewer again. Other kinds keep the existing fix.

### Planning guides (AC-07, AC-08)
- `spec/references/planning.md` step 2: a PADR withdrawn before `plan-accept` is deleted in the fold commit (Git keeps
  it), and its ID and reason go into the proposal's Planning decisions; no withdrawn status exists.
- `spec/references/worker-records.md` section 2: a correction of a recorded answer is a later `answer` envelope
  naming the same `worker` envelope and question with the corrected decision; its summary names the corrected
  `answer-NN.yaml`; the earlier envelope is never edited; the fold reflects the correction in the documents. The
  existing command accepts it (verified by a `devkit-agt` test).

### Handoff placement (AC-09)
- `features/proposals/services/body.py`: `classify` returns `contract` for a heading naming a non-goal keyword with
  `acceptance`/`validation`/`verification`, or `validation`/`verification` alone; `CarriedProposal` gains
  `contract`, carried with headings demoted.
- `features/proposals/usecases/specs.py`: render `## 5. Carried Proposal Contract` (with a one-line note that the
  scenarios and exclusions are to be rewritten as acceptance criteria and non-goals) after the acceptance criteria,
  then Carried Proposal Notes numbered after it.

### Living Spec
- `CAP-DLV-proposal-incubation` (4.6 table, report section, PADR section), `CAP-DLV-spec-bundles` (4.3 skeleton),
  `CAP-DLV-workflow-envelopes` (`--from` row), `CAP-HARN-agent-guidance` (`spec-review-proposal` row).

## 3. Verification & Test Plan
- `just test devkit-spec tests/integration/features/proposals tests/unit/features/proposals
  tests/integration/bundles/spec` for AC-01 to AC-05 and AC-09.
- `just test devkit tests/integration/features/workflow` for AC-06 and AC-08.
- `just lint devkit-spec`, `just lint devkit`, `just check devkit-spec`, `just check devkit`, `just test-affected`,
  `uv run devkit sync`, `uv run devkit status`, `uv run devkit rules check --staged` for AC-10.
