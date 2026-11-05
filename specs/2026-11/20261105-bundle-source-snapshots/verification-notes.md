# Snapshot verification notes

Initial sync check: PASS exit=0. Codex path/role isolation is emulated through explicit absolute workdirs,
per-operation approval and range/snapshot audits. No runtime/dependency edge was added.

- Initial filesystem tests exposed a missing required strict_json_loads argument; fixed and 30 cases passed.
- Initial installed-consumer test used an incorrect override path; corrected to the existing bundle-relative
  override contract. Both installed CLI/consumer cases pass, including real wheel builds, fresh clone, editable
  reinstall, overrides, global duplicate refusal and harness-equipped relative-helper rule execution.
- Initial just test-dist: 1 failed, 1337 passed. Exact failure:
  packages/devkit-dist/tests/unit/architecture/test_layering.py::test_distribution_never_imports_the_harness[distribution].
  Static public API allowlist literals were interpreted as optional module references. Supported APIs are now
  distribution-name/public-suffix metadata describing consumer requirements; no harness module import/discovery,
  test change or policy exception. Architecture plus filesystem focused verification passed 49 cases.
- The first affected selector used its full fallback because tests/support/distsupport/snapshots.py was added.
  It reported 6645 passed, 15 skipped, 2 failed: the above architecture assertion and missing documentation of four
  snapshot error codes in packages/devkit/tests/integration/package/test_documented_codes.py.
  The error codes are now documented in docs/development/reference/distribution.md.
- Static types and dist lint pass. Fresh just test-dist: 1338 passed in 31.94s.\n- Final full-fallback verification runs against the committed implementation before review completion.

No private provider, measured auth latency or arbitrary source-code correctness is claimed.

## Independent code review fixes

The mandatory reviewer reproduced P1 concurrent authored-edit loss and P2 incorrect INVALID classification of
post-replacement validation failure. The replacement transaction now receives the verified prior file inventory,
moves the current tree to backup, compares that captured tree before installing anything, and restores/refuses
CONFLICT on mismatch. Transaction validation exceptions become WRITE_FAILED after rollback; preflight validation
remains outside the transaction. Regression tests cover edits during candidate preparation and both OSError and
the validator's actual SnapshotInvalidError. Focused filesystem/installed-consumer checks pass 34 cases.

## Verified commit and path spelling

Fresh reviewer independently passed seven transaction probes and found a new provenance defect: source_commit
captured one SHA but queried mutable HEAD. A real-Git retained regression failed before the fix, returning an old
commit that lacked copied bytes. All ls-tree lookups now use the once-captured immutable SHA. This is the reviewer's
concrete suggested correction, with no changed decision or API.

The Host's ordinary sibling-path case also reproduced: ../source yielded unknown commit and a different digest
from the canonical source. Source roots are now canonicalized after existing source symlink/directory validation,
before Git-relative identity checks. Its regression and explicit source-symlink rejection pass. Both failing
provenance regressions are retained; the complete focused filesystem/installed consumer set passed36 before adding
the third symlink guard regression, which also passed. Fresh fixed-content broader checks run before final report.
