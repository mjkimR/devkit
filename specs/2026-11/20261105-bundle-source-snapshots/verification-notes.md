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
