---
id: PADR-response-style-adaptive-replies
title: Write adaptive replies with a small shared instruction set
summary: "Uses a conclusion-first opening and arrow-marked core sentences with supporting explanation as the ordinary reply format, preserving required content and format exceptions."
proposal: PROP-response-style-survey
status: draft
created_at: 2026-10-20
---

# [PADR-response-style-adaptive-replies] Write adaptive replies with a small shared instruction set

## 1. Context & Problem Statement

The current style combines content obligations with recurring visual instructions. Block-count thresholds and
fixed paragraph sizes are separate choices from a consistent point format; none establishes measured reading
benefits. The selected presentation preference uses a complete core sentence followed by supporting explanation.
A successful edit or survey also needs to remain distinct from completion of the whole task in a progress report.

## 2. Decision Drivers

Preserve meaning and required formats, adapt depth to the request, keep a portable bundle, and give users clear
scope and verification in work reports. Avoid rules that confuse a subjective presentation preference with an
objective quality guarantee.

## 3. Considered Options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Retain every visual rule and polish wording | Small edit | Preserves the rigid presentation without testing its need. |
| Select several source-inspired presets | Exposes preferences | Adds configuration and review combinations without a demonstrated need. |
| One style with conclusion-first, arrow-marked core sentences and explicit exceptions | Consistent ordinary replies with adaptable depth and preserved output contracts | User preference, requiring example-based review; no universal quality gain is claimed. |

## 4. Decision Outcome

Recommend the third option. `MAT-response-style-rewrite-draft` supplies reviewable text, a <=300-byte pointer
and clearly labelled authored examples. Respect user/repository output contracts; preserve decision-relevant
facts and material limits; distinguish a finished step from a finished request. For an ordinary reply, the first
sentence gives the overall answer or explicitly unknown result. Use `→ **Core sentence.** Supporting explanation`
for each ordinary explanatory point, with blank lines between points and no fixed point or sentence count.
The bold lead is a complete conclusion, not a topic label; supporting text carries needed reasons and conditions.

Presentation-preference authority: user. A one-sentence reply may omit the marker; ordered steps or choices use
numbers, requested artifacts and required reports follow their own formats, and ASCII-only media use `->`.
Keep the language variable and short Korean-specific wording guidance. Add no presets or extra decorative marks.
The 300-byte cap applies only to the guidance fragment; no skill-body length ceiling is introduced.

The draft is a direction for user review, not a `plan-accept` decision or deployed instruction. Formal adoption
follows the existing workflow; a source citation or illustrative reply does not establish observed runtime quality.

## 5. Consequences

Development changes the bundle and existing deployment assertions, reflects the behavior in
`CAP-DIST-content-packages`, and runs the repository's normal checks and independent review. Required report
fields stay intact. Rewriting the shared distribution guidance contract or changing workflow report schemas is
outside this direction.
