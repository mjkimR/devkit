---
name: spec-sync
description: Reconcile a completed feature spec and discovered behaviors into the durable Living Spec (docs/capabilities/, docs/stories/) and its reconcile.md record, so documentation never rots.
---

# spec-sync: Living Specification Reconciliation Workflow

Use this skill right after `spec-review` passes: the `living-spec-draft` stage (it opens on `envelope-review-passed`).
It promotes what the feature spec established into the Living Spec. Read the `living-spec-writing` instruction before
editing `docs/`.

## 1. Prerequisites & Inputs

- The feature's `spec.md` and `tasks.md` in `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`, and the actual code changes.
- `docs/capabilities/`, `docs/stories/`, `docs/architecture/`, `docs/decisions/`.

## 2. Reconciliation Principles

- Keep transient task lists in `specs/`.
- Record a changed decision as a new ADR that sets `supersedes`, not as an edit in place. Edits that keep the decision
  (wording, stale names, references, consolidation through the `adr-compaction` playbook) are allowed.
- Write no index tables in directory `README.md` files; `devkit spec list <kind>` and `devkit spec refs <ID>` list
  them.
- Link capabilities and stories both ways by exact ID in frontmatter: `stories:` in a capability, `capabilities:` in a
  story (`RULE-traceability-link`; `devkit rules fix <document>` appends a missing reverse link). Never nest one kind
  inside the other.
- Rewrite a changed statement in place, citing the deciding ADR or spec by full ID where the reason matters. Write no
  dated notes or history sections.
- Start a new capability or story from `.devkit/managed/spec/templates/capability.md` (or `story.md`).

### Verification and confirmation

- The implementer writes, fixes and resolves the reflection and `reconcile.md`.
- Verification by `activity-effort`:
  - `low`: self-check;
  - `medium`: read-only `reconcile-reviewer` (`spec-delegate`); the `spec` skill's `references/effort.md` defines
    medium's initial self-check exception (record omission reason and evidence) and discretionary repeat calls;
  - `high`: read-only `reconcile-reviewer` in the bounded rounds of the `spec` skill's `references/review-loop.md`.
- Every check is a `reconcile-check` envelope. A `session` has none: Living Spec impact raises it to `spec`.
- Return an implementation-versus-contract mismatch for a code fix (the stage returns to `build-verify`, or
  `fix-verify` for a bugfix); never endorse it by documentation or waive it.
- The Developer or the integration executor (`spec-integrate`) does the confirmation (`reconcile.md`
  `status: resolved`, spec `status: completed`) before the `dev-integration` gate.
- Intermediate commits do not complete this stage; the final check is `devkit rules check --ci --base <ref>`.

## 3. Reconciliation Workflow

### Step 1: Identify Impact on Permanent Backbone

- Read `spec.md` and the code changes. Find the documents a changed behavior is described in with
  `devkit spec refs <ID> --direction in` and `devkit spec search "<topic>"`.
- Map each change to its document:
  - new user story → `docs/stories/<area>/US-<slug>.md`;
  - new capability → `docs/capabilities/<area>/CAP-<AREA>-<slug>.md`;
  - changed capability → edit it;
  - changed architecture → `docs/architecture/`.
- If the change introduced or renamed a domain term, update `docs/glossary.md` where it exists, by the Glossary
  section of the `living-spec-writing` instruction.

### Step 2: Document Reconciliation Record

The `spec` skill's `references/completion.md` holds the evidence rules (waivers, required mismatches). Retain resolved
records in place.

- Create `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/reconcile.md` with one target per Living Spec file changed. If there is
  none, write the no-impact reasoning in the body.
- Put check results in the final change report envelope, not here.

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

- In a registered task worktree, then run `devkit spec scope update --spec <dir>`. On `SPEC_SCOPE_TOKEN_MISSING` the
  worktree is not registered: skip it. `[SCOPE_ACK]` overlaps inform scheduling, never block.

### Step 2a: Hand Off Deferred Work

- Before deleting a source proposal or marking the spec completed, apply the Deferred Work Handoff in the `spec`
  skill's `references/completion.md`, and record the destination in `reconcile.md`.
- Never transfer unmet requirements still in the agreed scope to make the feature appear complete.

### Step 2b: Resolve Source Feedback

- Apply [Source feedback resolution](../spec/references/completion.md#source-feedback-resolution) to the spec's
  explicit open direct-fix sources.
- Record their resolutions and verification, or remaining scope, in `reconcile.md`.
- Terminal sources need no disposition or re-verification.
- Handoff never resolves open feedback; unrelated newly captured feedback stays open.

### Step 2c: Sync Entrypoints from the Bundle

- Run the `spec-entrypoints` skill for this bundle: derive (doc, code) candidates, review them, apply the chosen ones.
- A document whose `entrypoints` changed is a `modified` target in `reconcile.md`.

### Step 3: Run Deterministic Lint Gates

- Run `devkit rules check --staged` for staged changes or `devkit rules check --ci --base <ref>` for a committed
  branch. State which scope was checked and follow each violation's remediation.
- Where the project's own lint (e.g., `just lint`) covers Markdown and Mermaid diagrams in the updated docs, run it.

### Step 4: Mark the Feature Spec Completed

- Once every target is reflected or waived, set `reconcile.md` `status: resolved`, then run
  `devkit rules fix <dir>/spec.md`, which sets `spec.md` `status: completed` once every task is checked.
- The stage exits on `frontmatter(reconcile.md status resolved)` and `anchor-status-completed`.
- Put documentation updates in the same commit as the feature code or the one right after it.

## 4. Definition of Done

- [ ] Capabilities and stories reflect the change, linked both ways.
- [ ] `reconcile.md` `resolved`; concrete deferred work tracked or none retained; spec `completed`.
- [ ] `devkit rules check` (`--staged` or `--ci --base <ref>`) and the project lint pass with 0 errors.
