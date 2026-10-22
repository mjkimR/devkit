# Pilot: `spec-plan` under `agent-asset-writing`

The old text is `spec-plan/SKILL.md` at base commit `542f4461`; the new text is this unit's version.

## 1. Constraint Mapping (AC-08)

| # | Old text (section) | New location |
| --- | --- | --- |
| O1 | Trigger: `specify` stage of `sdd-spec-feature`, `plan-tasks` of `sdd-spec-bugfix` (intro) | Intro, "Use this skill at" list |
| O2 | Purpose: design, map onto architecture, set contracts and boundaries (intro) | Intro, first sentence |
| O3 | Input `spec.md`; `plan.md` skeleton from `spec new` or `proposal handoff` (1) | 1. Inputs, items 1-2 |
| O4 | Bugfix bundle without `plan.md`: write it at `plan-tasks` with `id`/`spec` frontmatter (1) | 1. Inputs, item 3 |
| O5 | Inputs `docs/architecture/`, `devkit spec list capability`, `devkit spec list decision` (1) | 1. Inputs, item 4 |
| O6 | Accepted ADRs via `devkit spec search "<topic>" --kind decision` (Step 0) | 2. Procedure, step 1 |
| O7 | Module boundaries, imports, runtime, packaging, dependency constraints (Step 0) | 2. Procedure, step 1 |
| O8 | Duplicated or broken capabilities, `devkit spec refs <CAP-ID> --direction in` (Step 0) | 2. Procedure, step 1 |
| O9 | Changed MUST needs a new ADR: path, ID, template (Step 0) | 2. Procedure, step 2 |
| O10 | Recommended option inside intent, reason recorded; outside intent is a Host problem (Step 0) | 2. Procedure, step 3 |
| O11 | Bugfix needing a different defect scope returns to `characterize` (Step 0) | 2. Procedure, step 3 |
| O12 | Components and internal contracts; external API/CLI flags, codes, payloads (Step 1) | 2. Procedure, step 4 |
| O13 | Every story has a path, every `[AC-NN]` a component, no non-goal (Step 2) | 2. Procedure, step 5 |
| O14 | Failure modes; backwards-compatible rollout for migrations (Step 3) | 2. Procedure, step 6 |
| O15 | Tests and checks per scenario; bugfix regression and preservation checks (Step 4) | 2. Procedure, step 7 |
| O16 | Read the skeleton, rewrite, keep `id` and `spec` (3) | 3. Plan Output, item 1 |
| O17 | Invariant review, impacted components, verification always present (3) | 3. Plan Output, item 2 |
| O18 | Other sections only with content; drop instead of "N/A"; short plan for small change (3) | 3. Plan Output, item 3 |
| O19 | Cite by full ID in backticks, not Markdown path (3) | 3. Plan Output, item 4 |
| O20 | Plan template, sections 1-6 with diagram, data contracts, storage, errors, verification (3) | 3. Plan Output, template (unchanged) |
| O21 | Section 1 lists only conflicts with their ADR, "None" when conforming (template) | Template section 1 |
| O22 | New dependencies: none or with rationale (template) | Template section 2 |
| O23 | Verification commands under repository policy, reuse of results (template) | Template section 6 (unchanged) |
| O24 | DoD: every story and scenario has a path; non-goals out; inapplicable sections omitted (4) | 4. Completion, item 1 |
| O25 | DoD: skeleton marker removed, `not-skeleton(plan.md)`, next `spec-tasks` (4) | 4. Completion, items 2-3 |

Dropped entries: 0.

## 2. Behavior Comparison (AC-09)

Method: three dry-run scenarios (S1 feature with a CLI flag, S2 feature breaking an architecture MUST, S3 bugfix
without `plan.md` that finds a wider defect). Each run was a fresh agent context given only the skill text and the
scenario; skill copies were named by run ID so neither runner nor grader knew the version. The expected-behavior
lists (S1: 11, S2: 9, S3: 8 items) were fixed before any output was read. A separate agent graded each output.

| Scenario | Old text | New text | Unmet items |
| --- | --- | --- | --- |
| S1 | 10/11 | 11/11 | Old: cited a capability by Markdown path (S1-E6) |
| S2 | 9/9 | 9/9 | None |
| S3, round 1 | 8/8 | 7/8 | New: referred to the unit's spec as `spec.md` (S3-E8) |
| S3, rerun | 6/8 | 7/8 | Both: a read command with the unit's spec path (S3-E8); old: no named preservation check (S3-E5) |

- Round 1 failed AC-09 in S3. Both texts held the same ID-citation directive, and the old text missed the same
  directive in S1, so the miss is run variance; following the plan, the new text's directive now names the unit's
  own spec, and S3 was rerun for both versions. The rerun meets AC-09 (new 7 ≥ old 6).
- The rerun grader counted a path inside a read command as a citation, which round 1 did not; S3-E8 is the least
  reliable item.
- Result: no regression and no measurable improvement (all runs: old 33/38, new 34/38). Size: 5107 to 5065 bytes.
  One run per version and scenario cannot separate small differences; the rollout spec needs more runs per scenario.
