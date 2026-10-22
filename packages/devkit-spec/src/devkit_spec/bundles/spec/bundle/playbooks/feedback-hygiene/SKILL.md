---
name: feedback-hygiene
description: Triage open feedback files under specs/ in one hygiene session; group them by target, order them by severity and recurrence, and with the user's decision promote them to rules, playbooks, decisions or spec work, or dismiss or forward them and update their status.
---

# Feedback hygiene

Feedback capture starts observations `open` and never changes their status. This playbook triages selected items:
`promoted` closes them by routing to follow-up work, `dismissed` declines them, and `forwarded` records an authorized external
submission. An authorized direct fix without promotion uses terminal `resolved`, through the `spec` skill's
[completion procedure](../../skills/spec/references/completion.md#source-feedback-resolution), without requiring
another hygiene session. Run this playbook only in a hygiene session the user asks for.

Disposition records keep destinations traceable; promotion does not assert that the observation is fixed.

## Prerequisites

- The user asked for this playbook. Destinations are the user's decisions; this playbook drafts and asks.
- A clean working tree (`git status`), or an isolated branch or task worktree.
- The Step 1 listing shows at least one item; otherwise report an empty backlog and stop.

## Step 1: Collect

```bash
uv run devkit spec list feedback --status open --all-namespaces -n 0
```

Feedback of completed spec bundles is included; `--query <text>` narrows by ID or title. Each line carries `severity`,
`scope` and `target`, critical items first. A scope or severity the user names narrows the selection with
`--where scope=<scope>` or `--where severity=<a>,<b>`; otherwise take every open item. Read each selected file's
remaining frontmatter (`kind`, `category`, `recurring`, `origin`) in Step 2.

## Step 2: Group and order

- Determine ownership from the observed target and evidence: `repo`, `upstream` or `unknown`. Repository-owned
  rules, skills, instructions and tools are the base targets. Do not ask the user to classify tools; propose the
  resolution destination yourself. Unknown or cross-tool items stay eligible and may need multiple linked fixes.
- Group items with the same `target`; a group shares one decision.
- Order groups and items: `critical`, then `recurring: true`, then `blocked`, `workaround`, `noise`.
- Read each body's Evidence section. A suggestion without observed evidence is a dismissal candidate
  ("insufficient evidence").

## Step 3: Decide the destination with the user

Propose the resolution destination or destinations per group. Draft artifacts within existing authorization
first; request decisions only beyond that scope:

| Scope | Destination | Action |
| :--- | :--- | :--- |
| `repo` | Rule | Draft it with the `spec-rule` skill in the project's in-repository bundle |
| `repo` | Playbook | Draft `playbooks/<slug>/SKILL.md` and its `kind = "playbook"` asset in the project's in-repository bundle (`devkit get-context devkit`, instruction `in-repo-bundle`), then `uv run devkit sync` |
| `repo` | Decision | Draft `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md` from `.devkit/managed/spec/templates/decision.md` |
| `repo` | Living Spec fix | A wrong capability, story or architecture statement: fix it through the `spec` skill |
| any | Dismissal | Record the reason in the disposition line (Step 4) |
| `upstream` | Forward draft | Prepare a report for the owning tool or bundle, including devkit and devkit-spec; submit only with explicit external-send authorization |
| `unknown` | Ownership review | Inspect the observed targets, propose repository or upstream destinations, and keep unresolved items open |

An asset developed in this repository has `scope: repo` even when shipped as an upstream tool to other projects; address it locally: a defect with clear
expected behavior becomes a `bugfix` task (`sdd-session-bugfix`, or `sdd-spec-bugfix` when its behavior must be written
down), a small wording fix a `session` change, an open design question a draft proposal (`uv run devkit spec proposal new <slug>`).
Record full source FB IDs and the scope received in the destination proposal/spec body (`Source feedback`), or in a
session's agreed scope. Include only open direct-fix source paths in implementation boundaries for completion updates; promoted references
remain traceability and require no further feedback work.

## Step 4: Update status and seal

An item is `forwarded` only after authorized submission, citing the actual report location; a draft alone stays
`open`, as does an item whose ownership is unresolved. Link all resolution destinations for an issue spanning several
tools.

Set terminal `promoted` when follow-up work receives the observation. Track subsequent progress in that destination;
never convert promoted to resolved merely because the work finishes. Set terminal `resolved` only for an open
observation directly fixed and verified without promotion, including a session or spec fix. Partial or unverified
direct fixes stay `open`. Use `dismissed` for a reasoned decline and `forwarded` for an actual
submission. Append a disposition line so each outcome is traceable:

```markdown
- **Disposition**: <destination ID, path or issue link>: <one-line summary of what was done>
```

The destination is the spec, proposal, decision, rule or playbook ID that received the item, the changed file path
for a `session` fix, or the report location for a forward. A resolution also states the implemented outcome and
concrete test/review evidence. A dismissal states its reason in the same line.

## Step 5: Stale activity branches

A hygiene session also surfaces stalled work. `uv run devkit rules check -p hygiene` warns about each `plan-*` and
`dev-*` branch idle longer than `[worktree] stale_after` (it needs `gh auth status`; otherwise it notes the skip);
`uv run devkit worktree status --stale` prints the same as `[STALE_BRANCH: ...]` lines with the pull request state and the
resume command. List them for the user with the two ways on, resume or discard, per §4 of the `spec` skill's
`references/branches.md`, and do neither unasked: the warning never cleans anything up.

## Step 6: Rejected proposals

The same run lists each rejected proposal still in the base (`SPEC_PROPOSAL_REJECTED_PENDING`). Its cleanup is
Host work, done here once the user agrees: find the rejection commit and the user's reason
(`git log -1 --format='%H %B' -S'status: rejected' -- <proposal.md>`), write a rejection ADR under `docs/decisions/`
that references the proposal and that commit. Before deleting, follow the
[feedback retirement procedure](../../skills/spec/references/feedback-retirement.md): preserve open observations,
retire historical references with Git context, update relative links and validate current references. Keep the proposal
on collision, invalid input or an unresolved live dependency. Put preservation, the ADR and deletion in the same commit. Nothing is rewritten from
the reason; quote it.

## Completion conditions

- Every dispositioned item selected in Step 1 has `status` `promoted`, `resolved`, `dismissed` or `forwarded` and a disposition line,
  and the Step 1 listing no longer shows it; items left `open` (Step 4) are reported.
- Every promotion has a destination receiving its scope under user authorization; every resolution has implementation and verification evidence. No observation is marked resolved merely because it was handed off.
- Every rejected proposal the run listed is cleaned up (rejection ADR and deletion in one commit) or reported as left
  for later.
- `uv run devkit rules check` exits `0`; the status updates and drafts are proposed as one commit.
