---
id: FB-strict-frontmatter-loader-without-libyaml
title: Strict frontmatter loader parses YAML in pure Python
scope: repo
kind: suggestion
category: other
target: packages/devkit-core/src/devkit_core/core/frontmatter.py
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-strict-frontmatter-loader-without-libyaml] Strict frontmatter loader parses YAML in pure Python

Performance: the shared frontmatter loader ignores libyaml even when PyYAML has it.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `load_header` loads every frontmatter header with `_StrictLoader`, a subclass of the
  pure-Python `yaml.SafeLoader` that rejects duplicate keys. Every document index load, every rule run and every
  other frontmatter read pays the pure-Python scanner and parser.
- **Proposed Procedure**: build the strict loader on `yaml.CSafeLoader` when PyYAML has libyaml, with the same
  duplicate-key check, and keep `SafeLoader` as the fallback. Confirm that errors (impossible dates, nesting depth,
  duplicate keys) keep their messages and `FrontmatterError` mapping.
- **Expected Benefit**: the 640 headers of this repository load in about 15 ms instead of about 128 ms, with equal
  results; fresh `DocumentIndex` builds and rule runs get faster even without `SPEC-document-index-cache`'s memo.
- **Cost & Risk**: libyaml error messages and marks differ from the pure-Python ones; a test asserting message text
  or recursion behavior can change. The `SPEC-document-index-cache` fingerprint covers `frontmatter.py`, so a changed
  loader invalidates its memo automatically.
- **Attempted**: measured in this session with a `CSafeLoader` subclass carrying the same duplicate-key check;
  not implemented.

## Evidence

```text
cProfile of devkit spec resolve: frontmatter.load_header 0.40 s of 1.07 s (pure-Python yaml composer/scanner).
headers=640 pure=128ms libyaml=15ms equal=True   (yaml.__with_libyaml__ True, PyYAML 6.0.3)
```

- **Disposition**: `SPEC-frontmatter-libyaml`: guarded libyaml parsing preserves strict errors and deep-input
  fallback; 116 frontmatter tests passed, independent review and 2,960 differential probes passed, and 682 headers
  produced equal values with a 3.55x median parsing speedup. Python-only import, lint, type checks and wheel build
  verified.
