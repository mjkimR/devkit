# Evidence for Q1 and Q2 (Planning, worktree HEAD a09ce5300)

## How handoff rewrites become current overlap

- `features/scope/services/collection.py` `observe()`: a Development unit's observation adds every path changed in
  `committed(root, sha, base_sha, cap)`, the range from the unit's base to its head. The handoff commit is the first
  commit of a `dev-<slug>` branch, so its reference rewrites (`SPEC_PROPOSAL_REFS_REWRITTEN`) enter as `observed`
  paths of the unit.
- `horizon()` returns `future` only for a Planning activity's declared or candidate paths; an `observed` path of a
  spec unit is always `current`. `compare()` emits one evidence entry per overlapping path pair with `source`,
  `other_source` and `horizon`. So the output already tells an `observed`-only overlap apart from a declared target
  (`declared-doc`, `declared-code`, `candidate`), but not a handoff-commit path from a worker-commit path.

## Q1: can a worker still need to edit a handoff-rewritten path?

- Yes, in two ways: a planned Living Spec update (reconcile or target-docs) or `_Boundary:` naming the same file, and
  an unplanned edit (link repair after a move).
- The first is already caught independently of the handoff: the unit's declarations add the path as `declared-doc`
  or `declared-code`, both `current` for a spec unit, so the pair still overlaps on non-`observed` evidence.
- The second is bounded by the worker's write boundary (`_Boundary:` is the expected scope; an extension is reported),
  and becomes visible once committed: the path then appears in `git diff --name-only <handoff commit>..<worker head>`.
- What remains after excluding both is a reference rewrite the Host's handoff transaction already completed. Two such
  rewrites on one file conflict only at integration, which `spec-integrate` already runs one unit at a time in
  overlap order. Concurrent Development adds no new conflict there.

## Q2: provenance in code, path class, or wording

- Path class is unsafe: the rewritten files in the source feedback were a capability, an ADR, pilot evidence, sibling
  proposal files and a milestone, exactly the classes workers also edit as declared Living Spec targets.
- Provenance in code would need collection to identify each unit's handoff commit, split the committed range and add
  a new evidence source to the `scope collect` output contract (CAP-COLL-work-scope-registry), with tests. The Host
  already has the handoff `commit` from the handoff return (`git-operator-operations.md`, `handoff` row) and the
  per-entry `source`, so it can apply the same distinction with one `git diff --name-only` per unit.
- The sibling-alias handoff bugfix (branch `dev-handoff-sibling-alias-rewrite`, not landed) adds alias rewrites
  inside the same handoff commit, limited to the files the handoff carried and promoted. A provenance rule keyed to
  "changed only by the unit's handoff commit" covers them without change; a path-class rule would not.
- The source feedback is `recurring: false`, `severity: workaround`.

## Living Spec mirror

The scheduling sentence in `spec-orchestrate/SKILL.md.jinja` is mirrored in CAP-HARN-agent-guidance, section
"Host scope observation". CAP-COLL-work-scope-registry describes collection output, which this change leaves as is;
UC-run-parallel-work-safely step 6 already says the Host uses overlaps, horizon and provenance.
