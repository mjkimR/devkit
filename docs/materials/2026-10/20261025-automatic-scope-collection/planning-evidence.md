# Planning evidence: explicit Host work scope collection

## Scope and provenance

Planning starts from `main` at `10269581972a4dce7eddf8ffaf77b8bb3bfc6bfd`. The proposal at that commit declares no
`depends_on` prerequisite. This is a local reversible feature with Planning/Development effort `medium`.
The source Scout read that base without changes; Codex role isolation is emulated. The Host owns all proposal edits.
Runtime acceptance remains Development work.

## Source findings

| Concern | Evidence | Decision |
| --- | --- | --- |
| Existing creation registration | `features/delivery/usecases/handoff.py:56`, `specs.py:57`; `features/scope/usecases/flow.py:233-257` | Keep linked-worktree registration; remove worker repair directives from automatic failures |
| Full inventory | `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:182-183`, `stale.py:129-150` | Reuse Git primitives, not higher application use cases; preserve all refs |
| Collapsing branches loses evidence | `features/policy/repositories/branches.py:104-129` prefers local planning refs | Do not reuse its slug-to-single-ref mapping |
| Pinned unit discovery | `features/worker/usecases/inputs.py:48-59,106-130` | Extract a scope-owned source reader; verify markers and exact slug matches |
| Mixed-source risk | `features/scope/usecases/inputs.py:71-109,137-157,206-254` uses filesystem reads throughout | Read targets, entrypoints and granularity through the same source as task declarations |
| Historical cap | `features/scope/usecases/inputs.py:311-334`; `tests/integration/features/scope/test_flow.py:235-309` | Preserve registered cap/intersection; unregistered ranges use an explicitly labelled merge-base-to-tip diff |
| Comparison cost | `features/scope/services/compare.py:30-37,54-56` traverses path pairs for every task pair | Keep matching semantics, introduce cooperative deadline checkpoints for collection comparison |
| Discovery | `features/scope/cli/commands.py:260`; `packages/devkit-dist/tests/integration/adapters/test_cli.py:295-304` | Hidden commands remain callable and introspectable; ordinary discovery must filter hidden commands |
| Strict warnings | `packages/devkit-cli/src/devkit_cli/output.py:135-138` | Explicit partial results exit 0, or 1 under strict; inability to run exits 2 |

Paths beginning `features/` and `tests/` above are relative to `packages/devkit-spec/src/devkit_spec/` and
`packages/devkit-spec/` respectively. Public source labels and matching semantics stay unchanged; report provenance
adds observation IDs outside the stored registry schema.

## Reproducible Git and comparison probe

Run from the repository: `uv run python docs/proposals/PROP-automatic-scope-collection/materials/probe.py.txt`.
The script writes a synthetic Git repository and JSON results beneath `/tmp`; it does not mutate this repository.
The captured result is `probe-results.json`. Environment: Python 3.12.3, Git 2.43.0, Linux/WSL2, local `/tmp` storage.

| Probe | Three elapsed times (seconds) | Median (seconds) |
| --- | --- | --- |
| 8 refs, seven Git calls each | 0.2321 / 0.1968 / 0.2036 | 0.2036 |
| 80 refs, seven Git calls each | 1.7843 / 1.7498 / 1.8992 | 1.7843 |
| Existing comparison: 8 sets, 20 paths each | 0.00314 / 0.00328 / 0.00274 | 0.00314 |
| Existing comparison: 80 sets, 100 paths each | 7.7663 / 7.7176 / 7.1110 | 7.7176 |

The comparison probe performs 31,600,000 path-pair checks in the larger case. The smaller repository pipeline proves
pinned declarations ignore a dirty Host checkout, merging the selected integration base excludes upstream-only
paths, and a stacked branch compared to the integration base includes its parent's paths. All assertions passed.

The fixture has tiny objects, warm local caches and disjoint code paths. It omits registry IO, permissions,
network fetch, large tree enumeration and overlap-output allocation. It is not an end-to-end collector benchmark.
A default 30-second total and 5-second source budget leave room for the measured work but promise no universal
latency. Development must enforce deadlines during comparison and retain explicit incomplete-pair coverage.

## Hidden-command probe

The Host changed `scope_group.commands['update'].hidden` only in memory, invoked Click through `CliRunner`, then
restored the value. Ordinary help omitted update and direct `update --help` succeeded. `list_commands` still included
update. A repository Python search found no production tree-walking command-discovery generator requiring changes;
the recursive walker in dist's CLI tests intentionally checks hidden leaves too. Source guidance must remove update
obligations and agent-facing listings must omit it; do not alter Click's dispatch/introspection contract globally.

## Alternatives and review limits

| Option | Operational cost | Limitation | Disposition |
| --- | --- | --- | --- |
| Skill-maintained updates | Worker tokens, retries and ACKs | Snapshot lag remains possible | Replace |
| Creation snapshots only | Minimal runtime cost | Misses later local/published changes | Keep as lowest observation mode |
| Workflow-next collection | Hook/provider and worker recovery design | Worker timing does not prove Host decision freshness | Exclude |
| Explicit Host collection | On-demand scanning and comparison | Partial remote/private visibility | Select |
| Cloud-backed registry now | Backend/identity/auth/publication contracts | Still cannot see later private edits | Future direction only |

No production source-reader extraction, total-deadline cancellation, fetch/auth integration, permission denial,
unstable worktree detection or full output-schema test was performed. AC-01–AC-08 require Development fixtures for
these behaviors. Source analysis, synthetic probes and a Challenger review support a direction decision only.

## Challenger resolution and Host verification

The independent medium-effort Challenger reviewed committed source `4ae2de071c86b99a1db5dc65545aeafe3f3516e2`
and returned two P2 findings. The Host folded both within the settled direction:

1. Deduplication now requires equivalent tip, selected base, historical cap, range semantics and declaration source.
   AC-05 retains same-SHA/different-base observations. Dirty layers remain distinct.
2. Section 3.6 caps declaration bytes, retained observations/pairs/evidence and encoded report size. It reserves
   summary/coverage space, returns complete entries only, and marks omitted work partial using bounded diagnostics.
   AC-06 requires dense-overlap and oversized-input fixtures. Result preparation uses the total deadline;
   blocked stdout consumers are explicitly outside its computation guarantee.

The Host checked the amended contract, acceptance criteria and PADR for agreement. No waiver was taken. Runtime
verification of these limits remains Development work; the original disjoint benchmark does not prove them.
The PADR also carries a machine-readable limited `supersedes` link and a metadata-only reciprocal ADR target.
