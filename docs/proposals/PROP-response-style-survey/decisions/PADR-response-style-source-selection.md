---
id: PADR-response-style-source-selection
title: Select established independent response-style sources
summary: "Uses popularity and maintenance to screen first-party prompt sources, and original synthesis with provenance rather than star-ranked rule selection."
proposal: PROP-response-style-survey
status: draft
created_at: 2026-10-20
---

# [PADR-response-style-source-selection] Select established independent response-style sources

## 1. Context & Problem Statement

One author's prompt and repository popularity cannot show whether response-style rules work. Widely copied
prompts can create false corroboration, and a repository license does not establish website reuse terms.

## 2. Decision Drivers

Use relevant first-party instructions, established projects, observable maintenance, diverse response goals,
traceable pins and original expression. Keep source-practice claims separate from measured effectiveness.

## 3. Considered Options

| Option | Benefit | Limitation |
| --- | --- | --- |
| Highest-star repositories only | Recognizable projects | Stars do not measure style effectiveness or expose actual instructions. |
| Arbitrary rule/AGENTS collections | Broad coverage | Weak provenance, duplicated opinions and uncertain default behavior. |
| Relevant established prompt sources plus official guides | Auditable source practice and contrasting intent types | Needs source and ancestry checks; no automatic quality guarantee. |

## 4. Decision Outcome

Use the third option with the explicit screen and exclusions in `MAT-response-style-source-selection`. Seven
repositories have pinned prompt/license sources and current metadata, including Attention Span as the identified
original reference. Its relationship to the current style is not independent corroboration. Three official writing guides are a
separate class with their own license gaps. Record each source, its scope and limitations; do not count shared
or unverified ancestry as independent votes. Transfer ideas using original wording, never source examples,
structure or copyleft/unknown-license expression. Track each candidate rule to a source idea or explicit local
requirement and later to observed fixture results.

## 5. Consequences

Smaller but directly relevant gptme qualifies; the higher-star Cline remains a reserve because its production
prompt path was not confirmed. Goose supplies a minimal-style contrast rather than a vote for brevity. Missing
reuse terms restrict source-expression reuse but do not create an evidence claim or implementation requirement.
