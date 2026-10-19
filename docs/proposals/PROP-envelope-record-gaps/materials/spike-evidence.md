# Spike evidence for envelope record gaps

Evidence gathered in the first Planning turn (worktree at 97cdcd8). Paths are repository-relative.

## Q1: challenger findings and round counts

- `packages/devkit/src/devkit/workflow/unit/envelope/model.py`: `REVIEW_REF = review-\d{2,}\.ya?ml`; a `reverify`
  without a `review: review-NN.yaml` is malformed. `Envelopes.review_state()` is the latest `review` or the last
  `reverify` naming it; `deciding(kind)` is `latest(kind)` for every other kind, so `envelope-check-pass(challenger)`
  would read the raw challenger envelope.
- `authoring.py` `carried_findings`: `--from` accepts only `review` or `reverify` files; `latest` means the review state.
- `devkit workflow envelope new --kind challenger --findings-file` accepts `resolution: resolved` (only `review`
  refuses it), so a worker could mark findings resolved in the challenger envelope itself; that mixes the reviewer's
  return with the implementer's disposition and loses what the challenger actually returned.
- No check of `sdd-proposal` reads `challenger` findings (`packages/devkit-spec/src/devkit_spec/bundle/workflows/sdd-proposal.md`:
  only `collect-feedback` has an envelope check, on `feedback`). The `plan-accept` request lists the support-role
  envelopes from `envelope check`, which prints `open_findings=N` for each.
- Repository records: 25 `reverify-*.yaml` and 11 `challenger-*.yaml` under `specs/` and `docs/`. Renaming the
  reverify `review` key would make every existing reverify malformed, so the key stays.
- Reproductions: `FB-challenger-findings-stay-open` (`challenger-01 ... open_findings=15`), and the
  `PROP-worktree-host-compatibility` feedback envelopes `feedback-01..03` (challenger-04 and -05 open after the fold).
- Round count: `FB-review-loop-round-count-across-procedure-change` (open, in
  `docs/proposals/PROP-worktree-host-compatibility/feedback/`). Its `worker-02.yaml` counted three unmarked rounds as
  rounds 1 to 3 and recorded round 4 as the cap round. `references/review-loop.md` section 1: "Counts are read from
  these markers"; nothing says what an unmarked round counts as, or whether folding user answers opens a new batch.

### Options compared

| Option | Works at `medium` (one pass) | Record shows the reviewer's return unchanged | Engine change |
| --- | --- | --- | --- |
| A. `reverify --from challenger-NN.yaml` closes the round | yes | yes | `--from` and the `review` reference accept `challenger-NN`; challenger deciding state like review |
| B. `--resolve` on the next `challenger-NN` | no: `medium` has no next round | no: the next round mixes dispositions into a reviewer return | carry-forward on `new` |
| C. Rule: the next round's summary resolves | no | yes | none; `open_findings` stays wrong |
| D. `envelope check` omits `open_findings` for unread kinds | yes | yes | output change; hides the count instead of recording the disposition |

## Q2: settled assumptions

- `model.py` `Answer` items carry `question`, `choice`, `decision`, `constraints`; `answers` is required and
  `answers_to` must name a worker envelope with questions.
- `Envelope.assumptions` is a tuple of strings, and envelopes are never overwritten, so a 1-based position into the
  named worker's `assumptions` is stable; `reverify --resolve N` / `--waive N=REASON` already address findings by
  1-based position.
- Reproduction: `FB-answer-envelope-no-slot-for-settled-assumptions` (`answer-02.yaml` of
  `specs/2026-10/20261019-devkit-dist-package-separation`, two constraints prefixed "Settled by the user in the same round:").

## Q3: proposal boundaries

- Frontmatter values in the ten proposals of `docs/proposals/` use three forms: a bare capability area
  (`delivery/`, `harness/`), a docs-root path (`capabilities/delivery/`, `stories/delivery/`) and a repository path
  (`packages/devkit-spec/src/devkit_spec/`, `docs/capabilities/delivery/`, `docs/glossary.md`,
  `.devkit/installation.json`). Every entry of the current proposals resolves under one of these forms.
- `packages/devkit-spec/src/devkit_spec/proposals/scaffold.py`: `DEFAULT_TARGET_AREA = "capabilities/<area>/"`,
  written to `target_area` and `boundaries.owns` when `devkit spec proposal new` gets no `--target-area`.
- `proposals/handoff.py` and `proposals/specs.py` copy `target_area`, `owns` and `excludes` into the spec's carried
  notes and the task boundary, unchecked.
- `RULE-spec-format` (`rules/spec_format.py`) already validates proposal-anchor fields (`namespace`, the effort
  hints). `Violation` has a `severity` field, but the evaluator overwrites it with the rule's effective severity
  (`packages/devkit/src/devkit/rules/engine/evaluator.py`, `effective_severity` with the project's overrides), so a
  rule reports at one severity (corrected after `challenger-01` finding 1).
- Gate behavior (`docs/capabilities/gate/`): error-severity violations refuse the commit (`GATE_RULES_FAILED`);
  warnings pass with `GATE_RULES_WARNINGS`.
- Namespaced docs roots (`docs/packages/<name>/`, `[[tool.spec.namespaces]]`) hold their own `capabilities/`.
