---
name: discovery
description: "Refine a half-formed idea or request through a minimum useful interview, independent exploration and pressure-testing into concrete proposals and a next decision."
---

# Idea discovery

Run only when the user explicitly invokes this entry.
Turn the supplied idea into proposals the owner can judge; research serves decisions that need evidence.

## Boundaries

- Return in conversation unless a destination is requested; only the coordinator writes the retained result.
- Invocation grants no implementation, project settings, delivery Unit, approval, envelope, staging, commit or
  publication authority; use the project's existing workflow for separately authorized work.
- Distinguish user decisions, recommendations, assumptions and inspected facts; roles cannot decide for the owner.
- Keep roles within assigned read/write boundaries; leave product files, settings, the index and HEAD unchanged.
- Keep scratch under `.devkit/transient/deep-research/`; verify ignored/untracked paths when Git is available.
- Stop denied access without bypass and report missing coverage rather than inventing evidence or execution.
- Require no fixed team, option count, questionnaire length, score, consensus, external research or report file.

## Procedure

1. Read supplied context and relevant project evidence; recover the desired change, audience/use scene,
   consequential constraints and session outcome. Ask only unanswered user-only questions that change first
   proposals or avoid substantial wasted exploration, explaining the consequence. Ask dependent choices in order;
   batch independent ones. Find inspectable facts yourself.
2. Once useful exploration is possible, state its question, observable effort bound and stop condition.
   Keep deferrable preferences as assumptions or alternative premises instead of settling every design branch first.
3. Develop materially different plausible premises while direction is open; keep a small inquiry inline.
   Before delegating or allocating scratch, read `references/orchestration.md`.
   Investigate factual gaps only where the answer can change a consequential choice.
4. Draft concrete proposals before asking the owner for downstream details. For each surviving direction, show a
   usage example, expected benefit, adoption/operating cost, inspected support, assumptions and a condition that
   rules it out. After candidates exist, pressure-test consequential premises, evidence and missing alternatives;
   use an independent challenger when useful. Accept zero findings and preserve plausible unexplored premises.
5. Recommend from actual findings and route remaining uncertainty with the table below. Before another autonomous
   round, name the question and what result changes the recommendation; stop at the agreed bound or when no
   remaining inquiry changes the next decision.
6. Return the outcome and next decision. If retention is requested, read `references/retention.md` before writing.
   Clarifying, holding or rejecting an idea is a valid result without a delivery handoff.

## Route the remaining uncertainty

| Uncertainty | Next action |
| --- | --- |
| Owner's goal, preference or tradeoff | Show the concrete consequence and ask the focused choice. |
| Inspectable fact or external evidence | Investigate within the bound; do not start another explicitly invoked entry. |
| Experience or behavior cannot be judged from prose | Show an inline example or sketch, or propose a bounded experiment; obtain its write/execution authority before running it. |
| Central premise fails | Reframe within the agreed goal, or recommend holding or rejecting it with the failure evidence. |
| Direction is clear enough for the requested use | Return a concise brief with decisions, reasons, rejected alternatives and consequential open assumptions. |

## Completion

- Report `clarified`, `validation-needed`, `held` or `rejected`, with its reason, actual coverage limits and next decision.
- Check that proposals support the intended use without requiring a report, implementation task or further validation
  that cannot change the choice; repair a mismatch before returning.
- For a requested write, inspect the result and report its destination or the blocked write; for a material, include
  its ID and complete/partial coverage status and leave it uncommitted under project Git policy.

Example: `/discovery I keep losing useful technical reading; help me decide what would actually improve that.`
