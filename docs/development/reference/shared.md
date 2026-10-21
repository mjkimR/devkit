# Shared artifacts

Contract: `CAP-COLL-shared-artifacts`. API: `devkit_dist.features.shared` exports PutRequest, Artifact, ArtifactMetadata, Page,
SweepResult, RepositoryContext, SharedArtifactAdapter and adapter(workspace).

```sh
printf '# Review\n' | devkit shared put --kind proposal-review --slug example --source-sha <full-commit-sha> --language en --format json
devkit shared get <artifact-uri> --format json
devkit shared list --kind proposal-review --slug example --format json
devkit shared sweep --format json
devkit shared sweep --apply --format json
```

All commands accept --workspace-root. Never infer report approval from artifact presence; compare source_sha and
language before consuming the exact URI. Cloud CLI's local store cannot share across hosts.

## Adapter authoring

Declare `[project.entry-points."devkit_dist.features.shared.adapters"]` with `my-adapter = "my_package:factory"`.
The factory accepts the service-owned RepositoryContext and returns a SharedArtifactAdapter whose adapter_id
matches its entry-point name. Expose a nonempty authorized repository_namespace. Never use a caller's repository
name as credentials. Implement put/get/list/sweep with the domain's immutable, bounded, expiry and error semantics;
return public result types and raise public devkit_dist.features.shared.models.errors advisories. Do not fabricate local paths.

Run `devkit_dist.features.shared.services.conformance.assert_conformance(adapter, advance_clock)` on an empty isolated namespace with an
injected clock; advance_clock accepts timedelta. The helper writes, retries, paginates, expires and sweeps fixtures.
Add backend-specific concurrency, authentication, permissions, transport-loss and real cross-host integration tests.
Passing this semantic harness does not certify production authorization or consistency.

Configure `[shared] adapter = "my-adapter"` in shared or checkout-local configuration, or set
DEVKIT_SHARED_ADAPTER. Unknown/malformed registrations fail explicitly without local fallback.

## Advisory codes

| Code | Meaning | Action |
| --- | --- | --- |
| `SHARED_INPUT_INVALID` | Invalid field, URI, cursor or content size/encoding | Correct the request |
| `SHARED_WORKSPACE_UNAVAILABLE` | Retained main checkout identity unavailable | Restore the retained checkout |
| `SHARED_EXCLUSION_CONFLICT` | Tracked or visible foreign storage would be hidden | Inspect all worktrees; preserve foreign content |
| `SHARED_ADAPTER_UNAVAILABLE` | Unknown, duplicate or malformed adapter | Correct installation/configuration |
| `SHARED_ARTIFACT_INVALID` | Corrupt envelope, unsafe path or missing stable lock | Inspect storage; preserve invalid evidence |
| `SHARED_ARTIFACT_MISSING` | Exact generation absent | Regenerate the report |
| `SHARED_ARTIFACT_EXPIRED` | Seven-day lifetime elapsed | Publish a fresh generation |
| `SHARED_ACCESS_DENIED` | Local permission refusal | Inspect permissions without rerouting |
| `SHARED_TIMEOUT` | Shared ten-second deadline elapsed | Retry the same bounded operation |
