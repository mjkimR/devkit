---
reconcile_id: REC-spec-playbook-discovery
status: pending
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-weekly-report.md
    resolution: modified
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/architecture/ARCH-08-cross-cutting.md
    resolution: modified
  - file: docs/usecases/governance/UC-reconcile-living-spec-drift.md
    resolution: modified
  - file: docs/usecases/governance/UC-inspect-weekly-repository-progress.md
    resolution: modified
  - file: docs/decisions/2026-10/20261021-external-playbook-execution.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-immutable-decisions-editable-records.md
    resolution: modified
---

# Reconciliation: Task-aware playbook discovery through spec

The Living Spec now states the delivered contract of `SPEC-spec-playbook-discovery` under
`ADR-spec-intake-playbook-discovery`:

- `CAP-HARN-agent-guidance`: §3 principle 7 replaces "Playbooks on request only" with the intake step (trigger, skip
  cases, conversation stops, one `--limit 3 --max-bytes 4096` search, the operation-not-topic selection rule, the
  one-line confirm-first offer, silent no-match and errors, the reference read only on a match, no `spec-playbook`
  skill); the `spec` skill row and the skill reference list name the step and `spec/references/playbooks.md`; the
  `spec-pointer` paragraph states the intake clause the fragment now carries.
- `CAP-DIST-context-and-playbooks`: §1 adds an entry skill's bounded intake search as a search trigger whose
  candidate runs only after confirmation; §3 says the draft offer belongs to explicit discovery and the generated skill
  names no other bundle's asset; §5 replaces "Ordinary task wording never authorizes catalog discovery" with the
  confirmed-offer rule.
- `ARCH-08-2-resource-taxonomy`: `package-playbook` gains entry condition 4 (confirmed intake offer, `devkit-dist`
  neutral); the consumption table, the per-task invocation paragraph, the entry-point contract (draft offer for
  explicit discovery only) and the open item are aligned. `ARCH-08-cross-cutting` lists the intake offer.
- `CAP-DLV-drift-reconciliation`, `CAP-DLV-weekly-report`, `CAP-DIST-content-packages`,
  `UC-reconcile-living-spec-drift` and `UC-inspect-weekly-repository-progress` add the confirmed intake offer to the
  explicit invocation paths of the maintenance playbooks, matching their new "invoked or confirmed" entry wording.
- `ADR-external-playbook-execution` §4 and §5 and `ADR-immutable-decisions-editable-records` §4 get the one-line
  pointers to `ADR-spec-intake-playbook-discovery` that its outcome requires; no other statement of them changes.

No other Living Spec document changes:

- `CAP-SRCH-document-search` and the search engine are unchanged: no ranking, option or default changed.
- `ADR-playbook-aliases-as-identifiers` is unaffected; intake searches name and description only.
- `CAP-DIST-agent-projections` and `CAP-DIST-manifest-spec` describe the generated skill's projection and the reserved
  ID, which did not change. `guides/install/` names only the generated skill paths, which did not change.
- Dated materials, completed specs and roadmap milestones that name the old entry rule are history.

Deferred work: `UC-route-development-intent` (`docs/usecases/delivery/`, outside this run's write scope) still goes
from entering the `spec` skill to classification without the intake step; tracked as
`FB-route-intent-intake-discovery`.

Entrypoints: no new capability or use case; the touched capabilities' `entrypoints` already name the changed files'
doorways (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/` for `CAP-HARN-agent-guidance`, the playbook
use cases for `CAP-DIST-context-and-playbooks`), so none is added.

No source feedback.
