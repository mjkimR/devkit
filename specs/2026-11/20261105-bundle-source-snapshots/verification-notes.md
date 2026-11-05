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
- Static types and dist lint pass. Fresh just test-dist: 1338 passed in 31.94s.
- Final full-fallback verification runs against the committed implementation before review completion.

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
provenance regressions are retained; the complete focused filesystem/installed consumer set passed 36 before adding
the third symlink guard regression, which also passed. Fresh fixed-content broader checks run before final report.

The Host's follow-up symlink-parent regression failed before the final path fix. Metadata reads now retain
the full lexical ancestor no-symlink validation before canonicalizing the source root. Both direct and parent
symlinks refuse; ordinary ../source preserves commit/digest. Full focused filesystem/consumer verification
passes 38 after these changes. No symlink policy was relaxed.

The Host requested explicit applicability on provider-removal actions: direct removal is skipped when absent,
--dev applies only to a dev-group declaration, and other direct requirements use their owning group while
transitive origins require separate resolution. Existing action detail, bundled/installation/reference guidance
and focused assertions now agree. This is an in-scope continuation clarification, no dependency parser/editing.

## Final frozen-content verification

Checked implementation and Living Spec head 5af40a4f9445c73272ec8bcb95f0a82d0e960eaa.
Focused filesystem/installed-consumer verification passed 38 cases; just test-dist passed 1344 without devkit-agt.
just test-affected --base a3367f0d94a8ecb9762bbf35b5d0d3f89a621fe0 selected mode=full for the new
tests/support helper and passed 6653 cases, skipped 15, in 143.21s. Its retained log is
/var/folders/4_/wzc3s9g57_b2yz788lj9kywh0000gn/T/devkit-run-501/a99295ba223d/20261105-143409-uv-run-qt_o41wo.log.
Distribution lint/format passed 221 files, Pyright reported 0 errors/warnings, sync --check reported no changes,
and cumulative CI governance against 2fd08f816e5c10991b92ba026c797eeb552aad02 passed all 22 rules.

Independent medium reconciliation verified all nine targets and accepted ADR with no findings. The reviewer
modified nothing and reported no explicit outside-worktree reads. Separate-index before/after tree was
68716429a413ba2bd39308198558219c01f77d72 and HEAD was unchanged. Native confinement is not claimed.

The recorded baseline SHA has no snapshot/refresh command adapters (confirmed by git show, without checkout).
The head outcome is measured by the retained real wrapper build/clone/install/refresh and rollback tests above.
No executable before-change consumer measurement was recorded in Planning or run here; the Host receives that
missing baseline measurement explicitly. No authentication latency or performance delta is claimed.
