---
id: PLAN-envelope-record-gaps
spec: SPEC-envelope-record-gaps
---

# Technical Plan: `SPEC-envelope-record-gaps` Close gaps in Planning records: folded challenger findings, settled assumptions, proposal boundaries

## 1. Constitution & Invariant Review

None. The three accepted ADRs (`ADR-reverify-closes-challenger-rounds`, `ADR-answer-envelopes-settle-worker-assumptions`,
`ADR-proposal-boundaries-name-existing-paths`) decide the design; `ADR-reverify-closes-challenger-rounds` refines
`ADR-bounded-high-effort-review-loop` without superseding it. Layering holds: the envelope changes stay in
`devkit.workflow` (devkit-agt), the rule in `devkit_spec.rules` using `devkit.rules` and `devkit_spec.entrypoints`.
No schema migration (AGENTS.md "Compatibility"): the `review` key keeps its name and existing envelopes stay valid.

Premise check against the base (03eef3f): the code points the spike evidence names exist unchanged (`REVIEW_REF`,
`carried_findings`, `Envelopes.deciding`, the `review`-only refusal in `parse_findings`, `Answer` items); the ten
proposal boundary values still use the three forms and all resolve; `RULE-spec-format` validates proposal anchors.
One difference inside the scope: the ordered Planning steps moved from the `planning-worker` contract to
`references/planning.md` (`SPEC-direct-planning-procedure`), so that reference receives the closing-reverify step.

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `packages/devkit/src/devkit/workflow/unit/envelope/model.py`: `REVIEW_REF` accepts `challenger-NN.yaml`;
    `Envelopes.round_state(kind)` (latest of `review` or `challenger`, or the last reverify naming it) backs
    `review_state()` and `deciding()`; new `Settle` items and `Envelope.settles`; `_check_kind_fields` lets an
    answer carry `answers` or `settles`; `reference_error` checks settles positions against the worker's
    `assumptions` and requires questions only when there are answers.
  - `packages/devkit/src/devkit/workflow/unit/envelope/authoring.py`: `carried_findings` accepts `challenger` files
    and names the challenger form in its fixes; `parse_findings` refuses non-open findings for `challenger` as for
    `review`; `parse_settle_flag`; `compose_envelope(settle=...)`; `render_envelope` writes `settles` after `answers`;
    the reverify skeleton comment.
  - `packages/devkit/src/devkit/workflow/cli/envelope.py`: `--settle` on `envelope answer`; `envelope check` appends
    `review=<file>` to reverify lines.
  - `packages/devkit-spec/src/devkit_spec/rules/proposal_boundaries.py` (new) with
    `bundle/rules/proposal_boundaries/{rule.py,guide.md,tests/test_rule.py}` and its `bundle.toml` asset;
    `devkit_spec.entrypoints.paths.exists` gains `directory=` for the trailing-`/` form.
  - Bundle text: `references/review-loop.md` (sections 1, 2, 4, 5), `references/planning.md` (steps 3, 4),
    `references/worker-records.md` (section 2), `references/envelope.md` where it lists reverify,
    `workflows/sdd-proposal.md` (`plan-accept` rule), `templates/proposal.md` (boundary comments).
  - Living Spec: `CAP-DLV-workflow-envelopes`, `CAP-DLV-delivery-workflows`, `CAP-DLV-proposal-incubation`,
    `CAP-GOV-spec-rules`, `CAP-HARN-agent-guidance` (rule asset list).
- **New Dependencies**: None.

## 3. Component & Interface Design

### Data Contracts & Types

```python
REVIEW_REF = re.compile(r"(?:review|challenger)-\d{2,}\.ya?ml")
CLOSABLE = ("review", "challenger")  # kinds a reverify closes

@dataclass(frozen=True)
class Settle:
    assumption: int  # 1-based position in the answers_to worker's assumptions
    decision: str

class Envelopes:
    def round_state(self, kind: str) -> Envelope | None: ...  # latest round of kind, or the last reverify naming it
    def review_state(self) -> Envelope | None: return self.round_state("review")
    def deciding(self, kind: str) -> Envelope | None: ...    # round_state for review and challenger, else latest
```

CLI: `devkit workflow envelope answer ... [--settle N=DECISION]...`; `envelope check` text line for a reverify:
`[ENVELOPE: envelopes/reverify-01.yaml kind=reverify seq=01 status=completed open_findings=0 review=challenger-01.yaml]`.
Key order: `..., answers_to, answers, settles, problem, resolves, activity_effort`.

`RULE-proposal-boundaries` (linter, warning, not fixable): for each proposal anchor (`docs/proposals/PROP-<slug>/proposal.md`
or `docs/proposals/PROP-<slug>.md`) with `status` `draft`, `reviewing` or `accepted` that `ctx.is_file_targeted`
accepts, each `target_area` string and `boundaries.owns` item is checked in order: a non-string or a non-list `owns`
or a non-mapping `boundaries` is malformed; an entry with `<...>` is a placeholder; `normalize` failures are invalid;
otherwise it resolves when one candidate exists (a trailing `/` requires a directory): `<path>`,
`<namespace docs root>/<path>`, `docs/<path>`, `<namespace docs root>/capabilities/<path>`, `docs/capabilities/<path>`.
Lines come from composing the frontmatter YAML (the item's line, else the key's).

## 4. Error Handling & Edge Cases

- A reverify naming a challenger round never changes the review state, so `envelope-review-passed` keeps reading
  only review rounds.
- `--from latest` with no review stays a refusal; the fix names the challenger path, since `latest` keeps meaning
  the review state.
- An answer whose settles do not fit is malformed as a whole (fail closed): its answers stop counting.
- A namespace that is not registered (or `global`) falls back to `docs/`; a malformed `[tool.spec]` propagates as
  `SPEC_CONFIG_INVALID`, as for the other rules.

## 5. Verification & Test Plan

- devkit-agt tests (`packages/devkit/tests/workflow/`): challenger reverify via CLI (AC-01), the deciding states
  through `evaluate` (AC-02), `--from` refusals (AC-03), challenger findings refusal (AC-04), reverify reference
  parsing (AC-05), settles authoring, loading and hold (AC-06, AC-07).
- Rule tests in `bundle/rules/proposal_boundaries/tests/test_rule.py` (AC-08 to AC-10) and the package's rule-ID list
  in `packages/devkit-spec/tests/test_package.py`.
- Wording tests in `packages/devkit-spec/tests/test_effort_procedure.py` and a new test for the settles and boundary
  procedure text (AC-11).
- The rule run against this repository's current proposals reports nothing (premise check).
- `just lint`, `just check`, `just test-affected`; the commit gate's `devkit rules check --staged`.
