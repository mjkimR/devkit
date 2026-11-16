---
id: OPS-search-mode-and-model-routing
title: "Document search mode and model routing"
status: active
summary: "Routes a lexical-only devkit docs search result or a SEARCH_* model error, using an explicit --mode hybrid run as the discriminating evidence, to the owner of the search extra or model package, and names the mode=hybrid observation that confirms the normal state."
related_capabilities: [CAP-SRCH-document-search, CAP-DOCS-document-search]
---

# [OPS-search-mode-and-model-routing] Document search mode and model routing

`devkit docs search` printed `[SEARCH: ... mode=lexical ...]` when hybrid ranking was expected, or it failed with
a `SEARCH_*` code. The default `--mode auto` hides the cause. When the search extra is not importable or no package
registers the model, auto falls back to lexical ranking and raises nothing (`CAP-SRCH-document-search` §2). An
explicit `--mode hybrid` run of the same query in the same environment turns that silent fallback into the
error code that selects the owner.

## Routing

| Symptom or state | Discriminating evidence | Next useful owner |
| --- | --- | --- |
| Default run reports `mode=lexical` | The run passed `--mode auto` or no `--mode`. Rerun the query with `--mode hybrid` and route by that result (rows below). | `CAP-DOCS-document-search` §3 rule 5; `CAP-SRCH-document-search` §2 |
| Search extra not importable | The explicit `--mode hybrid` run fails with `SEARCH_EXTRA_MISSING` and exit `2`. | The [reference row](../development/reference/search.md#error-codes) for `SEARCH_EXTRA_MISSING` and the advisory's own `[FIX]`. Which requirement carries the extra: `CAP-SRCH-document-search` §4 Model packages, `CAP-DOCS-document-search` §3 rule 5. |
| No package registers the model | The explicit `--mode hybrid` run fails with `SEARCH_MODEL_NOT_FOUND` and exit `2`. | The reference row for `SEARCH_MODEL_NOT_FOUND` and the advisory's `[FIX]`; `CAP-SRCH-document-search` §4 Model packages |
| Model package broken | `SEARCH_MODEL_INVALID` in `auto`, `dense` or `hybrid` mode, `auto` included because auto never falls back on it; a `--mode lexical` run never loads the model and does not report it. The message names the model and the cause: missing or malformed files, an import failure, or two packages registering one name. | The reference row for `SEARCH_MODEL_INVALID` and the advisory's `[FIX]`; `CAP-SRCH-document-search` §4 Model packages, §5 (an editable install builds without the model files) |
| Lexical was requested | The command line carried `--mode lexical`. `mode=` names the ranking that ran, so this is no fallback. | `CAP-DOCS-document-search` §3 rule 5 |
| Explicit run succeeds while an earlier auto run was lexical | The explicit `--mode hybrid` run prints `mode=hybrid`. Auto loads the model through the same path as the explicit run, so the earlier run used another environment (for example another `uv` project or virtual environment). | `CAP-SRCH-document-search` §2 |

Read the actual advisory before acting. The install or reinstall step and its target requirement stay with the
advisory's `[FIX]` and the reference row, not this map.

## Normal-state observation

After the owner's action, the explicit run and the default run of the same query both report hybrid ranking on
their first line:

```text
[SEARCH: query=override mode=hybrid count=2]
```

`CAP-DOCS-document-search` §4.2 owns this line. `CAP-DOCS-document-search` §3 rule 5 makes `mode=` the ranking
that ran, never `auto`; `--format json` carries the same value as `"mode": "hybrid"` (§4.3). The observation is the
mode, not the hits: `count=0` with exit `0` is still a successful search (§4.5).

## Authority boundary

This entry routes evidence and owns no recovery. Mode semantics, auto fallback and model packaging belong to
`CAP-SRCH-document-search` §2, §4 and §5. Command options, the `[SEARCH: ...]` line, JSON keys and exit codes
belong to `CAP-DOCS-document-search` §3 rule 5 and §4. Codes, levels and conditions belong to the
[search reference error rows](../development/reference/search.md#error-codes). The install or reinstall action belongs
to each advisory's `[FIX]` text, which this entry does not repeat.

A lexical result alone cannot tell a missing extra from a missing model or an explicit `--mode lexical`. A
successful hybrid run says nothing about ranking quality or the `--min-similarity` floor.

## Maintenance and next action

Review the routing when `CAP-SRCH-document-search` §2 changes which errors auto falls back on, when a `SEARCH_*`
code is added or renamed, or when `CAP-DOCS-document-search` §4.2 changes the `[SEARCH: ...]` line. For a code no row
names, such as `YAML_BINDING_UNAVAILABLE` or `DOCS_GLOSSARY_INVALID`, read `CAP-DOCS-document-search` §4.5 and the
actual advisory. For `devkit playbook search`, which ranks with the same library, read
`CAP-DIST-context-and-playbooks`.
