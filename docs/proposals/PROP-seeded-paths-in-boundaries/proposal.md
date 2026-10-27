---
id: PROP-seeded-paths-in-boundaries
title: Seeded and synced paths in proposal boundaries
summary: Lets a proposal's write scope cover the tracked files devkit sync writes because of the agreed change, such as a new seed in a selected preset, so Development does not stop on a path Planning could not name.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-27
target_area: delivery/
priority: high                        # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja
    - packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py
    - docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    - .devkit/installation.json
  excludes:
    - docs/decisions/
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/proposal_boundaries/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-seeded-paths-in-boundaries] Seeded and synced paths in proposal boundaries

## 1. Background & Hypothesis

A proposal's `boundaries.owns` becomes Development's write scope, and `RULE-proposal-boundaries` admits only paths
that exist at Planning (or their nearest parent). A change that adds a seed to a preset the repository selects makes
`devkit sync` write a new tracked file, such as `docs/ux/README.md` from the `docs-skeleton` seed in
`SPEC-ux-documentation`, that Planning could not name. The worker then stops on a problem until the Host admits the
path by hand. `.devkit/installation.json` and `AGENTS.md` do not hit this only because they already exist.

Hypothesis: the tracked outputs that `devkit sync` writes because of the agreed change can be derived, or at least
declared, so the handoff write scope includes them without a Host decision each time.

## Source feedback (when this proposal receives feedback)

- `FB-new-seed-sync-output-outside-boundaries`: the whole observation, a seeded path outside the handed-off write
  scope that stopped Development.

## 2. Technical Spike Questions

- **Q1**: Can Development derive the sync outputs of its own bundle change (for example from `devkit sync --check` in
  the worktree), or must Planning declare them?
  - Answer: the worker already derives them: `devkit sync` prints `[CHANGE: seed <path>]` and records the path under
    `seeded` in `.devkit/installation.json` (`docs/ux/README.md` is there now). The gap is only that the Host builds
    the payload before the change exists, so `devkit sync --check` on the accepted head lists no new seed. A
    derivation command would run after the change and duplicate `sync --check`; no code is needed.
- **Q2**: If declared, what does `RULE-proposal-boundaries` accept: a seeded target path the change creates, named
  with its seed source?
  - Answer: not needed. Declaring would add rule syntax for a path the receipt records anyway, and Planning cannot
    always foresee every output (a projection a new skill adds, for example).
- **Q3**: Is a standing rule ("sync outputs that follow from the agreed change are admitted; record them in
  `_Boundary`") enough as procedure, without code?
  - Answer: yes. The stop comes from two sentences: the payload reference's "tracked files `devkit sync --check`
    lists for that change" and the `development-worker` contract's "A tracked sync output the write scope omits is a
    problem". In the session that observed it, the `ux-documentation` worker stopped on `docs/ux/README.md` until
    the Host admitted it (`worker-01`, `resolution-01` of `SPEC-ux-documentation`), while the
    `backlog-subagent-roles` worker, told the rule up front, completed without stopping. `devkit spec worker inspect`
    derives its scope from `_Boundary:` and strips parenthetical notes, so a recorded `(sync output)` entry needs no
    code.

## 3. Proposed Design & Impact

Wording only, in the `spec` bundle's delegation text and its capability (`PADR-admit-change-sync-outputs`):

1. **Payload** (`spec-delegate` `references/payload.md`, the bundle-source bullet): the write scope admits, as a
   named class, every tracked path `devkit sync` writes in the worktree after the change (seeded files, projected
   files, `.devkit/installation.json`, the managed `AGENTS.md` block), not only the files `devkit sync --check` lists
   before the change. `.devkit/managed/` stays ignored and never a write path.
2. **Worker contract** (`subagents/development-worker.md.jinja`, step 5 and Write boundaries): before the first
   edit, run `devkit sync --check` and record its exit as the `sync_start` check of the `worker` envelope; a nonzero
   exit (drift that does not follow from the change) is a problem, never a `(sync output)`. After the change, run
   `devkit sync`, commit every tracked file it writes and name each one the payload did not list in the owning task's
   `_Boundary:` with the note `(sync output)`, and in the `worker` envelope summary. The `.devkit/` denial excepts
   these outputs.
3. **Host validation** (`spec-delegate` `references/worker.md`, Validate): `devkit spec worker inspect` derives its
   scope from `_Boundary:` at the returned head, so its scope pass is no evidence for a `(sync output)` entry. For each
   `(sync output)` entry `tasks.md` gained between `<accepted>` and `<returned>`, the path passes only when the
   worker's `sync_start` check is `0`, `devkit sync --check` exits `0` on the returned head, and the path is under
   `seeded` or `files` in the returned head's `.devkit/installation.json`, is `.devkit/installation.json` itself, or
   is the file that holds the managed guidance block (`AGENTS.md`; the receipt records that block only as a hash).
4. **Living Spec**: the delegated bundle-source sentence of `CAP-DLV-delivery-workflows` states the same class.
5. **Test**: `test_delegation_sandbox_guidance.py` pins the new payload and contract sentences in place of the old.

Not changed: `RULE-proposal-boundaries`, `devkit spec worker inspect`, `devkit sync` and any CLI. The interim
Host-admitted practice becomes the standing rule.

## Planning decisions

- Q3 (standing procedure) chosen over Q1 (derivation) and Q2 (declaration): the evidence shows the stop is a
  wording gap, and the existing receipt and `_Boundary:` parsing already carry what code would add.
- `challenger-01` (three P2, all folded): the receipt check names the receipt and the guidance-block file, the
  clean start is recorded as `sync_start`, and the Host checks `(sync output)` entries itself rather than trusting
  `worker inspect`'s scope pass.
- `size: S`, `dev_effort: low`: four text edits and one test update in one package plus its capability.
- Direct acceptance (`accept --direct`) no longer applies: Planning was requested (plan-intent) and the proposal is
  in `reviewing`; this turn ends ready for `plan-accept`.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr seeded-paths-in-boundaries "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept seeded-paths-in-boundaries --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff seeded-paths-in-boundaries.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
