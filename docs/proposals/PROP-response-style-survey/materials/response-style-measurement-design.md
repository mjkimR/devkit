---
id: MAT-response-style-measurement-design
title: Practical response-style review and verification
summary: "Uses transparent illustrative examples for design discussion and normal bundle checks for implementation; live comparisons remain optional and cannot imply an objective quality ranking."
created_at: 2026-10-20
---

# [MAT-response-style-measurement-design] Practical response-style review and verification

## Design review

Use `MAT-response-style-rewrite-draft` to discuss the concrete proposed instructions and its authored examples.
The examples are illustrative, not captured current/candidate outputs. They can show the intended factual scope,
request handling and presentation choices but cannot demonstrate that an installed model follows the draft or
that readers comprehend it better. No live model call is needed to discuss this direction.

Review four kinds of request: a scoped factual question, a report with unfinished work, an explanation request
and an artifact-only request. Write the review prompts and examples in English; keep identifiers and quantities
exact. Existing language-rendering checks still cover configured languages. For each, distinguish
required content and output format from subjective preferences such as wording, flow and explanation length.
Reject examples that omit or distort a supplied decision-relevant fact, condition or risk. Also review whether
repetition or irrelevant detail separates a necessary qualification from its claim or hides the result. Shortening
such an example must preserve its required information; a request for depth still gets the needed explanation.
A fixed score is not an adoption rule. Show the actual proposed wording and state why it fits the user's use.

## Development verification

Implement the accepted direction in the response-style bundle and preserve the existing language configuration,
opt-in packaging and host projections. Render the draft's Jinja language section for `auto` and configured
languages (including `ko` and `en`): only the selected default instruction remains, an explicit user request can
override it, and repository/task deliverable requirements remain present. No unresolved Jinja expressions may
reach installed or projected files. Run relevant lint, type checks, `just test-affected`, consumer smoke and
repository rules. Review the real diff and Living Spec reflection at the agreed medium effort. Existing
workflow gates and required reports still apply; examples do not waive missing facts or verification.

The final report states the checks actually run and the limits of what they establish. Template/projection
checks show that the right text is deployed; they do not prove conversational quality or equal behavior across
hosts. A completed task may report a reviewed rewrite with those checks, without claiming measured superiority.
No scorer, full fixture matrix, blinded rating, held-out split or repeated-generation quota is required.

## Optional observation after a concrete need

If actual generated comparison is useful, agree its inputs, host/model, comparison conditions and call/spending
allowance before any additional collection. Save actual outputs and settings. Inherited project or user style
can contaminate a no-style comparison, so isolate and record instruction sources when making such a claim.
A native role that inherits the existing style is not an unstyled baseline. Do not change the user's real profile
or infer permission for a headless launcher from the native workflow.

Limit any observations to the cases and conditions actually run. Length, first-sentence behavior and requested
syntax are inspectable properties; semantic preservation still needs review. Readability and helpful depth also
involve preferences, so do not turn those properties into an objective quality score. Source-published benchmark
results are not local measurements. Actual host compaction/reloading remains unverified.

No collection host or budget is selected here. The earlier structured-cohort question was withdrawn by the Host,
not answered by the user. A large evaluation tool and a shared guidance-limit experiment are outside the current
recommendation. This document creates neither a new approval gate nor a required benchmark phase.
