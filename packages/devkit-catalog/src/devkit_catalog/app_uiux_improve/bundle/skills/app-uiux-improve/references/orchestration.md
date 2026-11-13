# Delegation: local roles and Impeccable

Use local roles on either track. Use Impeccable sections only after the user selects it.

## Local roles

Resolve paths from the directory containing the invoked `SKILL.md`, not the working directory or this reference.
If unavailable, locate and verify the skill. Verify the selected role file exists; pass its absolute path to the
subagent type below with a directive to read it before acting. Load only selected roles.

- If the assignment interacts with a running UI (operating it, inspecting it in a browser or capturing it), spawn the
  host's general subagent (`general-purpose` on Claude Code), because those tools are outside `role-worker`'s list.
- Spawn a `role-worker` subagent for every other assignment.
- If `role-worker` is unavailable, stop that delegation and report the missing subagent and its cause, such as a
  deselected `devkit` bundle or a host without its projection; never spawn another subagent type in its place.

### Select assignments

| Local role | Useful assignment |
| --- | --- |
| `roles/designer.md` | Improve a concrete task flow, hierarchy or interaction state. |
| `roles/unconventional-designer.md` | Explore a different interaction or composition mechanism serving the same goal. |
| `roles/reference-researcher.md` | Find a precedent or evidence that changes a design choice. |
| `roles/critic.md` | Find consequential breakdowns or unnecessary burdens in supplied artifacts or a proposed direction. |

Research and criticism are optional; a critic can return zero findings. Use separate instances only for differing
questions or premises; require no role count or debate.

### Dispatch and receive

1. Give the child the user goal, relevant artifacts, hard constraints, open preferences, one concrete assignment,
   allowed reads/actions, an observable stop condition, its expected return and the absolute local role path; pass
   task-relevant facts, not the coordinator's full conversation.
2. Where supported, use a fresh context without parent conversation inheritance. If fresh children are unavailable,
   perform useful passes inline and disclose that they were not independent contexts. Preserve host restrictions;
   a role prompt supplies no enforcement guarantee or access permission.
3. Keep peer conclusions out of independent first-pass payloads; after returns arrive, give a selected refinement or
   critic only the material it needs. Make in-scope design choices without waiting for consensus.
4. Roles return suggestions, sketches or evidence, leave the index and HEAD unchanged and write no retained
   artifacts; product source edits stay with the coordinator through the selected route.
5. Validate inspected artifacts, actual work, assumptions, limits and failed/unavailable actions. A failed or missing role
   contributes no findings; continue inline and report missing coverage. Reinvoke only after input or cause changes.
6. Check consequential claims/conflicts selectively; distinguish evidence from analogy, taste and assumptions.
7. Default to one useful critique/refinement pass. Stop when outcome and checks are satisfied; require no issue quota,
   proof of benefit or agreement.

Example assignment:

```text
Read <absolute-skill-directory>/roles/unconventional-designer.md first.
Goal: resolve mobile calendar conflicts; preserve supplied attendees and event details.
Assignment: explore a decision-inbox flow. Read supplied states; return suggestions only, no edits.
Stop: one task sequence, states, benefit, tradeoff and weakest assumption.
```

## Impeccable session

Impeccable is separately installed; this bundle ships none of it. Its session may edit brief-listed product files,
unlike a local role. Accept its changes before continuing through the selected route.

### Select and set up

1. If the user has not selected Impeccable for this request, neither start a session nor load or invoke Impeccable in
   your own context; work inline. An installed Impeccable permits an offer. Treat output of a hook the user installed
   as consumer check evidence, not as an invocation.
2. If Impeccable is absent and the user wants it, name the upstream routes: `npx impeccable install` at the project
   root, the Claude Code route `/plugin marketplace add pbakaus/impeccable` followed by installing it from `/plugin`,
   or a manual copy of upstream `skills/impeccable` into the host's skill directory. Install only on the user's
   request, and run only a route that needs no prompt answers under the host's approvals: the manual copy, or the
   installer with non-interactive options whose values (scope, hook) the user stated, where upstream documents such
   options. Otherwise hand the user the exact command; the user runs interactive installers and the `/plugin` route
   and answers their prompts. The user can continue inline instead.
3. If the user selected the consumer workflow, complete its steps that precede implementation before delegating.
   Otherwise use the outside-workflow route already explicitly approved for this task; retain host permissions,
   product constraints and the same brief and acceptance boundaries.

### Brief

Write a self-contained brief with these fields:

- Goal and the framing result for this request, citing the project's OOUX documents by path as read-only sources
  instead of restating them, or the conversation framing when none exist.
- Consumer-supplied drafts or specifications for the change, by path, read-only.
- Non-goals: only user-stated constraints or explicit deferrals; a focus orders work without prohibiting in-goal changes.
- Precedence: authorized brief and consumer specification control craft defaults; return conflicts between authorized
  sources for a decision.
- Absolute working directory and the recorded base: HEAD, working-tree status and content hashes of the listed files
  under Git; the listed files' content hashes otherwise.
- Edit list: the product files the session may edit.
- Unchanged files and concerns: data schema, business logic, dependencies, the OOUX documents, and files with
  uncommitted user edits unless the user includes them. The session leaves index, HEAD and commits unchanged.
- Context-file permission: list `.impeccable/design.json`, `.impeccable/config.json` or `.impeccable/surfaces/` when
  the session may write them; list `PRODUCT.md` or `DESIGN.md` only on the user's explicit direction.
- If `PRODUCT.md` or `DESIGN.md` is untracked or excluded and the session runs elsewhere, pass absolute read-only
  paths. Keep consumer ownership and retention choices; infer no copy, commit, ignore or removal action.
- Commands to run, the stop condition and the expected return: changed files, commands run, detector or audit
  results, session output, degraded coverage and blockers, including any upstream question.

### Route the command

1. A fresh child can refine existing surfaces without user answers (`polish`, `audit` and narrow refinements),
   loading Impeccable through the host's skill mechanism and reading `PRODUCT.md` and the brief.
2. For new work, `init`, `shape` or `critique`, relay questions only after native loading and same-child continuation
   are observed for the actual host/project. Documentation, inherited skill names and cache reads prove neither.
   If unavailable or unverified, hand the user the brief for their own Impeccable session and wait for their report.
3. For `shape` and `critique`, also check the child's nested-role capabilities required by the loaded command.
   If unavailable or unverified, use the user-operated session; inline work cannot claim those roles ran.
4. Phase 1 only inspects and drafts questions: no retained-file, product, index or HEAD writes. Return the complete
   question packet with identifiers, suggested answers and source path/passage for each document-derived pre-fill.
   A child never answers an upstream question on the user's behalf.
5. Show the complete visible packet and confirm every answer, including every pre-fill. One explicit whole-packet
   confirmation is valid; silence, omitted answers and gaps-only confirmation are not. Preserve confirmed answers.
6. Resume the same child with the confirmed packet and same brief/base. Before writes, recheck relevant source facts and
   file state; if questions, answers or scope are affected, refresh the packet and confirm affected answers.
   Return additional questions before dependent writes. Lost continuation uses the user-operated session; never
   reconstruct a writing child from an assumed transcript.
7. If native loading fails, report observed current-project plugin enablement, native availability and the blocker;
   move the command to a session the user operates. Plugin cache reads are not a loading route; install or change
   enablement only on the user's setup request. An answer-free child meeting a question stops dependent writes
   and uses this confirmation route or the user-operated fallback.
8. Exclude `live` and any other route that turns off the host's sandbox or approvals.
9. Make no product edits until the session returns. Report partial execution against the recorded base without
   blindly replaying the command or reverting consumer files.

### Accept the return

1. Compare the working directory with the recorded base.
2. Accept only changes matching both the edit list and approved goal scope, then take listed product files into verification through the selected route.
   Report an in-list but out-of-scope change, such as an unrelated dependency bump; exclude it from accepted work
   without reverting or deleting it.
3. Report session output (critique snapshots, mocks, hook and runtime state under `.impeccable/`) as session output.
   Report any other change outside the edit list without reverting or deleting it, and do not deliver it as
   accepted work.
4. If HEAD moved, the base is missing or an ignored path cannot be observed, report attribution as unverifiable or
   coverage as limited.
5. Report each OOUX document (glossary, object register or UX document) the accepted change made stale, its affected
   statement and a concrete separate follow-up through the documentation process where present or a separate
   documentation task otherwise. Edit none in this run and create no follow-up record without a separate request.

### Project files and user requests

- `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files are consumer-owned project context.
  Report changed files and point to upstream's "Project files and git" guidance for retention.
- An OOUX reference section in `PRODUCT.md` names the glossary, object register and UX directory by path;
  copy none of their content. Say to read them before structural work.
- On the user's request, and not on your own initiative, you may:
  - install Impeccable through "Select and set up";
  - add upstream's recommended ignore entries confined to `.impeccable/` paths, after showing the user the exact lines;
  - remove Impeccable runtime or session output the user names;
  - add the OOUX reference section to `PRODUCT.md`;
  - link tracked context through this skill's helper, under its requested-setup and retention rules.
- Leave `PRODUCT.md` and `DESIGN.md` out of any cleanup unless named; change them only on the user's explicit direction.
- Carry every user-requested change through the selected route and host's approvals;
  reuse exact Git authority or obtain it before acting.

Example brief:

```text
Goal: recover invoices.
Framing: Customer/Invoice per docs/steering/glossary.md (read-only).
Drafts: none. Working directory: /abs/project. Base: HEAD a1b2c3d, clean status, listed-file hashes.
Edit list: src/views/CustomerDetail.tsx, src/components/InvoiceRow.tsx.
Unchanged: data schema, business logic, dependencies, OOUX documents, PRODUCT.md, DESIGN.md, index and HEAD.
Commands: polish, audit. Stop: finished or blocked.
Return: files, commands, audit/detector results, output, limits, blockers.
```
