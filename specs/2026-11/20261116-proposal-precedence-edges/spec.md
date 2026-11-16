---
id: SPEC-proposal-precedence-edges
title: Ordering claims between proposals checked when made
summary: Has Backlog and the first Planning turn verify a draft's claims about other proposals' handoff order against base status and Development branches, so a stale ordering premise surfaces before it shapes the draft or its first decision.
status: completed
created: 2026-11-16
related_capabilities: [CAP-HARN-agent-guidance]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-proposal-precedence-edges] Ordering claims between proposals checked when made

## 1. Problem Statement & Motivation

Handed off from proposal PROP-proposal-precedence-edges on 2026-11-16.
- **Preserved Materials**: `docs/materials/2026-11/20261116-proposal-precedence-edges`

A draft proposal stated in prose that its handoff precedes the handoff of two accepted proposals, and argued its
change was cheap because neither had a spec yet. Nothing flagged the stale premise: `depends_on` is declared only by
the dependent, the accepted proposals carried no edge to the draft, and `devkit spec proposal check` reported
`editable=yes` with no notice.

The premise was false before the draft existed: both dependents were handed off two to five minutes before the
draft was committed, and the base still showed them `accepted` because a handoff lives on `dev-<slug>` until
integration (`docs/materials/2026-11/20261116-proposal-precedence-edges/observed-case-timeline.md`). No handoff-time
edge could have fired.

Checking each proposal a draft names as following it, by base `status` and by local or fetched `dev-<slug>`
branches, when the claim is written and again at the first Planning turn, surfaces a stale ordering premise before
it shapes the draft or its first decision; an ordering still in the future goes to the user as a sequencing
decision.

## 2. User Stories

- **US-1**: As the Host writing a draft proposal that claims its handoff precedes another proposal's, I want the
  guidance to have me check each named proposal's actual handoff state before I commit the draft, so that the draft
  never rests on an ordering that already happened the other way.
- **US-2**: As the runner of a draft's first Planning turn, I want the head-pinned recheck to include the
  `dev-<slug>` state of each proposal the draft names as following it, so that a premise that went stale in Backlog
  is updated before the first Planning decision.

## 3. Non-Goals

1. **Scope Excluded**: a `precedes:` field, a reverse `depends_on` written onto an accepted proposal, or any change to
   `depends_on` semantics. Accepted proposals stay unedited.
   - **Rationale**: the successor-declared edge of `ADR-roadmap-and-milestones-ledger` and the immutability of an
     accepted proposal in `ADR-proposal-acceptance`; neither edge would have caught the observed case.
2. **Scope Excluded**: a handoff, accept or `devkit spec proposal check` notice or refusal; any change under
   `packages/devkit-spec/src/devkit_spec/features/`.
3. **Scope Excluded**: parsing ordering claims out of proposal prose.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Backlog checks a draft's ordering claim before committing it
- **Given** the rendered `skills/spec/references/backlog.md` of the spec bundle, in the local and the cloud
  environment
- **When** a bundle-text test reads its Requests and decomposition list
- **Then** one list item states that a draft claiming its handoff precedes another proposal's, or whose cost depends
  on another proposal's or spec's state, checks each named one before the draft is committed by its base `status`
  and `git branch -a --list 'dev-<slug>' '*/dev-<slug>'`, fetching only within existing network authorization
- **And** one list item states that a `dev-<slug>` branch or a `SPEC-<slug>` means the proposal was handed off and
  the premise is rewritten, and that an ordering against a still-accepted proposal with no `dev-<slug>` branch is
  sequenced by the user before the draft is committed and stated in its body

### [AC-02] The first Planning turn rechecks ordering claims with the branch check
- **Given** the rendered `skills/spec/references/planning.md` of the spec bundle, in the local and the cloud
  environment
- **When** a bundle-text test reads its Steps
- **Then** one item states that the head-pinned recheck runs on the first turn as well as after a Host refresh, and
  that for each proposal the draft names as following it the runner also runs the `dev-<slug>` branch check, because
  a base or HEAD read shows a handed-off proposal as `accepted` until its Development integrates
- **And** the branch-check item covers each proposal the draft names as following it or whose state its cost depends
  on, updates the premise when a branch exists, and asks the user to sequence a still-accepted proposal with no
  branch in the question round when the draft states no sequencing decision

### [AC-03] The documented branch check tells a handed-off proposal apart
- **Given** a Git fixture whose base lists a proposal as `status: accepted` and which holds that proposal's
  `dev-<slug>` branch locally, or only as a fetched remote-tracking branch, and an unrelated `dev-<slug>-extra`
  branch
- **When** the documented `git branch -a --list 'dev-<slug>' '*/dev-<slug>'` runs
- **Then** it lists exactly the matching local or remote-tracking branch, and lists nothing when no such branch
  exists

### [AC-04] The capability owns the two checks
- **Given** `CAP-HARN-agent-guidance`, section "Repository Backlog and next work"
- **When** it is read after the change
- **Then** it states the check at draft authoring and at the first Planning turn (base status plus local or fetched
  `dev-<slug>` branches), the rewrite of a stale premise and the user's sequencing decision, and that no ordering
  field, edge on an accepted proposal or handoff check is added; `uv run devkit rules check --ci --base main` exits
  `0`

### [AC-05] No CLI or document-system change
- **Given** the Development range from the handoff commit to the final head
- **When** `git diff --stat <base>..HEAD -- packages/devkit-spec/src/devkit_spec/features/ packages/devkit-docs/`
  runs
- **Then** it lists no file

## 5. Source feedback

- `FB-draft-precedence-claim-unenforced` (scope: repo): the whole item (detection of a stale ordering premise
  between proposals).

## 6. Assumptions

- A named proposal still in `draft` or `reviewing` needs no new step: its own `depends_on` stays editable, and the
  Planning recheck covers it. The settled design names only accepted proposals for the sequencing question.
- The branch pattern `*/dev-<slug>` matches remote-tracking branches under any remote name; a local branch named
  `<prefix>/dev-<slug>` would also match and is read the same way (a handoff branch by convention).
