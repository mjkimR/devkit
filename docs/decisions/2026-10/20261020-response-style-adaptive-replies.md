---
id: ADR-response-style-adaptive-replies
title: Write adaptive replies with a small shared instruction set
summary: "Uses a conclusion-first opening and arrow-marked core sentences with supporting explanation as the ordinary reply format, preserving required content and format exceptions."
proposal: SPEC-response-style-survey
status: accepted
created_at: 2026-10-20
---

# [ADR-response-style-adaptive-replies] Write adaptive replies with a small shared instruction set

## 1. Context & Problem Statement

The current style combines content obligations with recurring visual instructions. Block-count thresholds and
fixed paragraph sizes are separate choices from a consistent point format; none establishes measured reading
benefits. The selected presentation preference uses a complete core sentence followed by supporting explanation.
A successful edit or survey also needs to remain distinct from completion of the whole task in a progress report.

The existing `SKILL.md.jinja` already names omission and overload, limits brevity to reporting rather than work,
and renders `vars.language` into a concrete instruction. Preserve these behaviors in the rewrite. The proposed
change removes fixed block/sentence thresholds and adopts marked core sentences; it does not replace language
rendering with a generic instruction to use an unspecified configuration.

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

Presentation-preference authority: user. Requested artifacts and required reports follow their own formats.
Keep the language variable, its Jinja `auto`/configured-language branches and short Korean-specific wording
guidance. An explicit user language request overrides the conversation default; repository and task requirements
govern deliverables. State omission/distortion and obscurity as failure conditions, with omission the more serious
failure. Required content stays present and discoverable; concise reporting never reduces required work.
Add no presets or extra decorative marks.
The 300-byte cap applies only to the guidance fragment; no skill-body length ceiling is introduced.

The draft is a direction for user review, not a `plan-accept` decision or deployed instruction. Formal adoption
follows the existing workflow; a source citation or illustrative reply does not establish observed runtime quality.

## 5. Consequences

Development changes the bundle and existing deployment assertions, reflects the behavior in
`CAP-DIST-content-packages`, and runs the repository's normal checks and independent review. Required report
fields stay intact. Rewriting the shared distribution guidance contract or changing workflow report schemas is
outside this direction.
