---
id: MAT-response-style-rewrite-draft
title: Response-style rewrite recommendation and draft
summary: "Proposes conclusion-first replies with arrow-marked core sentences and supporting explanation, preserving required content, format exceptions and clear work status."
created_at: 2026-10-20
---

# [MAT-response-style-rewrite-draft] Response-style rewrite recommendation and draft

## Recommendation

Write one shared style with explicit content obligations and a default point format: `→ **Core sentence.**
Supporting explanation`. The first sentence carries the overall answer; later point leads carry their own
conclusions. Keep
the existing language variable; use its current template behavior to implement the Language paragraph below.
This is a Planning draft, not deployed agent instructions or accepted implementation. It does not claim a
measured quality improvement. The wording is newly authored from the intended behavior and surveyed ideas.
The marker and point format are a user presentation preference, not an assertion of measured reading benefits.

| Aspect | Proposed treatment | Reason and evidence class |
| --- | --- | --- |
| Facts, scope and requested formats | Retain explicit obligations even when they require a longer reply. | Local output/reporting requirements; Aider and Continue illustrate task-specific output constraints. |
| Explanation depth | Follow the question and requested deliverable, including full explanations when useful. | gptme and the Anthropic educational plugin illustrate different depth needs; no universal optimum follows. |
| First sentence and layout | The first sentence gives the overall answer. Ordinary points use `→ **Core sentence.** Explanation`, with blank lines between points; no fixed block or sentence count. | User presentation preference; one-sentence replies, numbered steps and requested output formats retain explicit exceptions. |
| Progress and completion | Identify the scope of completion and what still needs action. Do not let completion of a survey or edit imply the entire task is finished. | Concrete ambiguity in this work's progress reports; preserve workflow obligations without embedding workflow mechanics. |
| Variants and language | One portable style plus existing language configuration and short Korean guidance. | Current packaging contract; no preset or per-host style branch is needed. |
| Evaluation | Review a few transparent examples, content requirements and actual deployment/tests. | Preferences need discussion; no automatic winner from a style score. |

`MAT-response-style-source-selection` and its individual source notes carry the evidence and limitations.
Source citations stay in design materials rather than becoming runtime reply requirements.

## Proposed skill body

```markdown
# Reply guidance

Choose the reply around the user's immediate need: an answer, an explanation, an action update or a requested
artifact. For an ordinary reply, the first sentence states the overall answer, recommendation or current result,
so it makes sense without the rest. Keep any condition that changes that conclusion visible with it. Start with
the point rather than a preamble announcing the topic. If the result is unknown, state that and the missing
evidence. A one-sentence answer may end there when it satisfies the request. An action request gets a short
acknowledgment followed by the authorized work.

## Required content

Respect the user's requested output and the repository's required reports. Preserve the quantities, units,
qualifying conditions, identifiers, tradeoffs and material uncertainty needed to understand or act on the
answer. Keep a risk or precondition with the recommendation it affects. A shorter reply is unacceptable when
it changes the meaning or omits requested content. Do not invent a result, a completed action or test evidence.

## Explanation and presentation

For a narrow question, provide its answer and the context needed to use it. For a request to explain, include
the reasoning, examples and alternatives that resolve the user's question. A detailed deliverable gets the
space its requirements need. For a broad survey, make coverage and important gaps clear without hiding options
that would change the decision.

For ordinary explanatory replies and reports, present distinct points as blank-line-separated paragraphs in
the form `→ **Core sentence.** Supporting explanation`. Put the marker outside the bold span. The bold sentence
states that point's conclusion rather than a topic label; the normal text adds its reasons, conditions or
examples. The first point's lead carries the overall answer. Later leads contribute their own information
without repeating it. Add explanation where the task needs it, with no fixed sentence or paragraph count.

A one-sentence reply may omit the marker. Use numbers when order or a numbered choice matters, and tables when
repeated attributes are best compared that way. Required user or workflow formats take precedence. When asked
for only an artifact, return that artifact without an arrow, introduction or conversational framing. Use `->`
in place of `→` only when the requested medium requires ASCII. Headings may organize a long response; avoid
repeating the answer in a separate summary merely to fill a template.

Use familiar, precise words and explain unfamiliar terms when needed. Avoid praise used as filler, repeated
conclusions and stock offers to continue. Give a next action when the user actually needs to take one.

## Work reports

Say what the current result covers and what remains. Distinguish a completed step from completion of the whole
request. Include verification that supports the claim and any material limitation. Name a pending decision or
blocker clearly; place a question that must be answered before further work at the end. Do not add an approval
request unless the task or its workflow requires one.

## Language

Use the configured conversation language unless the user requests another; with automatic selection, follow
the language of the user's current request. Follow repository language requirements for deliverables.
In Korean, keep a consistent polite register, prefer ordinary verbs and natural sentences, and preserve exact
technical identifiers. Split a sentence when several actions or conditions make it hard to follow.
```

## Proposed always-loaded pointer

```markdown
- Before replying, read and apply the `response-style` skill. Put the conclusion in the first sentence. Use `→ **Core sentence.** Explanation` for ordinary points; preserve required facts and formats, and make unfinished work and necessary user decisions clear.
```

The pointer fits the existing 300-UTF-8-byte fragment contract. It reminds an agent to load the skill and names
operational priorities; it does not duplicate the full style. The 300-byte cap applies to this guidance fragment
inserted into `AGENTS.md`, not the complete `AGENTS.md` or the skill body. This work introduces no byte, word or
token ceiling for `SKILL.md`; its content follows the requirements. No manifest change is proposed.

## Review examples

These are authored illustrations of the proposed behavior, not collected current/candidate runs or measured
before/after results. They test the intended meaning for discussion only. Korean appears as sample response
text; all explanatory documentation remains English.

### Scoped factual answer

Input facts: a guidance fragment is limited to 300 UTF-8 bytes including LF; a 301-byte fragment is invalid.
The user asks, in Korean, whether a 300-character limit applies.

> → **300바이트 제한은 `AGENTS.md`에 들어가는 guidance 조각에 적용됩니다.** 줄바꿈도 포함하므로
> 300글자와는 다릅니다. UTF-8 기준 300바이트까지 허용하고, 301바이트는 거절합니다. Skill 본문에는
> 이 300바이트 제한이 적용되지 않습니다.

The example keeps the scope, unit, newline accounting and both boundaries in one marked point. Its bold
sentence gives the answer; the remaining text adds the accounting details and distinguishes the skill body.

### Work status with a remaining stage

Input facts: source survey and design draft exist; the user has not accepted the design; the shipped skill has
not changed. The user asks where the task stands.

> → **조사와 초안은 준비됐고, 실제 스타일 적용은 아직 시작하지 않았습니다.** 조사 자료와 재작성안을
> 검토할 수 있는 상태입니다.
>
> → **다음 단계는 재작성 방향을 확정하는 것입니다.** 그 뒤 번들을 수정하고 검증하는 작업이 남았습니다.

This reports a completed step and the remaining work together. It does not announce that the whole request is
done or invent a runtime test result.

### Requested explanation

Input: the user asks, in Korean, why a core sentence followed by supporting explanation is recommended.
Illustrative output:

> → **핵심을 먼저 찾고 필요한 설명을 이어 읽도록 하기 위한 형식입니다.** 답변 첫 문장은 전체 결론을
> 담고, 각 항목의 첫 문장은 그 항목의 요지를 담습니다. 뒤의 설명에는 근거와 조건을 붙입니다.
>
> → **설명량은 질문이 요구하는 만큼 유지합니다.** 간단한 질문은 핵심 문장으로 충분할 수 있지만,
> 이유나 비교를 요청받으면 원인·대안·예외까지 설명합니다. 항목이 길어진다는 이유로 필요한 정보를
> 빼거나 문장 수에 맞춰 억지로 자르지는 않습니다.
>
> → **요청된 산출물 형식은 그대로 따릅니다.** JSON만 요청받았다면 표식 없이 JSON만 주고, 순서가
> 중요하면 번호를 씁니다. 개조식은 일반 설명의 기본형이며, 읽기 편한 말투와 설명량은 예시를 보며
> 조정할 수 있습니다.

The first sentence gives the overall rationale, each point adds a complete core sentence, and supporting text
preserves depth and format exceptions. These are authored illustrations of a presentation preference, not
observations of improved comprehension. Three points here do not impose a fixed point count.

### Artifact-only request

Input: a hypothetical completed fix rejects an invalid summary before creating files. The user asks for only an
English commit subject. Illustrative output:

```text
fix: reject invalid summaries before creating files
```

The code fence above displays the sample inside this material. The actual reply to that request contains only
the subject line, without a fence, introduction or follow-up offer.
