# Python Rule Runner Architecture & Migration Notes

## Background

Specrig implemented its governance rule engine in Go (`template/specrig/governance/rules`), but faced two challenges:
1. Consumer repositories requiring custom rules needed a full Go build toolchain.
2. Each rule individually performed filesystem walks, file reading, and frontmatter parsing without a unified cache.

## Design Decisions in devkit

### 1. In-Memory Unified Workspace Cache (`WorkspaceCache`)
- Caches raw bytes and utf-8 text.
- Caches YAML frontmatter parsing and body offsets.
- Caches markdown link extraction (`[text](target)`).
- Caches global document catalog index (`DocumentCatalog`) mapping document IDs (`CAP-*`, `US-*`, `SPEC-*`, etc.) and file stems.
- Invalidation on autofix ensures safe convergence without repetitive disk I/O.

### 2. Sequential Execution & Convergence Loop
```text
CLI / Caller
  → Initialize WorkspaceCache & RuleContext
  → Filter rules by Phase (LINTER vs HYGIENE)
  → Order rules (format rules run first)
  → Check rules (collect initial violations)
  → If fix requested:
      → Execute Autofixable.fix()
      → Invalidate modified files in WorkspaceCache
      → Re-evaluate active rules to verify convergence
      → Return diagnostics with fixed status flag
  → Serialize to text or JSON
```

### 3. Clean Decoupled Rules
- `RULE-spec-format`: Markdown YAML frontmatter validation and automatic generation.
- `RULE-id-convention`: Enforces ID format and matching file stem.
- `RULE-document-reference`: Validates uniqueness of IDs and existence of references.
- `RULE-markdown-link`: Validates relative link targets with automatic relocation repair.
- `RULE-file-length`: Hygiene phase line limit warnings.
