---
name: spec-sync
description: Reconcile a completed feature spec and discovered behaviors into the durable Living Spec (docs/capabilities/, docs/stories/) and its reconcile.md record, so documentation never rots.
---

# spec-sync: Living Specification Reconciliation Workflow

Use this skill right after `spec-review` passes: the `living-spec-draft` stage (it opens on `envelope-review-passed`). It promotes what the feature spec established into the Living Spec. Read the `living-spec-writing` instruction before editing `docs/`.

---

## 1. Prerequisites & Inputs

- The feature's `spec.md` and `tasks.md` in `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`, and the actual code changes.
- `docs/capabilities/`, `docs/stories/`, `docs/architecture/`, `docs/decisions/`.

---

## 2. Reconciliation Principles

- Transient task lists stay in `specs/`; ADRs are append-only (a new ADR with `supersedes` replaces one). No index tables in directory `README.md` files (`devkit spec list <kind>`, `devkit spec refs <ID>` list them).
- Link capabilities and stories both ways by exact ID in frontmatter (`stories:` in a capability, `capabilities:` in a story; `RULE-traceability-link`, and `devkit rules fix <document>` appends a missing reverse link); never nest one kind inside the other.
- Rewrite a changed statement in place, citing the deciding ADR or spec by full ID where the reason matters; no dated notes or history sections. A new capability or story starts from `.devkit/managed/spec/templates/capability.md` (or `story.md`).

### Verification and confirmation
- The implementer writes, fixes and resolves the reflection and `reconcile.md`. Verification: `low` self-check; `medium`/`high` read-only `reconcile-reviewer` (`spec-delegate`), at `high` in the bounded rounds of the `spec` skill's `references/review-loop.md`. The `spec` skill's `references/effort.md` defines medium's initial self-check exception (record omission reason and evidence) and discretionary repeat calls. Every check is a `reconcile-check` envelope. A `session` has none: Living Spec impact raises it to `spec`.
- Implementation-versus-contract mismatches are returned for a code fix (the stage returns to `build-verify`, or `fix-verify` for a bugfix), not endorsed by documentation or waived.
- Confirmation (`reconcile.md` `status: resolved`, spec `status: completed`) is done by the Developer or the integration executor (`spec-integrate`), before the `dev-integration` gate. Intermediate commits do not complete this stage; the final check is `devkit rules check --ci --base <ref>`.

## 3. Reconciliation Workflow

### Step 1: Identify Impact on Permanent Backbone
- Read `spec.md` and the code changes; `devkit spec refs <ID> --direction in` and `devkit spec search "<topic>"` find the documents a changed behavior is described in.
- New user story → `docs/stories/<area>/US-<slug>.md`; new capability → `docs/capabilities/<area>/CAP-<AREA>-<slug>.md`; changed capability → edit it; changed architecture → `docs/architecture/`.
- Did the change introduce or rename a domain term? Then update `docs/glossary.md` where it exists, by the Glossary section of the `living-spec-writing` instruction.

### Step 2: Document Reconciliation Record
The `spec` skill's `references/completion.md` holds the evidence rules (waivers, required mismatches). Retain resolved records in place.
- Create `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/reconcile.md`: one target per Living Spec file changed, and the no-impact reasoning in the body when there is none. Check results belong in the final change report envelope, not here.

```yaml
---
reconcile_id: REC-<slug>
feature: SPEC-<slug>
status: pending            # pending | resolved
targets:
  - file: docs/capabilities/<area>/CAP-<AREA>-<slug>.md
    resolution: modified   # modified | waived (with a substantive rationale)
---
```
- In a registered task worktree, then run `devkit spec scope update --spec <dir>` (`SPEC_SCOPE_TOKEN_MISSING`: not registered, skip); `[SCOPE_ACK]` overlaps inform scheduling, never block.

### Step 2a: Hand Off Deferred Work
- Apply the Deferred Work Handoff in the `spec` skill's `references/completion.md` before deleting a source proposal or marking the spec completed, and record the destination in `reconcile.md`. Never transfer unmet requirements still in the agreed scope to make the feature appear complete.

### Step 2b: Resolve Source Feedback
- Apply [Source feedback resolution](../spec/references/completion.md#source-feedback-resolution) to the spec's
  explicit open direct-fix sources. Record their resolutions and verification, or remaining scope, in
  `reconcile.md`. Terminal sources need no disposition or re-verification. Handoff never resolves open feedback;
  unrelated newly captured feedback stays open.

### Step 2c: Sync Entrypoints from the Bundle
- Run the `spec-entrypoints` skill for this bundle: derive (doc, code) candidates, review them, apply the chosen ones. A document whose `entrypoints` changed is a `modified` target in `reconcile.md`.

### Step 3: Run Deterministic Lint Gates
- Run `devkit rules check --staged` for staged changes or `devkit rules check --ci --base <ref>` for a committed branch, and state which scope was checked; follow each violation's remediation.
- Run the project's own lint (e.g., `just lint`) where it covers Markdown and Mermaid diagrams in the updated docs.

### Step 4: Mark the Feature Spec Completed
- Set `reconcile.md` `status: resolved` once every target is reflected or waived, then `status: completed` in `spec.md` (`devkit rules fix <dir>/spec.md` does it once every task is checked and the record is resolved). The stage exits on `frontmatter(reconcile.md status resolved)` and `anchor-status-completed`.
- Documentation updates go in the same commit as the feature code or the one right after it.

---

## 4. Definition of Done (DoD) for Sync
- [ ] Capabilities and stories reflect the change, linked both ways.
- [ ] `reconcile.md` `resolved`; concrete deferred work tracked or none retained; spec `completed`.
- [ ] `devkit rules check` (`--staged` or `--ci --base <ref>`) and the project lint pass with 0 errors.
