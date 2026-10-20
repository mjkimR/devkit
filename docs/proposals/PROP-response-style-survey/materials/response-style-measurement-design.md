---
id: MAT-response-style-measurement-design
title: Response-style paired pilot design
summary: "Defines twelve self-contained English and Korean fixtures, loss-sensitive acceptance, reproducible host conditions and a bounded diagnostic for larger reminders."
created_at: 2026-10-20
---

# [MAT-response-style-measurement-design] Response-style paired pilot design

## Goal and limits

Compare no added bundle style (A), the frozen current rendered style (B), and one candidate (C). This is a small
engineering pilot, not an estimate of population-wide quality or evidence that each individual rule causes a gain.
Host defaults remain present in all arms. A baseline means no devkit response-style instruction, not no host prompt.
The current interactive session and its native child agents are ineligible baselines when they inherit this
repository's response-style instructions. A self-reported lack of inherited style is not proof of isolation.

Keep original fixtures and expected obligations in a proposal material directory through Planning; handoff promotes
materials, so Development adds the executable input set, result imports and scorer under its spec Unit's
`materials/benchmark/`. Do not create a reusable CLI, install a new package, add a dependency or create a process
launcher. Use a small standard-library script for import, structural validation and summary; record the exact
external generation command separately. Unit tests cover scorer rejection of a missing or duplicated cell and a
missing numeric condition, not literal prompt phrases. Model generation remains an explicitly selected execution
method; none has run during Planning.

## Fixed fixture set

All factual inputs are supplied, synthetic and safe to publish. Freeze exact prompts and obligations before the
first scored generation. The table specifies their required content rather than golden prose; Development expands
it into machine-readable fixtures without changing the contract. Six English and six Korean cases cover matched
intent categories. An English code artifact may still be requested in a Korean prompt.

| ID | Language / intent | Supplied facts and required output | Primary style check |
| --- | --- | --- | --- |
| EN01 | English / focused answer | Requests without an idempotency key retry at most 3 times; keyed requests retry at most 10. Explain who gets which cap. | Answer-first; preserve both caps and their conditions. |
| KO01 | Korean / focused answer | Batch cap is 300 UTF-8 bytes, including LF; 300 is valid, 301 is rejected before writes. Explain both boundaries and unit. | Answer-first; preserve bytes, LF and before-write condition. |
| EN02 | English / comparison | Compare two supplied storage options: A costs 12 units/month with 7-day retention; B costs 20 with 30-day retention. The stated need is at least 14 days. | Give the supported recommendation first; preserve both tradeoffs. |
| KO02 | Korean / comparison | Compare local integration (no remote push) and PR integration (requires CI); user explicitly requests a PR. | State the requested path; preserve CI and push scope without unsolicited alternatives. |
| EN03 | English / explicit depth | Explain a supplied four-stage retry sequence fully, including the wait of 2 seconds between attempts and the stop after attempt 3. | Cover every requested stage; length is not a minimization target. |
| KO03 | Korean / explicit depth | Explain all four supplied verification steps, with 2 failures and 14 skips distinct from passes. | Retain every step and result category; consistent polite register. |
| EN04 | English / acknowledgment | Acknowledge an already authorized instruction to continue a specified read-only review; no review has run yet. | One concise acknowledgment, no fabricated completion or extra question. |
| KO04 | Korean / acknowledgment | Acknowledge an authorized local documentation edit; publication was not requested and has not occurred. | One concise acknowledgment; no invented completion or permission request. |
| EN05 | English / artifact only | Return exactly one valid JSON object with supplied `retries: 3` and `unit: seconds`; no Markdown or prose. | Parse the whole output as one object; retain both exact values. |
| KO05 | Korean / artifact only | Return only an English commit subject for a specified fix with a supplied identifier that must appear verbatim. | One subject line, exact identifier, no wrapper or explanation. |
| EN06 | English / blocking decision | Two equally supported retention choices, 7 or 30 days; a supplied rule requires the user to choose before a destructive purge. The purge has not run. | Ask one clear decision; preserve the precondition and no-action state. |
| KO06 | Korean / required report | A supplied report schema requires tests, exact pass/fail/skip counts, one risk and the next required user decision. Two critical numbers belong in a table required by that schema. | Preserve every field, table and material risk even if a style rule favors short prose. |

Six cases (EN01, KO01, EN02, KO02, EN04, KO04) are calibration; the other six are held-out for one frozen candidate.
The author may inspect fixtures, but must not tune against held-out outputs. If the candidate fails, keep the
current style; any later candidate is a separately labelled iteration with new held-out evidence. Do not report
reruns as independent confirmation of the original candidate.

## Collection and cost bound

Per selected host: 12 cases x 3 arms x 2 independent fresh runs = 72 generation attempts maximum. No automatic
retries; failures remain recorded with status and cause. An explicit user-authorized rerun starts a named new
attempt and keeps the failed output. Use the same host build, model identifier, reasoning setting, token limit,
tool settings, language and supplied facts for all arms. Randomize and record arm order per fixture/repetition.
Run each cell in a fresh isolated conversation; never continue a baseline from a styled session. Each prompt and
style payload has a content hash. Keep the original current payload before changing the bundle.

Capture the model-visible instruction sources or a documented verified isolation method, plus source cwd,
explicitly disabled inherited project/global instructions, style arm and host flags. A throwaway cwd alone does
not exclude user/global settings. If a host cannot suppress or disclose a conflicting style source, mark the
cohort contaminated and do not score it as a baseline. Never change the user's real profile or auth settings.
Only the benchmark's synthetic facts and owned style text are submitted; no worktree content, credentials or
unrelated conversation. Record elapsed time, output characters, UTF-8 bytes and provider usage when available;
mark usage unknown instead of inferring token counts. A count of generations is not a currency spending cap.
Choose the host/execution method and any monetary/token ceiling with the user before collection.

Deployment/render tests for Codex, Claude Code and Antigravity do not count as live quality measurements. Publish a
host-by-host coverage table. An unavailable host remains unmeasured, and results from another host do not fill it.

## Scoring and promotion

The scorer enforces full cell identity `(host, model, arm, fixture, repetition)`, unique cells, no missing outputs,
exact artifact constraints, and the presence of required numeric/identifier tokens. A token check cannot prove
that a number has the right unit, condition or polarity. An evaluator other than the candidate author reads outputs with arm
labels hidden and checks every fixture's semantic obligation, unsupported assertions, mandatory format,
answer-first (except artifact-only requests), requested depth, Korean register and unnecessary wrappers.
Save each judgment with a short reason and evidence span. A second independent blind check adjudicates every
claimed candidate improvement, proposed regression and every disagreement between structural checks and semantic judgment; if still
unresolved, the fixture fails. Automated LLM judgment alone is not a proof of correctness.

A candidate is eligible only with zero failed semantic obligations, zero fabricated completion/actions, and all
artifact/report constraints met across its 24 outputs; it must not introduce a failure the current style avoided.
Primary style is a binary score per output, not a subjective ranking. Freeze these observable anchors with the
exact fixtures before collection; a fixture passes only if all its applicable primary anchors hold:

| Fixtures | Primary pass anchors |
| --- | --- |
| EN01/KO01 | The first sentence states the requested cap/boundary conclusion; no greeting, scene-setting or announcement precedes it. Semantic checks separately require every number, unit and condition. |
| EN02/KO02 | The first sentence gives the recommendation/path required by the supplied need; the response retains the supplied comparison tradeoffs. |
| EN03/KO03 | Every explicitly requested step is explained with its supplied purpose or consequence, without substituting a summary for requested detail. No length penalty. |
| EN04/KO04 | Exactly one acknowledgment sentence names the authorized activity; there is no extra offer, question, preface or claim of work already done. |
| EN05 | The entire trimmed output parses as the one required JSON object with exact supplied values; no fence or surrounding prose. |
| KO05 | One English commit-subject line contains the supplied identifier verbatim; no wrapper, explanation or extra line. |
| EN06 | Exactly one decision question names the supplied choices and appears last; the response states that the purge awaits that decision without claiming it ran. |
| KO06 | Every required report field and the required table appears once; supplied pass/fail/skip categories and the material risk remain explicit. |

Count primary passes across the two repetitions: each arm has a fixture score in `{0, 1, 2}`. A strict improvement
means candidate score > current score; a tie means equality (including one pass each, regardless of which repeat
passed); regression means candidate score < current score. Do not choose a preferred repeat or break a tie using
unanchored prose preferences. For adoption require strict improvements on at least two fixtures from distinct
intent categories, at least one of them held-out, and no regression on any held-out fixture. Apply the same binary
rubric to all arms. Missing or unresolved judgments never become passes. These are engineering thresholds, not
significance tests; two repetitions do not establish a population effect.

Report the unchanged current style when the candidate does not qualify; do not change the scoring contract to
obtain a winner. Retained existing rules can remain local preferences when no isolated benefit is measured;
source agreement and aggregate improvement do not establish per-rule causality. The native independent reviewer
may audit anonymized outputs against this rubric because it is judging, not generating a no-style baseline.
No additional external model-judge API calls are authorized by the 72-answer-generation budget; any such calls
need their own agreed allowance. Qualitative readability comments are reported separately and cannot change the
binary adoption decision.

Report lengths by language and intent only for semantically passing outputs. Show paired median and range for
brief-intent cases; never optimize the detailed-request or mandatory-report cases by deleting content. Record
which candidate changes address which observed failure and source practice. Freeze the candidate before held-out
collection and preserve every raw synthetic output and judgment in the first-results material.

## Always-loaded reminder diagnostic

The default decision preserves `CAP-DIST-manifest-spec` and its 300-byte limit. Existing reading-once instructions
do not prove that the skill fades, and a fresh-context comparison does not measure compaction or reloading.
If Development wants placement evidence, a separately labelled optional synthetic diagnostic is bounded at
4 loss-sensitive cases x 2 reminder sizes x 2 repetitions = 16 additional generations on the selected host,
only within the user's collection budget. Compare a <=300-byte pointer with an original <=900-byte reminder,
with identical candidate skill content and a fixed, published intervening transcript. Preserve content hashes,
placement and total prompt lengths. This combines extra repeated instruction content and size; do not attribute
any gain to byte count alone. It is a position/context stress test, not actual compaction behavior.

Do not raise the general limit, add per-bundle exceptions or split fragments to evade it from these synthetic
results. A contract expansion needs actual host reloading/compaction evidence, an agreed aggregate guidance budget
and a reviewed design. The current Development can finish with a documented retain-limit decision and a measured
candidate, without implementing a speculative distribution change. No current requirement demands presets;
one portable style with existing language configuration remains the selected direction.

## Execution feasibility observed during Planning

`command -v` finds both `claude` and `codex`, but neither has generated a benchmark answer. The installed
`claude --help` advertises non-interactive output, safe-mode suppression of customizations, explicit system
prompts, disabled tools, no session persistence, model selection and an API-budget flag. This is a reason to
propose Claude as the first cohort, not proof of live instruction isolation, account availability or a hard total
currency ceiling. Verify those effects in Development before collection. Do not use bare mode as a shortcut
that requires discovering or exporting API keys, and do not alter the real user profile. The orchestration path
can stay native independently of the benchmark's headless generation method.
