# Discovery evidence

Planning evidence for `PROP-spec-playbook-discovery`, collected in the Planning worktree at base `3137814f`.

## 1. Search probe (Q4)

`uv run devkit playbook search "<query>"` with the defaults (`limit=5`, `max_bytes=8192`, `mode=auto`, which resolved
to `hybrid` here). Four playbooks were synchronized: `spec/brownfield-adoption`, `spec/feedback-hygiene`,
`spec/adr-compaction` and `authoring/skill-authoring`.

| Query (representative task) | Relevant playbook | Bytes | Hybrid candidates (score) |
| --- | --- | --- | --- |
| adopt devkit in an existing repository | brownfield-adoption | 1809 | brownfield-adoption 0.033, skill-authoring 0.016, feedback-hygiene 0.016 |
| clean up open feedback | feedback-hygiene | 685 | feedback-hygiene 0.033 |
| compact ADR ledger | adr-compaction | 564 | adr-compaction 0.033 |
| reconcile living spec drift | none synchronized (catalog not selected) | 1305 | brownfield-adoption 0.033, feedback-hygiene 0.016 |
| add pagination to the viewer dashboard | none | 1784 | feedback-hygiene, adr-compaction, brownfield-adoption, each 0.016 |
| fix failing test in sync | none | 1302 | feedback-hygiene, brownfield-adoption, each 0.016 |
| review and refactor accumulated AI slop | none synchronized | 1810 | feedback-hygiene, brownfield-adoption, skill-authoring, each 0.016 |
| write a weekly report | none synchronized | 592 | skill-authoring 0.016 |

Per-mode check on three of the queries:

| Query | `--mode lexical` | `--mode dense` |
| --- | --- | --- |
| add pagination to the viewer dashboard | 3 candidates (1.41, 0.57, 0.47) | none |
| fix failing test in sync | 2 candidates (0.63, 0.61) | none |
| adopt devkit in an existing repository | 3 candidates (5.47, 0.76, 0.63) | brownfield-adoption 0.57 |

Findings:

- Cost is bounded: one search returned 564 to 1810 bytes at `limit=5`, about 360 bytes per candidate, never
  truncated. `limit=3` caps one discovery at about 1.2 KB of candidate metadata plus the envelope.
- Every relevant playbook ranked first. False positives are the problem, not misses: `hybrid` and `lexical` return
  candidates for unrelated tasks, and a hybrid score (reciprocal rank fusion) only shows whether a candidate was
  ranked by one or both rankers. A wrong match ("reconcile living spec drift" ranked brownfield-adoption at 0.033)
  scores like a right one.
- `dense` with the default `min_similarity=0.35` gave clean no-match results, but it needs the search extra, which a
  consumer may not install; lexical-only consumers always see noise.
- The selection must therefore rest on whether a candidate's `description` names the requested operation, never on
  its score, and the no-match path must be the ordinary result. Ranking changes stay a non-goal.

### Paraphrase probe (after the challenger round)

`--limit 3`, `hybrid` and `lexical` agree on the first candidate in every row.

| Query | First candidate (hybrid, lexical) | Note |
| --- | --- | --- |
| clean up old decisions | feedback-hygiene (0.033, 1.09) | user paraphrase: `adr-compaction` absent |
| tidy up old ADRs | adr-compaction (0.033, 1.94) | canonical noun "ADR" restores the match |
| consolidate ADR documents | adr-compaction (0.033, 2.86) | |
| triage open feedback files | feedback-hygiene (0.033, 4.39) | |
| adopt spec-driven development in an existing repository | brownfield-adoption (0.033, 7.61) | |

Misses come from paraphrase, not ranking: writing the query with canonical artifact nouns closes them without a
ranking change. Note that the `brownfield-adoption` positive arises through explicit discovery or exact retrieval, not
`spec` intake, in a repository that does not yet have `devkit-spec`.

## 2. Current explicit-only contract (Q3 and reconciliation inventory)

The explicit-only restriction is stated in these sources (base `3137814f`):

- Accepted decision: `ADR-external-playbook-execution` §4 "Ordinary requests do not authorize discovery." Reversing
  it needs a new ADR that supersedes it and restates its retained exact-retrieval and external-execution decision.
- Accepted decision: `ADR-immutable-decisions-editable-records` §4 "Compaction": a compaction runs when the user
  explicitly invokes the `adr-compaction` playbook, which authorizes its deletions, at `session` depth.
- Accepted decision: `ADR-playbook-aliases-as-identifiers`: aliases are never searched; unaffected by discovery.
- Generated skill: `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/playbook_skill.py`
  (`NAME = "devkit-playbook"`, `disable-model-invocation`, Codex `allow_implicit_invocation: false`), wired through
  `GENERATED_SKILLS` in `services/installation/inventory.py`, reserved in `services/bundles/manifest.py`
  (`RESERVED_SKILL_IDS`) and listed in `services/installation/guidance_block.py`.
- CLI help: `features/distribution/cli/playbooks.py` group docstring ("after explicit devkit-playbook invocation").
- `spec` skill constraint: `skills/spec/SKILL.md.jinja` "Do not search or route to playbooks from `spec`".
- `spec-next` skill: recommends `/devkit-playbook` for feedback hygiene.
- devkit bundle constitution: `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/AGENTS.md`.
- Spec seed: `bundle/seed/docs/README.md`; spec `bundle.toml` playbook comment.
- Playbook bodies whose prerequisites assume a user request: `brownfield-adoption` ("The user asked for this
  playbook"), `feedback-hygiene` ("only in a hygiene session the user asks for"), `adr-compaction` ("only when the
  user asks for it"), catalog `drift-reconciliation` and `weekly-report` ("only on explicit invocation through
  `devkit-playbook`").
- Living Spec: `CAP-DIST-context-and-playbooks` §1, §3 and §5, `ARCH-08-2-resource-taxonomy` (`package-playbook`
  entry conditions and the consumption table), `ARCH-08-cross-cutting`, `CAP-HARN-agent-guidance`,
  `CAP-DIST-agent-projections`, `CAP-DIST-content-packages`, `CAP-DIST-manifest-spec`,
  `CAP-DLV-workflow-orchestration`, `CAP-DLV-drift-reconciliation`, `CAP-DLV-weekly-report`,
  `UC-reconcile-living-spec-drift`, `UC-inspect-weekly-repository-progress`.
- Consumer-facing: `guides/install/new-repository.md` (generated skill paths), `packages/devkit-catalog/README.md`.
- Tests naming the generated skill: `packages/devkit-dist/tests/integration/features/distribution/`
  (`test_playbooks.py`, `test_guidance_block.py`, `test_guide_bundle.py`, `test_workflows.py`); the
  `skill_document_size` rule test uses the path only as fixture data.

Roadmap milestones and dated materials mention the old entry point as history and are not reconciled.

## 3. Interaction with `PROP-review-refactor`

`PROP-review-refactor` (Planning in parallel) adds a third `maintenance` playbook and owns
`packages/devkit-catalog/src/devkit_catalog/maintenance/` and `docs/capabilities/delivery/`, which this proposal also
needs for the entry-condition wording of the existing maintenance playbooks. Its new playbook must state its entry
condition in the form this proposal settles, and its `description` must name the operation (review and refactoring
of accumulated slop) so discovery can select it; the probe above shows that today no synchronized playbook matches
that request. Whichever lands second reconciles the other's wording.
