# Adaptive assignment commands

## Usage

Install devkit-adaptive and use `uv run devkit adaptive assignment new|return|verify|close|list|show`.
`CAP-DLV-adaptive-assignments` defines all flags, schemas and examples; `CAP-DLV-adaptive-development` defines
when the delegating agent records them. The command group works from every worktree without approach selection.

## Output

Use `--format json` for one compact result object. Text uses ASSIGNMENT, CHECK, OUT_OF_SCOPE, VERIFICATION,
SUMMARY, GRANT, FIELD, WRITE, GOVERNING, DEPENDS_ON, UNVERIFIED, DECLARED_CHECK and EVENT sentinels.
Verification exit 1 means a failed result or a warning under strict; inspect `result` and codes. Other refusals exit 2.

## Error codes

- `ADAPTIVE_ASSIGNMENT_CLOSED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_ASSIGNMENT_EXISTS`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_ASSIGNMENT_NOT_RETURNED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_ASSIGNMENT_UNKNOWN`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_AUTHORITY_NOT_NARROWED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_BASE_NOT_ANCESTOR`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_CHECK_NOT_PASSED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_CHECK_OUTCOME_MISSING`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_CHILDREN_OUTSTANDING`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_CLOSED_UNVERIFIED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_COMMIT_NOT_GRANTED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_GOVERNING_UNRESOLVED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_HEAD_MOVED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_LEDGER_FRAGMENT_IGNORED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_LEDGER_UNREADABLE`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_LEDGER_UNWRITABLE`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_NESTING_DEPTH`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_PREEXISTING_DIRTY`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_REPOSITORY_UNSUPPORTED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_RETURN_NOT_COMPLETED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_REVISION_UNRESOLVED`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_SCOPE_OVERLAP`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_SCOPE_VIOLATION`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_UNCOMMITTED_CHANGES`: see the code table in `CAP-DLV-adaptive-assignments`.
- `ADAPTIVE_WORKTREE_UNAVAILABLE`: see the code table in `CAP-DLV-adaptive-assignments`.

## Library

`devkit_adaptive.features.assignment.usecases.listing.ListAssignmentsUseCase.execute(root, options)` returns a
result with assignments, observations, summary and notices. The ledger format is private. This command executes
no declared check, observes no ignored/out-of-worktree file or submodule content, excludes preexisting dirty paths,
and makes no claim that an earlier agent still runs. Governing documents are validated at assignment creation only.
Concurrent edits in the same checkout cannot be attributed; merged-in paths count as changed. Git environment
variables GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE are inherited. See the capability for the complete limits.
