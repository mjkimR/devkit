---
id: SPEC-selective-package-releases
title: Selective package releases under a shared release version
summary: Keep unchanged package versions stable while assigning one shared release version to changed packages and required dependency updates.
status: in-progress
created: 2026-11-05
related_capabilities: [CAP-DIST-content-packages, CAP-DIST-in-repo-bundles]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-selective-package-releases] Selective package releases under a shared release version

## 1. Problem Statement & Motivation

Handed off from proposal PROP-selective-package-releases on 2026-11-05.
- **Preserved Materials**: `docs/materials/2026-11/20261105-selective-package-releases`
- Target Docs Blueprint: `PROP-selective-package-releases-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

`scripts/version.py` assigns root `VERSION` to every workspace package, every bundle manifest and each versioned
internal requirement. `scripts/release.sh` builds all workspace wheels and generates commands from one release URL.
`ARCH-07-deployment` and `ADR-package-ownership-and-release-version` state that lockstep contract.

An independently consumed library such as `devkit-advisory` changes version even when its distribution is unchanged.
The proposed direction keeps one human-selected release number while retaining unchanged package identities.
Changed dependency metadata is a package change: an advisory update can still advance its exact-pin dependents.

Example: release `0.1.7` changes only a dist-owned skill. `devkit-dist`, and the reverse dependency closure whose
exact pins change, take `0.1.7`; `devkit-advisory`, `devkit-cli` and `devkit-core` retain `0.1.6`. A later advisory
change advances advisory and its necessary dependents to that release number.

## 2. User Stories

- **US-1**: As a maintainer, I prepare one release while retaining unchanged published wheel and bundle identities.
- **US-2**: As a consumer, I install a complete compatible wheel or Git set using its actual versions and original artifact locations.

## 3. Non-Goals

1. **Scope Excluded**: Independent package version choices, ranges, registry publication, application refactors, new feature edges, model/npm policy changes, handbook regeneration and remote publication during Development.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Selective identity
- **Given** a dist-owned skill change or identical shipped content
- **When** the release tooling prepares, checks, builds or verifies the applicable fixture
- **Then** Given a dist-owned skill change or identical shipped content, preparation advances only changed packages and exact-pin reverse dependents; identical wheels and unchanged bundles retain versions.

### [AC-02] Dependency closure and consumers
- **Given** an advisory change
- **When** the release tooling prepares, checks, builds or verifies the applicable fixture
- **Then** Given an advisory change, every runtime and optional internal exact pin reaches a fixed point, preserving markers, extras and unversioned pass-throughs; clean wheel and Git consumers resolve outside this workspace.

### [AC-03] Deterministic repreparation and immutability
- **Given** repeated preparation and prepare/revert/prepare
- **When** the release tooling prepares, checks, builds or verifies the applicable fixture
- **Then** Given repeated preparation and prepare/revert/prepare, plans are deterministic against the completed baseline; only still-matching generated edits unwind and no false pin seeds remain. Reused identities retain URLs and bytes; corrupt or missing artifacts and retry mismatches refuse.

### [AC-04] Canonical payload identity
- **Given** metadata
- **When** the release tooling prepares, checks, builds or verifies the applicable fixture
- **Then** Given metadata, README, resources, member additions/removals, bundle or recipe changes, detection includes affected wheels. Only owned generated versions and derived container fields normalize; code literals and executable modes matter. Bundle editing byproducts do not change fingerprints.

### [AC-05] Complete installation variants
- **Given** a complete inventory
- **When** the release tooling prepares, checks, builds or verifies the applicable fixture
- **Then** Given a complete inventory, generated commands cover harness, dist, SDD, viewer, tool, advisory, CLI, search and MCP using per-package URL closure. Advisory stays standard-library-only, dist installs without agt, and executable version is installed dist version.

### [AC-06] Bootstrap and failure behavior
- **Given** an explicit historical lockstep baseline
- **When** the release tooling prepares, checks, builds or verifies the applicable fixture
- **Then** Given an explicit historical lockstep baseline, bootstrap verifies original wheel filenames, checksums and source identities. Missing/invalid baseline, inconsistent dependencies, unsupported wheels and failed lock/sync produce no success. A partial upload retry uploads missing assets only and refuses mismatched existing bytes.

## 5. Approved Design and Implementation Assumptions

The following approved design remains normative. The current base preserves its premises. No historical published baseline has been supplied; Development uses verified fixture originals and does not create a real pending release or bump VERSION.

### 2. Technical Spike Questions

The Planning decisions below settle change identity, dependency propagation, artifact reuse, installation and
migration. Evidence and the reverse-reference discovery are retained in `docs/materials/2026-11/20261105-selective-package-releases/release-evidence.md`.

| Option | Benefit | Cost and risk | Recommendation |
| --- | --- | --- | --- |
| Continue lockstep | Existing release scripts and metadata checks | Unchanged advisory and content receive a version on every release | Reject: does not meet the requested version stability |
| Selective versions with exact internal pins | Retains the existing compatibility baseline; minimizes independent-package churn | Requires a release inventory and reverse dependency propagation | Choose for this change |
| Selective versions with compatible ranges | Can reduce dependency-only version propagation | Adds a mixed-version compatibility promise and a testing policy for ranges | Exclude from this change; no demonstrated need requires weakening exact pins |

`ADR-selective-package-versions` records the release-policy choice and the limited supersession of
`ADR-package-ownership-and-release-version`. Package ownership, public advisory imports and feature layering remain
its existing decisions.

### 3. Proposed Design & Impact

#### 3.1 Release and package identities

- Root `VERSION` remains the sole human-selected `X.Y.Z` release number. It is strictly newer than the selected
  previous release. A package never selects a separate new version.
- Every package whose normalized distributed content or internal dependency metadata changes takes that release
  number. Other packages retain their last published versions. A newly added package takes the release number.
- Bundle versions track their own source content. A changed bundle takes the release number; an unchanged bundle
  retains its published version, including when its owning package advances for other content or dependency pins.
- Repository-only files, such as tests and root documentation, do not advance packages unless they affect shipped
  wheel members. A package README used as distribution metadata does count.
- `devkit --version` continues to report the installed `devkit-dist` version. It is not redefined as the newest
  release number. Release membership is read from the inventory.
- The embedding model and viewer's npm library retain their independent policies. The model wheel remains an
  explicitly named immutable extra artifact when installation commands need it.

#### 3.2 Change detection and dependency closure

Use wheel contents as the change boundary instead of a guessed list of source directories. Comparison builds may
build all workspace wheels; the optimization is version and publication stability, not build-time reduction.

1. Load the previous completed release inventory and verify its schema, release identity and digest. It supplies
   the latest released package identities and normalized payload fingerprints. Refuse an absent or inconsistent
   baseline except during the explicit bootstrap described below.
2. When a pending plan already exists for this release and baseline, read its exact before/after generated
   package, bundle and internal requirement edits. Before seeding changes, logically unwind only mutations whose
   generated after-value still matches the candidate. Preserve unrelated authored edits and removed requirements;
   never blindly restore worktree files. Reject an ambiguous or mismatched plan/baseline before writing. This
   logical authored input prevents a reverted source change from retaining its generated dependent pins as seeds.
3. Build comparison wheels from that logical candidate input using one recorded release build recipe. Pin the
   backend and interpreter/tool versions used for comparisons. A recipe change is explicit input; unexplained build drift
   is not accepted as an unchanged artifact.
4. Canonicalize each wheel to sorted member paths plus content hashes. Ignore ZIP timestamps, ordering and
   compression, and omit the derived `RECORD`. Normalize only the owning distribution's dist-info identity and
   `METADATA` Version, and the top-level version fields in its registered bundle manifests. Keep requirements,
   entry points, Python code, resource files, permissions affecting execution, and other metadata significant.
   No global replacement of version-looking strings is permitted. Reject an unsupported normalization shape.
5. Fingerprint each bundle through the existing manifest content enumeration, including required support files
   within its declared resource boundary. Apply its `CAP-DIST-manifest-spec` editing-byproduct exclusions:
   `.DS_Store`, `__pycache__/` and `*.pyc` are never hashed. Within that content normalize only the manifest's
   generated top-level version. Bundle additions and removals change the owning package fingerprint.
6. Seed changed packages from the normalized content comparison. Compute a fixed point over every versioned
   internal requirement in runtime dependencies and optional extras, preserving markers and extras. When the
   required package's version changes, update the requirement to its actual new version and include the dependent.
   Preserve existing unversioned pass-through requirements. Development-group changes alone do not propagate.
7. Assign the release number to the final changed set and update each affected exact pin to its dependency's
   selected version, including restoring no-longer-needed generated advances to their baseline values. Build the
   final changed wheels and verify their normalized content against the prepared
   plan. Resolve `uv.lock`, run normal sync and commit the resulting metadata and receipt together.

An internal requirement policy change, including a range edit, is significant metadata. The released set is the
supported combination; arbitrary mixtures of packages from different inventories are not a new promise. Optional
requirements participate even when their marker or extra is inactive on the release host.

#### 3.3 Release plans and inventories

Keep tracked release preparation data under `scripts/releases/`, within the existing release-tooling boundary.
The pending plan is deterministic JSON, keyed by normalized distribution name. It contains a schema version,
release tag, baseline inventory identity and SHA256, build recipe, package path and selected version, bundle
versions, normalized fingerprints, changed/reused disposition, dependency closure, exact before/after generated
metadata edits and original artifact provenance.
It does not embed its own eventual Git commit ID.

The release build validates the committed plan against the tagged tree and emits a completed
`release-inventory.json` asset. That asset adds the tag's source SHA and the actual filename, URL and SHA256 of each
wheel. New wheels use the current release URL; reused wheels keep their original URL and digest. The inventory
contains every workspace package, including catalog, starter and repository tooling, plus separately identified
model artifacts needed by supported extras.

Example shape, illustrating fields rather than freezing the schema:

```json
{
  "schema": 1,
  "release": "0.1.7",
  "packages": {
    "devkit-advisory": {
      "version": "0.1.6",
      "disposition": "reused",
      "artifact_release": "v0.1.6",
      "wheel": "devkit_advisory-0.1.6-py3-none-any.whl",
      "sha256": "<verified-original-digest>"
    }
  }
}
```

The concrete schema and command flags belong in the Development spec. They must expose stable result/error codes
and deterministic next actions under `ARCH-08-1-agent-output`. Existing `just version-sync`, `just version-check`
and `just release-build <tag>` remain the normal entry points; baseline selection and bootstrap are explicit,
inspectable inputs. Add no release service or registry.

#### 3.4 Artifact reuse and failure behavior

- A published `(distribution, version, wheel filename)` keeps its original bytes. Download and verify a reused
  artifact only when a build/check needs its bytes. Do not rebuild and republish that identity.
- Release installation commands use the inventory's dependency closure and original wheel URLs. They cannot
  construct every URL from the newest tag or assume one version for all companions. Support the existing harness,
  distribution-only, SDD, viewer, tool, advisory-only, CLI-only and search/MCP examples.
- Reused artifacts need not be attached again to the newest release. Its inventory and checksum listing identify
  the original location. A missing or checksum-mismatched original fails the build with an actionable condition;
  it is not silently replaced by a local rebuild.
- Preparation first computes and validates the entire plan. A failed lock or sync emits no success result and
  leaves an explicit incomplete preparation that a rerun can finish; publication refuses it. No Git commit or
  publication happens automatically during preparation.
- Repeated preparation against the same baseline and content preserves the selected versions and plan. An
  unpublished edit after preparation recomputes against the same completed baseline; it never treats the pending
  plan as a published release. Refuse edits to a completed release identity.
- Publish the completed inventory only after every expected artifact is present and its digest is verified.
  Retry inspects already-uploaded assets, reuses matching bytes and uploads only missing artifacts; an existing
  mismatched identity refuses. Preserve the ordinary tag authorization and main-ancestry checks.

#### 3.5 Bootstrap and source installations

The first selective release explicitly imports one chosen completed lockstep release. Verify its published wheel
filenames and SHA256SUMS, compare package/bundle identities with its source tag, and compute normalized fingerprints
from those original wheels. Retain that baseline provenance in the first plan. Never infer a published baseline
from the working tree or rebuild historical bytes and label them original. A missing historical asset is a
bootstrap error for the maintainer to resolve before the selective release.

Git/workspace installations continue to obtain all internal packages from the same pinned monorepo commit through
the existing workspace sources. Different static package versions must satisfy the actual exact pins. Git builds
promise the prepared release's distributed content, not byte identity with an earlier wheel's ZIP container.
Clean consumer tests must exercise Git resolution and wheel resolution outside the source workspace, including
optional extras and tool installation; source-workspace import success alone is insufficient.

#### 3.6 Boundaries and retained documentation

The broad package boundary is limited to package/bundle metadata, release-related tests and generated deployment
outputs. It grants no application behavior refactor or new feature edge. Narrow task boundaries at handoff.
`target-docs.md` identifies the lasting architecture/capability statements and quick-reference changes. Partial ADR
supersession must remove every same-version dependency assertion that conflicts with selected exact pins, including
those outside the old ADR's section titled Single release version; it preserves all ownership and isolation clauses.

**Scope excluded:** independently chosen package versions, a package registry, compatible dependency ranges,
automated release authorization, advisory API changes, a build cache service, handbook regeneration, npm/model
version policy changes, and unrelated package or runtime refactors.

### 4. Lifecycle & Retirement Criteria

Planning and Development effort are `high`; estimated size is `L` for the coherent version/install/release contract.
No prerequisite proposal is required. Development must produce metadata, release inventory/build changes and
consumer verification together. This Planning activity does not publish a release or promise historical asset
availability: bootstrap checks are required before the first selective release.

Candidate Development acceptance checks:

- **AC1:** Given a change only to a dist-owned skill, preparation advances dist and the necessary exact-pin reverse
  dependency closure to `VERSION`, while advisory, CLI and core retain their prior versions. Given test-only or
  root-doc-only changes with identical wheel contents, no package or bundle advances.
- **AC2:** Given advisory changes, runtime and optional exact-pin propagation reaches a fixed point. Every selected
  internal requirement resolves to its inventory package version, preserving markers/extras and unversioned
  pass-throughs. Clean wheel consumers and Git consumers install outside the workspace.
- **AC3:** Given unchanged inputs, repeated preparation produces the same plan and versions. Given changed input
  after preparation, recomputation uses the completed baseline and unwinds only recorded, still-matching generated
  mutations. A prepare → revert originating source change → prepare fixture leaves no unnecessary package or
  bundle advances and every requirement matches its selected package version. Published reused identities retain
  original URLs and bytes; missing/mismatched artifacts and mismatched retry assets refuse rather than overwrite.
- **AC4:** Given packaged README/metadata/resource changes, additions/removals, bundle-only changes or a changed
  build recipe, detection includes the affected distributions. Only owned generated version fields and derived
  wheel container fields are ignored. Creating or changing bundle editing byproducts leaves fingerprints and
  selected versions unchanged. Changed code containing a version-looking literal remains significant.
- **AC5:** Given the complete inventory, generated wheel commands cover every existing installation variant with
  per-package URLs. Advisory-only installation preserves its standard-library-only dependency and import checks;
  dist-only installation still passes without agt. The executable reports the dist package version.
- **AC6:** Given a verified historical lockstep baseline, bootstrap records its source/artifact provenance. A
  missing baseline, invalid schema, dependency inconsistency, unsupported wheel or incomplete lock/sync cannot
  produce a successful release. A simulated partial upload resumes without replacing published bytes.

For count comparisons, Development constructs local package/wheel fixtures representing the old lockstep policy
and selective policy in one process; no worker checks out another commit and no unmeasured latency claim is made.
Acceptance and handoff remain with the Host and user after the required Scout/Challenger evidence and checks.

