# Selective release Planning evidence

Source worktree: `plan-selective-package-releases`, initial Planning source
`f64e9b7813a218774658ddda1695e3a24be3bc7c`.

## Current boundaries

- `scripts/version.py:16-70` reads root `VERSION`, rewrites all workspace versions/internal requirements and every
  package bundle version. A raw diff after running it would make generated changes look like authored changes.
- `scripts/release.sh:30-52` builds every workspace wheel; lines 53-83 construct one current-tag URL for all wheel
  commands. No package index supplies omitted companion wheels (`CAP-DIST-content-packages` section 2).
- `packages/devkit/tests/integration/package/test_lockstep.py:27-54` asserts all package versions equal root
  `VERSION`, pins equal the depending package version, and release commands include companion wheel URLs.
- `ARCH-07-deployment` section 1.1 describes monorepo workspace-source Git installation from one commit. It must
  remain distinct from release-wheel URL selection.
- `ADR-package-ownership-and-release-version` sections Foundation, MCP runtime, Wheels/namespaces and Single release
  version contain the version policy. Partial supersession must include same-version qualifiers outside the last
  section while retaining its namespace/ownership decisions.

## Options and interpretation

The Scout supports selective exact pins with original wheel URLs and hashes. Compatible ranges require a new mixed
compatibility promise; retaining lockstep fails the requested independent advisory version stability. Full option
trade-offs and the chosen definition of a significant change are in the proposal, avoiding a second contract here.

The Planning uses existing local source/contracts; it does not claim to have fetched historical release assets,
measured build speed, enumerated live wheel member sets, or proven a clean Git installation. Those are explicit
Development/release-bootstrap checks. Comparison builds are intentionally permitted for unchanged packages.

## Boundary checks for delegated evidence

Codex support-role isolation is emulated. Absolute worktree read scopes, read-only role instructions and before/after
Git observations substitute for native enforcement. The worker created the PADR scaffold while Scout research was
in progress; its own authored paths are accounted separately. The Scout reports no writes or Git mutations.

## Complete reverse-reference discovery

The Scout reran each inbound query with `-n 0`, removing the first-pass pagination limit. Counts are recorded
for review discovery, not as a claim that every inbound document needs a change.

| Target ID | Inbound references | Relevant linked contracts |
| --- | --- | --- |
| `ADR-package-ownership-and-release-version` | 33 | `ARCH-07-deployment`, `CAP-DIST-content-packages`, `CAP-DIST-in-repo-bundles`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership` |
| `ARCH-07-deployment` | 32 | `ADR-package-ownership-and-release-version`, `CAP-DIST-in-repo-bundles`, `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions` |
| `CAP-DIST-content-packages` | 51 | `ADR-package-ownership-and-release-version`, `CAP-DIST-in-repo-bundles`, `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions` |
| `CAP-DIST-workspace-ownership` | 28 | `ADR-package-ownership-and-release-version`, `CAP-DIST-content-packages`, `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions` |
| `CAP-DIST-manifest-spec` | 38 | `ADR-package-ownership-and-release-version`, `CAP-DIST-content-packages`, `CAP-DIST-in-repo-bundles`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership` |
| `CAP-DIST-sync-and-transactions` | 72 | `ADR-package-ownership-and-release-version`, `CAP-DIST-content-packages`, `CAP-DIST-in-repo-bundles`, `CAP-DIST-manifest-spec`, `CAP-DIST-workspace-ownership` |
| `CAP-DIST-in-repo-bundles` | 6 | `ADR-package-ownership-and-release-version`, `CAP-DIST-content-packages` |

The Scout inspected every workspace member's build configuration. All select package roots under `src/`.
The viewer ships its committed static page (`packages/devkit-viewer/pyproject.toml:33-35`), while frontend sources
are outside that wheel. Its frontend changes affect the wheel only through the normal committed-page rebuild.
Unbounded `hatchling` build requirements and floating uv setup (`.github/workflows/release.yml:38-43`) mean the
release recipe must be made explicit before relying on canonical fingerprints. No remote artifact availability
or cross-tool fingerprint stability was experimentally established in Planning.
