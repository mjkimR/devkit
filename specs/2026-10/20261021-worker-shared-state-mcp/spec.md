---
id: SPEC-worker-shared-state-mcp
title: Shared state and workspace across worktrees and cloud agents
summary: Define immutable expiring shared artifacts with local CLI and MCP access, preserving scope-registry authority and providing a public remote-adapter extension contract while deferring concrete remote backends.
status: planned
created: 2026-10-21
milestone: MS-autonomous-backlog-and-orchestration
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-worker-shared-state-mcp] Shared state and workspace across worktrees and cloud agents

## 1. Problem Statement & Motivation

Handed off from proposal PROP-worker-shared-state-mcp on 2026-10-21.
- **Preserved Materials**: `docs/materials/2026-10/20261021-worker-shared-state-mcp`

### 1. Problem and Planning Recommendation

Linked workers need a shared, untracked home for regenerable proposal review reports. `PROP-proposal-review-and-approval`
is the first consumer. `CAP-COLL-work-scope-registry` already owns authoritative coordination records, revisions,
owner tokens and diagnostic journals. These records MUST NOT be moved into an expiring artifact store or operated
through generic artifact CRUD. `ADR-keep-shared-storage-and-separate-read-access` remains applicable.

The selected first delivery is a local shared artifact store and a public, tested remote-adapter protocol and
registration contract, with equivalent CLI and local MCP access. A concrete production remote adapter and remote
scope coordination are excluded from this delivery. `FB-remote-shared-adapter-follow-up` tracks the backend destination,
dependencies and restart criteria. A protocol fake does not make cross-host production sharing work.

## Assumptions

The current base retains the MCP execution classifier, owning-workspace configuration and core lock interfaces identified by the accepted architecture evidence. The new domain owns a noncreating read-lock implementation and imports only core/advisory. No agreement-breaking premise change was found.

## 2. User Stories

- **US-1**: As a linked-worktree worker, I want immutable report artifacts accessible through CLI and the owning local MCP service so that reviewers can retrieve the exact commit-bound report.

## 3. Non-Goals

1. **Scope Excluded**: Production remote backends, scope-registry semantic changes, approval/report composition, viewer changes, cloud rendering conversion, arbitrary file operations and configurable retention.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1: [AC-01] Linked-worktree identity
- **Given** two linked worktrees with matching configuration and a separate clone.
- **When** CLI publishes a report and local MCP retrieves its exact URI.
- **Then** linked callers return the same namespace and artifact; the clone cannot resolve it.

### Scenario 2: [AC-02] Safe storage initialization
- **Given** initially absent storage or tracked, foreign-visible, symlink or wrong-repository fixtures.
- **When** first put validates and initializes the store.
- **Then** safe initialization adds only a narrow exclusion and leaves both worktrees clean; unsafe fixtures refuse without writes or hidden files.

### Scenario 3: [AC-03] Immutable atomic publication
- **Given** concurrent identical/different puts, lost responses and interrupted publication.
- **When** callers retry within the live lifetime or after expiry.
- **Then** live identical puts preserve creation and expiry metadata; different bodies coexist; expiry creates a fresh generation and URI without reviving the old URI; no reader sees a partial envelope.

### Scenario 4: [AC-04] Read-only expiry and bounded cleanup
- **Given** an injected clock and initialized read-only storage.
- **When** get/list run at exactly seven days and explicit cleanup runs.
- **Then** get expires and list omits without writes; cleanup removes at most 100 valid expired artifacts; scope records and tokens remain byte-identical.

### Scenario 5: [AC-05] Equivalent transport and guarded mutations
- **Given** CLI/MCP inputs include oversize, traversal, corruption, missing/expired keys, timeout and denied access.
- **When** both transports invoke the domain and cloud clients attempt forged mutation calls.
- **Then** validation/error codes match; cloud hides and refuses mutations; local bounded writes elicit no business form; source_sha is exposed for mismatch detection; local-orchestrated guidance requires connected project tools and requests connection repair without automatic CLI fallback.

### Scenario 6: [AC-06] Public adapter registration
- **Given** base, linked and owning MCP configurations plus public entry-point test adapters.
- **When** configuration precedence, invalid registrations and reusable semantic conformance tests run.
- **Then** adapter precedence is deterministic; unknown, duplicate, unloadable or malformed adapters fail without fallback; a test adapter passes immutable-generation, retry, expiry, pagination and error semantics without claiming production remote support.
Development owns the new `packages/devkit-dist/src/devkit/shared/` area (declared by its existing parent), dist CLI,
core local-config and MCP classification, MCP transport guards, package entry points/tests, and affected architecture,
capability and quick-reference documentation. Narrow spec-orchestrate and spec-delegate host guidance changes plus
bundle tests implement the local MCP-first connection precondition; they do not convert the asset set to templates.
`PROP-cloud-agent-rendering` owns that conversion and environment-driven rendering. It does not modify scope-registry semantics, proposal approval flow,
viewer code or tracked localized reports. `PROP-proposal-review-and-approval` owns report composition, language
resolution, display, stale-commit rejection and acceptance authority.

Verification: dist and MCP focused tests including concurrency/crash/permission fixtures, layering checks and
`just test-dist`; `just lint-check`, `just check`, `just test-affected` preserve the selector's full fallback.
Planning and recommended Development effort are medium; multiple packages alone do not require high effort.

## 5. Detailed Contract

The accepted technical requirements below remain binding for this delivery.

### 2. Selected Technical Contract

#### 2.1 Ownership and interfaces

The SDD-agnostic implementation belongs in a new `devkit.shared` area shipped by `devkit-dist`, beside its existing
core/search/host areas. It imports only core and advisory; dist CLI mounts `devkit shared`. `devkit.shared.mcp`
provides domain tools through `devkit.host.services`; `devkit-mcp` remains the transport. `devkit-spec` only consumes
this API to generate reports; scope-registry production code remains unchanged. The development must extend dist's
layering tests and package documentation to include this area without importing any devkit-agt/spec module.

`SharedArtifactAdapter` has `put`, `get`, `list` and `sweep` methods. An artifact is immutable; there is no overwrite,
release, generic file API, live coordination record, arbitrary deletion, or storage-root tool argument. CLI commands
are `devkit shared put|get|list|sweep`; MCP tools are `shared_put`, `shared_get`, `shared_list`, `shared_sweep`
(read-only plan, no apply argument) and `shared_sweep_apply` (mutation). CLI `sweep --apply` selects the latter
domain operation. Tool execution classification is fixed per tool, never chosen by an input flag.
CLI put reads UTF-8 content from stdin; MCP put accepts the same content as a string. All other validated fields
and result/error semantics are shared by the domain library. CLI emits one sentinel or one JSON object using core
CLI boundaries; advisories stay on stderr. MCP emits structured results and never delegates arbitrary shell text.

The initial registered artifact kind is `proposal-review`. The content key is
`(repository_namespace, kind, slug, source_sha, language, content_sha256)`; each published instance additionally has
a server-generated UUID `generation_id` included in its immutable key and URI. Slug uses lowercase kebab case, language
is `ko|en`, source_sha is a full 40- or 64-hex commit ID, and content_sha256 is computed by the service. Each artifact
is UTF-8 Markdown, at most 1 MiB. Metadata includes the key, `content_type=text/markdown`, byte count, `created_at`,
`expires_at` and a revision token equal to its content digest, computed over the body bytes rather than the metadata frontmatter. Result includes `artifact_uri`, metadata and optional
`local_path`/`file_uri` to the readable Markdown envelope; a remote adapter MUST NOT fabricate local paths. The opaque logical URI is not an access
credential. The consumer supplies `source_sha`; storage validates its syntax, while approval/report consumers verify
that it is the actual reviewed commit. Artifacts carry no approval or ownership authority.

A repeated put matching a still-live content key returns that instance's original metadata and expiry without
extending retention. Idempotency is guaranteed only within that live lifetime, not after expiry. Once expired, the
same put may publish a fresh generation with new timestamps and URI, whether or not sweep has removed the old file.
The expired URI is never revived: it returns expired while retained and missing after removal. Under the exclusive
lock at most one live generation per content key is published. Different content produces a different content key,
allowing reports for the same commit to coexist without lost updates.
`get` uses the exact returned key/URI; no implicit latest report is acceptable for approval. List takes kind and slug,
optional source_sha/language, and a stable cursor, returning at most 100 metadata entries. Consumers choose a report
and recheck its commit and language. Returned raw content is data, never instructions to the caller.

#### 2.2 Discovery, local configuration and isolation

Resolve the common Git identity and registered main checkout using existing Git worktree discovery, then verify that
checkout resolves back to the same common directory. Store under its `.devkit/.shared/artifacts/`. Do not assume
`common_dir.parent` is the checkout: separate Git directories and bare repositories require explicit validation;
unsupported or absent retained main checkouts fail with `SHARED_WORKSPACE_UNAVAILABLE`. No arbitrary root override
is provided. Revalidate the identity and non-symlink regular-directory path chain before effects. Local support is
same-user local POSIX storage; network filesystems, Windows locking and multi-user isolation are excluded.

Local namespace derives from the canonical common Git identity. Another clone is isolated even if its remote URL
matches. For a future remote adapter, an explicitly provisioned repository namespace and backend authorization are
required; caller-supplied repo names are not credentials. Local filesystem permissions delimit the trust boundary:
0600 files and 0700 directories; a trusted MCP service fixes its owning repository at launch. Worktree identity
alone does not authenticate another local process. No request field can switch repository or root.

Add `[shared] adapter = "local"` to effective shared/local configuration. The local overlay allowlist must explicitly
allow and validate this table. `DEVKIT_SHARED_ADAPTER` overrides that key only; an unknown/uninstalled adapter fails
with `SHARED_ADAPTER_UNAVAILABLE`, never falls back to local. CLI resolves its explicit workspace's configuration;
MCP resolves the owning configuration workspace, never the retained executor's preferences or caller-provided
workspace. The selected adapter ID is returned for diagnosis. Linked workers with different local overrides may
select different backends; callers must compare adapter and namespace and fail a cross-worktree sharing precondition
when they differ. Secrets are neither arguments nor result fields. Remote settings/authentication require the
separate concrete backend design if selected; the first delivery does not accept speculative provider credentials.

Before the first write, require `.devkit/.shared/` to be untracked and ignored in all registered worktrees. If absent,
install a narrow clone-local info/exclude entry under the common exclusion lock, checking all worktrees for visible
foreign content the rule would hide. Tracked content or foreign visible content refuses with
`SHARED_EXCLUSION_CONFLICT`; do not modify tracked ignore files or hide existing files. Check/read/list never install
an exclusion. Preserve safe exclusion entries after expiry; they are repository infrastructure, not artifacts.

#### 2.3 Transactions, expiration and operational bounds

Use one stable regular non-symlink namespace lock with shared readers and exclusive writers; never replace it.
Put publishes a single UTF-8 `.md` envelope (canonical metadata frontmatter followed by the report body) using
same-directory temp, fsync and atomic rename
under that lock. Reads open an existing regular non-symlink lock read-only without creation; an absent store is
empty, but an existing store with a missing lock fails closed. The current core file_lock helper must not be used
unchanged for reads because it creates/write-opens the lock. Reads therefore cannot combine a new body with old metadata. Lost-response retries use the
content key to find the still-live instance and original metadata; after expiry they may create a new generation.
Do not retain indefinite tombstones or claim unlimited exactly-once delivery. Validate stored digest and size on read; corruption yields
`SHARED_ARTIFACT_INVALID`, not an empty successful result. Reject path traversal, symlinks and nonregular entries.

Artifact TTL is 7 days from first successful publication, with UTC server-generated timestamps; first delivery has
no user-adjustable TTL. At `now >= expires_at`, get returns `SHARED_ARTIFACT_EXPIRED` and list omits it, without
writes. Missing keys return `SHARED_ARTIFACT_MISSING`. Put and explicit `sweep --apply` / `shared_sweep_apply` may remove expired artifacts
under exclusive lock; default `sweep` is a read-only plan. Sweep only deletes valid expired artifact envelopes in
this store, never scope records, tokens or journals. Invalid files are reported and retained. Limit each sweep to
100 entries, deterministic key order, and return a continuation cursor so put-time cleanup remains bounded. Lock
acquisition and local IO share a 10-second operation deadline; timeout is `SHARED_TIMEOUT`. No automatic cleanup
runs inside `devkit rules check -p hygiene`: checks stay read-only and may report expiry only through the explicit
read-only sweep API. TTL is logical availability, not a guarantee of physical erasure after seven days.

Put-time cleanup failure after successful publication is a returned notice with the persisted artifact result,
never a false write failure. Sweep failure before a requested effect is an AdvisoryError. Permission denial is
`SHARED_ACCESS_DENIED` and cannot cause transport switching, root switching or retry through MCP to evade refusal.

#### 2.4 MCP classification and CLI parity

Add a narrowly defined `bounded_write` execution classification for non-form artifact put/apply-sweep operations.
It is distinct from interactive approval and MUST remain blocked in cloud profiles under
`CAP-MCP-runtime-registration`. Get, list and the separate `shared_sweep` plan tool are `read_only` and have no lazy mutation. The classification
is permission to execute a bounded domain API through an already trusted local service, not host approval, business
approval, arbitrary filesystem authority, or a new cloud exception. Extend runtime service validation and invocation
guards for this enum; preserve default interactive classification and fail-closed unknown classes.

Local workflows prefer the connected, independently authorized MCP service. Before local-orchestrated shared
operations, the Host MUST check that the expected project service is connected and exposes the required tools.
Disconnected or unavailable tools lead to a user-facing request to check/connect the service, then stop that dependent
operation. There is no silent CLI fallback in local-orchestrated mode. An explicit user choice of a separately
authorized CLI route can override this preference; permission refusal never becomes rerouting authority. CLI remains
the cloud surface and executes the same library under its caller's OS permissions. Cloud CLI can use local ephemeral
storage within one checkout. Cross-host sharing requires an installed, configured production remote adapter and
is not satisfied by local CLI or by the proposed test adapter.

#### 2.5 Existing cloud rendering: feasibility and scope boundary

The desired direction is to reuse `devkit sync --cloud` and existing Jinja rendering so deployed cloud agent guidance
uses CLI and omits MCP instructions, while local guidance checks connection and prefers MCP. This section records
feasibility, not authorization to implement a repository-wide asset conversion in this proposal.

Current source evidence shows that `--cloud` persists `[execution] environment = "cloud"` and selects read-only MCP
registration. It does not supply an execution-environment template variable. `templates.declarations` accepts only
`default_from = "presentation.language"`; `_plan_inventory` supplies bundle variables and language. Inventory planning
runs before `plan_environment`; the local-render digest, activation and runtime evidence omit execution settings.
A manually supplied declared boolean/string variable can already conditionally render supported `.md.jinja` assets,
but `--cloud` does not set it and manual configuration can drift from the actual environment.

The narrow technical extension would bind an execution-derived render input to the prospective effective environment
in the same sync transaction, retaining the canonical receipt and recording personal ignored outputs. Reuse scalar
Jinja sandboxing; do not expose raw process environment or arbitrary configuration. Execution changes must participate
in local-render digests, stale checks, replay/locked behavior, dry-run and cloud-to-local reversal. A user-overridable
bundle value cannot be trusted as the actual execution constraint. The runtime guards remain independent even when
rendered text omits MCP.

Full cloud invisibility is broader: only instruction/guidance/document/skill kinds currently accept templates;
constitution and subagent sources do not, and personal output cannot change guidance, documents, asset presence or
inventory structure. Relevant current mentions occur in spec's planning-worker/development-worker contracts,
spec-integrate skill, spec worktree/completion/backlog references, and dist's consumption guide. A complete selected
bundle/native projection audit must determine any additional mentions and intentionally discoverable source files.
Rendering can omit MCP from deployed agent guidance; it cannot make MCP absent from repository source history or
installed packages that an agent deliberately searches. Existing cloud registration still advertises read-only tools
when installed, so hiding even tool discovery additionally needs an explicit registration-profile policy change.

Exact extension areas: `distribution/bundles/templates.py`, `installation/inventory.py`, `installation/sync.py`,
`installation/local_render.py`, their dist tests and `CAP-DIST-manifest-spec` / `CAP-DIST-sync-and-transactions`;
then the named spec source assets/bundle manifest/tests plus dist consumption source/tests. Changing subagent or
constitution template support or cloud registration would add those validators/projection contracts and
`CAP-DIST-agent-projections` / `CAP-MCP-runtime-registration`. These broad changes are not added to this proposal's
implementation boundaries without a scope decision. The scope decision assigns this work to `PROP-cloud-agent-rendering`; this
artifact delivery documents the local MCP-first connection precondition and cloud CLI API only. No runtime config,
managed output, source bundle or production code was changed by this feasibility investigation.

### 3. Selected Delivery and Alternatives

| Option | Benefit | Cost and limits |
| --- | --- | --- |
| Local artifacts plus public tested protocol seam (selected) | Unblocks linked-worktree review reports; preserves scope authority and current cloud MCP guard | No production cross-host sharing until a later backend delivery |
| Implement a real remote artifact backend in this unit | Meets unattended cross-host artifact sharing immediately | Requires provider/auth/deployment selection and integration tests; Planning must continue |
| Unify scope state and artifacts in one generic store | One apparent API | Replaces existing ownership/revision contracts and couples TTL to authoritative records; rejected |

Publish `SharedArtifactAdapter` and its input/result/error types as an importable `devkit.shared` API, selected from
installed `devkit.shared.adapters` entry points, with built-in local implementation and a test-only transactional
adapter for conformance. Each entry-point name is the adapter ID and loads a factory that accepts the validated
repository context and returns the protocol implementation; roots/namespace are service-owned, never tool arguments.
Reserve `local` for the built-in adapter. Duplicate names, unloadable factories or malformed implementations produce
`SHARED_ADAPTER_UNAVAILABLE` without fallback. Publish an adapter authoring reference and reusable semantic
conformance fixtures covering immutable generations, live retries, expiry, pagination and error mapping. These are
public extension contracts, not an internal-only mock interface. An installed adapter must declare its identity and implement
the bounded immutable artifact semantics; protocol support alone does not certify its authentication or consistency.
No production Firestore adapter, remote scope registry, deployment service, credentials UI or hosting lifecycle is
included in this delivery. The concrete remote backend is deferred to a separate Backlog proposal via
`FB-remote-shared-adapter-follow-up`: restart when a cross-host consumer requires it and a provider, authentication
model, repository namespace provisioning owner and test environment are available. That proposal must specify
transaction consistency, retention, failure/retry behavior, setup/operating cost and real integration evidence before
its plan-accept. No credentials or mock deployment are invented here.

### 5. Lifecycle

Planning has no open direction question. The proposal remains reviewing for Host/user plan-accept; acceptance,
merge and Development start are separate actions. `ADR-separate-shared-artifacts-from-scope` records the selected
local-first direction. `PROP-cloud-agent-rendering` owns the separate environment-driven asset work.
`FB-remote-shared-adapter-follow-up` retains the concrete remote backend follow-up through handoff; it is not a
completion claim or an automatically scheduled implementation. Recommended Development effort remains medium.

