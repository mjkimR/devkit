---
id: SPEC-bundle-source-snapshots
title: Repository-committed bundle source snapshots
summary: Copy reusable bundle sources into a local content package with provenance and explicit updates so consumer repositories can install private bundle content without upstream credentials.
status: planned
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-bundle-source-snapshots] Repository-committed bundle source snapshots

## 1. Problem Statement & Motivation

Handed off from proposal PROP-bundle-source-snapshots on 2026-11-05.
- **Preserved Materials**: `docs/materials/2026-11/20261105-bundle-source-snapshots`
- Target Docs Blueprint: `PROP-bundle-source-snapshots-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

Private content packages shared through uv Git dependencies require upstream credentials in each consumer
environment. `CAP-DIST-in-repo-bundles` already supports ordinary content packages installed from local paths or a
workspace. `CAP-DIST-content-packages` discovers them through the same bundle entry points as installed wheels.
The bundle CLI exposes validation and planning, but no source snapshot or upstream refresh operation.

A repository-committed copy of upstream bundle sources could remove recurring private-content fetches while
retaining normal selection, synchronization, receipts and overrides. The hypothesis applies to private bundle
content; the devkit runtime and other Python dependencies still need their own installation path.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Repository-committed bundle source snapshots so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Planning Decisions

The comparison and code evidence are in `docs/materials/2026-11/20261105-bundle-source-snapshots/source-and-dependency-boundary.md`.
`ADR-bundle-source-snapshots` records the packaging and refresh choice.

| Question | Settled direction | Consequence |
| --- | --- | --- |
| Source | An explicit accessible local content-package checkout, with static `pyproject.toml` metadata and ordinary `src/` resource modules. | No cloning, credentials, installed-module import or arbitrary build execution in the snapshot command. |
| Granularity | Copy every bundle entry point of that content-only package into one generated local wrapper. | Existing package-level installation can replace the original without stranding its other bundles. No provider precedence or partial shadowing. |
| Assets | Preserve original manifests, all variants, constitutions, declared source trees, templates and bundle-local helper files. | Rule/gate Python assets are supported when their dependencies satisfy the boundary below; copying rendered projections is excluded. |
| Provenance | Source package/version, each bundle/version, optional verified source commit, ordered file hashes/modes and aggregate digest. | Record a commit only when copied source files match that commit; otherwise use null. Never persist source paths, remote URLs, credentials or timestamps. |
| Local identity | Generated distribution/module names come from an explicit unique package name; local package version remains `0.0.0`. | Git adoption commit plus source digest identifies updates; unchanged input is byte-for-byte idempotent. |
| Update | Explicit source-to-snapshot refresh, inspectable diff and expected-current digest before applying. | No background fetch, automatic Git commit or silent overwrite. |
| Loader | Normal installed content-package discovery, selection and sync. | Existing duplicate-name errors remain; replacing dependencies is an explicit consumer step. |

#### Supported dependency boundary

The initial supported source package has only `devkit.bundles` entry points, static name/version metadata,
no project runtime dependencies, and resource-module initializers containing only a docstring or no statements.
It may provide several bundles. `devkit-starter` and the content-only catalog demonstrate these shapes.
A mixed application/command-provider package is refused with its offending metadata named.

A bundle-owned rule, gate or helper Python module is not an application package. Preserve it unchanged when
its relative imports stay within the copied plugin/helper tree and its absolute imports use the standard library
or documented devkit runtime APIs. Preflight checks Python ASTs for imports outside that set, original-package
absolute imports and syntactically dynamic imports; those cases report unsupported input before destination writes.
This supports the ordinary dependency-free rule case without claiming to prove arbitrary Python behavior.
Declarative runtime references receive the same check: hook handler service IDs and workflow check/plugin
references must resolve to documented capabilities of the explicitly required devkit runtime or copied local
assets. An external handler or unknown runtime reference is an unsupported-input refusal naming the requirement.
No source Python or hook handler is executed during inspection. Shell/helper tools and agent instructions retain their declared
consumer environment requirements; copying them does not install a runtime or make an offline execution guarantee.

The generated wrapper declares no dependency on the upstream package. A consumer supplies devkit and, for
rules/gates/workflows, its required harness through the existing installation mechanism. License/notice files
explicitly named by source package metadata are retained. Inputs needing nonstandard build mapping, omitted
resource helpers or unavailable runtime code are refused; no successful partial snapshot is emitted.

#### Command and transaction shape

Proposed public CLI (names settle here; final result models/error codes belong in the feature spec):

```bash
uv run devkit bundle snapshot /checkout/team-assets --to tools/team-assets-snapshot --package team-assets-snapshot
uv run devkit bundle refresh tools/team-assets-snapshot --source /checkout/team-assets --check
uv run devkit bundle refresh tools/team-assets-snapshot --source /checkout/team-assets --expect <current-digest> --candidate <reviewed-source-digest>
```

Creation writes a generated package with `src/team_assets_snapshot/<bundle_module>/bundle/`, empty resource
initializers, `pyproject.toml` and a schema-versioned `snapshot.json`. Original bundle names, versions and content
bytes remain unchanged; generated entry points target the wrapper's distinct module namespace. A package with
colliding or invalid normalized wrapper module names is refused. The destination must be a new directory inside
the consumer repository and must not overlap the source, Git/devkit/agent state or another snapshot.

The payload inventory records every owned source and generated packaging file, excluding `snapshot.json` itself.
The aggregate digest covers canonical provenance metadata and this ordered path/byte-hash/normalized-mode
inventory, with the aggregate digest field omitted. Refresh structurally validates `snapshot.json`, recomputes its
aggregate and checks payload entries; no recursive self-file hash exists. Both inventory and drift checks exclude
only derived `__pycache__` trees and `*.pyc` files, following existing source-file conventions. Other unexpected
files remain authored drift. Editable discovery must not block a later refresh merely by writing bytecode. Version-only source changes are observable provenance updates. No local version bump is needed for an
editable repository package. A refresh with the same metadata/content writes nothing.

Creation and refresh stage and validate the complete candidate before touching the destination. Refresh compares
all owned files and unexpected additions against `snapshot.json` and refuses local changes, unknown provenance
schemas and an expected-current digest mismatch. Its result lists additions, modifications, mode changes and
removals deterministically; `--check` writes nothing. Apply uses a guarded staged replacement with rollback on
reported write/validation failure. Never merge local edits automatically. Source drift between preview and apply
is exposed through the candidate digest in both results; apply requires `--candidate <reviewed-source-digest>` in addition to `--expect`. Creation is explicit without a
preview; refresh apply always requires both digests. The feature spec defines the conflict code.

The command does not edit consumer `pyproject.toml`, `uv.lock`, config, overrides, receipt or Git. It returns exact
local package installation and upstream dependency replacement instructions. Before installation, the consumer
removes the original content-only provider and installs the wrapper in the dev dependency group. If another
requirement keeps the original provider installed, the existing duplicate-name error must be resolved explicitly;
no import/package precedence is invented. All original bundles are in the wrapper, so unrelated selections from
that provider remain available. If refresh changes generated packaging metadata or bundle entry points, its result requires reinstalling the
editable local package with an explicit `uv sync --reinstall-package <wrapper-package>` action before normal
discovery/sync. A removed bundle that is still selected must be explicitly deselected with `devkit remove <bundle>`;
refresh reports each affected selection and never silently removes it. Installed-consumer verification covers
bundle additions and removals, not just changed asset bytes. Normal `devkit sync` then updates receipts and keeps project overrides under
`CAP-DIST-workspace-ownership`, including upstream drift notices. Snapshot refresh alone does not sync.

#### Alternatives and impact

- **Manual source copy:** viable today, but has no shared inventory, local-edit refusal or refresh diff. Keep it as
  an escape hatch, not the repeatable command's implementation contract.
- **A `.devkit/local/` source loader:** avoids wrapper packaging but duplicates discovery/ownership. Rejected in
  `CAP-DIST-in-repo-bundles`; this proposal preserves that decision.
- **Installed-package or arbitrary wheel vendoring:** convenient input but importing/building runtime code and
  dependency closure would broaden the authentication promise. The first command reads an accessible checkout.
- **Selected-bundle extraction while leaving its package installed:** conflicts with global duplicate discovery.
  Whole content-package replacement is the first scope; partial extraction needs a demonstrated consumer case.

Implementation remains within the distribution feature: CLI calls typed use cases, services decide source/package
support, repositories read/write source snapshots, and models carry results/errors. No new feature edge is
admitted. `target-docs.md` names exact future paths and retained contracts. No production or Living Spec edit is
part of this Planning turn. Development effort remains `medium`; estimated size remains `L` (one spec with creation,
refresh and installed-consumer verification).

**Scope excluded:** devkit runtime copying, arbitrary executable-package vendoring, dependency/build execution,
automatic upstream access, credentials, all-network-free bootstrap, automatic Git commits, provider precedence,
a second loader and automatic three-way merging of locally edited sources.

### 3. Verification and Evidence Limits

No private source package was supplied. The design is grounded in the public starter/catalog layouts and existing
loader contracts, not a measured fix in a private consumer. That limit does not prevent specifying a supported
class; unsupported real inputs will name the needed dependency/layout rather than claim success.

Development acceptance checks:

- **AC1:** Given a supported multi-bundle content package, creation preserves all manifest/variant/template/helper
  bytes and executable modes, emits valid importable wrapper entry points and credential-free matching provenance.
  A self-contained rule fixture using the documented devkit APIs is included, not categorically rejected as Python.
  Dynamic Python imports and a declarative external hook handler produce explicit unsupported-input refusals.
- **AC2:** Given a fresh consumer with declared runtime/build dependencies available and private origin inaccessible,
  installing only the committed local wrapper and running locked sync reproduces its selected assets. No private
  origin requirement remains in the consumer dependency graph. A built-wheel consumer test proves this boundary.
- **AC3:** Given changed upstream bytes, modes, manifest metadata or deletions, preview lists the complete diff.
  Applying the reviewed source/current digests updates coherently; identical input after editable installation and
  discovery writes nothing despite bytecode. Provenance hashes round-trip without self-reference. An injected
  recoverable write failure leaves the previous package/provenance usable and unchanged.
- **AC4:** Given local source edits/additions, stale digests, unknown schemas, unsupported imports/layout/dependencies
  or conflicting bundle providers, the relevant command returns a stable actionable condition and never silently
  overwrites consumer content or claims a complete snapshot.
- **AC5:** Given a project override, explicit refresh followed by ordinary sync preserves the adaptation and reports
  upstream drift using existing ownership behavior. The snapshot operation leaves overrides and receipt untouched.
- **AC6:** Given a source package providing several bundles or runtime command entry points, preflight reports the
  complete replacement set or refuses the mixed runtime package; it never silently removes a still-needed provider.
  Refreshed entry-point additions/removals request reinstallation and explicit deselection where necessary.

Use real filesystem/inventory tests for hashing, safety and rollback, CLI result tests for codes/actions, and
installed-consumer tests for discovery, fresh clone bootstrap and supported rule assets. Run `just test-dist` to
retain dist's runtime independence from the harness; rule execution belongs only in a harness-equipped consumer
fixture. No performance improvement is claimed, so no timing baseline is required.

### 4. Lifecycle & Retirement Criteria

This proposal is in Planning at `medium` effort. It has no prerequisite proposal, including
`PROP-selective-package-releases`: source package version, bundle version and digest work under either release
policy. Acceptance decides the explicit source/whole-provider replacement and dependency boundary above.
Handoff starts one feature spec and promotes the PADR. Reject the proposal if private-content reuse does not justify
explicit provenance/refresh beyond manual local-package creation. Implementation and integration remain pending
until their lifecycle authorities and verification hold.

