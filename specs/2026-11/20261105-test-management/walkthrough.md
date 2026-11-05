# Author-led procedure walkthrough

## Method and limits

Read the shipped router and conditional references, then followed their decision paths against source/configuration
inputs below. These are author-led, source-driven walkthroughs, not application test execution, an agent-model
benchmark or performance evidence. Expected and observed actions below refer to this walkthrough only.
No consumer configuration was changed. No collection hooks, DB services or browser flows were executed.

## Scenarios

| Case / requirements | Input and expected action | Observed action / evidence | Result |
| --- | --- | --- | --- |
| Prerequisites / AC-02 | Unknown collection hook and shared database: inspect before collection; unresolved resource must stop that command | Followed router Constraints and step 1.4, then assessment section 2; identified collection as executable, kept DB command not_run pending disposable input | PASS procedural walkthrough; no hook executed |
| Unattended / AC-03 | Proposed worker default without user decision: produce decision-round report and edit nothing | Router entry and step 3.2 leave candidate pending; recorded proposed scope rather than applying it | PASS; no consumer edits |
| Approved candidate / AC-03 | User approves a bounded recipe edit: preserve native review/integration gates | Step 3.3 routes exact scope and checks through native workflow; no separate CI/branch change inferred | PASS simulated routing; no actual work item created |
| Devkit / AC-04 | Existing package tiers, affected selector, frontend instruction and landed-head checks | Read assessment contract and native scripts; kept selector full fallback/data-triggered e2e exceptions and saved-base final HEAD checks, with viewer checks separate | PASS source-driven; native locations in repository-assessment material |
| Auto Hub / AC-04 | SQLite workers, serial unit/shared PostgreSQL, SDK/UI/isolated SDD and manual CI | Kept native runner settings; distinguished SQLite from PostgreSQL/migrations and marked SDD prerequisites not_run; manual trigger was not a claimed CI pass | PASS source-driven; no DB/CI invocation |
| Resource Indexer / AC-02, AC-04 | Marker fast suite can need sockets; serial full gate includes Python/Go/web | Preserved markers and serial check; left optional parallel recipe optional, no unconditional fast-suite completion; identified async socket prerequisites outside server tier | PASS source-driven; no application checks executed |
| Non-pytest example / AC-04 | Labelled package scripts define npm test and npm run check | Followed router step 2.3 and assessment example, retained native commands and skipped pytest reference | PASS labelled synthetic example; no npm execution |
| Tuning mismatch / AC-05 | Serial and parallel exit 0, but collected identities/skips differ | Followed pytest comparison step 3; rejected equivalence and default promotion despite faster elapsed time | PASS labelled synthetic comparison; no performance claim |
| Inconclusive tuning / AC-05 | Missing resource prerequisites or noisy samples | Kept current command, reported missing evidence not_run; no fixed worker/time threshold inferred | PASS procedural walkthrough |

## Coverage mapping

AC-01 uses executable sync/search/retrieval integration tests (selected testing/all, existing presets, unselected).
AC-02 through AC-05 use the cases above. AC-06 combines real deployment/reference-budget checks with these
procedural observations; string presence alone cannot validate agent behavior. The two references are linked
with explicit before/when conditions; only the pytest branch applies to a pytest consumer.

The repository assessment under `docs/materials/2026-11/20261105-test-management/` pins the inspected application
revisions and source locations. Its historical timings are not reused as current benchmark results.
