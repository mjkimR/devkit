# Review-refactor run: guidance and CLI surfaces (2026-11-11)

Run of the `maintenance/review-refactor` playbook, read from
`packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/` (this repository does
not select the `maintenance` bundle). It follows the code-surface run of the same day
(`docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`).

## Intake

- **Run ID**: `rr-20261111-guidance-cli`.
- **Repository**: devkit monorepo, `main` at `2f40fe8c` (clean).
- **Surfaces and roots**:
  - `guidance`, three batches:
    - G1: the spec bundle (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`, rules excluded).
    - G2: the docs and adaptive-dev bundles (rule guides included, rule code excluded).
    - G3: the devkit, advisory, git_commits, harness, authoring, devkit-dev, starter and catalog bundles; the root
      `AGENTS.md` outside the managed block; `guides/`.
  - `cli`, one batch reviewed in three parts by owning package:
    - C1: devkit-dist (`add`, `bundle`, `config`, `get-context`, `host`, `list`, `override`, `playbook`, `remove`,
      `shared`, `status`, `sync`).
    - C2: devkit-agt (`exec`, `gate`, `generated`, `integration`, `maintenance`, `rules`, `run`, `workflow`,
      `worktree`).
    - C3: `spec`, `docs`, `adaptive`, `mcp`, `viewer`.
- **Compatibility policy**: no shims while there are no external consumers, except `devkit.advisory` and the
  devkit-cli semver API. A removed migration note (G3-8, G3-9) falls under this policy. The known consumer
  repositories (app-common, autohub, resource-indexer, rside) already pin post-split devkit-dist.
- **Order**: the reviews ran in parallel. The decision rounds went CLI first, then guidance.

## Coverage

Six read-only reviewers, one per guidance batch and CLI part. Each listed what it read. The Host rechecked at least
the cited location of these findings before the decision rounds: G1-3, G1-4, G1-10, G2-1, G2-2, G2-4, G3-3, G3-4,
C1-1, C1-3, C2-2, C2-5, C2-6 and the C3-4 drift.

| Batch | Gaps | Dropped without a named cost |
| --- | --- | --- |
| G1 | spec-rule skill only listed; cloud branches of `.jinja` read, not rendered; no representative-task runs | 8 (+3 counted) |
| G2 | adaptive-dev not selected here, so its projection was not read; seed skeletons partly read | 11 |
| G3 | maintenance playbooks other than review-refactor, deep_research and app_uiux_improve bodies only swept; catalog `cli_tool` guides §4-§5; parts of new-repository.md and mcp.md | 14 (+3 counted) |
| C1 | use-case error paths not traced; `status` vs `sync --check` not compared by behavior | 11 |
| C2 | `gate` and `generated` checked at help/caller level only | 14 |
| C3 | `worker inspect` and `scope collect` sentinel sets not opened | 14 |

No reviewer ran representative tasks, so no guidance removal relies on reduction ground 4.

## Findings

### Guidance G1 (spec bundle)

| Key | Location | Cost | Decision |
| --- | --- | --- | --- |
| G1-1 | Tier B scope-extension contract in 7 files | each change repeated 7 times plus token tests | consolidated to three owners |
| G1-2 | envelope-commit rule in 7 places | eligibility and recovery repeated | `envelope.md` §5 canonical |
| G1-3 | guidance passes the no-op `finish --local-only` | keeps a dead flag alive | moved to unit B |
| G1-4 | "local MCP executor", "through MCP" | names removed tooling | removed |
| G1-5 | worker/Host verification boundary in 5 files | 5 copies plus pinned tests | reduced to the isolated-execution, worker and payload owners |
| G1-6 | post-landing procedure restated in 4 assets | repeated landing procedure | points at `spec-integrate` steps 6-9 |
| G1-7 | composed acceptance repeated in dispatch | duplicate | removed |
| G1-8 | constitution UX bullet (always loaded) | always-loaded, restated on demand | one-line pointer |
| G1-9 | direction-handoff rule repeated in planning.md | duplicate of worker-records §1 | removed |
| G1-10 | dangling citation "(01 §6.1, 03 §3)" | unresolvable source | removed |
| G1-11 | retired `[integration] provider` note in sdd-baseline | retired concept kept alive | removed |
| G1-12 | proposals-catalog restates `--help`; padr hint lacks `--slug` | flag mirroring, conflicting directive | reduced; hint fixed |

### Guidance G2 (docs and adaptive-dev bundles)

| Key | Location | Decision |
| --- | --- | --- |
| G2-1 | qa-tester and reviewer overlays state their directive twice | merged |
| G2-2 | milestone template carries the spec close/drop/reopen lifecycle | removed (stays in spec milestone-completion) |
| G2-3 | docs instructions restate spec rules (task coverage, `plan.md`, `specs/`) | neutral wording; alias rule kept neutral in docs (no spec-side owner exists) |
| G2-4 | change-delta paragraph in the id_convention guide | folded into §2/§3 |
| G2-5 | decision_supersession guide repeats findings and the instruction | trimmed |
| G2-6 | adaptive approach check stated three times with different failure handling | single rule in the adaptive-dev skill |
| G2-7 | Host checkpoint restated in four files | current-context reference canonical |
| G2-8 | "coordinator" and "Host" name one actor | "Host" |
| G2-9 | current-context reference lists every template field | shortened |
| G2-10 | docs rule guides cite a spec rule and an unconditional spec command | dropped / conditioned |
| G2-11 | document-writing also scopes agent assets (duplicate of agent-asset-writing) | scope narrowed |

### Guidance G3 (other bundles, root guide, guides)

| Key | Location | Decision |
| --- | --- | --- |
| G3-1 | root `AGENTS.md` Verification (about 2.6 KB of Host procedure, always loaded) | applied, then extended by the user: the section keeps the completion checks and links `docs/development/setup.md` and `docs/development/ci-cd.md`. Root guide 10417 → 7643 bytes |
| G3-2 | devkit-dev `testing.md` repeats the root tier and worker split | testing.md owns tier selection |
| G3-3 | facts-memo paragraph in three rule guides | removed |
| G3-4 | landing-verification paragraph in five install guides | one copy in verification-ownership.md |
| G3-5 | Cloud setup section in four guides | INSTALL_GUIDE canonical, links elsewhere |
| G3-6 | docs-only choice restated three times | Step 3 canonical |
| G3-7 | adaptive setup restated in route files | links to INSTALL_GUIDE |
| G3-8 | former-`incubation` migration block (three copies) | removed; the test is relaxed to check only the add command |
| G3-9 | package-split upgrade section | removed (consumers checked); README link paragraph removed with it |
| G3-10 | `[integration]` provider sentences in guides and harness | guidance removed; the legacy key reader in code deferred |
| G3-11 | snapshot/refresh procedure inside `in-repo-bundle` and the guide | new `content-snapshot` instruction |

### CLI

| Key | Finding | Decision |
| --- | --- | --- |
| C1-1 | `host status --host` accepts one value | removed (unit B) |
| C1-2 | `playbook search --min-score/--min-similarity/--mode` no caller | kept: parity with `docs search` |
| C1-3 | `bundle refresh --check` means preview, unlike `sync --check` | preview without digests (unit C) |
| C1-4 | `status` and `sync --check` overlapping readiness gates | deferred: measure each command's detection first |
| C1-5 | `shared put/list` duplicate filter options with drifted help | shared help table |
| C2-1 | `worktree finish --local-only` no-op | removed (unit B) |
| C2-2 | `worktree` group help names the retired landing | help fixed |
| C2-3 | 22 `maintenance history` options without help | help added |
| C2-4 | `exec` paging/tail/timeout options without ranges; `wait` docstring | help added |
| C2-5 | `workflow envelope new` hidden though the main writer | unhidden (unit C) |
| C2-6 | `rules check/fix --summary-only` no caller | removed (unit B) |
| C2-7 | `workflow next --workflow`, `handoff --date` no caller | removed (unit B) |
| C2-8 | three paging contracts | deferred: revisit with the next exec output revision |
| C3-1 | 23 `adaptive assignment` options without help, template docstrings | help added |
| C3-2 | `spec scope register/query/compare/update` unused by guidance | group help leads with `collect`; the retirement is deferred and grouped with SP-1 |
| C3-3 | `scope collect` options no caller varies | deferred with C3-2 |
| C3-4 | `proposal accept` hides two operations behind `--mode` | deferred: needs a design choice (own proposal) |
| C3-5 | `spec new --workflow` vs `proposal new --task-kind` | `spec new --task-kind` (unit C) |
| C3-6 | `scope query --history` switches operation | deferred with C3-2 |
| C3-7 | `docs list --query` overlaps `docs search` | removed (unit B) |

## Changes

| Work item | Findings | Commits on main | Delta (excluding the receipt) |
| --- | --- | --- | --- |
| CLI help text (`dev-review-refactor-cli-help`) | C1-5, C2-2, C2-3, C2-4, C3-1, C3-2 (help) | `3d3a9b64`, landed `347b20ff` | 6 files, +133/−72 |
| Guidance (`dev-review-refactor-guidance`) | G3-1 to G3-10 | `e564afed`, `e7f5f457` | 16 files +51/−187; 3 files +12/−25 |
| | G2-1 to G2-11 | `18e985c8` | 21 files, +36/−54 |
| | G1-1, G1-2, G1-4 to G1-12 | `d442726e` (+ format `d3a82bf1`), landed `1ec42664` | 33 files, +59/−106 |
| Snapshot instruction (`dev-review-refactor-snapshot-guidance`) | G3-11, plus the remaining `spec new --task-kind bugfix` examples | `b79564a3`, landed `d8e4394a` | 7 files, +49/−44 |
| Contract unit `SPEC-remove-unused-cli-options` | C1-1, C2-1 (+G1-3), C2-6, C2-7, C3-7 | landed `39d49e17` | see the unit |
| Contract unit `SPEC-cli-naming-consistency` | C1-3, C2-5, C3-5 | landed `45b0dfe8` | see the unit |

Preservation evidence:
- Every guidance removal or merge came with a retained-constraint map from its applying subagent, against the
  file and line where the constraint remains. Where a constraint had no other home, it was moved instead of dropped:
  - "commas and colons are allowed" → development-worker.
  - "Required results remain pending" → isolated-execution.
  - Choosing UX alternatives in Planning → planning.md.
  - `assignment list` before checkpointing → orchestration.md.
  - `--e2e` compatibility → testing.md.
- Pinned guidance tests moved to the kept wording, and the tests of the touched bundles passed in each checkout.
- Each checkout's result was applied to the work-item branch one at a time. The name-status file set and the file
  contents were compared with the checkout before each commit.
- The help-text change altered no option name, type, default, required-ness or validation. The Host reviewed the
  diff, including the `filters` refactor in `shared/cli.py`.

Inputs no longer accepted: they are listed in the two contract units, plus `ADR-remove-unused-cli-options-without-shims`.

## Behavior changes

- `bundle refresh`, `envelope new` visibility and `spec new --task-kind` (unit C). These are contract changes,
  recorded in `CAP-DIST-in-repo-bundles`, `CAP-DLV-cli-and-output` and `CAP-DLV-spec-bundles`.
- Guidance: the adaptive-dev skill now stops product work in the not-adaptive-dev branch as well as on an
  inspection failure (G2-6). The removed constitution line implied this; the skill now states it.

## Deferred and follow-ups

| Item | Reason | Restart condition |
| --- | --- | --- |
| C1-4 | detection sets unmeasured | record which problems each command detects |
| C2-8 | exec sentinel contract change | next exec output revision |
| C3-2, C3-3, C3-6 | ADR-host-owned-scope-observation retains them | together with the code-pass SP-1 |
| C3-4 | two designs (split subcommand or retire the basic planning form) | a proposal |
| G3-10 code | the legacy `[integration] provider` reader is code, a surface not selected in this run | a code pass |
| `FB-entry-skill-explains-unprintable-bound-elsewhere` | the devkit-workflow entry skill text explains a sentinel the CLI no longer prints (recorded by unit B) | feedback hygiene |

Drift found, deferred to a separate drift reconciliation (12 items):
- C1:
  - the `OverrideChange` docstring says `accept` does not synchronize;
  - the devkit-dist `cli.py` docstring names `host` as the MCP server;
  - the `host` group help contains "DispatchHostHook";
  - the reference `devkit list` row says "Like" where it means "Unlike".
- C2:
  - the `INTEGRATION_CLEANUP_INCOMPLETE` `[FIX]` and CAP-INT name different recovery commands;
  - the CAP-DLV-maintenance-history `start` row omits `--repository`;
  - the justfile `workflow` comment lists a nonexistent `requests` command;
  - `workflow new/bind` lack `--format`, which ARCH-08-1 §4 implies.
- C3:
  - the `proposal accept --mode` help says accept_and_handoff starts Development;
  - CAP-HARN-command-mount §4.2 omits `docs supersession`, `spec proposal report` and `spec worker inspect`;
  - CAP-DLV-proposal-lifecycle 446 contradicts 234 and delivery-workflows 403;
  - CAP-COLL lists the hidden `scope update/sweep` without a marker.
- G1: the `spec proposal new --milestone` help says "global" only, but the code also accepts namespace milestones.
  (This is a thirteenth item, found by the guidance review.)

## Decisions

- CLI round (user): apply A (help text) in full; unit B with C2-1, C1-1, C2-6, C2-7 and C3-7 (keep C1-2); unit C
  with C1-3, C2-5 and C3-5; defer D; reconcile drift separately.
- Guidance round (user): G1 all, G2 all, G3 all. G3-1 was extended at the user's request to move the Verification
  details into `docs/development`.

Counts:

| Found | Applied as refactor | Contract work items | Deferred | Kept | Pending |
| --- | --- | --- | --- | --- | --- |
| 54 | 39 (C3-2 help part; its retirement is also counted deferred) | 2 units (8 findings) | 6 + drift | 1 | 0 |

## Outcome

`applied`. All work items are integrated:
- the CLI help text at `347b20ff`;
- the guidance at `1ec42664`;
- unit C at `45b0dfe8`;
- unit B at `39d49e17`;
- the snapshot instruction at `d8e4394a`.

Final checks on `d8e4394a` against the saved baseline `2f40fe8c`:

| Check | Result |
| --- | --- |
| `just test-affected` | 5720 passed, 1 skipped |
| `just test-affected --tier e2e`, through `devkit exec` | 259 passed |
| `just test-dist` | 1400 passed |
| lint, pyright | clean |
| `devkit rules check --ci` | OK |
| `devkit generated check` | 0 stale |

## Drift reconciliation (follow-up run)

Run of the `maintenance/drift-reconciliation` playbook over the 13 drift items above, at `6b8ae109` (clean), the
user invoking it right after this run. Each item was rechecked at that revision before the decision round.

| Key | Item | Evidence | User decision | Correction |
| --- | --- | --- | --- | --- |
| D1 | `OverrideChange` docstring: accept does not synchronize | deterministic | update docs | docstring |
| D2 | devkit-dist `cli.py` docstring: host is the MCP server | deterministic | update docs | docstring |
| D3 | host group help "DispatchHostHook" | deterministic | fix code (help) | help text |
| D4 | reference `devkit list` "Like" → "Unlike" | deterministic | update docs | reference row |
| D5 | `INTEGRATION_CLEANUP_INCOMPLETE` `[FIX]` reruns prepare for a deleted branch; CAP-INT names the owning extension command | deterministic | fix code | `[FIX]` in service and error class; regression assertion in test_pull_request |
| D6 | maintenance history `start` row omits `--repository` | deterministic | update docs | CAP row |
| D7 | justfile `workflow` comment lists `requests` | deterministic | update docs | comment |
| D8 | `workflow new/bind` lack `--format` | rechecked: ARCH-08-1 requires only `-q/-v/--strict` on every command | no drift | none |
| D9 | `proposal accept --mode` help says Development starts | deterministic | fix code (help) | help text |
| D10 | command-mount catalog omits supersession, proposal report, worker inspect | deterministic | update docs | catalog rows |
| D11 | composed accept is "the single route" vs basic-form examples | semantic: local guidance uses `--mode`; the basic form is the cloud-pr route | update docs | lifecycle §, example, delivery-workflows row |
| D12 | CAP-COLL lists hidden `scope update/sweep` unmarked | deterministic | update docs | `(hidden)` markers |
| D13 | `--milestone` help says global only | deterministic | fix code (help) | help text |

Also repaired in the same change: the `spec new` `--task-kind`/`--workflow` conflict `[FIX]` (unit C) carried a
placeholder. `test_fixes_carry_no_placeholder` failed on main, but affected selection had not run it. That gap is
recorded as `FB-affected-selection-misses-cross-package-fix-scan`.

The corrections landed at `19e5fe71`. Checks on that HEAD:

| Check | Result |
| --- | --- |
| full `just test` | 7117 passed, 17 skipped |
| branch `just test-affected --tier e2e` | 350 passed, 13 skipped |
| lint, pyright, `devkit rules check --ci` | clean |
| generated | 0 stale |

Counts:

| Detected | Resolved | Not drift | Deferred | Waived | Pending |
| --- | --- | --- | --- | --- | --- |
| 13 | 12 | 1 | 0 | 0 | 0 |

This batch is fully reconciled. It makes no claim beyond these items.
