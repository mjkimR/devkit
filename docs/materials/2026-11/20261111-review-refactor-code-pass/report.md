# Review-refactor run: code surface, per package (2026-11-11)

Run of the `maintenance/review-refactor` playbook, read from
`packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/` (this repository does
not select the `maintenance` bundle). It follows the 2026-11-10 bug review
(`docs/materials/2026-11/20261110-bug-review/report.md`) and the previous code pass
(`docs/materials/2026-10/20261027-review-refactor-code-pass/report.md`).

## Intake

- **Run ID**: `rr-20261111-code`.
- **Repository**: devkit monorepo, `main` at `4a186f0d` (clean).
- **Surface and roots**: `code` only, reviewed per package: `packages/*/src` (Python) and `tools/devkit-dev/src`.
  Excluded: the viewer frontend (Svelte/TS), bundle Markdown, tests.
- **Compatibility policy**: no shims or migration paths while there are no external consumers
  (`ADR-package-ownership-and-release-version`), except `devkit.advisory` (external runtime consumers) and the
  devkit-cli semver API.
- **Batch**: one batch (code), one decision round.

## Coverage

Seven read-only reviewers: cross-package duplication; devkit-agt `workflow` + `rules`; devkit-agt other features and
non-feature modules; devkit-spec; devkit-dist; devkit-docs; small packages (core, advisory, cli, mcp, viewer Python,
catalog, adaptive, starter, devkit-dev). Each listed files read fully, skimmed and not reached. The Host rechecked the
following against the code before the round: SP-2, AO-17, SM-2, AW-10.

- **Previous gaps now covered**: devkit-agt `workflow/usecases/evaluate.py` and `handoff.py` (line by line);
  devkit-spec `scope/usecases/{flow,query,history}.py`, `scope/cli`, `proposals/usecases/{backlog,prune}.py`,
  `worker/usecases/summary.py`; devkit-dist `features/search/*`, `services/bundles/subagents.py`,
  `installation/config.py`; devkit-adaptive and devkit-docs (first pass).
- **Remaining gaps**: bodies of devkit-agt `rules/models/{markdown,settings,contracts}.py`,
  `repositories/envelope_commit.py`, `isolated_execution` `supervise`; devkit-spec `governance` rule use cases,
  `proposals/services/{rewrite,body,history}`, `entrypoints` services; devkit-dist distribution use cases `commands.py`,
  `context.py`, several installation and bundle services, host models/adapters; tools/devkit-dev `facts.py`/`rule.py`
  (outline only).
- **Dropped candidates**: about 120 across the reviewers (no named cost, deliberate parallel structure, documented
  test seams, standard-library-only copies by contract, different semantics, earlier Keep decisions).

## Findings

Disposition codes: **P** consolidate/remove, behavior-preserving; **D** consolidation with behavior differences (each
difference decided); **C** contract change (own work item); **K** keep; **F** defer.

### Cross-package (X)

| Key | Finding | Cost | Proposed |
| --- | --- | --- | --- |
| X-1 | Entry-point loading/isolation in 8 copies (core `run_extensions`, docs overlays, dist context/status/templates, agt finish guards, integration cleanup, mcp discovery) | isolation policy drifted (SystemExit, discovery failure) | D: `call_extensions` in `devkit_core.core.extensions`; isolate SystemExit and discovery failure everywhere; mcp keeps raising |
| X-2 | Raw Git runners bypass `run_git` (maintenance_history ×3, dist snapshots, worktree `execution.py`, lifecycle `_git_session`) | Git env/timeout policy not shared | D: use `run_git`; add `isolated_env`/`new_session` options to core; core default timeout |
| X-3 | `flock` poll loop in 4 copies (core, workflow records, dist shared, spec scope) | errno/expiry/poll drift | D: expose `flock_fd` in `devkit_core.core.locks`; callers keep their error factory |
| X-4 | Code-span/paragraph scanning in agt rules vs docs reference masker | the same document masks differently | D: docs uses agt `closes_later`; agt paragraph-end rule kept (docs reference behavior change) |
| X-5 | Frontmatter scalar setter in 4 copies (agt workflow, docs id_convention, spec spec_lifecycle, spec status) | CRLF/comment/block edge cases each partial | D: `set_field` + `trailing_comment` in `devkit_core.core.frontmatter`; comments kept; missing key per caller |
| X-6 | Sentinel helpers byte-identical in docs and spec adapters; dead `devkit_spec/utils/output.py` | ARCH-08-1 format kept twice; dead copy with old quoting | P: remove dead module; `sentinel`/`fields_line`/`echo_page` into `devkit_dist.adapters.cli` |
| X-7 | Prose ID-reference extraction copied docs → spec rewrite | reference grammar must stay identical | P: spec calls public docs `body_references` |
| X-8 | Dirty/changed-path Git queries in adaptive, spec, agt | write-scope checks must agree | D: `dirty_paths`/`changed_paths` in `devkit_core.core.git` |
| X-9 | Two fingerprinted memos (docs parse memo, agt facts) | path safety and envelope validation kept twice | F: larger change; revisit with the facts cache |
| X-10 | Commented TOML template convention in dist and agt gate | `uncomment` round trip twice | D: agt uses dist `render_key`/`prose`; dist wrapping kept |
| X-11 | maintenance_history own atomic write | second writer | P: `atomic_write_bytes(mode=0o600)` |
| X-12 | `--version` callback ×4 | format/help repeated | P: `version_option` in `devkit_dist.adapters.cli` |
| X-13 | `_utf8_output` copied devkit-cli → dist | two copies | C: public devkit-cli helper (semver minor) — recommend defer |
| X-14 | Segment-boundary `covers` in adaptive and docs (+ inline checks) | root/boundary rule repeated | P: adaptive imports docs `covers` |

### devkit-agt `workflow` and `rules` (AW)

| Key | Finding | Proposed |
| --- | --- | --- |
| AW-01 | ~27 envelope flags threaded through 5 parallel keyword lists | P: frozen `EnvelopeFlags` |
| AW-02 | Constants defined twice (`WORKER/ANSWER/RESOLUTION`, `GATE_PREFIX`, `TITLE_LIMIT`, kind tuples) | P: keep `models` copies |
| AW-03 | Display-relative-path helper ×3 (workflow, rules, gate) + rules `_source` | D: one helper in `devkit_core.core.paths`; posix form outside the root |
| AW-04 | `inspect.getfile(type(rule))` lookup ×5 | P: `rule_file(rule)` in rules models |
| AW-05 | Managed/overrides pinned check ×4; `_workspace_of` vs `_counterpart` | D: helper in `cache.py`; targets keeps lexical+resolved test |
| AW-06 | Scope definition load duplicated in `envelopes.py` | P |
| AW-07 | `--head` hex check duplicated | P: keep the `compose_envelope` copy |
| AW-08 | Answer action/value checks duplicated | D: one fix text ("Drop --value, or use --action accept") |
| AW-09 | Defaults/fallbacks reached only by tests (`evaluate_handoff(unit="")`, `compose_envelope` defaults, `str | UnitRef`, `receipt=None`) | P |
| AW-10 | Unused: `touched_owners`, `ANSWER_CHANNELS`, `KINDS`, orphan comment, `read_binding`, `IDENT_HINT`, `_stdin_flags`; unreachable guards | P |
| AW-11 | Always-quote sentinel helper ×3 in agt adapters | P: merge into one agt helper |
| AW-12 | Hardcoded `uv run devkit workflow …` strings bypass `workflow_command` | P |
| AW-13 | Repeated list/mapping parsing in envelope model | P |
| AW-14 | Builtins set severity/phase the evaluator overwrites | P (after checking direct `rule.check` tests) |
| AW-15 | Handoff eligible/recommended recomputed; accepted-return filter ×3 | P |
| AW-16 | `ownership.workflow_ids` duplicates binding parsing | K: rules cannot import workflow |
| AW-17 | `--given` declared ×4 | P |

### devkit-agt other features (AO)

| Key | Finding | Proposed |
| --- | --- | --- |
| AO-01 | Two local landing implementations: `worktree finish --merge` and `integration integrate --route local`; already diverged (finish guards, push, moved target, seeding) | C: retire `finish --merge` → `integration integrate` (own work item) |
| AO-02 | Local and PR route post-merge phase duplicated | D: shared revalidation and runtime check in `integration/services`; local `RuntimeLocationError` kept |
| AO-03 | `[worktree]` policy parsed in 5 places | D: one `worktree_policy`; each caller keeps its refusal code |
| AO-04 | GitHub port and `PullRequestError` live in worktree but serve only integration; duplicated codes; hardcoded merge title | P: move to integration; use `merge_message` (public-module path change, internal) |
| AO-05 | Leftovers of the removed long-lived MCP process (128-record cap, per-record lock, thread-local budget, `wait`, test-only `to_dict`, `ui_action`, two flags for one state) | P, except `ui_action` removal → C (JSON field) |
| AO-06 | `Gate` Protocol duplicates `BaseGate` | P (public name, internal) |
| AO-07 | Gate settings introspection ×3 | P |
| AO-08 | Two `gh` runners and HTTP-status parsers | D: worktree runner's hardening kept |
| AO-09 | maintenance_history bypasses core Git/atomic helpers | see X-2/X-11 |
| AO-10 | `HistoryOperation` string dispatch over a 25-field request | P: one use case per operation |
| AO-11 | Git config query ×5, upstream lookup ×2 | D: `git_config` in `devkit_core.core.git` |
| AO-12 | Two `_rerun_on_base` | P |
| AO-13 | `before_remove` hook has no production caller (documented library API) | C |
| AO-14 | Hook Git environment built twice | D: keep `commands` behavior |
| AO-15 | Linked-position refusal ×6, partial-result attach ×2 | P |
| AO-16 | Small duplicates (`PERIOD`, `_shown`, `RUN_ID`, "and N more" ×7) | P |
| AO-17 | Stale `.devkit/architecture.toml` entries (integration→rules edge, `root_modules = ["bootstrap"]`) | P |
| AO-18 | Two process-group runners | K: different semantics |
| AO-19 | `worktree/repositories/execution.py` used only by isolated_execution | K: edge stays either way |

### devkit-spec (SP)

| Key | Finding | Proposed |
| --- | --- | --- |
| SP-1 | Two "paths changed since base" pipelines in scope (registry vs collection) | F: own work item; unresolved-reason codes and runners differ |
| SP-2 | Dead duplicate modules `utils/output.py`, `proposals/models/axes.py` (previous run said moved) | P |
| SP-3 | Plan-intent removal leftovers (`_record_gates` branches, one-element tuples, alias) | P |
| SP-4 | Three `status:` rewriters | see X-5 |
| SP-5 | Proposal anchor lookup ×5 | D: `proposal_anchor` in `base/units.py`; declarations' single-file fallback kept |
| SP-6 | Function wrappers around use cases | P |
| SP-7 | Unused constants (`SPEC_WORKFLOWS`, `INTEGRATION_GATE`, `FORMS`, `_PARTIAL_POINTER`) | P |
| SP-8 | Re-exports of devkit-docs names left by the move | P |
| SP-9 | Worktree-clean checks in several forms | see X-8 |

### devkit-dist (DS)

| Key | Finding | Proposed |
| --- | --- | --- |
| DS-01 | `[playbooks]` bounds validated ×3 (local overlay hardcodes numbers) | D: one checker; local overlay uses the constants; bool rejected everywhere |
| DS-02 | `config.toml` shared validation duplicated; `read_config` validates twice | D: `_load` delegates; message form with target kept |
| DS-03 | Playbook entrypoint resolution duplicated (get/search) | P |
| DS-04 | `planned_subagent_changes` rebuilds inventory inputs (effective vs canonical mix) | D: canonical, like `_inventory_inputs` |
| DS-05 | Native agent roots listed in 5 places | P: derive from `inventory.AGENTS` |
| DS-06 | Entry-point provider loop ×3 | see X-1 |
| DS-07 | Tree by-product filter duplicated | P |
| DS-08 | Third-party shared-artifact adapter path with no provider | C — recommend keep (documented extension) |
| DS-09 | Subagent projection hand-rolled YAML quoting | C/F: projected bytes change on next sync |
| DS-10 | Git tracked/ignored probes ×4 | F: low priority |
| DS-11 | Transient JSON reads repeated in sync | P |
| DS-12 | Receipt-overrides copy ×5 | P |
| DS-13 | Slug grammar repeated | P |
| DS-14 | Test-only search API members (`bm25_scores`, `limit=`, `to_dict`) | C |

### devkit-docs (DC)

| Key | Finding | Proposed |
| --- | --- | --- |
| DC-1 | Bundle/anchor path grammar ×6, copies disagree | D: one set of predicates beside `base/layout.py`; strict grammar (`PROP-` prefix, exact depth) |
| DC-2 | Historical-path rule re-derived in id_convention | D: `DocumentIndex.is_historical_path`; ID-less files kept covered |
| DC-3 | Dependency-cycle DFS ×2 | P |
| DC-4 | Frontmatter key-node lookup ×4 | D: `field_node` for the YAML callers; `field_line` kept |
| DC-5 | Entrypoint path re-exports; private `_bundle_dir` used by spec; `_within` | P (move `_bundle_dir` to spec) |
| DC-6 | Summary English/length check ×2 | D: shared helper; each rule keeps its messages |
| DC-7 | List page echo ×2 | P |
| DC-8 | Unused `_PARTIAL` regex | P |
| DC-9 | Body-start helper ×4 | D: callers keep their error fallback |
| DC-10 | Word-led slug check ×3 | P |
| DC-11 | `_usecase`/`_ux` grammar parallel | P |
| DC-12 | Refusal-notice attach ×2 | P |
| DC-13 | Orphan comments | P |
| DC-14 | Dead `GlossaryInvalidError` defaults | P |
| DC-15 | One-field `DocsConfig` wrapper | K |

### Small packages (SM)

| Key | Package | Finding | Proposed |
| --- | --- | --- | --- |
| SM-1 | adaptive | Verb-string dispatch in service, use cases and CLI | P: one function per operation |
| SM-2 | core/mcp | `McpTool.execution` has 5 values, runtime distinguishes 2; `read_only` duplicates it | C |
| SM-3 | core | `status_records` parameters used only by core tests | C |
| SM-4 | adaptive | Git records re-encoded as porcelain dicts | P |
| SM-5 | mcp | `build_server` binding never `None` | P |
| SM-6 | mcp | Two linked-source predicates | P |
| SM-7 | viewer | Hand-rolled worktree listing | P |

## Decisions (user, in one round, as recommended)

| Disposition | Items |
| --- | --- |
| Behavior-preserving consolidation/removal (one `sdd-overall-refactor` work item, branch `dev-review-refactor-2`) | All `P` items: X-6, X-7, X-11, X-12, X-14, AW-01/02/04/06/07/09/10/11/12/13/14/15/17, AO-04, AO-05 (except `ui_action`), AO-06/07/10/12/15/16/17, SP-2/3/6/7/8, DS-03/05/07/11/12/13, DC-3/5/7/8/10/11/12/13/14, SM-1/4/5/6/7 |
| Consolidation with decided differences (same work item) | All `D` items with the proposed kept behavior: X-1 (isolate SystemExit and discovery failure everywhere; mcp keeps raising), X-2, X-3, X-4 (agt paragraph-end rule; docs reference behavior change approved), X-5 (comments kept; missing key per caller), X-8, X-10, AW-03, AW-05, AW-08, AO-02, AO-03, AO-08, AO-11, AO-14, SP-5, DS-01, DS-02, DS-04 (canonical inputs), DC-1 (strict grammar), DC-2, DC-4, DC-6, DC-9. Each caller keeps its own error codes and messages unless stated. |
| Contract changes (own work items, normal development workflow) | AO-01 retire `worktree finish --merge`; SM-2 `McpTool.execution` to `read_only`/`bounded_write`; AO-05b `ui_action` removal; AO-13, SM-3, DS-14 test-only public parameters/APIs |
| Keep | AW-16, AO-18, AO-19, DC-15, DS-08 |
| Defer | SP-1 (scope pipelines: own work item later), X-9, X-13, DS-09, DS-10 |

## Changes

Route: `sdd-overall-refactor`, branch `dev-review-refactor-2`; each commit body is the change record (findings,
preservation evidence, differentials, verification before and after).

| Commit | Change |
| --- | --- |
| `4539847e` | Phase 1: shared helpers in devkit-core, `devkit_dist.adapters.cli`, the agt scanner and docs parse |
| `69f18d3b` | adaptive, mcp, viewer (SM-1/4/5/6/7, X-1, X-8, X-12, X-14 partly) |
| `b967f06e` | devkit-dist (DS-01/02/03/04/05/07/11/12/13, X-1, X-2, X-3) |
| `cfeb971a` | devkit-agt workflow and rules (AW-01..10, AW-12..15, AW-17, X-3, X-5, X-8) |
| `ce093e23` | devkit-agt other features (AO-02..08, AO-10..12, AO-14..17, X-1, X-2, X-10, X-11) |
| `6996b227` | devkit-docs (DC-1..6, DC-8..14, X-1, X-4..7, X-12) |
| `0a6ff65c` | devkit-spec (SP-2/3/5/6/7/8, X-3, X-5..8, X-12) |
| `90964fb2` | scripts, receipt and capability references |
| `c4bd651c` | Independent review fixes (flow-collection comments, config check order, merge method) |

## Behavior changes

Approved in the round and applied: X-1 isolation of `SystemExit` and failed discovery everywhere (mcp and integration
cleanup raise their own errors); X-4 docs code-span ends; X-5 frontmatter keys rewritten in place with comments kept,
any `status` value replaced; X-8 sorted, de-duplicated dirty paths; AW-03 `as_posix` display outside the root; AW-08
one fix text; DC-1 strict path grammar (non-`PROP-` names, wrong depth, feedback and paths outside a proposals root are
no units; none occur in the repository); DS-01 bool never a number; DS-02 shared-file messages carry their target;
DS-04 canonical inventory inputs; AO-08 maintenance gh calls hardened, last HTTP block read; X-10 template wrapping.

## Not applied, with reason

- AW-11: no module both `workflow` and `rules` may import holds a CLI quote helper.
- DC-7: `list`'s page line carries `hidden=`, which the shared `echo_page` cannot emit.
- AO-05 `_prepare(lifecycle, settle_generated)`: devkit-spec's composed acceptance needs both flags.
- X-12 for the dist root: `devkit --version` must import no area (tested); the root keeps its own option.
- X-14 `overlaps` and the scope observation `git config` reads (X-2/AO-11): the shared helpers would drop accepted
  inputs or the scope runner's hardening.

## Review

Independent `code-reviewer` (medium): no P1/P2; three P3 fixed in `c4bd651c`.

## Outcome

`applied` (partially: see above). Follow-up contract work items: AO-01, SM-2, AO-05b, AO-13/SM-3/DS-14. Deferred:
SP-1, X-9, X-13, DS-09, DS-10.
