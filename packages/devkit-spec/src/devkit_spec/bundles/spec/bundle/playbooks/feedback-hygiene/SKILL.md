---
name: feedback-hygiene
description: Triage open feedback files under specs/ in one hygiene session; group them by target, order them by severity and recurrence, and with the user's decision promote them to rules, playbooks, decisions or spec work, or dismiss or forward them and update their status.
---

# Feedback hygiene

Run this playbook only in a hygiene session the user invoked or confirmed, from a clean working tree or a task worktree. You
propose and draft; destinations beyond existing authorization are the user's decisions. A direct fix resolves its
feedback through the `spec` skill's
[source feedback resolution](../../skills/spec/references/source-feedback.md) instead.

## Step 1: Collect and group

```bash
uv run devkit docs list feedback --status open --all-namespaces -n 0
```

- If the listing is empty, report an empty backlog and stop. Narrow with `--where scope=<scope>` or
  `--where severity=<a>,<b>` only when the user names one.
- When the listing has more than 5 items and the host runs the `triage` role natively, delegate the rest of this step
  and the Step 2 recommendation to it through `spec-delegate`, from a clean checkout (`git status --porcelain`
  empty); verify and present its return as the `spec` skill's `references/backlog.md` (Backlog roles) says.
  Otherwise run this step inline; on a dirty checkout, delegate from a clean task worktree or run it inline.
- Confirm each item's ownership (`repo`, `upstream`, `unknown`) from its target and evidence; do not ask the user.
- Group items by `target`; a group shares one decision.
- Order by `critical`, then `recurring: true`, then `blocked`, `workaround`, `noise`.
- An item without observed Evidence is a dismissal candidate.

## Step 2: Decide the destination with the user

| Scope | Destination | Action |
| :--- | :--- | :--- |
| `repo` | Rule | Draft it with the `spec-rule` skill |
| `repo` | Playbook | Draft `playbooks/<slug>/SKILL.md` as a `kind = "playbook"` asset of the in-repository bundle (devkit's `in-repo-bundle` instruction) |
| `repo` | Decision | Draft an ADR from `.devkit/managed/spec/templates/decision.md` |
| `repo` | Fix | A defect: a `bugfix` task; a wording fix: a `session` change; an open design question: `uv run devkit spec proposal new <slug>` |
| `upstream` | Forward | Draft a report for the owning tool; submit only with explicit external-send authorization |
| `unknown` | Ownership review | Propose destinations; keep unresolved items open |
| any | Dismissal | A reasoned decline |

Record the source FB IDs in the destination's `Source feedback` or the session's agreed scope.

## Step 3: Update status

- `promoted`: follow-up work received the item. It stays `promoted` when that work finishes.
- `dismissed`: a reasoned decline.
- `forwarded`: only after the authorized submission. A draft or an unresolved ownership stays `open`.

Append a disposition line to each item, linking every destination for a cross-tool item:

```markdown
- **Disposition**: <destination ID, path or report location>: <one-line summary or dismissal reason>
```

## Step 4: Stale branches and rejected proposals

`uv run devkit rules check -p hygiene` also reports:

- `[STALE_BRANCH: ...]`: offer resume or discard per the `spec` skill's
  [stale branches](../../skills/spec/references/branches.md#4-leftovers-and-stale-branches); do neither unasked.
- `SPEC_PROPOSAL_REJECTED_PENDING`: once the user agrees, write the rejection ADR quoting the reason from the
  rejection commit (`git log -1 --format='%H %B' -S'status: rejected' -- <proposal.md>`), preserve feedback by the
  [feedback retirement procedure](../../skills/spec/references/feedback-retirement.md), and delete the proposal in the
  same commit.

## Completion conditions

- Every dispositioned item has a terminal status and a disposition line; items left `open` are reported.
- Every rejected proposal listed is cleaned up or reported as left.
- `uv run devkit rules check` exits `0`, and the changes are proposed as one commit; its body names the `triage` role
  when one was used.
