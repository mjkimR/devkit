---
id: PROP-delete-resolved-feedback
title: Retire resolved feedback by deletion
summary: "Deletes resolved feedback outright during feedback compaction instead of preserving summarized records and aliases, accepting that pytest tests prevent regressions and git history retains evidence."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-10-31
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/delivery/
    - packages/devkit-spec/
    - packages/devkit-docs/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-delete-resolved-feedback] Retire resolved feedback by deletion

## 1. Background & Hypothesis

The recent feedback compaction feature (`SPEC-feedback-dedup-and-compaction`, `ADR-closed-feedback-compacts-into-per-area-records-with-aliases`) introduced the `feedback-compaction` playbook, which groups closed feedback across all terminal statuses (`resolved`, `promoted`, `dismissed`, `forwarded`) into per-area summary records (`FB-compacted-<area>-<status>`) while preserving retired IDs as aliases.

In practice, `resolved` items represent the vast majority of closed feedback (over 60% of the ledger, 148 of 233 terminal files). Unlike `dismissed` feedback (which records reasons why proposed ideas were rejected) or `promoted`/`forwarded` feedback (which records destination routing), `resolved` feedback documents defects and friction points that have already been addressed in production code and verified through tests.

Retaining summarized `FB-compacted-<area>-resolved` records and aliases imposes maintenance and ledger overhead without tangible engineering benefit:
1. **Regression prevention belongs to tests**: Preventing regressions of resolved issues is the responsibility of `pytest` test suites and governance rules (`devkit rules`), not an agent reading historical feedback summaries.
2. **Re-observation naturally files fresh feedback**: If a defect regresses despite tests, an agent observing the failure can simply record a new feedback item or bugfix task based on current symptoms.
3. **Traceability remains intact**: Git commit history and completed spec records (`spec.md`, `reconcile.md`, `tasks.md`) retain the full historical context and resolving evidence. Much like proposals (`PROP-*`) are pruned after handoff and acceptance, `resolved` feedback can be retired by outright deletion during compaction rather than accumulating into permanent compacted ledger files.

Core hypothesis: Eliminating `FB-compacted-<area>-resolved` records and deleting `resolved` feedback outright during `feedback-compaction` simplifies the feedback ledger and compaction playbook, eliminates unnecessary summary records, and avoids artificial alias lookups, while requiring minimal adjustments to governance reference rules.

## 2. Technical Spike Questions

- **Q1**: How does `RULE-document-reference` handle deleted `FB-*` IDs cited in historical and active documents?
  - *Finding*: Completed spec bundles (`DocumentIndex.is_historical`) are already excluded from default governance checks by `reportable()`. When a historical spec is explicitly targeted (e.g. `devkit rules check specs/.../spec.md`), `document_reference.py` already exempts handed-off proposals via `if historical: return`. Adding a matching exemption for historical `FB-*` references (`if historical and ref.target.startswith("FB-"): return`) ensures reference checks stay clean without needing alias records. Active documents citing `FB-*` (only 9 current documents across the entire repository) can reference the resolving `SPEC-*` ID or use plain text.
- **Q2**: Will deleting `resolved` feedback break worker inputs in `inputs.py` (`devkit spec worker inputs`)?
  - *Finding*: `inputs.py` resolves `## Source feedback` only for the current unit being worked on. Because the compaction playbook explicitly excludes items belonging to uncompleted spec bundles (`spec.md` not `completed`) and items referenced by unmerged branches, worker input resolution will never encounter deleted files.
- **Q3**: How does outright deletion affect feedback lookup before recording (`ADR-recording-looks-up-existing-feedback-of-every-status-first`)?
  - *Finding*: `spec-feedback` searches existing feedback with `devkit docs search --kind feedback --history -n 5`. Removing `resolved` records means the search will no longer return resolved hits. If an issue recurs, it is recorded as a clean new observation (or bugfix) rather than requiring the recorder to determine whether it is a `recurring: true` regression citing a retired summary entry.

## 3. Proposed Design & Impact

- **Compaction Playbook (`feedback-compaction`) update**:
  - Step 1 (Collect): Continues to collect terminal feedback under `specs/`, but partitions `resolved` items separately from `promoted`, `dismissed`, and `forwarded`.
  - Step 3 (Write or extend): Only creates or extends `FB-compacted-<area>-<status>` records for `promoted`, `dismissed`, and `forwarded`. No `FB-compacted-<area>-resolved` records or aliases are produced.
  - Existing `FB-compacted-<area>-resolved` records are also retired by deletion, including their aliases; apply the same eligibility and reference checks as for individual resolved files. Test this migration on an already compacted ledger.
  - Step 4 (Apply and verify): `resolved` files are deleted via `git rm` outright. Alias verification and status equality checks apply only to compacted groups (`promoted`, `dismissed`, `forwarded`).
- **Governance Rule (`RULE-document-reference`) update**:
  - This deliberately gives up detection of misspelled or never-existing unresolved `FB-*` IDs in historical documents; active documents retain strict reference validation. Test both cases. Git history remains the evidence for retired IDs.
  - In `document_reference.py`, permit historical documents (`index.is_historical(document)`) to cite deleted `FB-*` references without reporting unresolved errors when explicitly targeted, mirroring the existing treatment of handed-off proposals.
- **Feedback Recording Procedure (`spec-feedback`) update**:
  - In `spec-feedback/SKILL.md` and `references/sweep.md`, update the matched status action table: remove special handling for `resolved` hits, or clarify that any recurrence is recorded as a fresh feedback item.
- **Living Spec & ADR Updates**:
  - Supersede the relevant clauses of `ADR-closed-feedback-compacts-into-per-area-records-with-aliases` (specifically regarding `resolved` status compaction and alias retention) and update `ADR-recording-looks-up-existing-feedback-of-every-status-first`.
  - Update `CAP-HARN-agent-guidance` and `CAP-DLV-delivery-workflows` to document outright deletion of `resolved` feedback.
  - Update integration test suites (`test_feedback_compaction_guidance.py` and `test_feedback_lookup_guidance.py`) to reflect the new behavior.
- **Non-Goals**:
  - Deleting `open`, `promoted`, `dismissed`, or `forwarded` feedback outright (they still require resolution, tracking, or compacted reason records).
  - Deleting feedback files belonging to uncompleted spec bundles or unmerged local branches.
  - Automatic compaction runs without explicit user invocation or confirmation.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr delete-resolved-feedback "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept delete-resolved-feedback --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff delete-resolved-feedback.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
