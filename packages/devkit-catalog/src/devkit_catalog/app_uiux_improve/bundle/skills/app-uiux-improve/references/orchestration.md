# Delegation: local roles and Impeccable

Local-role sections apply on both tracks; Impeccable sections apply only after the user selects Impeccable for
this request.

## Local roles

Resolve paths from the directory containing the invoked `SKILL.md`, not the working directory or this reference;
if its location is unavailable, locate and verify the invoked skill first. Verify the selected role file exists and
pass its absolute path to the subagent type below with the directive to read it before acting. Do not load every
role into the coordinator.

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

Prefer the smallest useful assignment; research and criticism are optional, and a critic can return zero findings.
Use separate instances only for differing questions or design premises; require no role count or debate.

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
   artifacts; product source edits stay with the coordinator through the existing workflow.
5. Validate that a return names its inspected artifacts, actual work, assumptions, limitations and any failed or
   unavailable action. A failed or missing role contributes no findings; continue inline when useful and report
   missing coverage. Reinvoke only after the input or cause changes.
6. Check consequential claims or conflicts selectively, without repeating a well-supported investigation in full;
   distinguish inspected evidence from analogy, taste and assumptions before synthesis.
7. Keep one useful critique/refinement pass as the default. Stop when the requested outcome and applicable checks
   are satisfied; never iterate to prove benefit, fill an issue quota or reach agreement.

Example assignment (illustrative; assign a different mechanism only when it serves the actual user task):

```text
Read <absolute-skill-directory>/roles/unconventional-designer.md first.
Goal: make conflicts in a mobile calendar understandable and recoverable.
Artifacts: supplied conflict states; preserve attendees and event details.
Assignment: explore a decision-inbox flow instead of a calendar-grid interaction.
Actions: read the supplied artifacts; return suggestions only, no source or retained-file edits.
Stop: return one concrete task sequence, affected states, expected benefit, tradeoff and weakest assumption.
```

## Impeccable session

Impeccable is a separately installed design skill with its own commands, detector and project files; this bundle
ships none of it. A delegated session is not a local role: it may edit the product files its brief lists, and you
accept its changes before they continue through the consumer workflow.

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
3. Complete the consumer workflow's steps that precede implementation before delegating.

### Brief

Write a self-contained brief with these fields:

- Goal and the framing result for this request, citing the project's OOUX documents by path as read-only sources
  instead of restating them, or the conversation framing when none exist.
- Consumer-supplied drafts or specifications for the change, by path, read-only.
- Absolute working directory and the recorded base: HEAD, working-tree status and content hashes of the listed files
  under Git; the listed files' content hashes otherwise.
- Edit list: the product files the session may edit.
- Unchanged files and concerns: data schema, business logic, dependencies, the OOUX documents, and files with
  uncommitted user edits unless the user includes them. The session leaves index, HEAD and commits unchanged.
- Context-file permission: list `.impeccable/design.json`, `.impeccable/config.json` or `.impeccable/surfaces/` when
  the session may write them; list `PRODUCT.md` or `DESIGN.md` only on the user's explicit direction.
- Commands to run, the stop condition and the expected return: changed files, commands run, detector or audit
  results, session output, degraded coverage and blockers, including any upstream question.

### Route the command

- Fresh child: run only commands that refine existing surfaces without user answers, such as `polish`, `audit` or
  narrow refinement commands like `distill`, `typeset` or `layout`. The child loads Impeccable through the host's
  skill mechanism and reads `PRODUCT.md` and the brief.
- If the child cannot load Impeccable or meets an upstream question, it returns that as a blocker and never answers
  the question; move the command to a session the user operates.
- User-operated session: new work, `init`, `shape` and `critique` ask the user questions (`critique` also needs two
  isolated sub-agents), so hand the user the brief to run in their own Impeccable session and wait for their report.
  The user may start `shape` from the brief; for a fresh child, your framing covers its structural role.
- Exclude `live` and any other route that turns off the host's sandbox or approvals.
- Make no product edits until the session returns.

### Accept the return

1. Compare the working directory with the recorded base.
2. Take changes to listed product files into verification and continue them through the consumer workflow.
3. Report session output (critique snapshots, mocks, hook and runtime state under `.impeccable/`) as session output.
   Report any other change outside the edit list without reverting or deleting it, and do not deliver it as
   accepted work.
4. If HEAD moved, the base is missing or an ignored path cannot be observed, report attribution as unverifiable or
   coverage as limited.
5. Report each OOUX document (glossary, object register or UX document) the accepted change made stale. Edit none
   of them in this run; the consumer workflow's own step updates them.

### Project files and user requests

- `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files (`config.json`, `design.json`, `surfaces/`, critique
  snapshots) are consumer-owned project context. Report the ones a session created or changed and point to upstream's
  "Project files and git" guidance for what to commit or ignore.
- `PRODUCT.md` can hold a short OOUX reference section that names the glossary, object register and UX document
  directory by path and says to read them before structural work. Copy none of their content into it.
- On the user's request, and not on your own initiative, you may:
  - install Impeccable through a route in "Select and set up";
  - add upstream's recommended ignore entries, confined to `.impeccable/` paths (prefixed in the root `.gitignore` or
    in `.impeccable/.gitignore`), after showing the user the exact lines;
  - remove Impeccable runtime or session output the user names, such as screenshots or `review/`;
  - add the OOUX reference section to `PRODUCT.md`.
- Leave `PRODUCT.md` and `DESIGN.md` out of any cleanup the user does not name them in. Change them, or let a session
  change them, only on the user's explicit direction.
- Carry every user-requested change through the consumer workflow and the host's approvals like any product change.

Example brief:

```text
Goal: make overdue invoices recoverable from the customer view.
Framing: objects Customer and Invoice per docs/steering/glossary.md and docs/steering/ux-objects.md (read-only);
  states per docs/ux/billing/ (read-only); "Send reminder" sits on an overdue Invoice.
Drafts: none. Working directory: /abs/project. Base: HEAD a1b2c3d, clean status, hashes of the listed files.
Edit list: src/views/CustomerDetail.tsx, src/components/InvoiceRow.tsx.
Unchanged: data schema, business logic, dependencies, OOUX documents, PRODUCT.md, DESIGN.md, index and HEAD.
Commands: polish, then audit. Stop: both finish or a blocker occurs.
Return: changed files, commands run, audit and detector results, session output, degraded coverage, blockers.
```
