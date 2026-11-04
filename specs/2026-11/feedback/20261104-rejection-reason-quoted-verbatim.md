---
id: FB-rejection-reason-quoted-verbatim
title: The rejection path asks for the user's reason verbatim while records otherwise carry decisions, never quotes
scope: repo
kind: change-request
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md
origin: user
severity: noise
recurring: false
status: resolved
created_at: 2026-11-04
---

# [FB-rejection-reason-quoted-verbatim] The rejection path asks for the user's reason verbatim while records otherwise carry decisions, never quotes

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the spec constitution says records "carry decisions, never conversation quotes, paraphrases
  or dates", and the feedback template says "Never quote or paraphrase the user". The `sdd-proposal` workflow's Gate
  rules say the rejection commit carries "the user's reason, unrewritten", and the `feedback-hygiene` playbook (Step
  4) says the rejection ADR is written "quoting the reason from the rejection commit". A rejection therefore puts a
  verbatim conversation quote, in the conversation's language, into a commit message and into an accepted ADR, where
  every other record would hold a rewritten decision in English.
- **Proposed Procedure**: align the rejection path with the constitution: the rejection commit and the rejection
  ADR state the user's decision and its reason as a rewritten, English decision sentence naming `user` as the
  decider (the ADR's Decision Outcome and Context already hold the rejected direction and the chosen alternative).
  Edit `sdd-proposal.md` ("with the user's reason, unrewritten" → "with the user's decision and reason, rewritten as a
  decision sentence"), the `feedback-hygiene` playbook Step 4 ("quoting the reason from the rejection commit" →
  "stating the reason recorded in the rejection commit") and `CAP-DLV-proposal-planning` rule 9 if its wording is
  read as verbatim. If the verbatim quote is deliberate (the one place where the user's own words are the record
  because no later actor may reinterpret a rejection), state that exception and its reason in the constitution's
  records rule instead.
- **Expected Benefit**: one rule for every record; ADRs stay English and readable to agents that did not see the
  conversation; no Korean conversation fragments in accepted decision documents.
- **Cost & Risk**: a rewritten reason can drift from what the user meant; the rejection commit keeps the original
  decision context in Git either way.
- **Attempted**: hypothesis; observed while writing `ADR-reject-ux-rules-path-exclusion`, which follows the current
  rule and carries the verbatim quote.

## Diagnostic Details

- **Reproduction**: run the `feedback-hygiene` playbook Step 4 on a rejected proposal; the ADR body receives the
  rejection commit's quoted reason.
- **Expected / Actual**: expected one records rule (decisions, no quotes); actual: the rejection path requires the
  quote.
- **Versions**: repository head 8dda2a75.
- **Conditions**: any rejected proposal whose rejection commit quotes the user.
- **Workarounds Attempted**: not attempted; the ADR followed the current rule.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md` line 115;
  `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/SKILL.md` Step 4; the spec
  constitution section 3 (records rule); `.claude/skills/spec-feedback/references/template.md` ("Never quote or
  paraphrase the user"); `CAP-DLV-proposal-planning` rule 9; `ADR-reject-ux-rules-path-exclusion`.

## Evidence

```text
constitution §3: "Records name `user` or `policy` and carry decisions, never conversation quotes, paraphrases or dates."
sdd-proposal.md:115: "sets `status: rejected` with the user's reason, unrewritten, in the commit message"
feedback-hygiene/SKILL.md:81: "write the rejection ADR quoting the reason from the rejection commit"
CAP-DLV-proposal-planning.md:103-104: "sets `status: rejected` with the user's reason in the commit message"
```

- **Disposition**: `SPEC-rejection-reason-rewritten`: the `sdd-proposal` workflow, the `feedback-hygiene` playbook, the proposal scaffold hint and `CAP-DLV-proposal-planning` rule 9 ask for the decision and reason as a decision sentence, never a quote; `ADR-reject-ux-rules-path-exclusion` restated accordingly; verified by the spec bundle guidance test and `devkit rules check`.
