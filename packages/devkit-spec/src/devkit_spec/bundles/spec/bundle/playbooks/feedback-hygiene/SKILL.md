---
name: feedback-hygiene
description: Triage open feedback files under specs/ in one hygiene session; group them by target, order them by severity and recurrence, and with the user's decision promote them to rules, playbooks, decisions or spec work, or dismiss or forward them and update their status.
---

# Feedback hygiene

Run this playbook only in a hygiene session the user invoked or confirmed, from a clean working tree or a task
worktree. Propose and draft; the user decides destinations beyond existing authorization.

- Resolve a direct fix's feedback through the `spec` skill's
  [source feedback resolution](../../skills/spec/references/source-feedback.md) instead.
- Leave terminal feedback to the `feedback-consolidation` playbook, which runs only when the user invokes or
  confirms it.

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
- Determine each item's ownership (`repo`, `upstream`, `unknown`) from its target and evidence instead of asking the
  user.
- Separate the observed symptom, its proposed cause and its suggested remedy. Check the relevant current code or
  contract, with a narrow reproduction only when needed. Mark unverified causes and treat the suggested remedy as a
  candidate. Repeated requests alone do not establish repeated remote effects.
- Classify the observation against the current contract: defect, normal behavior, improvement or already addressed;
  evidence of an event alone does not establish a defect.
- Treat normal, obsolete or already addressed items and items without observed Evidence as dismissal candidates. If
  evidence is insufficient to recommend a destination, keep the item open and name the missing fact.
- Group items by `target`; a group shares one decision.
- Order by `critical`, then `recurring: true`, then `blocked`, `workaround`, `noise`.

## Step 2: Decide the destination with the user

- Recommend the smallest sufficient response, such as a wording correction, removing unhelpful advice or an
  existing procedure.
- Before recommending a mechanism such as a cache, persistent state or a new extension point, state its known
  frequency and exposure (ordinary use or an exceptional case), demonstrated impact and one smaller alternative;
  mark unknown frequency or impact as unknown.
- Choose Planning depth apart from size and effort. For work starting now, use the `spec` classification: a settled
  fix with no contract impact can be a session; a settled contract change uses spec depth; an unresolved material
  choice about guarantees, policy or operation needs a proposal. Implementation details alone do not make the
  direction unsettled.
- Queue deferred work by the existing Backlog procedure, stating the material decision still needed or that the
  direction is settled.

| Scope | Destination | Action |
| :--- | :--- | :--- |
| `repo` | Rule | Draft it with the `spec-rule` skill |
| `repo` | Playbook | Draft `playbooks/<slug>/SKILL.md` as a `kind = "playbook"` asset of the in-repository bundle (devkit's `in-repo-bundle` instruction) |
| `repo` | Decision | Draft an ADR from `.devkit/managed/docs/templates/decision.md` |
| `repo` | Fix | A defect uses task-kind `bugfix`; choose depth by the classification above. Draft an unresolved material direction with `uv run devkit spec proposal new <slug>` |
| `upstream` | Forward | Draft a report for the owning tool; submit only with explicit external-send authorization |
| `unknown` | Ownership review | Propose destinations; keep unresolved items open |
| any | Dismissal | A reasoned decline |

Record the source FB IDs in the destination's `Source feedback` or the session's agreed scope.

## Step 3: Update status

- `promoted`: follow-up work actually received the item, whatever its size or effort; it stays `promoted` when
  that work finishes.
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
- `SPEC_PROPOSAL_REJECTED_PENDING`: once the user agrees, write the rejection ADR stating the decision and reason
  recorded in the rejection commit (`git log -1 --format='%H %B' -S'status: rejected' -- <proposal.md>`) as a decision
  sentence, never as a quote, preserve feedback by the
  [feedback retirement procedure](../../skills/spec/references/feedback-retirement.md), and delete the proposal in the
  same commit.

## Completion conditions

- Every dispositioned item has a terminal status and a disposition line; items left `open` are reported.
- Every rejected proposal listed is cleaned up or reported as left.
- `uv run devkit rules check` exits `0`, and the changes are proposed as one commit; its body names the `triage` role
  when one was used.
