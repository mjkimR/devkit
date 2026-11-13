# Snapshot source commit probe

Baseline: `7161366d4c1908f13cea6e54c771c42244d9ad0d`; Planning performed no production-source edits. The ignored probe
is `.devkit/transient/plan-snapshot/probe.py` in the assigned Planning worktree. It creates a real local Git repository
with the existing content-provider fixture at `tools/content`, creates a snapshot with the unfixed implementation,
then wraps only the in-memory `ls-tree` call to insert `--full-tree`.

Run: `uv run python .devkit/transient/plan-snapshot/probe.py`.

| Observation | Result |
| --- | --- |
| Unfixed committed subdirectory source | `source.commit=null` |
| Same source with `ls-tree --full-tree` | captured fixture `HEAD` recorded |
| Metadata-only preview | only `snapshot.json` modified; different current/candidate digests |
| Preview destination writes | none |
| Packaging flag | `false` |
| Reviewed apply | `updated`, captured commit recorded |
| Repeated apply | `unchanged`, `snapshot.json` modification time preserved |
| Uncommitted copied-input addition | `source.commit=null` |

The aggregate digest includes `source.commit` through canonical metadata (`seal()`), and `snapshot.json` itself is in
candidate file comparison. Thus adopting the corrected commit is an ordinary metadata refresh, with no protocol
change. Existing copied-input, captured-HEAD and source-path-spelling tests separately protect the retained behavior.

Development can reproduce the failing baseline by adding its subdirectory test before the one-flag fix; no checkout
of a different revision is needed. Probe fixtures remain ignored until guarded worktree cleanup.

Focused existing regression run at Planning source HEAD `416a493d1`:

```text
uv run pytest packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py -q -k 'optional_commit_matches_only_copied_committed_inputs or source_commit_is_bound_to_the_captured_head or source_path_spelling_does_not_change_provenance'
3 passed, 36 deselected
```

The Development changes stay in that existing test module. AC-02 adds subdirectory copied-byte and executable-mode
mismatch cases beside the verified root-provider case, and retains the captured-HEAD binding regression. AC-03
checks every destination file's modification time on the final unchanged apply, beyond the probe's metadata-file
check. These expanded regressions are acceptance criteria, not already implemented tests.
