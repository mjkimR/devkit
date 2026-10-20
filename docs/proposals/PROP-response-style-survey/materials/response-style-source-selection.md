---
id: MAT-response-style-source-selection
title: Response-style survey source selection and rule candidates
summary: "Selects seven established prompt and reply-style repositories and three official writing guides, separates source practice from measured effect, and records exclusions and rule-level limits."
created_at: 2026-10-20
---

# [MAT-response-style-source-selection] Response-style survey source selection and rule candidates

## Selection policy

Community repositories normally need at least 1,000 GitHub stars, a first-party public instruction with actual
reply requirements, a readable license, no archive flag and a default-branch commit within 180 days of inspection.
An official vendor source or official writing guide may be an explicit exception with its reason recorded. All
seven selected repositories meet the community screen without an exception. Stars indicate visibility and adoption,
not correctness, safety, quality or evidence of a rule's effectiveness. No relative star ranking selects a rule.

Retain breadth of behavior: concise technical communication, mode-specific artifacts, completeness, educational
explanation and minimal style policy. Separate first-party owners are separate source records, not proven
independent prompt lineages. Matching text remains one unverified lineage for synthesis; never use a majority vote.
A rule ledger can say multiple projects publish a practice, but cannot call it independently corroborated until
its relevant ancestry is checked. Investigate attribution around any candidate wording that appears shared.

Metadata was retrieved from public GitHub REST endpoints, followed by default-branch commit endpoints and pinned
raw prompt/license files. The observations span 2026-10-19 23:04 UTC (2026-10-20 Asia/Seoul). Mutable branch pages
from the scout were revalidated by pin; OpenCode's moved path was located in its pinned Git tree. Browser-cached
content alone is not current-source proof. `response-style-source-snapshot.json` records exact metadata and hashes.

| Source | Observed stars | Role in survey | Source record |
| --- | ---: | --- | --- |
| Attention Span | 1,475 | Presentation variants and published evaluation limits | `MAT-response-style-source-attention-span` |
| OpenCode | 217,747 | Direct factual technical replies; model-specific prompt | `MAT-response-style-source-opencode` |
| Aider | 49,645 | Short explanation plus an obligatory tool edit format | `MAT-response-style-source-aider` |
| Continue | 36,267 | Code-only request and mode-specific formatting | `MAT-response-style-source-continue` |
| gptme | 4,456 | Concise/completeness tradeoff, compact/full prompt modes | `MAT-response-style-source-gptme` |
| Anthropic official plugins | 43,168 | Educational depth as a counterexample to universal terseness | `MAT-response-style-source-anthropic` |
| Goose | 55,446 | Minimal-style contrast; Markdown only in the inspected base section | `MAT-response-style-source-goose` |

Official writing guides are a distinct evidence class: `MAT-response-style-source-google`,
`MAT-response-style-source-microsoft` and `MAT-response-style-source-toss`. They supply writing ideas, not live
agent behavior. Page-specific Microsoft and Toss reuse terms remain unresolved, so import no source expression.

## Exclusions and reserve candidates

- Cline has an observed API count of 70,555 from the scout, but its former production prompt URLs returned 404.
  The available SDK examples do not establish current defaults. Reserve it until an actual production prompt is
  pinned; a larger star count does not replace relevant evidence. Starting point: https://github.com/cline/cline.
- Roo/Kilo or other related forks are not independent corroboration merely because their repositories differ.
  Inspect rule ancestry before adding one: https://github.com/RooCodeInc/Roo-Code and https://github.com/Kilo-Org/kilocode.
- Prompt-leak collections, mirrors, arbitrary AGENTS.md lists and copied proprietary system prompts are excluded.
- Cursor/Windsurf rule collections are not evidence of those products' first-party defaults. No arbitrary
  community collection fills an unavailable official prompt.
- Anthropic's former Explanatory style and the inspected plugin are one lineage. block/goose and aaif-goose/goose
  are one project.

Attention Span metadata and pinned files were retrieved separately on the same local date after the original
six-source snapshot. Its published benchmark is a source report, not an independently reproduced devkit result.


The concrete recommendation is `MAT-response-style-rewrite-draft`; its authored examples are not live measurements.

## Rule ledger for one candidate

This is a candidate-design ledger, not measured findings. The current local bundle remains the baseline. Author
candidate text from requirements and the ideas below; do not follow any source's order, examples or branded format.

| Rule or pressure | Source practice / local requirement | Candidate treatment | Test or limit |
| --- | --- | --- | --- |
| Attention-oriented presentation | Attention Span | Assess the attention and presentation ideas against local requirements using newly written guidance. | Practical examples; no demonstrated comprehension benefit is inferred. |
| Direct factual lead | OpenCode; Google and Microsoft writing guides; existing local preference | Preserve answer-first while allowing artifacts to begin with their required syntax. | Illustrative factual/recommendation examples; not claimed universally present across the repositories. |
| Required content before brevity | Aider editing protocol; Continue code-only exception; local workflow contract | Preserve numbers, conditions, risks and all mandatory report fields. | Review required content and report formats; use existing deployment checks for implementation. |
| Requested depth | gptme concise/completeness balance; Anthropic educational mode | Length follows intent. Do not adopt mandatory educational decorations. | Illustrative explanation request; length is descriptive, not a minimization objective. |
| Wrapper-free artifacts | Continue code-only mode; current local user-output requirement | Obey the requested artifact syntax without a conversational preface. | Illustrative artifact-only request. |
| Appropriate next step | gptme discourages generic closing offers; current local rule requires an actual user action | Retain only necessary next actions; reject an unconditional closing step. | Review acknowledgment, completion scope and necessary user decisions. |
| Plain Korean | Toss UI-writing principles; current local language contract | Use ordinary Korean while preserving identifiers and domain constraints. | Korean sample discussion; UI-copy advice is not a complete conversation policy. |
| Lightweight structure | Goose is a minimal-policy contrast, not support for concision | Evaluate the current mandatory bold lead-ins after three blocks and fixed block size as local hypotheses; do not preserve them solely because they already exist. | Editorial review of the proposed text and examples; exact requested artifacts override form. |

No copied wording, examples or document structure from copyleft or unknown-license sources enters the bundle.
For permissive sources this project still uses original synthesis and records provenance; license labels do not
stand in for source-level scope checks. This is an engineering reuse policy, not a legal clearance opinion.
