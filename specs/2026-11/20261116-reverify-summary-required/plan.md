---
id: PLAN-reverify-summary-required
spec: SPEC-reverify-summary-required
---

# [PLAN-reverify-summary-required] envelope reverify requires a summary that envelope commit accepts

## 1. Constitution & Invariant Review

None. The fix adds a refusal inside the existing authoring contract of `CAP-DLV-workflow-envelopes` (section 2:
"every authoring command refuses an envelope ... that cannot produce a valid envelope") and sharpens the message and
fix of an existing `ENVELOPE_COMMIT_INVALID` refusal (section 5 item 3), without changing which files commit.
`ARCH-08-1-agent-output` is followed: stable codes, a `[TARGET]` naming the flag to correct and a deterministic
`[FIX]`. No ADR is needed and no feature edge is added.

## 2. Architecture Overview & Impact

Only `devkit_agt.features.workflow` changes.

- `services/envelope/authoring.py` (`compose_envelope`): refuses an authored `reverify` whose `--summary` is missing
  or blank. This is the service every adapter calls through `WriteEnvelopeUseCase`, so the rule holds outside the CLI
  too.
- `services/envelope/commit.py` (`require_authored`): names each failing field (empty summary, undeclared stage,
  stale workflow/segment) and the flag that fills it, and builds a fix naming the kind's writer command and the
  same-file retry.
- `usecases/commit_envelope.py`: passes the Unit path and retry command to `require_authored`.
- `models/envelope.py`: owns `KIND_COMMANDS` (the kinds with a writer command of their own), moved from
  `cli/envelope.py` so the service can name the right writer without importing an adapter; the CLI imports it.
- Bundle text: the `spec-review` skill and the `spec` skill's `references/planning.md` show `envelope reverify`
  invocations without `--summary`; they gain it, followed by `devkit sync` and its outputs.
- Derived docs: `docs/development/reference/workflow.md` example gains `--summary`.

### Choice: refuse, not derive

The feedback offers refusing a missing summary or deriving one. Refusal is chosen:

- The summary is the reviewer's judgment of the round; a derived line such as "2 findings resolved" restates the
  findings and records no judgment, which would let a review loop close without the author ever stating one.
- The commit gate already treats an empty summary as unauthored; refusing at the writer moves the same rule earlier,
  before any file is written, so the writer and the commit agree.
- Refusal keeps the written envelope byte-identical to the flags passed, the property section 2 relies on.

### Choice: reuse `ENVELOPE_FLAG_INVALID`

A missing required value of an authoring flag is "authoring flags that cannot produce a valid envelope", the
documented meaning of `ENVELOPE_FLAG_INVALID` (`CAP-DLV-cli-and-output` error table), with `[TARGET]` the flag to
correct, as `--stage` on `envelope worker` already does. A new code would add a branch for agents with no different
next step. The commit refusal keeps `ENVELOPE_COMMIT_INVALID` for the same reason; its message and fix become
specific.

## 3. Component & Interface Design

```python
# services/envelope/authoring.py, inside compose_envelope, after the other flag checks and before the draft
if kind == "reverify" and not (flags.summary or "").strip():
    raise EnvelopeFlagError(
        "a reverify needs --summary: the judgment that closes the round",
        target_files=["--summary"],
        fix='Add --summary "<1-3 line judgment of the round>" to the same command',
    )

# services/envelope/commit.py
def require_authored(
    envelope: Envelope, workflow: str, segment: int, stages: set[str], *, unit: str = "", retry: str = ""
) -> None: ...
```

The check sits after `--from`, `--resolve`, `--waive`, `--check` and `--findings-file` validation, so those refusals
keep precedence and their existing tests unchanged (AC-05).

Commit refusal (AC-02, AC-03), one message listing every failing field:

```text
[ERROR]  (ENVELOPE_COMMIT_INVALID) envelope is not authored: summary is empty
[TARGET] <unit>/envelopes/reverify-01.yaml
[FIX]    Remove the uncommitted [TARGET] and write it again with `uv run devkit workflow envelope reverify --unit <unit>` and its original options plus --summary "<1-3 line judgment>", then run `uv run devkit workflow envelope commit --unit <unit> --file envelopes/reverify-01.yaml`
```

Failing fields and the flag each names: empty summary → `--summary`; a stage the workflow does not declare →
`--stage` (message names the stage and workflow); a workflow or segment other than the bound one → "the current
segment" (no flag; rewriting in the current segment records it). The writer is `envelope <kind>` for a kind in
`KIND_COMMANDS`, else `envelope new --kind <kind>`.

## 5. Error Handling & Edge Cases

- `--summary ""` and whitespace-only summaries are refused like a missing one.
- A bare skeleton (no authoring flag) is unaffected: `flags.authoring` is false and `compose_envelope` is not called.
- Stored reverify envelopes without a summary still load (`model.py` unchanged), so existing units are not made
  malformed; only a commit of such an uncommitted file is refused, as before, with the specific fix.

## 6. Verification & Test Plan

- Regression tests (written red first, kept):
  - `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`: reverify without `--summary` is
    refused with `ENVELOPE_FLAG_INVALID`, `[TARGET] --summary`, no file written (AC-01, whitespace case included);
    the commit refusal of an empty-summary file names `summary`, `--summary` and the retry (AC-02); an undeclared
    stage names the stage, workflow and `--stage` (AC-03).
  - AC-04: the existing `test_review_reverify_final_report_readiness_and_read_only_commands`.
  - AC-05: existing `test_output_contract.py` (`--resolve 9` without `--summary`), `test_layouts_and_authoring.py`
    (`reverify needs --from`), and a skeleton case in the new test.
- Callers of `compose_envelope` for `reverify` without a summary in existing tests gain a summary (approved behavior).
- Checks: `uv run devkit rules check --ci --base main`, `just lint`, `just typecheck` (pyright),
  `just test-affected --base 22b28c936` (fallback `mode=full` kept), `uv run devkit workflow envelope check --unit
  specs/2026-11/20261116-reverify-summary-required`.
- Baseline: the reproduction tests fail on the head before the fix (the red envelope records it); after the fix they
  pass on the fix head.
