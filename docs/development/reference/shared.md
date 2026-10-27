# Shared artifacts

Contract: `CAP-COLL-shared-artifacts`. API: `devkit_dist.features.shared` exports PutRequest, Artifact, ArtifactMetadata, Page,
SweepResult, RepositoryContext, SharedArtifactAdapter and adapter(workspace).

```sh
printf '# Review\n' | uv run devkit shared put --kind proposal-review --slug example --source-sha <full-commit-sha> --language en
uv run devkit shared get <artifact-uri>
uv run devkit shared list --kind proposal-review --slug example
uv run devkit shared sweep
uv run devkit shared sweep --apply
```

All commands accept `-w/--workspace-root` and `--format text|json`.

## Output

```text
[SHARED_ARTIFACT: shared://<namespace>/<generation> kind=proposal-review slug=example source_sha=<sha> language=en expires_at=<UTC time>]
```

- `put` prints the sentinel of the published artifact; `list` one per live artifact; `get` the sentinel followed by
  the content exactly as written.
- `list` and `sweep` print `[NEXT_CURSOR: <cursor>]` when more entries remain; pass it to `--cursor`.
- `sweep` prints `[SHARED_EXPIRED: <uri> removed=yes|no]` per expired artifact and `[SHARED_INVALID: <name>]` per
  retained invalid file.
- A result with no entries prints `[OK: ...]`.
- JSON: `put` and `get` return `artifact_uri`, `metadata` (without the URI and namespace), `local_path` for the local
  adapter, `adapter` and `repository_namespace`; `get` adds `content`. `list` returns `entries` and `cursor`;
  `sweep` `entries`, `invalid`, `cursor` and `applied`.

All commands require a Git checkout root with a retained main checkout. Never infer report approval from artifact presence; compare source_sha and
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

| Code | Mode | Meaning |
| --- | --- | --- |
| `SHARED_INPUT_INVALID` | `INPUT_ERROR` | Invalid field, URI, cursor, limit or content size/encoding; `[TARGET]` names the flag (`--kind`, `--slug`, `--source-sha`, `--language`, `--cursor`, `--limit`, `ARTIFACT_URI` or `stdin`) |
| `SHARED_WORKSPACE_UNAVAILABLE` | `INPUT_ERROR` | Not a Git checkout root, or its retained main checkout is unavailable; `[TARGET]` `--workspace-root` |
| `SHARED_EXCLUSION_CONFLICT` | `BLOCKED` | Tracked or visible foreign storage would be hidden; nothing was hidden |
| `SHARED_ADAPTER_UNAVAILABLE` | `MAINTENANCE` | Unknown, duplicate or malformed adapter |
| `SHARED_ARTIFACT_INVALID` | `MAINTENANCE` | Corrupt envelope, unsafe path or missing stable lock; invalid evidence is preserved |
| `SHARED_ARTIFACT_MISSING` | `INTERACTION` | Exact generation absent; the report must be published again |
| `SHARED_ARTIFACT_EXPIRED` | `INTERACTION` | Seven-day lifetime elapsed; the report must be published again |
| `SHARED_ACCESS_DENIED` | `INTERACTION` | Local permission refusal; never reroute to another transport or root |
| `SHARED_TIMEOUT` | `DEFER` | Shared ten-second deadline elapsed; retry the same bounded operation later |
