---
reconcile_id: REC-direct-planning-procedure
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconcile: SPEC-direct-planning-procedure

## CAP-DLV-delivery-workflows

- §4.6 role table: the `planning-worker` row's Skill column now says the procedure is in
  `spec/references/planning.md`, which the contract cites (AC-05).
- §4.6 contract-body sentence: the roles whose procedure lives in the contract are `challenger`, `scout` and the
  `development-worker`; a new sentence says the Planning steps live in the `spec` skill's `references/planning.md`
  because a main session runs Planning in `direct` mode, and the contract keeps only the worker's own obligations
  (`ADR-executor-neutral-planning-steps-in-a-spec-reference`).
- Frontmatter `entrypoints`: adds `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/planning.md`,
  beside the `review-loop.md` entrypoint already listed.

## Checked without change

- `CAP-HARN-agent-guidance`: its subagent row lists asset ids only (`planning-worker` stays). Its "Skill references"
  paragraph is a selection, not a complete list (it already omits `effort.md`, `review-loop.md` and
  `worker-records.md`), so the new reference needs no entry there, as
  `ADR-executor-neutral-planning-steps-in-a-spec-reference` §5 decides.
- `CAP-DLV-proposal-incubation`, `CAP-DLV-workflow-envelopes`, `CAP-DLV-project-policy`, `CAP-DLV-spec-bundles`: no
  statement on where the Planning steps live; the steps' content is unchanged, so their Planning and envelope
  contracts hold.
- `docs/architecture/`: no statement on role procedures.
- The rest of `CAP-DLV-delivery-workflows` §4.6 (the workers' shared obligations: worktree, nested roles, records,
  emergency commit) still holds; both workers keep those obligations in their contracts.
