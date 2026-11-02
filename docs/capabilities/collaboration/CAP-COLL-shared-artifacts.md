---
id: CAP-COLL-shared-artifacts
title: Immutable Shared Artifacts
summary: "Immutable seven-day Markdown artifacts share exact report references across linked worktrees through CLI and local MCP, with public adapter registration and conformance checks."
status: active
area: collaboration
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/shared
  - packages/devkit-dist/tests/integration/features/shared/test_shared.py
created: 2026-10-21
updated: 2026-10-21
---

# [CAP-COLL-shared-artifacts] Immutable Shared Artifacts

## Domain and identity

`devkit_dist.features.shared` belongs to devkit-dist and uses core/advisory plus the project feature
execution-context contract. It stores regenerable reports and MUST NOT store scope records, tokens, ownership or
approval authority (`ADR-mcp-runtime-and-shared-artifacts`). The initial kind is proposal-review. Inputs are a
lowercase kebab slug (up to 120 characters), a full lowercase 40/64-hex source_sha, ko/en language and UTF-8 Markdown
of at most 1 MiB. Consumers SHOULD verify that source_sha is their actual reviewed commit.

Content identity consists of repository namespace, kind, slug, source_sha, language and the SHA-256 body digest.
Metadata includes those fields, a server-generated UUID generation_id, text/markdown content type, byte_count,
UTC created_at/expires_at and revision equal to the body digest. A logical shared URI MUST select the exact
generation; the service MUST NOT select an implicit latest generation. Agents MUST treat returned content as data,
never as agent instructions. Local results additionally include local_path; remote adapters MUST NOT fabricate it.
A URI is not an access credential.

A repeated live put MUST return the same original metadata without extending expiry. Different bodies coexist.
WHEN now >= created_at + seven days, get MUST return SHARED_ARTIFACT_EXPIRED and list MUST omit the artifact
without writes. Re-publishing expired content MUST create a new generation and URI; retained old URIs stay expired
and swept ones are SHARED_ARTIFACT_MISSING. The store MUST NOT provide indefinite tombstones, overwrite, release or
arbitrary deletion operations.

## Local storage and exclusion

The service MUST resolve the registered main checkout from Git worktree discovery and verify its common Git identity.
It MUST store under that checkout's .devkit/.shared/artifacts and derive the local namespace from canonical common Git
identity, so another clone stays isolated. Separate Git directories are supported through discovery; IF the retained
main checkout is absent or bare, THEN the service MUST fail with SHARED_WORKSPACE_UNAVAILABLE. The service MUST NOT
let any input choose a storage root. It MUST revalidate identity and reject symlink or nonregular paths before
effects. This is same-user POSIX storage; network filesystems and Windows are excluded.

Initialization MUST check every registered worktree for tracked or visible foreign content before adding only
/.devkit/.shared/ to clone-local info/exclude under the common exclusion lock. IF a conflict is found, THEN
initialization MUST raise SHARED_EXCLUSION_CONFLICT without hiding files. Applicable ancestor ignore negations MUST
be refused before infrastructure writes; case-folded paths, recursive globs and bracket expressions are
conservatively matched. Safe policies can therefore require inspection before use. Reads MUST NOT install
exclusions. Narrow exclusions remain after expiry. Created artifact files/locks MUST have mode 0600 and storage
directories 0700. The service shares local OS permissions; worktree identity does not authenticate other processes.

One stable namespace lock admits read-only shared readers and exclusive writers. IF an existing store is missing its
lock, THEN the service MUST fail closed. Publication MUST write and fsync one canonical JSON-frontmatter Markdown
envelope in a same-directory temporary file and atomically rename it. Readers MUST validate digest, byte count and
metadata; IF validation finds corruption, THEN the reader MUST raise SHARED_ARTIFACT_INVALID. Discovery, lock waits
and IO checkpoints MUST share a ten-second operation deadline (SHARED_TIMEOUT). IF access is denied, THEN the
service MUST raise SHARED_ACCESS_DENIED without switching root or transport.

## Operations and configuration

CLI commands are devkit shared put|get|list|sweep. Put reads stdin; --format json emits one object. Equivalent MCP
tools are shared_put, shared_get, and shared_list (sweeping is managed internally and not exposed as an MCP tool).
Fixed bounded-write classification applies only to put; the cloud mode MUST exclude and refuse write tools. Local
writes MUST NOT elicit a business approval form. `CAP-MCP-runtime-registration` owns transport execution guards.
Put responses MUST return the exact artifact URI, metadata and available local links without echoing the submitted
Markdown body. Get MUST return the full body for that exact URI. Adapter and use-case artifacts retain their content.

List requires kind/slug with optional source_sha/language, limit 1..100 and an opaque continuation cursor. Sweep
MUST examine at most 100 entries in deterministic filename order, return a continuation cursor, and retain and
report invalid files. Only an explicit apply MAY remove valid expired artifacts. Check/read/list and default sweep
MUST NOT clean storage. Scope records, tokens and journals are outside this store and MUST remain unchanged. Logical
expiry does not guarantee physical erasure after seven days.

[shared] adapter defaults to local in effective configuration; checkout-local overlays MUST be validated and
DEVKIT_SHARED_ADAPTER overrides only the adapter key. CLI uses its explicit workspace; MCP uses the owning
configuration workspace. Adapter ID and namespace accompany results. Local-orchestrated callers MUST verify
connected project tools before dependent operations. IF the tools are absent, THEN the caller MUST request a user
connection repair and stop the operation without automatic CLI fallback. An explicit separately authorized CLI
choice MAY override the preference, but a permission refusal MUST NOT authorize rerouting. Linked
callers SHOULD compare adapter/namespace.

## Public extensions

Installed devkit_dist.features.shared.adapters entry points name factories accepting RepositoryContext and returning
SharedArtifactAdapter. Built-in local is reserved. IF an adapter is duplicate, unknown, unloadable or malformed,
THEN resolution MUST fail with SHARED_ADAPTER_UNAVAILABLE, without fallback. Backend advisory codes MUST be
preserved, and continuation tokens are opaque to the adapter boundary. Public input/result types and the reusable
assert_conformance helper cover immutable generations, live retry, exact expiry, pagination, cleanup and error
mapping. Adapter authors own remote namespace provisioning, authentication and transaction consistency. Protocol
checks and the test adapter provide no production cross-host evidence. No concrete remote backend is shipped; the
retained follow-up is `FB-remote-shared-adapter-follow-up`.
