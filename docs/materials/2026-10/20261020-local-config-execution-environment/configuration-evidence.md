# Configuration Planning evidence

Repository baseline: `ffd6e2bbc684c71bb363a3c658f8f2303678eaae`.

| Evidence | Design consequence |
| --- | --- |
| `packages/devkit-dist/src/devkit/core/project.py:183` reads shared TOML without table validation | Preserve shared read for governance; introduce a distinct effective accessor |
| `packages/devkit-dist/src/devkit/distribution/installation/config.py` owns closed fields, bundle variables, selection writes and template updates | Extend distribution validation, leave shared selection destinations explicit |
| `packages/devkit/src/devkit/{rules/engine/config.py,workflow/project/config.py,gate/engine/config.py,worktree/config.py,integration/providers.py}` and `packages/devkit-spec/src/devkit_spec/config.py` use shared core reads | Do not switch these policy consumers to local overrides |
| `packages/devkit-dist/src/devkit/distribution/installation/{sync.py,status.py,context.py,reading.py}` consume selected inventory and receipt | Route distribution runtime reads through validated local-render evidence |
| `packages/devkit-dist/src/devkit/core/receipt.py` loads canonical receipt, shared with engines | Preserve canonical loader for executable asset discovery |
| `packages/devkit/src/devkit/rules/engine/{project.py,discovery.py}` pins snapshot config and managed rules to snapshot receipt | Prohibit local rule/workflow/gate alterations; exercise existing optimized and materialized snapshot paths |
| `packages/devkit/src/devkit/worktree/lifecycle.py` starts setup then locked sync without local-file propagation | Copy local config before these subprocesses; existing nested-start refusal defines source ownership |
| response-style bundle declares language string and uses it in skill template; guidance pointer has no language interpolation | Local language can change ignored skill bytes while shared guidance remains identical |
| `CAP-DIST-sync-and-transactions` requires committed receipt equality for locked sync | Plan canonical inventory first and do not record local hashes in shared receipt |
| `CAP-DIST-workspace-ownership` seeds ignore file once | A narrowly managed local-config ignore entry needs an explicit contract update |

No live environment was mutated and no product code was changed. The design is supported by repository reads;
Development must test the proposed accessors, ledger and subprocess behavior. No external product claim is required.
