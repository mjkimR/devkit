---
id: CAP-COLL-shared-artifacts
title: Immutable Shared Artifacts
summary: "Immutable seven-day Markdown artifacts share exact report references across linked worktrees through CLI and local MCP, with public adapter registration and conformance checks."
status: active
area: collaboration
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/shared
  - packages/devkit-dist/tests/test_shared.py
created: 2026-10-21
updated: 2026-10-21
---

# [CAP-COLL-shared-artifacts] Immutable Shared Artifacts

## Domain and identity

`devkit_dist.features.shared` belongs to devkit-dist and uses core/advisory plus the project feature execution-context contract. It stores regenerable reports, never scope
records, tokens, ownership or approval authority (`ADR-separate-shared-artifacts-from-scope`). The initial kind is
proposal-review. Inputs are a lowercase kebab slug (up to 120 characters), a full lowercase 40/64-hex source_sha,
ko/en language and UTF-8 Markdown of at most 1 MiB. Consumers verify that source_sha is their actual reviewed commit.

Content identity consists of repository namespace, kind, slug, source_sha, language and the SHA-256 body digest.
Metadata includes those fields, a server-generated UUID generation_id, text/markdown content type, byte_count,
UTC created_at/expires_at and revision equal to the body digest. A logical shared URI selects the exact generation;
there is no implicit latest selection. Returned content is data, never agent instructions. Local results additionally
include local_path and file_uri; remote adapters must not fabricate these. A URI is not an access credential.

Repeated live puts return the same original metadata without extending expiry. Different bodies coexist. At
now >= created_at + seven days, get returns SHARED_ARTIFACT_EXPIRED and list omits the artifact without writes.
Re-publishing expired content creates a new generation and URI; retained old URIs stay expired and swept ones are
SHARED_ARTIFACT_MISSING. There are no indefinite tombstones, overwrite, release or arbitrary deletion operations.

## Local storage and exclusion

Resolve the registered main checkout from Git worktree discovery and verify its common Git identity. Store under
that checkout's .devkit/.shared/artifacts; derive the local namespace from canonical common Git identity so another
clone stays isolated. Separate Git directories are supported through discovery; absent/bare retained main checkouts
fail with SHARED_WORKSPACE_UNAVAILABLE. No input can choose a storage root. Revalidate identity and reject symlink
or nonregular paths before effects. This is same-user POSIX storage; network filesystems and Windows are excluded.

Initialization checks every registered worktree for tracked or visible foreign content before adding only
/.devkit/.shared/ to clone-local info/exclude under the common exclusion lock. Conflicts raise
SHARED_EXCLUSION_CONFLICT without hiding files. Applicable ancestor ignore negations are refused before
infrastructure writes; case-folded paths, recursive globs and bracket expressions are conservatively matched.
Safe policies can therefore require inspection before use. Reads never install exclusions. Narrow exclusions remain after
expiry. Created artifact files/locks have mode 0600 and storage directories 0700. The service shares local OS
permissions; worktree identity does not authenticate other processes.

One stable namespace lock admits read-only shared readers and exclusive writers. Existing stores missing their
lock fail closed. Publication writes and fsyncs one canonical JSON-frontmatter Markdown envelope in a same-directory
temporary file and atomically renames it. Readers validate digest, byte count and metadata; corruption raises
SHARED_ARTIFACT_INVALID. Discovery, lock waits and IO checkpoints share a ten-second operation deadline
(SHARED_TIMEOUT). Denied access raises SHARED_ACCESS_DENIED without switching root or transport.

## Operations and configuration

CLI commands are devkit shared put|get|list|sweep. Put reads stdin; --format json emits one object. Equivalent MCP
tools are shared_put, shared_get, shared_list, shared_sweep (plan only) and shared_sweep_apply. Fixed bounded-write
classification applies only to put/apply-sweep; cloud excludes and refuses these tools. Local writes elicit no
business approval form. `CAP-MCP-runtime-registration` owns transport execution guards.

List requires kind/slug with optional source_sha/language, limit 1..100 and an opaque continuation cursor. Sweep
examines at most 100 entries in deterministic filename order, returns a continuation cursor, and retains/reports
invalid files. Only explicit apply removes valid expired artifacts. Check/read/list and default sweep never clean
storage. Scope records, tokens and journals are outside this store and remain unchanged. Logical expiry does not
guarantee physical erasure after seven days.

[shared] adapter defaults to local in effective configuration; checkout-local overlays are validated and
DEVKIT_SHARED_ADAPTER overrides only the adapter key. CLI uses its explicit workspace; MCP uses the owning
configuration workspace. Adapter ID and namespace accompany results. Local-orchestrated callers verify connected
project tools before dependent operations; absent tools require a user connection-repair request and stop the
operation without automatic CLI fallback. An explicit separately authorized CLI choice can override the preference,
but permission refusal cannot authorize rerouting. Compare adapter/namespace across linked callers.

## Public extensions

Installed devkit_dist.features.shared.adapters entry points name factories accepting RepositoryContext and returning
SharedArtifactAdapter. Built-in local is reserved. Duplicate, unknown, unloadable or malformed adapters fail with
SHARED_ADAPTER_UNAVAILABLE, without fallback. Backend advisory codes are preserved and continuation tokens
are opaque to the adapter boundary. Public input/result types and the reusable assert_conformance helper
cover immutable generations, live retry, exact expiry, pagination, cleanup and error mapping. Adapter authors own
remote namespace provisioning, authentication and transaction consistency. Protocol checks and the test adapter
provide no production cross-host evidence. No concrete remote backend is shipped; the retained follow-up is
`FB-remote-shared-adapter-follow-up`.
