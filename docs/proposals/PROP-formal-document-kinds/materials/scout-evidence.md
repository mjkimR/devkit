# Scout evidence and boundary verification

Read-only nested Scout inspected HEAD c8ef8ba1e71c3bbe6423052e3e28a4874efecf0a, base
bde0a923192aaea7f6a467bb6a575db4ca447f9e. Caller frozen all author writes and HEAD during its run and supplemental
return. Before and after complete temporary-index snapshot tree was ca60f585836c42fb3005bc9eb02267ab671cce45;
HEAD unchanged and real worktree/index clean. Emulated isolation only; this comparison is the substitute measure,
not a native guarantee. Scout reported no reads outside this worktree.

## Incoming-reference stages and bounded body coverage

Scout began with `docs refs <ID> --direction in -n 0` (initially paged ownership/ADR queries were fully fetched).
All result pages were inspected; counts are returned source rows per target, not distinct sources across targets.

| Target | Returned source rows |
| --- | ---: |
| `CAP-DOCS-document-model` | 127 |
| `CAP-DOCS-documentation-ownership` | 7 |
| `CAP-DOCS-document-lookup` | 49 |
| `CAP-DOCS-document-search` | 28 |
| `CAP-DOCS-namespaces` | 35 |
| `CAP-DIST-sync-and-transactions` | 92 |
| `CAP-DLV-proposal-lifecycle` | 23 |
| `ADR-documentation-ownership-and-linked-design-entries` | 7 |
| `ADR-linked-domain-relationship-views` | 6 |
| Total target/source rows | 374 |

Body inspection was bounded to those seven CAPs and two ADRs, ARCH-05-2-components, architecture.toml, proposal/
target/audit, glossary, four canonical role docs, current design template and relevant parser/model/governance/
bundle source. Output of one large body batch was truncated; neither Scout nor caller claims every returned
source body was read. Historical design/domain evidence and materials README were sampled only. The caller also
read the preserved operations source body. No lifecycle/viewer code or runtime implementation tests were delegated
to Scout. Supplemental early neutral entrypoint/schema owners CAP-TRACE-code-entrypoints and CAP-GOV-spec-rules
are inspected by caller and included in the pre-Challenger reference addendum.

## Exact inspected facts

- `models/kinds.py:25,64,303`: enum/explicit definitions/coverage and unique prefix+relation checks.
- `models/model.py:12-17`: separate list/scalar fields and provenance; aliases identity only. Own current ID is
  forbidden in aliases (`models/parse.py:64-85`), correcting an ambiguous Scout phrase.
- `id_convention.py:301`: explicit Living Spec grammars; full prefixed filename is required by selected contract,
  correcting Scout's shorthand `<slug>.md`.
- `spec_format.py:189-193`: table-derived scope; new strict status/reserved-field behavior must be implemented.
- `cli/commands.py:192,241`: dynamic choices but manual help text; generic selection is not test proof.
- `entrypoint_paths.py:31`: existing shared definition-based API; DESIGN optional path anchors have semantic use.
- `bundle/bundle.toml:8-53,124-155`, integration `test_distribution.py:47-58` and E2E
  `test_installed_consumer.py:32-67`: registrations, selections and exact inventories must change.
- `ARCH-05-2-components:145-150`, `.devkit/architecture.toml:101-103`: core docs ownership and no docs-to-spec edge;
  no new feature edge needed for selected model/governance changes.

Exactly four current canonical role files exist: two designs including nested detail and two domain entries.
`docs/operations/`, `docs/packages/` and registered docs namespaces are absent at inspected HEAD. Namespace behavior
therefore needs real registered fixtures in Development, not a claim from current repository data.

Current ingress is glossary lines 16/48, distribution capability lines 114/370 and delivery lifecycle capability
line 43. Source living-spec-writing lines 33-48 and design-template lines 1-17 prescribe the ID-free form. The
archived operations input is under this proposal's materials, never a current main file. Full migration and
historical-path ingress closure is specified in the target blueprint.

No runtime/test behavior is verified by this audit. The selected contract intentionally differs from Scout's
initial no-terminal/all-entrypoints-false suggestion: strict retired semantics and DESIGN optional source anchors
are explicit choices in core-contract §8, with new governance/query tests required.

## Added neutral owners before Challenger

Caller ran complete incoming-ref queries for CAP-TRACE-code-entrypoints (42 source rows) and CAP-GOV-spec-rules
(90 source rows) at ca386097a6fc4f7600acf5e9a9bc7253d5cc3b6d. Bounded metadata aggregation avoided treating
truncated console bodies as full inspection. TRACE status counts: accepted 1, active 8, promoted 1, dismissed 1,
empty 8, draft 2, planned 1, resolved 10, completed 10. GOV: accepted 11, active 10, resolved 24, done 1, empty 13,
draft 8, completed 23. Body reads covered the two capabilities and relevant current model/lookup/namespace/rule
contracts; the full returned source bodies were not read. Those current contracts are in the exact target scope;
other callers retain generic path/rule contracts unchanged. Completed Unit children with empty status are not
asserted current merely because their frontmatter status is blank. `docs list spec --limit 0` returned zero current
specs and 249 hidden historical specs. Counts are inspection inputs, not test counts or distinct-source claims.

The source/path ingress sweep and exact historical preservation paths are in target-docs §3. No external source
was needed. The pre-existing missing PATH guesses during caller reads were corrected using rg discovery; no source
content was inferred from nonexistent files.

## Challenger round 1 and fix batch

Nested Challenger reviewed whole selected bundle at 440302f0163f695ba3acb315ea1503890ec2c417. Before/after complete
tree 6ddc5f02dbb380adc607fddd3d124af19071fb29, unchanged HEAD and clean real index/worktree verified; no outside-tree
reads reported. It found two P2 maintenance composition gaps, recorded in challenger-01. The batch specifies
artifact-carrying rename/root move/split/cross-kind transfer with ordinary-link repair, and continuing retired-node
governance with source-deletion entrypoint cleanup. Target matrix adds composed fixtures. Flat layout rationale
also names subject-qualified globally unique slugs and package-move/alias policy. These strengthen the contract,
so a fresh HIGH Challenger round is required; this is not minor-fix self-verification.

## Final Planning verification

Fresh Challenger round 2 reviewed 440302f0163f695ba3acb315ea1503890ec2c417..504e2e12006ab3e2aad2b8ce470607646ad4c4ac
and all affected contract meaning. It returned no findings. Caller verified the full pre/post temporary-index tree
16507f7f9f0cceed2fa5c95755aebe5de8937292, unchanged HEAD and clean real worktree/index; no outside-tree reads reported.
Round 1's two P2 findings are resolved by reverify-01; round 2 is challenger-02. Scout's four recorded source
observations are incorporated in core-contract §§1–8 and target-docs §§1–5; they are future implementation
obligations, not unresolved Planning choices. No unresolved user question or execution problem remains.

Native scoped proposal rules: PASS 22 rules, errors=0 warnings=0. Exact proposal.md boundary check: PASS, no
RULE-proposal-boundaries reports. Envelope check: blocked=false, pending_questions=[], malformed_workers=[],
errors=[]. Workflow after feedback: direction-handoff, plan-accept ask pending; worker never records acceptance.
`git diff --check` against bde0a923192aaea7f6a467bb6a575db4ca447f9e passes. Native Backlog `spec proposal check
formal-document-kinds` returns exit 1 SPEC_PROPOSAL_IN_PLANNING as expected for reviewing on its Planning branch;
it is a mutability refusal, not a Planning validation pass, and was not bypassed. Its refusal stops that command
only; the assigned Planning remains authorized. Feedback sweep covers this run (repo and upstream), no new
observations. Initial commit gate rejected one abbreviated architecture ID; it was corrected and the normal gate
passed. No approval operation was refused or rerouted.

All tracked changes are inside this proposal. No current source/runtime/canonical docs were modified and no code
unit/integration/E2E/lint/type tests are claimed. Required F1–F6, built-wheel consumer, all migrations and dependent
L1–L4/V1–V4 tests are Development obligations. The selected complete core contract remains one L unit; mandatory
lifecycle/viewer scope is separately owned, not dropped to shrink implementation. No UX screens are drafted by
this core Planning turn. The sole final worker records HIGH effort and these limits; the proposal stays reviewing.
