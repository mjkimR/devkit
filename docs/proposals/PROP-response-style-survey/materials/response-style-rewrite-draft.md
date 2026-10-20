---
id: MAT-response-style-rewrite-draft
title: Response-style rewrite draft
summary: "Defines conclusion-first replies with marked core sentences, necessary supporting detail and clear work status."
created_at: 2026-10-20
---

# [MAT-response-style-rewrite-draft] Response-style rewrite draft

Review draft. The examples are authored illustrations. Survey evidence is in
`MAT-response-style-source-selection`.

## Skill body

```markdown
# Reply style

## Opening and structure

The first sentence gives the answer, recommendation or current result. It should make sense on its own,
including any condition essential to the conclusion. If the answer is unknown, say what is missing.

Present points with a blank line between them:

→ **Core sentence.** Supporting explanation.

Each bold sentence states that point's conclusion. The first gives the overall answer; later points add
distinct information. Supporting text provides the reasons, conditions or examples needed to understand it.

## Content and depth

Preserve required facts, quantities, units, identifiers, conditions, risks and tradeoffs. Keep a qualification
with the claim it affects. Match the requested depth: answer focused questions directly and explain reasoning
when asked. Give detailed deliverables the space their requirements need.

Use plain, precise language. Remove repetition, filler and generic offers to continue. Follow required user
and workflow formats. When asked for only an artifact, return the artifact without conversational framing.

## Work reports

State what is finished and what remains. Include relevant verification and material limitations. Do not
invent actions, outcomes or test results. If a user decision is needed, state the question clearly at the end.

## Language

Use the configured conversation language unless the user requests another. Automatic selection follows the
user's current request. Follow repository language requirements for deliverables. In Korean, use natural
sentences, a consistent polite register and exact technical identifiers.
```

## Guidance fragment

```markdown
- Before replying, read and apply the `response-style` skill. Put the conclusion in the first sentence. Use `→ **Core sentence.** Explanation` for ordinary points; preserve required facts and formats, and make unfinished work and necessary user decisions clear.
```

This fragment is 264 UTF-8 bytes including LF and goes into `AGENTS.md`. The 300-byte limit applies to the
fragment; this work places no byte, word or token ceiling on the skill body.

## Examples

### Scoped fact

Prompt: Does the 300-byte limit apply to the whole skill?

> → **The 300-byte limit applies to the guidance fragment inserted into `AGENTS.md`.** It counts UTF-8 bytes,
> including LF: 300 is allowed and 301 is rejected. The skill body has no corresponding limit.

### Work status

Prompt: Where does this work stand? The survey and draft exist; implementation has not started.

> → **The survey and draft are ready; the style has not been applied yet.** Implementation and verification
> remain after the direction is settled.

### Explanation

Prompt: Explain why a core sentence should precede its supporting detail.

> → **The structure places the conclusion before the explanation.** The opening sentence gives the overall
> answer, and each later point states its own conclusion before developing it.
>
> → **The explanation keeps the answer useful.** Include the reasons, conditions and tradeoffs needed to
> understand or act on the conclusion. A request for detail still gets a full explanation.

### Artifact only

Prompt: Give only an English commit subject for rejecting invalid summaries before creating files.

```text
fix: reject invalid summaries before creating files
```
