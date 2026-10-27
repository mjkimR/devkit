# Author self-review of PROP-automatic-scope-collection

This is a source-backed review of a Backlog draft, not independent Planning acceptance. No runtime implementation,
remote observation experiment or performance measurement was performed. The operational contract and Planning evidence settle the design findings below; runtime verification remains Development work.

## Source evidence and findings

Source paths below are relative to `packages/devkit-spec/src/devkit_spec/` unless otherwise stated.

| Finding | Source evidence and failure condition | Disposition |
| --- | --- | --- |
| Creation registration already exists | `features/delivery/usecases/handoff.py` and `specs.py` call `auto_register`; `features/scope/usecases/flow.py` limits it to linked worktrees. | Retain both paths and linked-worktree eligibility. A base or isolated checkout does not gain registration. |
| Initial scope is incomplete | `features/scope/usecases/inputs.py:from_spec` marks skeleton tasks unresolved and uses target entrypoints as candidates until code boundaries exist. | Retain initial evidence without claiming completed scope. Host live collection supplies later observable evidence. |
| Worker guidance publishes scope | Source skills `spec-tasks`, `spec-sync` and `spec-delegate/references/worker.md` require `scope update`. | Remove publication/registration/ACK duties. Hidden maintenance invocation remains available to operators. |
| Stored query is not live collection | `features/scope/usecases/query.py:QueryScopesUseCase` compares stored records; `--spec` reads only the supplied local declaration. | Provide a distinct explicit Host operation; preserve current query/history/compare meanings. |
| Inputs are checkout-oriented | `features/scope/usecases/inputs.py:from_spec` reads files through `Path`; `observe_git` observes the execution checkout. | Settled in section 3.6; Development verifies: introduce pinned-ref declaration inputs and suitable base semantics without misattributing the Host checkout. |
| Branch inventory has reusable precedents | `features/policy/repositories/branches.py` enumerates planning refs; `packages/devkit/src/devkit_agt/features/worktree/usecases/stale.py` enumerates local/remote refs. | Settled in section 3.6; Development verifies: validate development/activity candidate discovery and lifecycle classification. Do not treat ref existence as proof of active work or import higher application layers. |
| Registry is not distributed discovery | CAP-COLL-work-scope-registry uses Git common-directory storage and classifies other-host records as unverifiable. | Explicit remote boundary: no automatic snapshot sharing across clones; other-PC dirty/unpushed work stays invisible. |
| Local and remote sources can disagree | The same named branch can have different tips; worktree dirtiness is independent of HEAD identity. | Settled in section 3.6; Development verifies: merge only confirmed identities, preserve divergence and dirty layers, and define source precedence. |
| Partial observation can resemble independence | Inaccessible paths, shallow history, missing refs and deadlines limit observable scope. | Settled in section 3.6; Development verifies: explicit coverage/provenance, stable codes and finite budgets; never translate unknown inputs into zero overlap. |
| Automatic creation currently asks for repair | `features/scope/usecases/flow.py:auto_register` returns `SPEC_SCOPE_REGISTER_FAILED` with a worker-side registration directive. | Q5/AC-01 require silent best-effort creation failures, verbose diagnostics and no replacement worker recovery duty. Explicit Host/maintenance errors remain visible. |
| Click hiding alone may not cover discovery | `features/scope/cli/commands.py` exposes `update` and its ACK; generated discovery needs separate inspection. | Settled in section 3.6; AC-02 verifies: verify ordinary and generated discovery plus direct maintenance invocation. |
| Accepted refresh decision needs replacement | ADR-worktrees-branches-and-scope assigns updates to skills and retains linked-worktree participation/storage. | Require a PADR replacing only the affected maintenance decision; retain ownership/storage/cleanup. |

## Design consistency review

- The proposal has no worker refresh or `workflow next` collection trigger. The harness needs no runtime extension.
- Standalone registration/recovery and workflow-boundary timing experiments are outside this direction.
- Host observation is invocation-local and needs no worker token or registry mutation.
- `snapshot`, `refs` and `worktrees` select observation inputs; fetch is explicit and separate. Snapshot-plus-fetch
  is rejected. Illustrative CLI spelling remains subject to Planning.
- Creation failures are silent best effort. Explicit Host partial results and failures retain the advisory contract.
- Source timestamps, pinned commits, missing layers and divergent refs prevent fallback evidence appearing current.
- Cross-PC handoff snapshot sharing assumes a future cloud-backed registry repository, such as Firestore, with
  shared identity, credentials and publication/ownership contracts. This draft records that direction without
  implementing an adapter or extending registration eligibility. It cannot expose later private changes.
- Initial handoff helps only where its snapshot or committed declarations are available to the Host. PR guidance
  improves published-change visibility without promising private worktree observation.

## Review judgment and verification scope

The Planning contract settles inventory/active-work criteria, source reading, attribution, observation
reconciliation, output contracts and budgets. `materials/planning-evidence.md` records source and experimental
support; Challenger findings and their verification are recorded separately. Runtime discovery, deadlines and
failure-isolation checks remain Development acceptance work. They do not justify adding worker duties.

This Backlog edit validates proposal consistency and document governance. AC-01 through AC-08 describe future
Planning/Development evidence; none are claimed as runtime checks passed by this document.
