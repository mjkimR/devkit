---
id: PADR-response-style-adaptive-replies
title: Write adaptive replies with a small shared instruction set
summary: "Keeps required content and reporting obligations explicit while allowing explanation depth, emphasis and layout to follow the request."
proposal: PROP-response-style-survey
status: draft
created_at: 2026-10-20
---

# [PADR-response-style-adaptive-replies] Write adaptive replies with a small shared instruction set

## 1. Context & Problem Statement

The current style combines content obligations with many recurring visual instructions. Mandatory bold openings
and fixed paragraph sizes can produce repetitive replies without establishing that the reader understands more.
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
| One compact style with explicit content obligations and flexible layout | Clear common behavior with fewer visual constraints | Requires example-based editorial review; no universal quality gain is claimed. |

## 4. Decision Outcome

Recommend the third option. `MAT-response-style-rewrite-draft` supplies reviewable text, a <=300-byte pointer
and clearly labelled authored examples. Respect user/repository output contracts; preserve decision-relevant
facts and material limits; choose depth and layout for the request; distinguish a finished step from a finished
request. Keep the language variable and short Korean-specific wording guidance. Do not add presets, fixed
paragraph/sentence counts, mandatory bold openings or decorative source-specific formats.

The draft is a direction for user review, not a `plan-accept` decision or deployed instruction. Formal adoption
follows the existing workflow; a source citation or illustrative reply does not establish observed runtime quality.

## 5. Consequences

Development changes the bundle and existing deployment assertions, reflects the behavior in
`CAP-DIST-content-packages`, and runs the repository's normal checks and independent review. Required report
fields stay intact. Rewriting the shared distribution guidance contract or changing workflow report schemas is
outside this direction.
