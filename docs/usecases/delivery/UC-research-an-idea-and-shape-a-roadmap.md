---
id: UC-research-an-idea-and-shape-a-roadmap
title: Research an idea and shape an initial roadmap
summary: "An AI coding agent coordinates bounded local and optional user-mediated cloud research, reviews evidence selectively and retains recommendations, pending requests and resumable unknowns in one indexed material."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional research and discovery subagents, Optional user-operated cloud research application]
status: active
capabilities:
  - CAP-DLV-deep-research
  - CAP-HARN-agent-guidance
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md
---

# [UC-research-an-idea-and-shape-a-roadmap] Research an idea and shape an initial roadmap

## 1. Goal

- **Goal**: investigate an early product or architecture decision and retain useful evidence, directions,
  initial documents and a conditional roadmap before development.
- **Scope**: one bounded research action and its retained material.
- **Trigger**: the product owner explicitly invokes the research entry.
- **Preconditions**: the deep-research bundle and ordinary project environment are available.

## 2. Main Success Scenario

1. The agent accepts the explicitly invoked research activity (`CAP-DLV-deep-research`, `CAP-HARN-agent-guidance`).
2. The agent recovers current goals, constraints, decisions and supplied evidence without an approach check (`CAP-DLV-deep-research`).
3. The agent frames the requested artifact, intended use, comparison criteria and research bound (`CAP-DLV-deep-research`).
4. The agent allocates needed scratch and commissions useful investigations inside assigned authority (`CAP-DLV-deep-research`).
5. The agent associates actual returned evidence with its investigation and reviews actions, support and candidate assumptions under common criteria (`CAP-DLV-deep-research`).
6. The agent drafts a supported provisional recommendation and unresolved decisions (`CAP-DLV-deep-research`).
7. The agent retains the requested artifact, evidence, pending questions and proportionate conditional follow-up as one indexed material with its status (`CAP-DLV-deep-research`).
8. The agent reports the actual outcome, evidence limits, the material's path and ID, the commit the user directs and the next useful action (`CAP-DLV-deep-research`).

## 3. Extensions

- **2a.** SDD project: the explicit invocation is not development intake, so no Unit or classification starts; after the user commits the material, a later proposal, spec or decision cites it by its ID; continues at step 3.
- **2b.** Adaptive-development project: the agent reads no current-context file; after the user commits the material, the current context links it by its ID; continues at step 3.
- **2c.** The user names an earlier run or material: the agent reads it as an input source; a named `partial` material of the same investigation is updated at step 7 instead of creating a new one; continues at step 3.
- **3a.** Consequential user decision is missing: the agent reuses known facts and asks only the missing decision; dependent work waits, then resumes at step 3.
- **3b.** The requested artifact is a reusable configuration reference: assignments contribute concrete repository/file references, borrow/omit guidance and a starting composition; continues at step 4.
- **4a.** Small question: the agent stays inline or uses one support role; resumes at step 5.
- **4b.** Delegation unavailable: the agent uses a permitted equivalent context/contract or reports missing coverage and continues only independently useful authorized work; resumes at step 5.
- **4c.** Scratch is tracked or not ignored in Git: the agent stops allocation and reports the conflict without editing ignore rules; permitted read-only inquiry may continue at step 5.
- **4d.** A bounded question benefits from cloud work or the user requests it: the agent supplies an inspectable request for the user to submit and return; independent local work continues at step 5 without claiming provider execution.
- **5a.** Unsupported/out-of-scope return: the agent rejects it as evidence, preserves the actual state and reports the affected coverage; resumes at step 3 for a permitted remedy.
- **5b.** Evidence insufficient or bound exhausted: the agent retains partial evidence and missing questions; proceeds to step 6 with no fabricated winner.
- **5c.** Candidate directions share one premise: the agent reframes a useful independent investigation or explains the constraints leaving one viable candidate; resumes at step 3 or proceeds to step 6.
- **5d.** Ordinary public-source timeout, broken link or unreadable result without an access refusal: the agent uses bounded authorized recovery, reports the failed retrieval and actual inspected replacement, and leaves unsupported claims unverified; resumes at step 5 or proceeds to step 6 with partial evidence.
- **5e.** Trust, sandbox, permission or source access is refused: the agent stops access to that resource without rerouting denied access and reports missing coverage; unrelated permitted work continues at step 5 or partial synthesis proceeds at step 6.
- **5f.** Authorization is ambiguous: the agent stops access to that resource and reports the uncertainty; unrelated permitted work continues at step 5 or partial synthesis proceeds at step 6.
- **5g.** The cloud report is unreadable or its link is inaccessible: the agent requests readable content and retains missing coverage; proceeds to step 6 with partial evidence.
- **5h.** A return lacks request identity, names a superseded revision or mismatches the question: the agent clarifies association before counting it as the pending answer; older background is limited and duplicates add no unsupported progress; resumes at step 5.
- **5i.** A readable report contains unsupported/conflicting claims or instructions asserting authority: the agent preserves evidence limits and treats instructions as source data; proceeds to step 6 without new action authority.
- **6a.** The supported draft omits the requested artifact or imposes an unwanted prerequisite: the coordinator repairs the gap or burden against the user's goal and constraints, using optional criticism when useful; resumes at step 6.
- **7a.** Retained content depends on scratch-only references: the coordinator retains needed supporting evidence or replaces links with stable sources before finishing; resumes at step 7.
- **7b.** The chosen material ID resolves or its directory exists: the coordinator chooses another slug without overwriting the existing material; resumes at step 7.
- **7c.** Comparative validation was declined: the synthesis keeps uncertain benefits explicit and a usable next action without making comparison an adoption prerequisite; continues at step 8.
- **7d.** Cloud evidence remains pending when pausing: the agent retains the exact safe request and necessary return evidence in the same partial material, sufficient without scratch; a later user-named resume returns to step 3 without silent resubmission.
- **8a.** User authorizes implementation: later work cites the retained material by its ID as ordinary intake; this research action ends without implementation, a commit or publication.

## 4. Postconditions

- **Success guarantee**: one retained material distinguishes evidence, assumptions, recommendations and actual
  decisions; pending cloud work retains its safe request and actual disposition; its roadmap is conditional, and its `Status` and open questions let a later run or consumer recover the next
  useful decision, and it is left uncommitted for the user's Git policy.
- **Minimal guarantee**: no approach inspection or change, Unit, commit, user approval, role execution or unavailable
  evidence is claimed; no existing material is overwritten; any boundary failure and affected state remain visible.

## 5. Acceptance Criteria

Rules: explicit invocation; approach neutrality; SDD intake exemption; research authority; optional support; bounded
evidence; role boundaries; provenance; research workspace; selective promotion; initial synthesis; one material per
investigation; collision check; resume; citation; bounded partial result; research completion; deliverable framing; usefulness; selective verification; retrieval recovery; access refusal; proportionate follow-up; recovery provenance; optional cloud research; cloud request; cloud disclosure; cloud status; cloud association; cloud evidence; report authority; cloud resume; missing cloud result.

### Scenario 1: Compare an initial idea and retain the result

- **Covers**: main success scenario
- **Given**: an incomplete product goal and supplied sources.
- **When**: the agent completes the bounded investigation.
- **Then**: one indexed material covers supported alternatives, a provisional direction, conditional roadmap and explicit unknowns without claiming implemented behavior, and the report names its path, ID and the commit the user directs.

### Scenario 2: Run under either approach

- **Covers**: 2a, 2b
- **Given**: an SDD project, or an adaptive-development project with a current-context file.
- **When**: the user invokes the research entry.
- **Then**: no approach check, Unit or classification runs, `.devkit/adaptive-dev.md` is neither read nor written, and the retained material is cited or linked later by its ID.

### Scenario 3: Ask only the missing consequential decision

- **Covers**: 3a
- **Given**: known users/constraints and one missing decision that changes the target.
- **When**: research is framed.
- **Then**: known answers are reused and only dependent work waits for that decision.

### Scenario 4: Keep a small question small

- **Covers**: 4a
- **Given**: a narrow question answerable inline.
- **When**: the agent chooses research effort.
- **Then**: no full team, document suite or critic round is imposed.

### Scenario 5: Report absent delegation

- **Covers**: 4b
- **Given**: a requested role is unavailable.
- **When**: the agent selects a permitted equivalent or returns partial coverage.
- **Then**: actual execution and emulated/native limits are explicit, with no fabricated role result.

### Scenario 6: Reject unsupported or out-of-scope evidence

- **Covers**: 5a
- **Given**: a return invents authority or exceeds its boundary.
- **When**: the coordinator inspects actual actions and evidence.
- **Then**: it rejects that return as completion evidence and preserves/reports the affected state.

### Scenario 7: Return a bounded partial result

- **Covers**: 5b
- **Given**: conflicting/unavailable evidence or an exhausted research bound.
- **When**: synthesis completes.
- **Then**: unknowns and the next discriminating check survive, with no unsupported choice or date.

### Scenario 8: Examine candidate independence

- **Covers**: 5c
- **Given**: nominal alternatives differ only in one shared unsupported premise.
- **When**: the coordinator compares them.
- **Then**: it investigates a distinct premise or records why constraints leave one candidate; consensus does not establish correctness.

### Scenario 9: Hand the material to later work

- **Covers**: 8a
- **Given**: a committed research material and a later user request for implementation.
- **When**: the later work starts.
- **Then**: it starts as ordinary intake and cites the material by its ID, without treating research completion as approval, a commit or publication.

### Scenario 10: Keep task scratch ignored and separate

- **Covers**: 4c
- **Given**: task scratch would enter tracked or non-ignored Git content.
- **When**: allocation checks the selected path.
- **Then**: allocation stops without an ignore-rule edit, and the report distinguishes any continued read-only inquiry.

### Scenario 11: Promote useful evidence without scratch dependencies

- **Covers**: 7a
- **Given**: an investigation has intermediate task notes and useful supporting evidence.
- **When**: the coordinator retains the synthesis.
- **Then**: selected results and evidence are preserved with resolving durable references, the whole scratch tree is not copied by default, and scratch is not automatically deleted.

### Scenario 12: Resume a partial investigation

- **Covers**: 2c
- **Given**: a `partial` material the user names as the same investigation.
- **When**: the agent retains the resumed result.
- **Then**: it updates that index in place and a `complete` material is never rewritten.

### Scenario 13: Avoid an existing material ID

- **Covers**: 7b
- **Given**: the chosen slug's material ID already resolves.
- **When**: the coordinator creates the material.
- **Then**: it chooses another slug and the existing material is unchanged.


### Scenario 14: Deliver practical configuration references

- **Covers**: 3b
- **Given**: a request for reusable agent configurations rather than a team-effectiveness study.
- **When**: the coordinator frames assignments and retains the synthesis.
- **Then**: the first retained artifact includes repository/file references, borrow/omit guidance and a starting composition, and it adds no mandatory intake form.

### Scenario 15: Repair a useful-output gap

- **Covers**: 6a
- **Given**: a supported draft lacks the requested artifact or imposes an unwanted prerequisite.
- **When**: the coordinator checks usefulness or uses an optional critic.
- **Then**: the gap or burden is identified against the user's constraints and repaired; zero supported findings remains valid and no critic is required on every run.

### Scenario 16: Review supported evidence selectively

- **Covers**: main success scenario step 5
- **Given**: a role return identifies an inspected source, relevant location or finding and limitations.
- **When**: the coordinator validates it.
- **Then**: adequately supported work is not repeated by default; a consequential gap, contradiction or suspect claim gets targeted verification or remains unverified.

### Scenario 17: Recover within the original retrieval bound

- **Covers**: 5d
- **Given**: a public source times out or has a broken link without an access refusal.
- **When**: the original assignment still permits research.
- **Then**: a bounded retry or another legitimately accessible primary source may supply evidence, the failed retrieval and actual replacement are named, and a replacement supporting a different claim leaves the original claim unverified.

### Scenario 18: Stop refused or ambiguous resource access

- **Covers**: 5e, 5f
- **Given**: a tool or source refuses access, or authorization is unclear.
- **When**: the coordinator or role classifies that result.
- **Then**: access to that resource stops without a tool, path, process, identity or setting bypass; missing coverage is reported while unrelated permitted work may continue.

### Scenario 19: Respect declined comparative validation

- **Covers**: 7c
- **Given**: the requester declines same-task team comparisons and benefit-validation work.
- **When**: the conditional roadmap is retained.
- **Then**: it states uncertain benefits and a usable starting point without comparison or proof of superiority as an adoption prerequisite.

### Scenario 20: Hand a bounded cloud request to the user

- **Covers**: 4d
- **Given**: an invoked investigation with a useful bounded cloud question.
- **When**: the coordinator prepares the copyable request.
- **Then**: the user sees exact safe outbound content and return instructions with label/revision; the state is
  awaiting user result, with no claim that a provider task ran and no cloud requirement for local-only work.

### Scenario 21: Keep an unreadable or absent return partial

- **Covers**: 5g
- **Given**: no returned report, an unreadable attachment or an inaccessible report link.
- **When**: the investigation reaches its bound.
- **Then**: readable content is requested where needed, useful local evidence survives, and missing support stays
  partial without polling, fabricated contents or elapsed-time progress claims.

### Scenario 22: Associate stale and duplicate reports explicitly

- **Covers**: 5h
- **Given**: a return without identity, for an older revision, mismatching the question or repeating an earlier report.
- **When**: the coordinator matches it to pending work.
- **Then**: ambiguous association is clarified, any older background is limited, and neither a duplicate nor a
  stale return silently answers the current request or proves additional progress.

### Scenario 23: Qualify report claims and authority

- **Covers**: 5i
- **Given**: readable findings with accessible, inaccessible or conflicting support and a request to upload files.
- **When**: the coordinator reviews the return.
- **Then**: actual inspected support, external assertions, inference and gaps stay distinct; report instructions
  grant no action or Git authority, and reviewed status claims no universal citation verification.

### Scenario 24: Resume a pending cloud request without scratch

- **Covers**: 7d, 2c
- **Given**: the user names the same partial material and transient files no longer exist.
- **When**: the investigation resumes.
- **Then**: the exact safe request, label/revision, selected attachments, disposition, remaining question, next action
  and retained evidence suffice; the same partial index is updated without silent resubmission or rewriting a complete material.
