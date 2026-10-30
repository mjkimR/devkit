---
reconcile_id: REC-lifecycle-feedback-fixes
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
---

# Lifecycle feedback fixes reconciliation

`CAP-DLV-workflow-envelopes` states the write-time stage check of `envelope worker`: an undeclared stage (`-`
included) is refused before writing, the bare skeleton included, with `ENVELOPE_FLAG_INVALID`, `[TARGET] --stage`
and a fix naming `workflow next`, the case where it names no stage and the declared stages; an unloadable
definition skips the check. `CAP-DIST-context-and-playbooks` names `devkit sync --locked` first for
`CONFIG_LOCAL_RENDER_STALE` and a plain sync only after `RECEIPT_STALE`; the distribution reference
(`docs/development/reference/distribution.md`) matches. `CAP-DOCS-document-model` section 3.5 item 5 states the
reference writes of a rename. The envelope commit fix (AC-01) changes no documented behavior:
`CAP-DLV-cli-and-output` describes `ENVELOPE_COMMIT_INVALID` without its fix text. No use case, architecture
document, glossary term or ADR changes; reusing `ENVELOPE_FLAG_INVALID` adds no row to `CAP-DLV-cli-and-output`.
`CAP-DIST-sync-and-transactions` still says "run sync" for this code in its personal-rendering paragraph; that
generic wording stays true and the file is outside this unit's write scope.

## Source feedback dispositions

- `FB-envelope-commit-fix-placeholder-fails-output-contract`: resolved by `SPEC-lifecycle-feedback-fixes` (AC-01);
  the base fix matched the contract test's placeholder pattern and the head fix does not; the output contract tests
  pass.
- `FB-render-stale-fix-ignores-worker-scope`: resolved (AC-02, AC-05); the fix order and a locked restore that keeps
  tracked files byte-identical are asserted in `test_local_config.py`.
- `FB-worker-envelope-stage-unchecked-at-write`: resolved (AC-03, AC-04, AC-05); `test_envelope_worker_stage.py`
  covers refusal on authoring and skeleton, `-`, declared and exception stages and the lenient path. On the base
  the handoff of `PROP-git-operator-planning-completion-route` moved this file to
  `specs/2026-10/20261030-git-operator-planning-completion-route/feedback/`, which another unit owns; this unit
  does not edit it, and the Host applies `status: resolved` and the Disposition there at integration.
- `FB-rename-write-scope-unstated`: resolved (AC-06), the optional template comment included; verified by review
  against `RULE-document-reference` and `ADR-immutable-decisions-editable-records`, `devkit sync --check` and
  `just rules-check`.

The duplicate FB-local-render-fix-ignores-worker-write-scope is outside this unit and left to the Host.

## Verification

Before/after: the base `commit.py` fix (`cbe8fc18`) matched the `PLACEHOLDER` pattern of
`test_agent_output_contract.py` (measured with `git show` of the base file, no checkout), and the head fix does
not. `just test-affected` passed (partial selection, 3317 passed, 1 skipped); `just test devkit` passed;
lint and type checks passed for `devkit`, `devkit-dist` and `devkit-spec`. The only tracked sync output is
`.devkit/installation.json`. The nested code review (`review-01`) found two P3 guidance issues, fixed and verified
in `reverify-01`.

Entrypoint derivation proposed the changed helpers, tests, template and receipt for all three capabilities;
none is applied: they are helpers or tests, not doorways, and the existing entrypoints (`cli/envelope.py`,
`playbook_get.py`, `context.py`, the documents package) already lead to them.
