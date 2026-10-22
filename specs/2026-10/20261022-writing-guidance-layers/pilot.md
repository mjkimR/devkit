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
lists below were fixed before any output was read; a separate agent graded each output item by item.

Text revisions: "first text" is the rewrite before review; "final text" is the shipped text, whose only change is
the ID-citation directive naming the unit's own spec (`SKILL.md` section 3, item 4).

### S1

| Item | Expected behavior | Old (r4) | New, first text (r1) | New, final text (r9) |
| --- | --- | --- | --- | --- |
| S1-E1 | Checks accepted ADRs with `devkit spec search "<topic>" --kind decision` (or equivalent search scoped to decisions). | met | met | met |
| S1-E2 | Checks what depends on `CAP-APP-export` with `devkit spec refs CAP-APP-export --direction in`. | met | met | met |
| S1-E3 | Consults `docs/architecture/` for module boundaries or constraints. | met | met | met |
| S1-E4 | plan.md keeps frontmatter `id: PLAN-export-dry-run` and `spec: SPEC-export-dry-run`. | met | met | met |
| S1-E5 | plan.md omits the storage/state section (no "N/A" placeholder section). | met | met | met |
| S1-E6 | plan.md cites Living Spec documents by full ID in backticks, not by Markdown path. | **unmet** | met | met |
| S1-E7 | plan.md maps each of AC-01, AC-02, AC-03 to a handling component. | met | met | met |
| S1-E8 | The interactive confirmation non-goal is not planned. | met | met | met |
| S1-E9 | The verification section names validation commands (affected tests, lint/type/governance checks). | met | met | met |
| S1-E10 | plan.md specifies the CLI contract: the flag, exit codes 0 and 2, and `EXPORT_FLAGS_CONFLICT`. | met | met | met |
| S1-E11 | Removes the `<!-- devkit:skeleton -->` marker and names `spec-tasks` as the next step. | met | met | met |
| Total | | 10/11 | 11/11 | 11/11 |

### S2

| Item | Expected behavior | Old (r2) | New, first text (r6) | New, final text (r10) |
| --- | --- | --- | --- | --- |
| S2-E1 | Identifies the conflict with the architecture MUST ("core MUST NOT write outside the workspace root"). | met | met | met |
| S2-E2 | Proposes a new ADR at `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`. | met | met | met |
| S2-E3 | Gives the ADR the ID form `ADR-<slug>`. | met | met | met |
| S2-E4 | Uses the template `.devkit/managed/spec/templates/decision.md`. | met | met | met |
| S2-E5 | States the reason for the rule change in the ADR proposal. | met | met | met |
| S2-E6 | Lists the conflict in plan section 1 together with the ADR it needs. | met | met | met |
| S2-E7 | Checks accepted ADRs (`devkit spec search ... --kind decision`) and/or `devkit spec refs CAP-GOV-rules-engine --direction in`. | met | met | met |
| S2-E8 | Covers failure modes (for example a stale or corrupt cache) in the plan. | met | met | met |
| S2-E9 | Removes the skeleton marker and names `spec-tasks` as the next step. | met | met | met |
| Total | | 9/9 | 9/9 | 9/9 |

### S3

| Item | Expected behavior | Old, round 1 (r5) | New, first text, round 1 (r3) | Old, rerun (r7) | New, final text, rerun (r8) |
| --- | --- | --- | --- | --- | --- |
| S3-E1 | Creates `plan.md` (does not expect a skeleton). | met | met | met | met |
| S3-E2 | Frontmatter `id: PLAN-sync-drops-mode`. | met | met | met | met |
| S3-E3 | Frontmatter `spec: SPEC-sync-drops-mode`. | met | met | met | met |
| S3-E4 | Keeps `test_preserves_exec_bit` as the regression test. | met | met | met | met |
| S3-E5 | Names checks covering the preserved behavior (other sync behavior that must not change). | met | met | **unmet** | met |
| S3-E6 | Treats the symlink finding as a different defect scope within the agreed expected behavior and returns to `characterize` (instead of silently widening the fix or asking the user). | met | met | met | met |
| S3-E7 | Runs an invariant pre-flight (ADR search or `devkit spec refs CAP-DIST-sync-and-transactions --direction in`). | met | met | met | met |
| S3-E8 | Cites documents by full ID, not by Markdown path. | met | **unmet** | **unmet** | **unmet** |
| Total | | 8/8 | 7/8 | 6/8 | 7/8 |

### Outcome

- Final text against old text: S1 11/11 vs 10/11, S2 9/9 vs 9/9, S3 7/8 vs 6/8 (rerun). AC-09 holds for the
  shipped text in each scenario.
- Round 1 of S3 failed AC-09 with the first text (7/8 vs 8/8). Both texts held the same ID-citation directive and
  the old text missed it in S1, so the miss is run variance; following the plan, the directive was tightened and S3
  was rerun for both versions, and S1 and S2 were rerun with the final text after review.
- The S3 rerun grader counted a path inside a read command as a citation, which the round-1 grader did not; S3-E8
  is the least reliable item, and it is the only item the final text missed.
- The pilot shows no regression and no measurable improvement; one run per version and scenario cannot separate
  small differences, so the rollout spec needs several runs per scenario. Size: 5107 to 5065 bytes.
