---
id: FB-worker-scope-misses-link-repairs
title: Worker write scope misses documents whose links a file move breaks
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/payload.md (development-worker write scope)
skill: spec-delegate
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-worker-scope-misses-link-repairs] Worker write scope misses documents whose links a file move breaks

## 2. Suggestion / Change Request

- **Current Procedure**: The payload reference derives a development worker's write scope from the unit's
  directory, the tasks' `_Boundary:` paths and the Living Spec paths the reconcile targets. A unit that moves source
  files (here a package split moving `packages/devkit/src/devkit/distribution/` to `packages/devkit-dist/`) also
  breaks every relative Markdown link to a moved file. `RULE-markdown-link` in `--staged` mode targets the Markdown
  files whose links point at a deleted path, so the commit gate refuses the move until those links are repaired,
  including links in documents outside every derived scope (dated or evaluation materials).
- **Proposed Procedure**: When the Host builds the write scope of a unit that moves or deletes files, it runs the
  link check over the planned moves (or `rg` for the moved paths in Markdown links) and adds the documents that link
  to them as link-repair-only paths, or states that link repairs to such documents are an allowed extension.
- **Expected Benefit**: The worker can commit the move through the gate without choosing between a scope violation
  and a stopped run; the Host validates a range it predicted.
- **Cost & Risk**: One search per moved directory at payload time; a broad allowance could hide unrelated edits, so
  the allowance should be limited to link targets.
- **Attempted**: This run edited one link in `docs/materials/evaluations/hybrid-binaries.md`, outside the listed
  write scope, and reported it as a necessary extension.

## Diagnostic Details

- **Reproduction**: Move `packages/devkit/src/devkit/distribution/installation/playbook_search.py` in a worktree,
  stage the move, run `devkit rules check --staged`.
- **Expected / Actual**: Expected a write scope that already contains every document the move forces to change;
  actual: the one document with a link to the moved file was under `docs/materials/`, which the payload did not list.
- **Versions**: devkit-spec 0.1.0, devkit-agt 0.1.1 (workspace source at the spec handoff commit).
- **Conditions**: local-orchestrated development worker; write scope given by the Host without `docs/materials/`.
- **Workarounds Attempted**: Rewrote the single link path to the new location; reported it in the final report.
- **Related Assets**: `RULE-markdown-link` guide (snapshot targets), the `spec-delegate` payload reference, the
  development-worker role contract (one path outside the write scope rejects the whole result).

## Evidence

```text
rg '](...packages/devkit/src/devkit/(distribution|core|search|host)' over the worktree:
  docs/materials/evaluations/hybrid-binaries.md:32  [playbook_search.py](../../../packages/devkit/src/devkit/distribution/installation/playbook_search.py)
RULE-markdown-link guide: "in --staged and --ci runs the targets are the changed files plus every Markdown file
  whose links point at a path the diff deletes, so deleting a document fails the commit that breaks the links to it."
payload.md (development-worker): write scope = "the unit's directory, the tasks' _Boundary: paths, the Living Spec
  paths the reconcile targets"
```

- **Disposition**: Deferred as open feedback. `PROP-worker-range-validation` uses the Host-supplied scope;
  automatic scope derivation and link-repair ownership are outside its scope.
