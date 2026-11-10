---
id: PADR-impeccable-session-authority
title: Bounded Impeccable sessions under coordinator acceptance
summary: For user-selected Impeccable craft work, we let one bounded session edit only brief-named product files while the coordinator accepts, verifies and delivers the result through the consumer workflow, keeping context isolated, accepting host-dependent enforcement.
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
commands and writes project context files that its README recommends committing. Running it inside the coordinator's
context loads its instruction set into the rest of the improvement request; running it in a separate session lets a
second actor edit the working tree. The skill must state who may edit what, when that actor runs and who answers for
the result, without granting workflow authority the consumer has not given.

## 2. Decision Drivers

- Keep consumer workflow, permissions and approvals authoritative for every product change.
- Keep Impeccable's instruction volume out of the coordinator's context.
- Make every product edit attributable and checked before it is reported or delivered.
- Leave consumer-owned files in place; never delete or hide them without the consumer's direction.
- Keep small requests inexpensive; invoke no external skill the user did not select.
- Add no runtime, installer or vendored upstream text to devkit.

## 3. Considered Options

- Keep coordinator-only edits and borrow Impeccable perspectives as guidance: no authority change, but the user
  cannot apply Impeccable's maintained commands and detector through the skill.
- Brief-only handoff: the coordinator writes a brief, the user runs Impeccable in a session of their own, and the
  coordinator inspects the result as supplied artifacts. No delegated edits, but every craft round needs a manual
  round trip and the skill cannot finish a selected Impeccable track by itself.
- Coordinator runs Impeccable commands in its own context: edits stay with the coordinator, but the external
  instruction set shares the coordinator's context for the rest of the request.
- Bounded delegated session under coordinator acceptance: on the user's selection, one Impeccable session edits only
  the product files its brief names; the coordinator pauses its own edits, inspects the resulting changes, verifies
  them and continues through the consumer workflow. Context stays isolated; the file boundary is behavioral and is
  checked after the session.

## 4. Decision Outcome

Chosen option: bounded delegated session under coordinator acceptance, because it keeps Impeccable's instructions out
of the coordinator's context while every product change still passes the coordinator's inspection and the consumer's
checks and approvals. A session the user runs from the same brief is the route when no fresh child is available.

- The coordinator starts an Impeccable session only when the user selects the Impeccable track for the request;
  an installed Impeccable permits an offer, not an invocation. → `CAP-DLV-uiux-improvement` rule 15 (MUST).
- The coordinator never installs Impeccable. When it is absent, the coordinator names the upstream install routes
  and continues inline if the user wants. → `CAP-DLV-uiux-improvement` rule 10 (MUST).
- The session receives a self-contained brief: goal, framing result, the product files it may edit, the files and
  concerns it leaves unchanged (data schema, business logic, dependencies), the Impeccable commands to run, the stop
  condition and the expected return. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The session leaves index, HEAD, commits and every file outside the brief's edit list unchanged. It writes
  Impeccable project context files (`PRODUCT.md`, `DESIGN.md`, shared `.impeccable/` files) only when the brief lists
  them. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The brief excludes Impeccable's `live` mode and any other route that turns off the host's sandbox or approvals,
  because such a route bypasses the consumer's permissions. → `CAP-DLV-uiux-improvement` rule 16 (MUST).
- The coordinator makes no product edits while the session runs. A fresh child where the host supports one and a
  session the user runs from the same brief follow the same brief and acceptance. → `CAP-DLV-uiux-improvement`
  rule 16 (MUST).
- After the session, the coordinator compares the working tree with its state before the session, takes changes
  inside the edit list into verification and reports any change outside it to the user without reverting or deleting
  it. → `CAP-DLV-uiux-improvement` rule 17 (MUST).
- The coordinator owns synthesis, acceptance, verification and continuation of accepted changes through the
  consumer's existing workflow. Selection or delegation grants no commit, integration or publication authority.
  → `CAP-DLV-uiux-improvement` rules 3 and 17 (MUST).
- Impeccable's project context files are consumer-owned project files. The coordinator reports which ones the session
  created or changed, with upstream's commit-versus-ignore guidance, and changes neither them nor `.gitignore`
  without the user's direction. → `CAP-DLV-uiux-improvement` rule 14 (MUST).
- Local roles keep returning suggestions and evidence only; the delegated session is not a local role.
  → `CAP-DLV-uiux-improvement` rule 9 (MUST).

On promotion, this decision supersedes Decision Outcome clause 2 of `ADR-uiux-improvement-workflow-boundary` in
part: its coordinator-only continuation of requested implementation now admits one user-selected, brief-bounded
Impeccable session whose changes the coordinator accepts before continuing. That clause's statements that selection
changes no workflow policy and grants no commit, integration or publication authority stay in force, as do clauses
1, 3 and 4.

## 5. Consequences

- Positive: the user can apply Impeccable's maintained commands within one improvement request while the
  coordinator's context carries only the brief and the session's return.
- Positive: every delegated edit is compared against the brief before the coordinator reports or delivers it.
- Negative: the edit list is a behavioral boundary. A host without per-path write limits cannot prevent an
  out-of-list edit, only expose it afterward.
- Negative: uncommitted user edits in a listed file make attribution unreliable, so the brief leaves such files out
  unless the user includes them.
- Risk: Impeccable's commands, files and install routes are upstream contracts that can change. The skill names them
  without vendoring them; a session that finds a changed contract reports it in its return.
- Follow-up: when the user asks to retain or ignore Impeccable files, the coordinator applies that request through
  the consumer workflow as an ordinary product change.

## 6. Confirmation

- The renamed integration test (`test_entry_preserves_improvement_scope_and_consumer_authority` and the delegation
  assertions planned beside it) checks the selection, brief, pause, acceptance and file-ownership instructions.
- Review only: whether a host enforces the edit list and whether a delegated session honors its brief.
