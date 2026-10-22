---
id: PLAN-retained-runtime-receipt
spec: SPEC-retained-runtime-receipt
---

# Technical Plan: `SPEC-retained-runtime-receipt` Diagnose a retained MCP runtime older than the code it reads

## 1. Constitution & Invariant Review

None. Both diagnoses only refuse, earlier and with a dedicated code, what already fails. Receipt validation, the
receipt schema (`CAP-DIST-sync-and-transactions`), runtime selection and execution guards
(`CAP-MCP-runtime-registration`) and integration authority (`CAP-INT-mcp-services`) are unchanged, so no ADR is
needed. The layering rules hold: the MCP adapter calls new `BaseUseCase` objects of its own feature, and the
integration service calls a new repository function; `devkit-dist` gains one constant and imports nothing new.

## 2. Architecture Overview & Impact

- `devkit-dist` (`features/project/repositories/receipt.py`): `READER_MODULES`, the module names whose code decides
  what the reader accepts: the module itself (accepted keys and types) and `models/receipt.py` (`SCHEMA` and record
  types), derived from `__name__` and `Receipt.__module__` so a rename keeps it correct.
- `devkit-agt` integration:
  - `models/errors.py`: `ReceiptReaderChangedError` (`INTEGRATION_RECEIPT_READER_CHANGED`, guardrail).
  - `repositories/receipts.py`: `check_reader(root, source_sha, target_sha)` raises it when the source's committed
    receipt is refused, the target's committed receipt parses, and `git diff --name-only --no-renames
    merge-base(target, source) source` names a path at a reader module path (the module name as a path ending in
    `.py`, matched at a path-component boundary). Every other combination returns, leaving the existing outcome.
  - `services/providers.py`: `check(provider, context)` calls `check_reader` with the context's base, source and
    target before running the provider, so local prepare, pull-request prepare and every build share it, through
    the MCP service and the CLI.
- `devkit-mcp` runtime:
  - `models/errors.py`: `RuntimeStaleError` (`MCP_RUNTIME_STALE`, guardrail, a `HostError`).
  - `services/loaded_code.py`: `record()` hashes every `*.py` file under the import locations of the top-level
    `devkit` namespace and every `devkit_*` package on `sys.path` (`pkgutil.iter_modules`, `importlib.util.find_spec`),
    keyed by real path; `stale(baseline)` lists the loaded `devkit`/`devkit_*` modules whose `.py` file is absent,
    unreadable, unrecorded or differs.
  - `usecases/loaded_code.py`: `RecordLoadedCode` (returns the baseline) and `GuardLoadedCode(baseline)` (raises
    `RuntimeStaleError` with the stale module names as details).
  - `mcp/server.py`: `build_server` records the baseline when the server is built (at `devkit mcp serve` start) and
    runs the guard before every non-`read_only` tool, ahead of `guard_execution()` and the tool.

## 3. Component & Interface Design

```python
# devkit_dist.features.project.repositories.receipt
READER_MODULES: tuple[str, ...]  # ("devkit_dist.features.project.repositories.receipt", "devkit_dist.features.project.models.receipt")

# devkit_agt.features.integration.repositories.receipts
def check_reader(root: Path, source_sha: str, target_sha: str) -> None: ...  # raises ReceiptReaderChangedError

# devkit_mcp.features.runtime.usecases.loaded_code
class RecordLoadedCode(BaseUseCase):
    def execute(self) -> Mapping[str, str]: ...  # real path -> SHA-256
class GuardLoadedCode(BaseUseCase):
    def __init__(self, baseline: Mapping[str, str]) -> None: ...
    def execute(self) -> None: ...  # raises RuntimeStaleError
```

| Code | Mode | `[ACTION]` |
| --- | --- | --- |
| `INTEGRATION_RECEIPT_READER_CHANGED` | BLOCKED | A runtime built from the target cannot read this source's receipt and restarting the MCP service does not help; obtain separately granted `dev-integration` authority for the CLI route, then run `devkit worktree finish <branch> --merge --local-only` in the base checkout with a devkit runtime built from the source's code |
| `MCP_RUNTIME_STALE` | BLOCKED | Restart or reconnect the retained devkit MCP service so it loads the installed code, then call the tool again; nothing ran, and a request retained by the old process must be prepared again after inspecting Git |

## 4. Error Handling & Edge Cases

- A source without a committed receipt, a target receipt that is absent or refused, a parsing source receipt or a
  range that does not touch a reader module path: no diagnosis; the existing outcome stands (`RECEIPT_INVALID` from
  the provider for a corrupted receipt).
- A cleanup-only request (the target contains the source) has an empty range and is never diagnosed.
- A module loaded after start from a file changed since start runs a mixed code generation and is reported stale.
- `read_only` tools skip the guard, keeping retained read-only diagnostics available. The guard runs once at the
  start of a call; a merge the same call lands does not refuse that call, and the next protected call is refused.
- The guard never re-imports, restarts or selects a runtime and grants no authority.

## 5. Verification & Test Plan

- Reproduction (kept as regression tests):
  - `packages/devkit/tests/integration/features/integration/test_receipt_reader.py`: the fixture provider reads the
    source receipt with `load_receipt`, as `devkit-spec` does; prepare with a reader-changing source currently
    raises `RECEIPT_INVALID` and must raise `INTEGRATION_RECEIPT_READER_CHANGED` without calling the provider
    (AC-01); the same source without a reader change keeps `RECEIPT_INVALID` (AC-02); a direct `providers.check` on
    the pull-request context shares the diagnosis.
  - `packages/devkit-mcp/tests/integration/features/runtime/test_loaded_code.py`: a `devkit_*` fixture package on
    `sys.path`, imported before `build_server`; after its file changes, a protected tool currently runs and must
    return `MCP_RUNTIME_STALE` without running (AC-04); a `read_only` tool and a change to an unimported file are
    not refused (AC-05).
- Preservation: `packages/devkit-dist/tests/integration/features/project/test_receipt.py` (AC-03), the integration,
  MCP runtime and shared transport suites, through `just test-affected`.
- Checks: `just lint` and `just check` for `dist`, `agt` and `mcp`; `uv run devkit rules check`; `git diff --check`.
