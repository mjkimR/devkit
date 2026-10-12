# Hybrid Architecture & Native Binary Distribution Evaluation

**Status**: Deferred. Evaluation record (2026-10-11); the hybrid model is not adopted  
**Decision**: `devkit` stays pure Python until one of the triggers in [section 6](#6-adoption-criteria-and-recommended-roadmap) occurs  
**Target Modules**: `devkit.distribution` (playbook search, sync engine), `devkit.rules` (workspace scanner)  
**Related Documents**: [Resource Taxonomy](../resource-taxonomy.md), [Distribution Overview](../../distribution/overview.md)

---

## 1. Overview and Objectives

This document evaluates the feasibility, mechanics, and trade-offs of adopting a **hybrid runtime architecture** within the `devkit` monorepo. Specifically, it assesses bundling precompiled native binaries (such as standalone executables compiled from Go or Rust) alongside Python packages distributed and installed via `uv`.

The baseline `devkit` architecture is pure Python (standard library BM25 lexical search, POSIX file transactions, and three pure-Python runtime dependencies: `click`, `pyyaml` and `tomlkit`), so it needs no compiled dependencies, installs instantly, and ships as one universal wheel. However, as the repository scales and agent interaction patterns expand, certain subsystems may benefit significantly from compiled native acceleration.

### Target Evaluation Areas
1. **Hybrid Playbook & Asset Search Engine**: Combining lexical BM25 with lightweight semantic embeddings (e.g., Go-based Word2Vec or portion-based vector representation) without requiring heavy Python machine learning dependencies (such as PyTorch, Transformers, or full vector databases).
2. **High-Performance Workspace Traversal & Hashing**: Parallel directory diffing, BLAKE3/SHA-256 digest computation, and ACID journal rollbacks during large-scale `devkit sync` operations.
3. **High-Throughput Rule Evaluation**: Static Markdown link analysis, file scanning, and repository governance checks within `devkit.rules`.

---

## 2. Packaging and Distribution Feasibility with `uv`

### Python Wheel Standard Compliance (PEP 427)

Python Wheels are standard ZIP archives containing a package directory and a `.dist-info` metadata directory. Including precompiled executables within a wheel is fully supported by the packaging standard and widely practiced across the ecosystem (e.g., `ruff`, `uv`, `ninja`, `cmake`, and `tiktoken`).

Because `uv` adheres strictly to standard Python packaging specifications:
- Any binary bundled inside a wheel package is extracted intact into the virtual environment during `uv add`, `uv sync`, or `uv tool install`.
- Execution permissions (POSIX `0755` / `+x`) are preserved on unpack when configured in the build backend.
- Packaged binaries can be discovered and invoked via Python wrappers using `importlib.resources` or registered directly as command-line entry points.

### Distribution Models

Three packaging models were evaluated for compiled binaries:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Wheel Packaging Models                           │
├───────────────────────────────────┬─────────────────────────────────────────┤
│ Model A: Multi-Arch "Fat" Wheel   │ Model B: Platform-Specific Wheels       │
│ (py3-none-any.whl)                │ (manylinux_x86_64, macosx_arm64, etc.)  │
│                                   │                                         │
│ ├── src/devkit_pkg/               │ ├── src/devkit_pkg/                     │
│ │   ├── bin/                      │ │   ├── bin/                            │
│ │   │   ├── engine-linux-amd64    │ │   │   └── engine (single native binary)│
│ │   │   ├── engine-linux-arm64    │ └── pyproject.toml                      │
│ │   │   └── engine-darwin-arm64   │                                         │
│ └── pyproject.toml                │                                         │
└───────────────────────────────────┴─────────────────────────────────────────┘
```

#### Model A: Multi-Platform "Fat" Universal Wheel (`py3-none-any.whl`) — Recommended for Internal/Private Use
* **Mechanics**: Go's native cross-compilation (`GOOS=linux GOARCH=amd64 go build`, etc.) builds binaries for the primary developer targets (`linux-amd64`, `linux-arm64`, `darwin-arm64`). All compiled binaries are placed under `src/<package>/bin/` and bundled into a single universal wheel.
* **Advantages**:
  - One build artifact satisfies all supported developer platforms.
  - No complex platform-specific matrix required in internal wheel indexes.
  - Stripped and compressed Go binaries typically add only 10–20 MB per architecture.
* **Selection at Runtime**: A Python entry-point wrapper inspects `platform.system()` and `platform.machine()`, selecting and executing the appropriate local binary.

#### Model B: Platform-Tagged Wheels (`manylinux`, `macosx`, `win_amd64`) — Standard for Public Distribution
* **Mechanics**: CI matrix builds individual wheels per platform containing only the relevant native binary.
* **Advantages**:
  - Minimal download footprint per consumer machine.
  - Full alignment with public PyPI conventions.
* **Disadvantages**: Higher CI pipeline overhead and matrix release complexity.

---

## 3. Interoperability and Runtime Integration Patterns

### Pattern 1: Subprocess Execution with Structured JSON I/O (Recommended)

The Python CLI invokes the compiled binary as a child process via `subprocess.run` or `subprocess.Popen`, passing inputs via CLI arguments or `stdin` and parsing results via structured JSON stdout:

```python
import platform
import subprocess
from importlib.resources import files
from pathlib import Path

def resolve_engine_binary() -> Path:
    sys_name = platform.system().lower()     # "linux", "darwin"
    mach = platform.machine().lower()        # "x86_64", "arm64"
    arch = "amd64" if mach in ("x86_64", "amd64") else "arm64"
    
    bin_name = f"engine-{sys_name}-{arch}"
    bin_path = Path(str(files("devkit.distribution").joinpath(f"bin/{bin_name}")))
    if not bin_path.is_file():
        raise FileNotFoundError(f"Missing precompiled binary for {sys_name}-{arch}: {bin_path}")
    
    if not (bin_path.stat().st_mode & 0o111):
        bin_path.chmod(bin_path.stat().st_mode | 0o755)
    return bin_path

def execute_search(query: str, catalog_json: str) -> str:
    binary = resolve_engine_binary()
    result = subprocess.run(
        [str(binary), "--query", query],
        input=catalog_json,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout
```

* **Rationale**:
  - **Memory & Process Isolation**: Go runtime (garbage collector, M:N scheduler) operates in its own process without interfering with Python's GIL, memory allocator, or signal handlers.
  - **Zero CGo Complexity**: Avoids cross-compilation C-toolchain dependencies, shared library search path (`LD_LIBRARY_PATH` / `rpath`) issues, and dynamic linker crashes.
  - **Sub-Millisecond Overhead**: Local subprocess startup in Linux/macOS for small static Go binaries is typically under 1–3 ms, well within interactive CLI budgets.

### Pattern 2: Persistent Local Daemon / IPC (For In-Memory Embeddings)

If word embeddings (e.g., Word2Vec vectors) or large inverted indexes require warm retention in RAM to avoid per-invocation disk reads:
- The compiled Go engine can run as a background daemon communicating via a local Unix domain socket (`.devkit/transient/search.sock`).
- `devkit playbook search` checks socket availability, auto-starting the daemon if absent, and executes zero-latency queries.

---

## 4. Subsystem Analysis & Candidate Use Cases

### 1. Hybrid Playbook & Asset Search Engine

* **Current Implementation**:
  - Pure Python standard library BM25 in [playbook_search.py](../../../packages/devkit/src/devkit/distribution/installation/playbook_search.py).
  - Lexical-only index built from receipt-owned entry files on each invocation.
  - Strict limitation: No semantic vector expansion, requires explicit aliases in frontmatter for alternate search vocabulary.
* **Go Hybrid Evaluation**:
  - **Engine**: Go standalone binary utilizing pure Go BM25 and a compact, quantized Word2Vec/portion model (or lightweight word-centroid embeddings).
  - **Benefit**: High-speed hybrid lexical + semantic matching capable of bridging vocabulary mismatch without introducing multi-hundred-megabyte Python neural dependencies (`torch`, `sentence-transformers`, `faiss`).
  - **Delivery**: Binary bundled in `devkit` wheel; invoked transparently by `uv run devkit playbook search`.

### 2. Workspace File Traversal and Transactional Engine

* **Current Implementation**:
  - Python-based atomic writes, advisory project lock (`.devkit/transient/lock`), write-ahead journal (`.devkit/transient/sync-journal.json`), and SHA-256 calculation.
* **Go Hybrid Evaluation**:
  - Parallel directory crawling (`filepath.WalkDir` with worker goroutines) and SIMD-accelerated BLAKE3 hashing.
  - **Benefit**: Instant synchronization planning in repositories with tens of thousands of files.

---

## 5. Trade-off Matrix: Pure Python vs. Hybrid Go Engine

| Dimension | Pure Python Baseline | Hybrid Go / Binary Model |
| :--- | :--- | :--- |
| **External Dependencies** | Pure Python only (`click`, `pyyaml`, `tomlkit`) | Go toolchain required only at build time; zero runtime deps |
| **Installation Friction** | Native `uv add`, instant wheel unpack | Native `uv add`, instant wheel unpack (with ~15MB binary overhead) |
| **Cross-Platform Portability** | Universal (`py3-none-any`) | Requires build matrix for `linux-amd64`, `linux-arm64`, `darwin-arm64` |
| **Search Latency (10k docs)** | ~30–50 ms (lexical only) | ~1–3 ms (lexical + lightweight semantic) |
| **Semantic Matching** | None (requires manual aliases) | Viable via embedded word vectors or portion models |
| **CI / Release Complexity** | Minimal (standard `uv build`) | Requires Go compilation step in `justfile` / GitHub Actions |
| **Codebase Maintenance** | Single language (Python) | Multi-language (Python CLI + Go engine) |

---

## 6. Adoption Criteria and Recommended Roadmap

### When to Transition to the Hybrid Model

The repository should remain on the pure Python standard library implementation until one or more of the following triggers occur:
1. **Semantic Search Necessity**: Agent interactions frequently miss playbooks due to lexical mismatch, and frontmatter `aliases` impose prohibitive authoring overhead.
2. **Catalog Scale**: The total volume of synchronized playbooks, rules, and instructions exceeds several thousand entries, causing Python startup and indexing latency to exceed 100 ms.
3. **Large Monorepo Sync Bottleneck**: Full-tree workspace diffing during `devkit sync` takes longer than 200 ms.

### Possible Adoption Path (Not Scheduled)

Today only the baseline exists: pure Python BM25 in `devkit.distribution`. The later phases describe how adoption would proceed if a trigger occurs; none of them has started.

```text
Phase A: Baseline
  └── Pure Python BM25 in devkit.distribution; verified contracts and limits.

Phase B: Experimental Prototype
  ├── Standalone Go search engine in a new tools/ workspace member
  ├── Benchmarking lexical BM25 vs Go-portion/Word2Vec scoring
  └── CLI proof-of-concept wrapper using subprocess and stdio JSON

Phase C: Packaging & Wheel Pipeline Integration
  ├── Multi-arch compilation recipes in root justfile
  ├── Hatchling force-include configuration in packages/devkit/pyproject.toml
  └── Automated OS/architecture resolution next to devkit.distribution.installation.playbook_search

Phase D: Production Cutover & Optional Fallback
  └── Default to Go binary with graceful fallback to pure Python stdlib if binary execution is blocked.
```
