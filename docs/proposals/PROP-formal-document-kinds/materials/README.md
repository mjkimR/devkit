# Formal-kind correction materials

## Source and retention boundary

The corrected objective requires formal design, domain and operations kinds with complete existing-system support.
The adjacent [support audit](support-audit.md) records inspection against main commit
534ad541e9d1e87beffa6bbc4f1afa95c71f6106. It does not claim implementation or test execution.

`legacy-operations/` preserves exact file bytes from the halted worktree
`/Users/mj/workspace/workbench/repos/devkit-wt-dev-operations-documents` at commit
55bc46fb5ce350e0a84666d6df338f8947e54e1b. Original relative paths are retained below that directory with an extra
`.txt` suffix, so historical IDs do not become duplicate indexed documents. This work was not integrated into
main. Its ID-free direction is superseded; recorded tests and independent reviews concern only that old scope.
Formal kinds, prefixes, IDs and complete integration remain unimplemented/unverified by that evidence.

## Preserved original paths

- docs/operations/distribution-sync.md
- specs/2026-11/20261116-operations-documents/spec.md
- specs/2026-11/20261116-operations-documents/plan.md
- specs/2026-11/20261116-operations-documents/tasks.md
- specs/2026-11/20261116-operations-documents/target-docs.md
- specs/2026-11/20261116-operations-documents/envelopes/worker-01.yaml
- docs/materials/2026-11/20261116-operations-documents/development.md
- docs/materials/2026-11/20261116-operations-documents/direction.md
- docs/materials/2026-11/20261116-operations-documents/incoming-refs.txt

The supplied `docs/materials/2026-11/20261116-operations-documents/development-evidence.md` path does not exist at
that head. The actual evidence file is `development.md`, preserved under its original name plus `.txt`.
The worker envelope records the halt and limits. Preserve useful symptom composition and owner analysis as inputs;
repeat verification against the formal implementation rather than inheriting historical passing claims.

## Closure preservation

`legacy-operations/source-range.patch.gz` preserves the complete unmerged source/record diff from
85a79e22f74fbd4175be0a6c635285de8dbb342a to 55bc46fb5ce350e0a84666d6df338f8947e54e1b.
`legacy-operations/accepted-proposal/` preserves every file of the accepted proposal before its supersede closure.
The nine selected source files were byte-compared against the halted worktree before closure.
No old-direction review or test result is formal-kind implementation evidence.

The source patch is gzip-compressed without timestamps to retain exact patch bytes while avoiding diff-context whitespace in the repository diff.
Uncompressed SHA-256: `25aa8aff8f35e9a551756b2c60503a24d505e5ea802822acea1363f9748e9d7c`.
