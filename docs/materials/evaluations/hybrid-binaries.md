# Hybrid Architecture & Native Binary Distribution Evaluation

**Status**: Not adopted. Evaluation record (2026-10-11), updated 2026-10-13  
**Decision**: `devkit` stays pure Python. Semantic search, the main candidate, landed without native code: [`devkit.search`](../../search/overview.md) embeds with a static Model2Vec model through numpy and tokenizers (prebuilt wheels) and ships the model as a data-only wheel, at about 20 ms more than a Go engine per search. The other triggers in [section 6](#6-adoption-criteria-and-recommended-roadmap) still apply to the sync engine and the rule scanner  
**Target Modules**: `devkit.distribution` (playbook search, sync engine), `devkit.rules` (workspace scanner)  
**Related Documents**: `ARCH-08-2-resource-taxonomy`, [Distribution Overview](../../distribution/overview.md)

## 1. Objectives

The evaluation asks whether to bundle precompiled native binaries (Go or Rust executables) inside the Python wheels that `uv` installs. The baseline is pure Python: standard-library BM25 search, POSIX file transactions, and three pure-Python runtime dependencies (`click`, `pyyaml`, `tomlkit`), shipped as one universal wheel. Candidate areas for native acceleration:

1. **Hybrid playbook search**: lexical BM25 combined with lightweight semantic embeddings (for example quantized Word2Vec in Go), without Python ML dependencies (`torch`, `sentence-transformers`, `faiss`).
2. **Workspace traversal and hashing**: parallel directory diffing and digest computation during large `devkit sync` runs.
3. **Rule evaluation throughput**: Markdown link analysis and file scanning in `devkit.rules`.

## 2. Packaging Feasibility with `uv`

Wheels (PEP 427) may contain executables, as `ruff`, `uv`, `ninja` and `cmake` do. `uv` extracts them intact on `uv add`, `uv sync` or `uv tool install`; execute permissions survive when the build backend sets them; a Python wrapper finds the binary with `importlib.resources` or it is registered as an entry point.

| Model | Mechanics | Trade-off |
| --- | --- | --- |
| A: multi-platform universal wheel (`py3-none-any`) | Go cross-compiles `linux-amd64`, `linux-arm64` and `darwin-arm64` binaries into `src/<package>/bin/`; a wrapper picks one from `platform.system()` and `platform.machine()` | One artifact for every developer platform, at 10–20 MB per architecture; suited to internal use |
| B: platform-tagged wheels (`manylinux`, `macosx`) | A CI matrix builds one wheel per platform with only its binary | Minimal download and PyPI conventions, at higher CI and release complexity; standard for public distribution |

## 3. Runtime Integration Patterns

1. **Subprocess with JSON over stdio (recommended)**: the Python CLI runs the binary with `subprocess.run`, passing input as arguments or stdin and parsing JSON from stdout. The Go runtime stays out of Python's process (GIL, allocator, signal handlers), no CGo toolchain or shared-library path issues arise, and startup of a small static binary costs about 1–3 ms.
2. **Persistent local daemon**: when embeddings or large indexes must stay warm in memory, the engine runs as a daemon on a Unix domain socket (`.devkit/transient/search.sock`) that `devkit playbook search` starts on demand.

## 4. Candidate Subsystems

- **Playbook search**: today pure-Python BM25 in [playbook_search.py](../../../packages/devkit/src/devkit/distribution/installation/playbook_search.py), a lexical index rebuilt from receipt-owned entry files on every invocation, with no semantic expansion (alternate vocabulary needs frontmatter `aliases`). A Go engine with BM25 and compact embeddings would bridge vocabulary mismatch without heavy Python dependencies, invoked transparently by `devkit playbook search`.
- **Sync engine**: today Python atomic writes, the project lock (`.devkit/transient/lock`), the write-ahead journal (`.devkit/transient/sync-journal.json`) and SHA-256 hashing. Parallel crawling (`filepath.WalkDir` with worker goroutines) and BLAKE3 hashing would speed sync planning in repositories with tens of thousands of files.

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

## 6. Adoption Criteria and Recommended Roadmap

`devkit` stays on the pure-Python implementation until at least one trigger occurs:

1. **Semantic search necessity**: agents frequently miss playbooks through lexical mismatch, and frontmatter `aliases` impose prohibitive authoring overhead.
2. **Catalog scale**: synchronized playbooks, rules and instructions exceed several thousand entries, pushing startup and indexing latency above 100 ms.
3. **Sync bottleneck**: full-tree workspace diffing during `devkit sync` takes longer than 200 ms.

Possible adoption path (not scheduled; only phase A exists):

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
