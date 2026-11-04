# Internal contracts and constraints for PROP-maintenance-history

Scope: repository evidence only, at worktree head `c0d060b7` (branch `plan-maintenance-history`). The proposal is `docs/proposals/PROP-maintenance-history/proposal.md`. Citations are `path:line`, with paths relative to the worktree root. Shorthand used below:

- `PB` = `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/`
- `CAP-DLV-*`, `CAP-COLL-*`, `ADR-*`, `UC-*`, `FB-*`, `MS-*` are document IDs; `devkit docs resolve <ID>` gives their paths (each resolved in this pass).

## 1. Touched contracts

### 1.1 Incoming references (`devkit docs refs <ID> --direction in -n 0`)

| Document (status) | Incoming refs | Referrers that matter for this design |
| --- | --- | --- |
| `CAP-COLL-shared-artifacts` (active) | 8 | `FB-remote-shared-adapter-follow-up` (dismissed), `SPEC-maintenance-history`, `CAP-MCP-runtime-registration`, `CAP-INT-mcp-services`, `CAP-HARN-agent-guidance`, `CAP-DIST-sync-and-transactions`, `PLAN-cli-host-lifecycle`, `SPEC-cli-host-lifecycle` (completed) |
| `CAP-DLV-weekly-report` (active) | 10 | `UC-publish-a-weekly-report`, `UC-inspect-weekly-repository-progress`, `SPEC-weekly-report` (completed), `SPEC-release-handbook` (completed), `REC-feedback-dedup-and-compaction` (resolved) |
| `CAP-DLV-drift-reconciliation` (active) | 12 | `CAP-DLV-review-refactor`, `UC-reconcile-living-spec-drift`, `SPEC-spec-playbook-discovery`, `PROP-incubation-sdd-baseline-target` (draft) |
| `CAP-DLV-review-refactor` (active) | 12 | `ADR-review-refactor-application` (accepted), `CAP-DLV-performance-pass`, `UC-review-and-refactor-accumulated-slop`, `SPEC-review-refactor-lessons`, `SPEC-review-refactor` |
| `CAP-DLV-performance-pass` (active) | 5 | `CAP-DLV-review-refactor`, `UC-speed-up-selected-slow-operations`, `FB-compacted-delivery-dismissed` |
| `ARCH-08-1-agent-output` (active) | 37 | `CAP-ADV-agent-advisory-protocol`, `CAP-CLI-agent-cli-toolkit`, `ADR-document-system`, `SPEC-maintenance-history`, `ARCH-05-2-components` |
| `CAP-ADV-agent-advisory-protocol` (active) | 28 | `ARCH-08-1-agent-output`, `CAP-CLI-agent-cli-toolkit`, `SPEC-maintenance-history`, `CAP-DLV-cli-and-output` |
| `ADR-mcp-runtime-and-shared-artifacts` (accepted) | 21 | `ADR-delivery-approval-and-lifecycle-authority`, `ADR-retire-native-approval-and-moved-ownership-clauses`, `CAP-COLL-shared-artifacts`, `CAP-DLV-weekly-report`, `PLAN-weekly-report`, `REC-weekly-report`, `SPEC-mcp-runtime-pending` (completed) |

Observation: `SPEC-maintenance-history` is an incoming reference of `CAP-COLL-shared-artifacts`, `ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol` and `ADR-mcp-runtime-and-shared-artifacts`. It is not an incoming reference of the four delivery capabilities whose playbooks it would change (`CAP-DLV-weekly-report`, `CAP-DLV-drift-reconciliation`, `CAP-DLV-review-refactor`, `CAP-DLV-performance-pass`). The proposal body cites them only by name in the Background, not by ID.

### 1.2 Clauses

Clause relation key: **R** = the history design would restate it; **E** = extend it; **C** = conflict with it (needs an ADR or a changed scope before Development).

#### Run ID

- `CAP-DLV-weekly-report` `docs/capabilities/delivery/CAP-DLV-weekly-report.md:72-74`: "Each run MUST have a unique ID and source SHA, and its artifact MUST be collision-checked and exclusively created. Reruns MUST name superseded runs and preserve earlier bytes." **R**
- `CAP-DLV-review-refactor` `:43`: "the playbook MUST record the run ID, repository identity, HEAD, dirty paths, prior reports and the report destination". **R**
- `CAP-DLV-performance-pass` `:49`: "the playbook MUST record the run ID, a credential-free repository identity, HEAD, dirty paths, prior reports, the report destination and the environment". **R**
- `CAP-DLV-drift-reconciliation` `:34-35`: intake MUST record repository identity, HEAD, dirty paths, contract IDs, roots, report destination and prior reports. **No run ID is required.** **E** (the drift playbook would gain a run ID; `PB/drift-reconciliation.md:14-16` has the same omission).
- `ADR-mcp-runtime-and-shared-artifacts` `:182-183`: "each generation gets a unique run ID and inspected revision. New content means a new run." **R**
- `CAP-COLL-shared-artifacts` `:26-27`: the identity is a server-generated UUID `generation_id`, plus the content digest. It has no run ID and no playbook identity. **E** (history records must not reuse `generation_id` as the run ID).

#### Run / outcome records

- `CAP-DLV-weekly-report` `:83-86`: "A separate local companion record MUST store run ID, artifact, digest, generation outcome, publication outcome, destination, authority, attempts and receipt/error evidence. It MUST preserve attempts and changes without altering the report. IF the companion is missing, THEN publication MUST be blocked; a missing companion MUST NOT erase a verified report." **R** (the proposal's record is this companion record, moved to a remote branch).
- `CAP-DLV-review-refactor` `:129-135`: the report is an ordinary local Markdown file; it records intake, coverage, findings, "changes as separate records", decisions with provenance, follow-ups, counts and the outcome. "A report written before its work item integrates has its outcome updated". **R/E**
- `CAP-DLV-drift-reconciliation` `:67-68`: the artifact "MUST contain intake, coverage, findings, decisions, corrections and completion evidence". `:59-63`: completion counts detected, resolved, deferred, waived and pending. **R**
- `CAP-DLV-performance-pass` `:166-175`: candidates and changes "as separate records"; outcome `stopped at decision round`, `applied` or `partially applied`. **R**
- `CAP-DLV-review-refactor` `:56`: "Subagents MUST NOT ask the user, approve a change or write the run's records." Any history writer is therefore a Host or CLI step, not a subagent step. **R**
- `ADR-mcp-runtime-and-shared-artifacts` summary `:4`: "keep reports immutable apart from scope and publication records". `:190-193`: "Record destination, authority, artifact digest and verified receipt separately." **R**

#### Intake identity (HEAD, dirty paths)

- `CAP-DLV-weekly-report` `:28-29`: "Intake MUST record credential-free repository identity, scope, inspected SHA, local integration ref and resolved SHA, generation timestamp and dirty state." `:36-37`: "explicitly selected uncommitted content MUST have a preserved diff/artifact reference." `:38-39`: "The playbook MUST recheck HEAD, integration ref and relevant dirty content after collection and before final verification." **R**
- `CAP-DLV-drift-reconciliation` `:39-40`: code/guidance citation "at the recorded revision (including dirty content)". `:56-58`: "IF HEAD or relevant dirty paths change before correction or final verification, THEN the playbook MUST revalidate evidence." **R**
- `CAP-DLV-performance-pass` `:78-80`: revalidation when "HEAD or a relevant dirty path moved since intake". **R**
- `CAP-DLV-review-refactor` `:43-44`: intake records HEAD and dirty paths. **R**
- `ADR-mcp-runtime-and-shared-artifacts` `:190-192`, `:216-217`: "consumers must retain exact artifact references and verify source commits". **R**

#### Report destination

- `CAP-DLV-weekly-report` `:70-72`: "The playbook MUST select a local location explicitly, defaulting to owning-unit materials or an existing repository materials location; otherwise it MUST resolve the location at invocation. It MUST NOT silently create a tracked report on the default branch." **R; the phrase "destination" is also used for publication (`:88-95`)** (see Glossary, section 5).
- `CAP-DLV-review-refactor` `:129-130`: "an ordinary local Markdown file under the owning unit's materials or the repository's materials location." `CAP-DLV-drift-reconciliation` `:67-68` and `CAP-DLV-performance-pass` `:166-167` use the same words. **R**
- `ADR-mcp-runtime-and-shared-artifacts` `:194-196`: "Artifact location and any external destination are invocation inputs, not fixed organization policy." **C** with the proposal's fixed default `maintenance-history` (`proposal.md:42`), unless the default is only a suggested input.

#### Publication outcomes

- `CAP-DLV-weekly-report` `:86-91`: exactly four states. "pending without destination, authority, publisher or permission; published only after verified destination receipt/link and matching content/run/digest; failed for confirmed failure; unknown for lost response or unverifiable destination." **R** (the proposal's "authentication, permission, conflict, rate-limit and lost-response failures", `proposal.md:55-56`, must map onto these four states; a fifth state would **C**.)
- `ADR-mcp-runtime-and-shared-artifacts` `:190-193`: "Unknown publication outcomes require checking the destination before retrying; an unverifiable outcome remains unknown." **R**
- `SPEC-weekly-report` `specs/2026-10/20261021-weekly-report/spec.md:70`: AC-07 repeats the four states. **R**
- `UC-publish-a-weekly-report` steps `:69-76`: lost response → `unknown`; inspection confirms absence → retry "with the same run ID and exact bytes". **R**

#### Authority for external publication

- `CAP-DLV-weekly-report` `:23-24`: "Publication MUST have separate authority." `:93-94`: "The playbook MUST use only an existing authorized connector/command for an explicitly user-selected destination. Invocation and integration policy MUST NOT authorize upload, message, commit, push or other external mutation." **C** with a design in which every playbook run writes its record to a remote branch by default (`proposal.md:45-47`, `:57-59`). A remote commit through `gh api` is an external mutation under this clause. The only compatible design is: destination selected per invocation, authority recorded, default `pending`.
- `CAP-DLV-weekly-report` `:96-98` and `:99`: a publication failure "MUST leave completed generation intact". **R**
- `ADR-mcp-runtime-and-shared-artifacts` `:194-196`: "It creates no standing publication permission." **C** with any standing default branch name in the proposal.
- `ADR-delivery-approval-and-lifecycle-authority` `:79`: "Keep publication and cloud mutation outside local authority." `:95`: "Local merge, pull-request policy, required checks and publication limits remain effective." `:99`: "proposal report publication retain their existing boundaries." `:211`: "no policy value grants new commit or publication authority." **R/C** (the same).
- `CAP-DLV-project-policy` `docs/capabilities/delivery/CAP-DLV-project-policy.md:44`: "Scope Excluded: granting commit, publication or host permission authority". **R**

#### Retries with the same run ID

- `CAP-DLV-weekly-report` `:96`: "A retry MUST retain run ID and exact bytes." `:96-98`: inspect unknown destination state first; "a matching receipt resolves published without resending; unverifiable stays unknown and requests disposition; confirmed absence permits retry within authority." **R**
- `PB/weekly-report.md:77-79`: same rule in playbook text. **R**
- `proposal.md:52`: "retrying the same run neither duplicates logical records nor silently replaces different content." **E**: "logical record" is not defined in any capability; the capability uses exact bytes plus digest. The proposal needs a definition of the logical key (playbook identity, repository identity, run ID, digest).
- `ADR-mcp-runtime-and-shared-artifacts` `:182-184`, `CAP-DLV-weekly-report` `:73` and `:81`: changed content is a new run; the same run never changes its bytes. **R**

#### What the shared artifact store must not do

- `CAP-COLL-shared-artifacts` `:33-36`: "A repeated live put MUST return the same original metadata without extending expiry ... The store MUST NOT provide indefinite tombstones, overwrite, release or arbitrary deletion operations."
- `CAP-COLL-shared-artifacts` `:73-75`: "Only an explicit apply MAY remove valid expired artifacts ... Logical expiry does not guarantee physical erasure after seven days."
- `CAP-COLL-shared-artifacts` `:17-22` and `:18-19`: "It stores regenerable reports and MUST NOT store scope records, tokens, ownership or approval authority."
- `CAP-DLV-weekly-report` `:74-75`: "No seven-day TTL or automatic history discovery applies." `SPEC-weekly-report:142`: "retention policy and a history backend remain separate work."
- `proposal.md:58-59` states that durable history is not subject to the TTL. This is consistent. The consequence is that the history branch must not be routed through `devkit_dist.features.shared`. `ADR-mcp-runtime-and-shared-artifacts:111-112` rejects a production remote artifact adapter for now, and `FB-remote-shared-adapter-follow-up` (dismissed) keeps it deferred until a concrete backend is needed. **C** if the history branch is implemented as a `SharedArtifactAdapter`.

#### Review-refactor and drift report/record requirements (quoted in full above)

- `CAP-DLV-review-refactor` `:127-135`: report location `:129-130`; components `:130-133`; "Completion applies to a batch with no pending decision; a batch never claims the whole repository" `:135`.
- `CAP-DLV-drift-reconciliation` `:59-63`: "IF any decision is pending, THEN the playbook MUST NOT claim the batch fully reconciled." `:65-71` report interface; `:69-71` seeded exercises "MUST label simulated decisions ... MUST NOT authorize a real source change."

#### Output and advisory clauses (for any history CLI or script)

- `ARCH-08-1-agent-output` `:16-18`: "Text output MUST be one fact per line ... Every condition worth reporting MUST have a stable UPPER_SNAKE code ... A condition the agent must act on MUST carry an [ACTION] directive." `:21`: "Libraries never print." `:63`: "under --format json ... stdout MUST be exactly one JSON object." `:75`: a failing command prints `{"error": {...}}`. **R**
- `CAP-ADV-agent-advisory-protocol` `:216-218`: `DEFER` covers "rate limits, external jobs still running, a lock another process holds". `:160-162`: `HALT` for "half-applied mutations, lock conflicts, possible state corruption". `:194-197`: `INTERACTION` for "ambiguous intent, drift that needs confirmation, destructive operations that need sign-off". `:284`: "A transport adapter never executes fix on the agent's behalf." **R/E**: the proposal does not say which advisory mode each publication outcome uses. Mapping rate-limit to `DEFER` and an `unknown` outcome to `HALT` or `INTERACTION` is a design decision, not a current contract.

#### Summary: restate, extend, conflict

| Clause | Relation | Where it bites |
| --- | --- | --- |
| Run ID, unique per run, exclusively created, reruns name superseded runs (`CAP-DLV-weekly-report:72-74`) | R | Keep; drift and perf passes gain the run ID by extension (`CAP-DLV-drift-reconciliation:34-35` lacks it) |
| Companion record fields and "missing companion blocks publication" (`CAP-DLV-weekly-report:83-86`) | R | The history record is this companion record; define it as such |
| Four publication states (`CAP-DLV-weekly-report:88-91`) | R, **C** if extended | Map auth, permission, rate-limit and conflict onto them |
| Publication needs separate, explicit, per-destination authority; invocation grants none (`CAP-DLV-weekly-report:23-24, 93-94`) | **C** with a default-on history write | Default must be `pending`; no standing permission |
| Scope excludes "history backend" (`CAP-DLV-weekly-report:22-24`); `ADR-mcp-runtime-and-shared-artifacts:229` says the history backend "remains independent" | **C** | Needs a new ADR or an explicit scope change for `MS-maintenance-run-history` |
| No shared artifact TTL for reports (`CAP-DLV-weekly-report:74-75`) and shared store must not overwrite or delete (`CAP-COLL-shared-artifacts:35-36`) | R | Do not implement the history store as a shared adapter |
| Report destination: owning unit materials or repository materials location; ordinary local file (`CAP-DLV-review-refactor:129-130`, `CAP-DLV-weekly-report:70-72`) | **E/C** | "Repository's materials location" does not describe a remote branch (section 2) |
| Intake records HEAD and dirty paths (`CAP-DLV-review-refactor:43`, `CAP-DLV-drift-reconciliation:34`, `CAP-DLV-weekly-report:28-29`) | R | Dirty paths are paths only; section 4 |
| Run outcome vocabulary: performance pass uses `stopped at decision round`, `applied`, `partially applied` (`CAP-DLV-performance-pass:171`) | **C** with the proposal's `completed | failed | interrupted` (`proposal.md:47-48`) | Pick a per-playbook outcome set, or keep the proposal's set as a separate field |
| Retry keeps run ID and exact bytes (`CAP-DLV-weekly-report:96`) | R | Define "logical record" (`proposal.md:52`) |
| `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol` output rules | R | Advisory mode per outcome is undecided |

## 2. "Repository's materials location"

What it is:

- `docs/materials/` is a directory for "dated research artifacts, technical spikes, benchmarks, surveys, and evidence gathered during development", with the layout `docs/materials/{YYYY-MM}/{YYYYMMDD}-{slug}/` and exemption from strict Living Spec structure rules (`docs/materials/README.md:3-11`).
- Materials are tracked in the default branch (their paths appear in ADRs and specs, for example `docs/decisions/2026-11/20261102-orchestration-workers.md:413`, and in `git` history). Materials are a document kind: `MAT` / `material` / `docs/materials/...` (`docs/capabilities/documents/CAP-DOCS-document-model.md:193`). Free-form materials "follow no authoring convention" (`packages/devkit-docs/src/devkit_docs/features/governance/services/documents.py:111-113`).
- Some rules skip materials: the ADR-supersession check (`CAP-DOCS-document-model.md:161`) and the reference check, where references written inside materials are not checked (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py:83-86`).

How materials get IDs:

- A retained investigation is an index document `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>.md` carrying `id: MAT-<slug>`, `created_at`, and H1 `# [MAT-<slug>] <title>`. Other notes in the same directory get a `MAT-` ID only when a consumer cites them alone. Before creating a material, the coordinator checks that `devkit docs resolve MAT-<slug>` finds nothing and the directory is absent (`docs/decisions/2026-11/20261102-adaptive-development-and-research.md:300-312`, `ADR-retain-research-as-cited-materials`).
- Example in the repo: `docs/materials/2026-10/20261030-worker-audit-known-host-advance/20261030-base-observation-options.md` with `id: MAT-base-observation-options` (line 2).
- A consumer cites a material by its ID and "never copies or moves the material into its own `materials/`" (`adaptive-development-and-research.md:307-308`). An SDD proposal's own `materials/` moves into `docs/materials/` at handoff (`adaptive-development-and-research.md:57`; `ADR-orchestration-workers` `:413` lists the unit's materials directory as the materials of a unit).
- `steering`/glossary: "Deep research" is "retained as one indexed material under `docs/materials/` and cited by its `MAT-<slug>` ID" (`docs/steering/glossary.md:45`). The glossary's "Steering document" excludes "evidence (materials)" (`glossary.md:34`).

Does a run record belong there?

- Not in the default branch. Materials are "research artifacts and evidence" (`docs/materials/README.md:3`); a run record is operational history, and the proposal's Non-goal says "records on the default code branch" are out (`proposal.md:64-66`). `CAP-DLV-weekly-report:70-72` forbids a silent tracked report on the default branch.
- The report itself may live in the owning unit's `materials/` or the repository materials location as an ordinary local file (`CAP-DLV-review-refactor:129-130`). That is a local file, not a tracked one, unless the user says otherwise (`PB/weekly-report.md:21-23`).
- Conclusion: the history branch is a new destination kind. Calling it "the repository's materials location" would give the phrase a meaning that `docs/materials/` and the capabilities do not have. Keep the local report in the materials location, and treat the history branch as a publication destination.

Existing in-proposal evidence: `docs/proposals/PROP-maintenance-history/materials/github-publication-api.md` (created by an earlier Planning step; not reviewed here beyond its headings and its `Unverified` items at lines 79, 100, 104, 114, 135).

## 3. Package placement and existing GitHub usage

### 3.1 devkit-catalog ships content, not features

- `packages/devkit-catalog/README.md:62-64`: "A catalog bundle holds content only: instructions, playbooks, skills, documents, guidance fragments, rules and declarative hooks using installed devkit handlers ... A bundle that needs devkit code (a gate, a workflow check, a command) belongs in `devkit-agt` instead."
- `packages/devkit-catalog/pyproject.toml:7` `dependencies = []`; `:9-15` one entry point per bundle; `:17-18` dev group only (`devkit-dist`, `devkit-agt` for tests).
- `packages/devkit-catalog/src/devkit_catalog/maintenance/__init__.py` is 0 bytes. No `features/`, `usecases/`, `cli/` or `services/` exists under `maintenance/`. Its files are `bundle/bundle.toml` and `bundle/playbooks/*` (`find` output in this pass).
- `docs/architecture/ARCH-05-2-components.md:80-87`: "Content-only packages may retain their existing bundle-only layouts. The content-only catalog owns the opt-in `adaptive-dev` and `deep-research` bundles ... add no runtime module or dependency." `docs/capabilities/distribution/CAP-DIST-content-packages.md:212-213`: the content-only `devkit-catalog` "registers `maintenance` as a resource module with no runtime dependencies".
- Caveat: the catalog does ship Python in one bundle, as rule plugins: `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/*/rule.py`. Rules are a plugin kind (`packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/manifest.py:54-55`). These are rule-engine modules, not features.
- Therefore `boundaries.owns` = `packages/devkit-catalog/src/devkit_catalog/maintenance/` is correct only for playbook/reference content. Any Python for `gh api` (client, canonicalisation, digest, retry) belongs in a devkit package with a feature layout (`ARCH-05-2-components` feature layers, `docs/architecture/ARCH-05-2-components.md:60-70`), most naturally `devkit-agt` beside the existing GitHub code (section 3.2). That changes the `owns` list.

### 3.2 Existing GitHub and `gh` usage

- `gh api` is not used anywhere in the code, scripts or docs. A search of `packages/*/src`, `scripts/` and `docs/` for `gh api`, `"api"`, `gh-api` finds only the proposal and its materials.
- `gh` is used through one runner: `packages/devkit/src/devkit_agt/features/worktree/repositories/pull_request.py:1` ("Bounded, injectable GitHub operations. Authentication remains owned by gh."). `run_gh` (`:50-72`) runs `["gh", *args]` with `GH_PROMPT_DISABLED=1`, `GH_PAGER=cat`, clears `GH_REPO`, `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and sets `GIT_CONFIG_GLOBAL`/`SYSTEM` to devnull. It returns `CommandResult(127)` when `gh` is missing and `CommandResult(None)` on timeout. `GitHub` (`:75-97`) takes an injectable `runner`. Timeouts: `NETWORK_TIMEOUT = 5.0`, `NETWORK_BUDGET = 20.0` (`:22-23`).
- Calls seen: the stale report's `_pull_requests` (`packages/devkit/src/devkit_agt/features/worktree/usecases/stale.py:156`) and its `GhRunner` hook (`:49-54`); the test double shows the arguments it expects, `gh auth status` and `gh pr list --state all` (`packages/devkit/tests/integration/features/worktree/test_stale.py:45-47`). Integration constructs `GitHub(self.root)` at `packages/devkit/src/devkit_agt/features/integration/usecases/service.py:124`; pull-request operations go through that object (`.../integration/usecases/pull_request.py:62` returns `service.github`). The `gh` argument lists for merge and PR list are not reproduced here.
- Decision: `docs/decisions/2026-11/20261102-local-and-pull-request-integration.md:191-193`: "GitHub only, through `gh`, behind a narrow protocol in `devkit.worktree` beside `run_gh` (selected)". `:99-100`: "Tests run without network through an injectable runner, as the stale report does." `:60-63`: `gh pr merge --match-head-commit` pins a head, and the stale report uses an injectable `GhRunner` with a 60-second bound.
- Relation to the proposal: a `gh api` procedure for the history branch would be a second GitHub operation family. The decision above covers PR operations in `devkit.worktree`, not a repository-contents writer. Extending the `GitHub` protocol to `gh api` needs a note in an ADR or the proposal's spec (that is a new decision about which package owns GitHub writes).

### 3.3 Integration provider and `pull_request` policy

- `[worktree] pull_request` default `"auto"`: `docs/capabilities/delivery/CAP-DLV-project-policy.md:53-54` and `packages/devkit/src/devkit_agt/features/integration/services/providers.py:58`. Example config `pull_request = "required"` (`CAP-DLV-project-policy.md:160-161`).
- `[integration] provider = "spec"` selects `devkit_spec.features.delivery.usecases.integration` for `IntegrationService` (`CAP-DLV-project-policy.md:54`, `:166-167`). `devkit spec policy` reports `pull_request` (`packages/devkit-spec/src/devkit_spec/features/policy/usecases/inspect.py:48`).
- What the policy does with GitHub: it selects the route for landing committed work (local merge or PR). It grants nothing for publication: `CAP-DLV-project-policy.md:44` ("granting commit, publication or host permission authority" is Scope Excluded). Integration itself is "Host-authorized" (`docs/steering/glossary.md:66-67`, `ADR-delivery-approval...`).
- The history branch is not a code branch. The integration policy does not apply to it, but the same `pull_request` config could be misread as covering it. The spec should state that explicitly.

### 3.4 Where a documented `gh api` procedure would live

Options grounded in the bundle format:

- **A playbook reference file** (`PB/<playbook>/references/<name>.md`, directory form). Precedent: `PB/review-refactor/SKILL.md` with `references/applying.md` and `references/criteria.md`, and `performance-pass` cites them (`CAP-DLV-performance-pass.md:20-26`). Lowest cost; no new asset kind.
- **A new playbook** (`kind = "playbook"`, `bundle.toml`), e.g. `history-init` or `history-read`. Playbooks are retrieved by `devkit playbook get maintenance/<id>` (`CAP-DLV-weekly-report.md:18-19`). Each new asset needs a preset (`bundle.toml:11-36` lists the presets) and tests (`packages/devkit-catalog/tests/integration/bundles/test_bundles.py:115-147`).
- **A skill** (`kind = "skill"`, e.g., `skills/<name>/SKILL.md`, as `adaptive-dev` does, `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md`). A skill is an entry point; no catalog skill is a maintenance playbook. A skill would also need a `devkit-playbook` suggestion rule, which the user memory says must not be added for explicit-only skills.
- Asset kinds accepted by devkit-dist (`packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/manifest.py:40-53`): `skill`, `subagent`, `instruction`, `playbook`, `rule`, `workflow`, `gate`, `document`, `guidance`, `hook`. Plugin source directories are only for `rule` and `gate` (`:54-55`). `VARIANT_KINDS` (`:56-57`) applies only to `skill` and `subagent`. Bundles declare `[[assets]]` with `id`, `kind`, `source` (`PB`-bundle `bundle.toml:6-9`, `:22-25`).
- The repository rule for editing bundle assets: "Before editing any bundle's skill, playbook, instruction or guide, also run `uv run devkit get-context authoring` and apply its `agent-asset-writing` instruction" (`AGENTS.md`, Documentation section of the devkit guide).
- Budget tests bound playbook size: `test_review_refactor_is_self_contained_and_within_budget` (`test_bundles.py:199`) and `test_performance_pass_is_self_contained_and_within_budget` (`:260`).

## 4. Q2: identifying uncommitted state

### 4.1 What the three playbooks record today

- `weekly-report`: `PB/weekly-report.md:14-15`: "dirty paths with local Git only (`git rev-parse HEAD`, `git rev-parse <ref>^{commit}`, `git status --short`)". `:32`: "include uncommitted content only when selected, labeled separately." `:41`: "Before writing, recapture HEAD, integration ref and dirty content; if they changed, restart or mark the affected evidence unverified."
- `drift-reconciliation`: `PB/drift-reconciliation.md:14`: "Record repository, HEAD, dirty paths". `:25-26`: "code or guidance citation at the recorded revision, dirty content included". `:50`: revalidation on change.
- `review-refactor`: `PB/review-refactor/SKILL.md:20`: "HEAD, dirty paths". `:57`: finding location "at the recorded revision, dirty content included". `:88`: revalidation. `:95`: "Intake: run ID, repository identity, intake revision and dirty state". Also `PB/review-refactor/references/applying.md:32-33`: if the tree holds changes not belonging to the run, "stop and have the user commit, stash or exclude them; never discard them yourself."
- `performance-pass`: `PB/performance-pass/SKILL.md:28` (`HEAD, dirty paths`); `PB/performance-pass/references/candidates.md:11` (location "dirty content included").

Gap: all three record dirty paths (a list), but none records a content identity for the dirty content. The weekly playbook's "labeled separately" (`:32`) is weaker than the capability's requirement of "a preserved diff/artifact reference" (`CAP-DLV-weekly-report.md:36-37`; `specs/2026-10/20261021-weekly-report/spec.md:98-100`). The weekly SPEC's AC-05 (`spec.md:57-60`) also requires the reference.

### 4.2 What CAP-COLL-shared-artifacts requires of `source_sha`

- `CAP-COLL-shared-artifacts.md:20-22`: "Inputs are ... a full lowercase 40/64-hex source_sha ... Consumers SHOULD verify that source_sha is their actual reviewed commit."
- Content identity `:25-27`: namespace, kind, slug, `source_sha`, language, SHA-256 body digest; `revision` equals the body digest (`:27`).
- Consequence: `source_sha` names a commit. It has no dirty field. A tree hash has the same 40/64-hex shape, so it would pass validation while meaning something different. A dirty-state identifier must not go into `source_sha`.

### 4.3 Existing devkit mechanisms that digest the working tree

- `spec-delegate` step 2 (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/SKILL.md:29-36`): `index="$(git rev-parse --git-path devkit-delegate.index)"; GIT_INDEX_FILE="$index" git read-tree HEAD && GIT_INDEX_FILE="$index" git add -A && GIT_INDEX_FILE="$index" git write-tree`. "The temporary index lives in the Git directory; the real index and `git status` stay unchanged." It covers tracked edits and untracked files. Step 4 compares two such snapshots (`:38`). `CAP-DLV-delivery-workflows.md:426-428` describes this as the post-run comparison "of two snapshots of the working tree, each a tree written from a temporary index".
- `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/snapshot.py:119-145` (`git_snapshot`): with `staged=True`, `write-tree` on the commit index (`:127`); with `staged=False`, only `HEAD^{tree}` (`:135`) and a merge base. So the non-staged working tree is not digested by the rules engine.
- `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:216`: `git status --porcelain --untracked-files=normal` as a clean/dirty boolean only.
- `devkit spec worker inspect`: its errors describe committed-branch derivation (`packages/devkit-spec/src/devkit_spec/base/errors.py:743-752`). No working-tree digest was found.
- Artifact SHA-256 (not tree): `PB/weekly-report.md:61` and `CAP-DLV-weekly-report.md:80-81` (digest of the report bytes after verification).
- `packages/devkit-core/src/devkit_core/core/git.py:85-92, 142`: `run_git(..., index=...)` sets `GIT_INDEX_FILE` per call. This is the helper a temp-index snapshot would use.

### 4.4 Candidate identifiers

| Candidate | What it identifies | Evidence | Trade-offs |
| --- | --- | --- | --- |
| A. HEAD SHA + dirty path list (`git status --short` or `--porcelain`) | Which paths were dirty; not their content | Current playbooks (`PB/weekly-report.md:14-15`, `PB/review-refactor/SKILL.md:20`) | Cheap, already required. Two different dirty contents give the same record. Not a content identity; cannot prove "same state" on a rerun. |
| B. Tree hash from a temporary index (`read-tree HEAD`, `add -A`, `write-tree`) | Exact tree of HEAD plus tracked and untracked changes, as Git content | `spec-delegate/SKILL.md:31-36`; `snapshot.py:127` | Deterministic for the same content. The real index and `git status` stay unchanged (spec-delegate `:36`). Caveats: `git add -A` respects ignore rules, so ignored files are not covered (not verified in this pass); the tree object exists only in the local object store unless uploaded; a remote reader cannot check it without the objects. Cost grows with the size of the working tree. Must not go into `source_sha` (section 4.2). |
| C. Diff digest (`git diff --binary HEAD` plus untracked files, SHA-256 of bytes) with the diff kept as a local artifact | The changed bytes | `CAP-DLV-weekly-report.md:36-37` requires "a preserved diff/artifact reference"; SHA-256 precedent `:80-81` | Matches the capability's wording most directly. The diff may contain secrets or PII; the capability requires credential-free identity (`:28`) and the repo has a secret-leak rule (`packages/devkit/src/devkit_agt/features/rules/services/builtins/secret_leak/`). Storing the diff on a remote history branch would publish it, so keep the diff local and store only its digest on the branch. |
| D. Hybrid (recommended for evaluation): HEAD SHA + dirty path list + tree hash from the temporary index + local diff artifact digest in the record; diff stays local | Path set, content identity and the preserved evidence | Combines A, B and C; the capability's preserved-reference rule (`:36-37`) is met by C | More fields. A remote reader can confirm the digests only when the local artifact or the tree objects are available; otherwise the record must say "digest not verifiable remotely", which fits the existing unverifiable-stays-unknown discipline (`CAP-DLV-weekly-report.md:96-98`). |
| E. `git stash create` (not in the repo; from Git's documentation, unverified here) | A commit object for the working-tree state without touching refs | Not found in repository evidence | Would give a commit-shaped identity, which is attractive for `source_sha`. It covers tracked changes only, and it creates a dangling commit that needs retention. Verify before use; do not place it in `source_sha`. |

Recommendation for the evaluation (not a decision): D, with B computed in a temporary index exactly as `spec-delegate` does, and C kept local. Revisit if the history design needs remote verification of dirty content, which would require uploading tree or blob objects.

## 5. Glossary (`docs/steering/glossary.md`, `docs/steering/glossary.yaml`)

Registered terms with Owner and Avoid (Avoid column in parentheses; `glossary.md` rows, with line numbers):

- **Shared artifact** (`:54`): "Immutable expiring report content shared by exact generation reference; excludes scope coordination and approval authority." Owner `CAP-COLL-shared-artifacts`. Avoid: "shared state, coordination record". Code identifiers: `devkit_dist.features.shared`, `Artifact`.
- **Envelope** (`:53`): "A structured YAML file recording the findings, questions, problems, or resolution of a workflow stage." No Avoid.
- **Receipt** (`:22`): "`.devkit/installation.json`: records every deployed file, checksum, and origin bundle in one transaction." No Avoid.
- **Snapshot run** (`:33`): "Rule execution against an exact Git snapshot ..." No Avoid.
- **Work scope observation** (`:46`): "Invocation-local evidence from one snapshot ... excludes a persistent registry revision or write authority." Uses "revision" in an exclusion.
- **Deep research** (`:45`): "retained as one indexed material under `docs/materials/` and cited by its `MAT-<slug>` ID".
- **Steering document** (`:34`): Avoid "foundation, background"; excludes "evidence (materials)".
- **Development approach** (`:42`): excludes "publication authority".
- **Host** (`:66`), **git-operator** (`:67`), **Scoped CLI integration** (`:72`, Avoid "Integration MCP"), **Agent advisory** (`:70`), **Feedback promotion/resolution** (`:59-60`), **Source feedback** (`:56`).

Terms the proposal uses, and what the glossary says:

- **run**: not registered. "Snapshot run" (`:33`) already uses "run" for a rules execution. The proposal should qualify it (for example "playbook run").
- **record**: not registered. "Receipt" (`:22`) is registered for installation records, while the capabilities use "receipt" for a publication destination's proof (`CAP-DLV-weekly-report.md:88-91`). Avoid bare "receipt" in the proposal.
- **report**: not registered. Used throughout the capabilities as the Markdown artifact. Keep that meaning.
- **artifact**: only "Shared artifact" (`:54`) is registered, with `Artifact` as a code identifier. The weekly playbook uses "artifact" for the local file (`PB/weekly-report.md:61`). Using bare "artifact" risks implying the shared store.
- **publication**: not registered. The four outcome states are defined only in `CAP-DLV-weekly-report.md:88-91`.
- **outcome**: not registered. Used as "generation outcome", "publication outcome" (`CAP-DLV-weekly-report.md:83`), and as "stopped at decision round", "applied", "partially applied" (`CAP-DLV-performance-pass.md:171`). The weekly playbook says "companion outcome record" (`PB/weekly-report.md:65`), while the capability says "companion record" (`CAP-DLV-weekly-report.md:83`). Pick one.
- **revision**: not registered. `CAP-COLL-shared-artifacts.md:27` uses "revision" for the body digest, while playbooks use it for commits. Use "source SHA" or "source commit" for commits.
- **source revision**: not registered. `ADR-mcp-runtime-and-shared-artifacts.md:69` uses "source revision"; `CAP-COLL-shared-artifacts.md:21` and `CAP-DLV-weekly-report.md:72` use "source_sha" / "source SHA". Prefer the latter.
- **destination**: not registered. Used for both the report location (`CAP-DLV-review-refactor.md:43-44`, "report destination") and the publication target (`CAP-DLV-weekly-report.md:88`). The history branch is a publication destination, not a materials location.
- **materials**: not registered as a term. The glossary refers to materials under "Deep research" (`:45`) and excludes "evidence (materials)" under "Steering document" (`:34`). Use "repository's materials location" as the capabilities do, and reserve `MAT-` IDs for indexed research.

`glossary.yaml` (`docs/steering/glossary.yaml:3-28`) holds search synonyms for bundle, sync, projection, rule, workflow, envelope, worktree, gate, advisory, compact, steering document, adaptive development and proposal Planning. It holds none for run, record, report, artifact, publication, outcome, revision, source revision, destination or materials.

Which terms to use in the proposal: "playbook run" and "run ID"; "report" for the Markdown file; "companion record" (the capability term) or "run record" if the proposal registers it; "publication" with the four states; "destination"; "source SHA" for commits. Avoid bare "revision", "receipt", "artifact" for history records, and bare "run". A new glossary row for "run record" would be a Living Spec change, and the glossary says to read it "before naming a domain concept, choosing user-facing or interface terms, or registering a term".

## 6. Related work

Searches run: `devkit docs search` for "maintenance history", "run record", "outcome record", "publication", "orphan branch", "remote shared adapter", "weekly report destination", with and without `--history`.

| Document (status) | What it decided or states | What this proposal must respect | What it could reuse |
| --- | --- | --- | --- |
| `FB-remote-shared-adapter-follow-up` (dismissed; `specs/2026-10/20261021-worker-shared-state-mcp/feedback/remote-shared-adapter-follow-up.md`) | Concrete remote shared adapter deferred; restart needs a provider, authentication, namespace owner, integration environment; "a protocol fake is insufficient" (`:31-37`); disposition `:58` | The history branch is not the deferred adapter. It must not be presented as a remote shared adapter or as production cross-host evidence. Fake `gh` tests are not production evidence. | The restart criteria for a remote store (authentication, namespace owner, real-backend evidence) apply to any GitHub writer |
| `MS-maintenance-run-history` (planned; `docs/roadmap/MS-maintenance-run-history.md`) | Exit: a durable, revision-linked record per run kept apart from code history; agents list and read it without changing the checkout (`:21-22`); non-goals: scheduler, and "changes to the maintenance playbooks' own procedures beyond recording their outcome" (`:26-27`); depends on `MS-maintenance-operations` (`:7`) | The proposal is its direct member (`proposal.md:31-32`). Keep changes to the playbooks at the level of recording outcome. Completion review is pending (`:31-32`). | The exit condition is the acceptance criterion to cite |
| `MS-maintenance-operations` (done, archived; `docs/roadmap/_archive/MS-maintenance-operations.md`) | Durable history moved to `MS-maintenance-run-history` (`:31`); aliases include `MS-maintenance-history` (`:13`); non-goals: scheduler, automatic code changes or integration from a run (`:35-36`) | The moved ownership is why the history work now sits in `MS-maintenance-run-history`; the scheduler and integration exclusions carry over | Cite for the scope boundary |
| `ADR-mcp-runtime-and-shared-artifacts` (accepted; `docs/decisions/2026-11/20261102-mcp-runtime-and-shared-artifacts.md`) | Shared artifacts are immutable and TTL-bound (`:171-178`); a production remote artifact adapter is deferred (`:111-112`); reports are evidence, with publication as a separate record (`:190-193`); "a history backend and automatic maintenance sweeps with reporting" rejected (`:121-123`); "The future history backend remains independent" (`:229`); preliminary, no standing publication permission (`:194-196`); driver "without a new runtime or database" (`:73-74`) | The strongest constraint. A history store is a decision this ADR explicitly deferred. The proposal needs its own ADR (or a supersession) for the history backend and for destinations. | Its publication-record split (`:190-193`) and "unknown needs a check before retry" rule |
| `CAP-DLV-weekly-report` (active) | Scope excludes "history backend" (`:22-24`); publication separate, explicit authority (`:93-94`) | Section 1.2 conflicts | Companion record fields (`:83-86`) |
| `SPEC-weekly-report` (completed; `specs/2026-10/20261021-weekly-report/spec.md`) | "without a scheduler or history backend" (`:25`); history databases out of scope (`:33`); "retention policy and a history backend remain separate work" (`:142`); "no upload, message, commit, push or external mutation follows implicitly" (`:155-156`) | Same as the capability; the proposal is the "separate work" | Its AC-07 publication checks |
| `UC-publish-a-weekly-report` (active; `docs/usecases/governance/UC-publish-a-weekly-report.md`) | Developer selects destination and grants authority; lost response → `unknown` (`:69-70`); retry with same run ID and bytes after inspection (`:75-76`) | The proposal's publication flow should match these steps | The use-case steps as acceptance scenarios |
| `ADR-local-and-pull-request-integration` (accepted; `docs/decisions/2026-11/20261102-local-and-pull-request-integration.md`) | GitHub only, through `gh`, behind a narrow protocol in `devkit.worktree` beside `run_gh` (`:191-193`); tests without network through an injectable runner (`:99-100`) | A `gh api` writer is a new GitHub operation family; decide its package and protocol | `run_gh`, `GitHub` protocol and the `FakeGitHub` test pattern |
| `ADR-delivery-approval-and-lifecycle-authority` (accepted; `docs/decisions/2026-11/20261102-delivery-approval-and-lifecycle-authority.md`) | Publication and cloud mutation stay outside local authority (`:79`); no policy grants publication authority (`:211`) | The history writer needs its own explicit authority; policy cannot grant it | Its authority wording |
| `ADR-retain-research-as-cited-materials` (in `ADR-adaptive-development-and-research`; `docs/decisions/2026-11/20261102-adaptive-development-and-research.md:300-312`) | MAT index, ID rules, check before create | Run records are not research materials (section 2) | ID-check procedure before creating a path |
| `SPEC-proposal-review-auto-write` (completed; `specs/2026-10/20261024-proposal-review-auto-write/spec.md:16`) | A source-bound proposal review is "stored through the shared artifact adapter" with the TTL | Precedent for a review record that is a shared artifact; the history branch should not be the same thing | Source-bound report pattern |
| `ADR-proposal-acceptance` (accepted; `docs/decisions/2026-10/20261022-proposal-acceptance.md:45`) | "Shared reports expire" | Reports that must persist cannot rely on the shared store | Source-bound review pattern |
| `PROP-maintenance-history/materials/github-publication-api.md` (this proposal's materials) | GitHub API options for atomic multi-file publication, orphan branch creation, retrieval, idempotency; its own Unverified list | Its findings are not verified in this pass | Use for Q1 of the proposal's spike |

Not read in full (search hits only): `ADR-review-refactor-application`, `ADR-retire-native-approval-and-moved-ownership-clauses`, `ADR-proposal-handoff`, `ADR-worktrees-and-scope`, `SPEC-cli-host-lifecycle`.

## 7. Testing constraints

- Injectable runner is the established pattern. `packages/devkit/tests/integration/features/worktree/test_stale.py:43-50` defines `fake_gh(...)` that answers `gh auth status` and `gh pr list`, then injects it through `stale_branches(..., gh=fake_gh(...))` (`:60`, `:85`). Missing `gh` is tested with exit codes `1` and `127` (`:57-63`).
- `FakeGitHub(GitHub)` pattern: `packages/devkit/tests/integration/features/integration/test_pull_request.py:16-28` subclasses `GitHub`, models the remote in memory and counts merge calls. It is assigned as `service.github = fake` (`:110-111`), and it covers pending, failed and retry states (`:142-151`).
- PATH-shim pattern: `packages/devkit/tests/integration/package/test_module_script.py:18-29` writes an executable `uv` shim into `tmp_path` and prepends it to `PATH`, logging calls to a file. The same pattern would fake `gh` without the network.
- `run_gh` has a runner-identity check (`pull_request.py:95-97`): only the real `run_gh` gets the bounded timeout, so injected fakes bypass it. Tests of timeouts and missing `gh` need the real runner with a fake binary on `PATH`.
- devkit-catalog tests load bundles through `devkit-dist`'s manifest reader and check selection, presets and budgets (`packages/devkit-catalog/tests/integration/bundles/test_bundles.py:108-147`, `:199-209`). Playbook prose is checked by content tests, not by behaviour.
- ADR-mcp `:240-242`: "The reporting playbook remains content-only; manual scenario evidence supplements package and governance tests." This is the accepted verification approach for playbook behaviour.
- CI does not run on push or pull request. `.github/workflows/ci.yml:12-14` says so, and manual dispatch, nightly and release run the full CI. `ci.yml:21-22` sets `permissions: contents: read`. No `gh` install step and no `secrets`/`GITHUB_TOKEN` reference appear in `ci.yml` or `nightly.yml` (`rg` in this pass). The `release.yml` job runs `gh release create` (`release.yml:48`), so `gh` exists in the release job only.
- Local verification commands: `just test-affected`, `just test <module> <path>`, `just smoke`, `just rules-test`, `just check` (`AGENTS.md` verification table).

Verification approach the proposal can state without GitHub: unit and integration tests through an injected `GitHub`/`runner` fake (section above); a fake `gh` on `PATH` for `run_gh` tests; tree-hash and digest tests on a temporary Git repository (as `test_stale.py` does with `init_repo`); content tests for playbook text. Live publication evidence needs a manually run scenario against a throwaway repository, labelled as such (ADR-mcp `:240-242`; `CAP-DLV-weekly-report.md:99-100`: "Controlled exercises MUST label simulated authority/receipts and MUST NOT claim external publication.").

## Implications for the design

1. **Do not implement the history store as a `SharedArtifactAdapter` or inside `devkit_dist.features.shared`.** The 7-day expiry, no-overwrite and no-delete rules (`CAP-COLL-shared-artifacts.md:33-36`) do not fit durable history, and `ADR-mcp-runtime-and-shared-artifacts.md:111-112` defers a production remote adapter. (Section 1.2, `C`.)
2. **Resolve the "no history backend" scope before Development.** `CAP-DLV-weekly-report.md:22-24`, `SPEC-weekly-report` (`:33`, `:142`) and `ADR-mcp-runtime-and-shared-artifacts.md:229` exclude or defer it. The proposal needs an ADR (new, or superseding the relevant clauses) that names the history backend and its owner. The proposal also does not reference the four delivery capabilities by ID (`devkit docs refs <ID> --direction in` lists `SPEC-maintenance-history` for none of them), so cite them explicitly.
3. **Make default publication `pending`.** A history write is an external mutation (`CAP-DLV-weekly-report.md:93-94`). Each run needs a user-selected destination and explicit authority (`ADR-mcp-runtime-and-shared-artifacts.md:194-196`). "All three playbooks publish" (`proposal.md:45-47`) must be an opt-in path, not the default.
4. **Keep the report bytes immutable and the publication state separate.** Store the run record as the companion record (`CAP-DLV-weekly-report.md:83-86`). A publication outcome change must not change the report digest (`ADR-mcp-runtime-and-shared-artifacts.md:224-229`).
5. **Define the logical key and the retry rule.** The capability keys reports by repository identity, scope and interval, and retries keep run ID and exact bytes (`CAP-DLV-weekly-report.md:72-73`, `:96`). The proposal's "logical records" (`proposal.md:52`) needs the same definition, and it must extend the drift and performance playbooks, which have no run-ID rule for drift (`CAP-DLV-drift-reconciliation.md:34-35`).
6. **Keep the four publication states closed.** Map authentication, permission, rate-limit and conflict failures onto `pending`, `failed` and `unknown` (`CAP-DLV-weekly-report.md:88-91`). A rate-limit (`CAP-ADV-agent-advisory-protocol.md:218`, `DEFER`) is a retry-later condition, not a new publication state.
7. **Reconcile the run outcome vocabulary.** `completed | failed | interrupted` (`proposal.md:47-48`) differs from the performance pass outcomes (`CAP-DLV-performance-pass.md:171`). Either adopt per-playbook outcomes or a separate common field with a mapping.
8. **Use a dirty-state identity that is not `source_sha`.** Record HEAD, the dirty path list (existing practice), a tree hash from a temporary index (`spec-delegate/SKILL.md:31-36`), and a digest of the local diff that `CAP-DLV-weekly-report.md:36-37` requires. Do not put a tree hash in `source_sha`, which is defined as a commit (`CAP-COLL-shared-artifacts.md:21-22`). Keep the diff local; publish only its digest.
9. **Do not call the history branch "the repository's materials location".** `docs/materials/` is tracked research with `MAT-` IDs (`docs/materials/README.md:3-11`; `ADR-adaptive-development-and-research.md:300-303`). The capabilities' "ordinary local file" (`CAP-DLV-review-refactor.md:129`) is the report; the history branch is a destination kind to name in the proposal.
10. **Placement: content in the catalog, code elsewhere.** `packages/devkit-catalog/src/devkit_catalog/maintenance/` may hold playbook and reference content (`packages/devkit-catalog/README.md:62-64`; `ARCH-05-2-components.md:80-87`). A `gh api` client, digest and retry logic belongs to a devkit package with feature layers. The natural home is `devkit-agt` beside `run_gh` (`pull_request.py:50-97`), which the local-and-PR integration ADR already names (`ADR-local-and-pull-request-integration.md:191-193`). Change `boundaries.owns` (`proposal.md:14-16`) to match.
11. **Where the `gh api` procedure goes.** A reference file under the playbook directory (`references/…`, precedent `review-refactor/references/applying.md`) is the lowest-cost option. A new playbook or skill needs a preset, tests and `devkit get-context authoring` before editing (`AGENTS.md`).
12. **Advisory modes are undecided.** Use stable UPPER_SNAKE codes and `[ACTION]` (`ARCH-08-1-agent-output.md:17-18`). Map rate-limit to `DEFER`, half-applied or lock conflicts to `HALT`, and destination or authority questions to `INTERACTION` (`CAP-ADV-agent-advisory-protocol.md:160-197`, `:216-218`).
13. **Lost responses need inspection before retry.** `CAP-DLV-weekly-report.md:96-98` and `UC-publish-a-weekly-report.md:69-76` require destination inspection before any retry. The `gh api` retry design must check the remote branch for the same run ID and digest before resending, and must not resend on `unknown`.
14. **Verification without GitHub.** Use an injected `GitHub`/runner fake (`test_pull_request.py:110-111`), a PATH-shim `gh` (`test_module_script.py:18-29`) and temporary-repository tests for digests. Label live publication as a manual exercise (`CAP-DLV-weekly-report.md:99-100`). Do not present fakes as production evidence (`FB-remote-shared-adapter-follow-up.md:36-37`).
15. **Terminology.** Use "playbook run", "run ID", "companion record" (or a registered "run record"), "report", "publication", "destination", "source SHA". Avoid bare "run", "record", "receipt", "artifact", "revision" and "materials" for history objects (section 5).

## Unverified

- Behaviour of GitHub's endpoints (atomic multi-file commits, ref update races, rate-limit responses, orphan branch creation). Not checked here; see `materials/github-publication-api.md` and its own Unverified list, which this pass did not verify.
- Whether `git add -A` in the temporary index excludes ignored files in all configurations (section 4.4, candidate B).
- `git stash create` (candidate E) is from Git's general documentation, not from repository evidence. It needs a check before use.
- Whether GitHub-hosted CI runners have `gh` installed or authenticated; `ci.yml` and `nightly.yml` do not set this up.
- `devkit spec worker inspect` behaviour beyond its error classes (`packages/devkit-spec/src/devkit_spec/base/errors.py:743-782`).
- The full text of `ADR-review-refactor-application`, `ADR-retire-native-approval-and-moved-ownership-clauses`, `ADR-proposal-handoff`, `ADR-worktrees-and-scope` and `SPEC-cli-host-lifecycle`: only search hits and their IDs were used.
- Whether a `references/` directory is accepted under a single-file playbook: only directory-form playbooks (`review-refactor`, `performance-pass`) were checked.
- The full incoming-reference lists (`--direction in -n 0`) were summarised, not read item by item; the proposal's own list of touched contracts may need the rest of the IDs.
- Whether the `PROP-maintenance-history/materials/` directory moves into `docs/materials/` at handoff exactly as `ADR-adaptive-development-and-research.md:57` describes; the handoff ADR (`ADR-proposal-handoff`) was not read.
