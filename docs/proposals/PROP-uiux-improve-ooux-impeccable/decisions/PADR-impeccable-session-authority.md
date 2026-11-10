---
id: PADR-impeccable-session-authority
title: Bounded Impeccable sessions under coordinator acceptance
summary: For user-selected Impeccable craft work, we let one bounded session edit only brief-named product files under coordinator acceptance and let the coordinator set up or clean up only on the user's request, keeping consumer authority and context isolation, accepting host-dependent enforcement.
proposal: PROP-uiux-improve-ooux-impeccable
supersedes: [ADR-uiux-improvement-workflow-boundary]
status: draft
created_at: 2026-11-10
---

# [PADR-impeccable-session-authority] Bounded Impeccable sessions under coordinator acceptance

- **Status**: Draft
- **Date**: 2026-11-10

---

## 1. Context & Problem Statement

`ADR-uiux-improvement-workflow-boundary` lets only the coordinator change product files. Local roles return
suggestions and leave product source, retained files, index and HEAD unchanged, and the capability excludes automatic
companion skill invocation. Impeccable, a separately installed design skill, changes product source through its own
commands, writes project context files that its README recommends committing and writes its own session output under
`.impeccable/`. A project may also keep its OOUX model in a glossary, an object register and UX documents that the
consumer's own workflow maintains. Several of its commands ask the user questions before they act (new work, `init`,
`shape`,
`critique`). Running it inside the coordinator's context loads its instruction set into the rest of the improvement
request; running it in a separate session lets a second actor edit the working tree. The skill must state who may
edit what, when that actor runs and who answers for the result, without granting workflow authority the consumer has
not given. Installing Impeccable and removing its output are steps the user can take by hand; the skill must say
when the coordinator may take them instead.

## 2. Decision Drivers

- Keep consumer workflow, permissions and approvals authoritative for every product change.
- Keep Impeccable's instruction volume out of the coordinator's context.
- Make every product edit attributable and checked before it is reported or delivered.
- Leave consumer-owned files in place; never delete or hide them without the consumer's direction.
- Let the user hand routine setup and cleanup to the coordinator without the coordinator acting on its own.
- Keep one source for the object model; reference the consumer's OOUX documents instead of copying them.
- Keep the user in the loop wherever Impeccable asks the user; no actor answers on the user's behalf.
- Keep small requests inexpensive; invoke no external skill the user did not select.
- Add no runtime, installer or vendored upstream text to devkit.

## 3. Considered Options

- Keep coordinator-only edits and borrow Impeccable perspectives as guidance: no authority change, but the user cannot
  apply Impeccable's maintained commands and detector through the skill.
- Brief-only handoff: the coordinator writes a brief, the user runs Impeccable in a session of their own, and the
  coordinator inspects the result as supplied artifacts. No delegated edits, but even a narrow refinement needs a
  manual round trip.
- Coordinator runs Impeccable commands in its own context: edits stay with the coordinator, but the external
  instruction set shares the coordinator's context for the rest of the request.
- Bounded delegated session under coordinator acceptance: on the user's selection, one Impeccable session edits only
  the product files its brief names; a fresh child runs refinement commands that need no user answers, and the user
  runs interactive commands from the same brief. The coordinator pauses its own edits, then inspects, verifies and
  continues through the consumer workflow. Context stays isolated; the file boundary is behavioral and is checked
  after the session.

## 4. Decision Outcome

Chosen option: bounded delegated session under coordinator acceptance, because it keeps Impeccable's instructions out
of the coordinator's context while every product change still passes the coordinator's inspection and the consumer's
checks and approvals. Routing interactive commands to a session the user runs keeps Impeccable's questions with the
user. Setup and cleanup stay steps the user takes or requests, so the coordinator gains no initiative over consumer
files, and the OOUX reference section keeps one source for the object model.

- Without the user's selection of the Impeccable track, the coordinator neither starts an Impeccable session nor loads
  or invokes Impeccable in its own context. An installed Impeccable permits an offer. Output of a hook the user
  installed is consumer check evidence, not an invocation. → `CAP-DLV-uiux-improvement` rule 15 (MUST).
- When Impeccable is absent, the coordinator names the upstream install routes and continues inline if the user wants.
  → `CAP-DLV-uiux-improvement` rule 10 (MUST).
- On the user's request, and never on its own initiative, the coordinator may install Impeccable through an upstream
  route that needs no prompt answers, add upstream's recommended ignore entries confined to `.impeccable/` paths after
  showing the user the exact lines, remove Impeccable runtime or session output the user names, or add an OOUX
  reference section to `PRODUCT.md`. A user-directed action is the consumer's decision and goes through the consumer
  workflow and the host's approvals. An installer that asks questions goes to the user as an exact command, because no
  actor answers on the user's behalf. → `CAP-DLV-uiux-improvement` rule 19 (MUST).
- `PRODUCT.md` and `DESIGN.md` stay out of any cleanup the user does not name them in, and any change to them, by the
  coordinator or by a session the brief permits, needs the user's explicit direction. → `CAP-DLV-uiux-improvement`
  rule 19 (MUST).
- The OOUX reference section in `PRODUCT.md` names the consumer's OOUX documents by path and copies none of their
  content. → `CAP-DLV-uiux-improvement` rule 19 (MUST).
- Before delegating, the coordinator completes the consumer workflow's steps that precede implementation (for example
  a branch, worktree or required record). → `CAP-DLV-uiux-improvement` rule 3 (MUST).
- The session receives a self-contained brief: goal, the framing result citing the consumer's OOUX documents by path
  read-only (or the conversation framing when none exist), consumer-supplied drafts or specifications by path
  read-only, the absolute working directory, the recorded base, the product files it may edit, the files and concerns
  it leaves unchanged (data schema, business logic, dependencies, the OOUX documents, files with uncommitted user
  edits unless the user includes them), whether it may write consumer context files, the commands to run, the stop
  condition and the expected return. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The recorded base is HEAD, the working-tree status and the content hashes of the listed files where the project uses
  Git, and the listed files' content hashes otherwise. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- A fresh child runs only commands that refine existing surfaces without user answers (`polish`, `audit` and narrow
  refinement commands), loading Impeccable through the host's skill mechanism. New work, `init`, `shape` and
  `critique` run in a session the user operates from the same brief. A child that meets an upstream question or cannot
  load Impeccable returns it as a blocker and never answers it; the coordinator moves the command to the user's
  session. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The brief excludes Impeccable's `live` mode and any other route that turns off the host's sandbox or approvals,
  because such a route bypasses the consumer's permissions. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The session leaves index, HEAD, commits and every file outside its permitted classes unchanged. It writes consumer
  context files (`PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, `.impeccable/config.json`,
  `.impeccable/surfaces/`) only when the brief permits them. Impeccable's own session output (critique snapshots,
  mocks, hook and runtime state under `.impeccable/`) is permitted and reported as session output. →
  `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The coordinator makes no product edits while the session runs. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- After the session, the coordinator compares the working directory with the recorded base, takes changes to listed
  product files into verification and reports any other change without reverting or deleting it on its own initiative.
  A moved HEAD, a missing base or a change to an ignored path it cannot observe is reported as unverifiable
  attribution or limited coverage. → `CAP-DLV-uiux-improvement` rules 10 and 17 (MUST).
- After accepting a change, the coordinator reports each consumer OOUX document (glossary, object register or UX
  document) the change made stale; the skill run edits none of them, and their update follows the consumer workflow's
  own step. → `CAP-DLV-uiux-improvement` rule 17 (MUST).
- The coordinator owns synthesis, acceptance, verification and continuation of accepted changes through the consumer's
  existing workflow. Selection or delegation grants no commit, integration or publication authority. →
  `CAP-DLV-uiux-improvement` rules 3 and 17 (MUST).
- Consumer context files are consumer-owned project files. The coordinator reports which ones the session created or
  changed, with upstream's commit-versus-ignore guidance. → `CAP-DLV-uiux-improvement` rule 18 (MUST).
- Local roles keep returning suggestions and evidence only; the delegated session is not a local role. →
  `CAP-DLV-uiux-improvement` rule 9 (MUST).

On promotion, this decision supersedes Decision Outcome clause 2 of `ADR-uiux-improvement-workflow-boundary` in
part: its coordinator-only continuation of requested implementation now admits one user-selected, brief-bounded
Impeccable session whose changes the coordinator accepts before continuing. That clause's statements that selection
changes no workflow policy and grants no commit, integration or publication authority stay in force. Clauses 1 and 3
stay in force, and clause 4 stays in force for local roles; an Impeccable child receives its brief and Impeccable's
own instructions.

## 5. Consequences

- Positive: the user can apply Impeccable's maintained commands within one improvement request while the coordinator's
  context carries only the brief and the session's return.
- Positive: every delegated product edit is compared against the brief before the coordinator reports or delivers it.
- Negative: new work and other interactive commands still need a session the user operates.
- Negative: the edit list is a behavioral boundary. A host without per-path write limits cannot prevent an out-of-list
  edit, only expose it afterward; ignored paths can escape a Git comparison.
- Risk: Impeccable's commands, files and install routes are upstream contracts that can change. The skill names them
  without vendoring them; a session that finds a changed contract reports it in its return.
- Positive: Impeccable commands that load `PRODUCT.md` see the object model through its reference section, without a
  copy that drifts.
- Negative: a stale UX document stays stale until the consumer workflow updates it; the skill only reports it.
- Negative: whether a fresh child can load Impeccable depends on the host and is unverified on every host (Claude Code
  documents Skill-tool discovery for subagents, Codex only skill inheritance); where it cannot, refinement also needs
  the user's session.

## 6. Confirmation

- The renamed integration test (`test_entry_preserves_improvement_scope_and_consumer_authority` and the delegation
  assertions planned beside it) checks the selection, brief, command routing, question return, pause, acceptance,
  stale-document report, file-ownership and user-requested setup and cleanup instructions.
- Review only: whether a host enforces the edit list and whether a delegated session honors its brief.
