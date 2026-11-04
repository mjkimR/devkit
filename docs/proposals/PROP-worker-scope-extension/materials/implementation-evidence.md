# Worker extension implementation evidence

Inspected head: `7df81ddeb72fd7c052bfe6e2ce5db31d9278dd24` (Planning start).

## Implementation facts

| Concern | Evidence | Consequence |
| --- | --- | --- |
| Derived scope | `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inputs.py`, `derive_scope` | Returned task boundaries already add literal prefixes; derived scope is evidence, not payload authority. |
| Scope override | `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inspect.py`, `InspectWorkerUseCase.execute` | Explicit scope replaces derived entries, and exact/descendant matching is already supported. Preserve this contract. |
| Annotation loss | `packages/devkit-spec/src/devkit_spec/features/entrypoints/repositories/bundle.py`, `split_boundary` | Parenthesized notes are stripped. Expose notes additively without changing `TaskBoundary.values`. |
| Glob behavior | `inputs.py`, `prefix`; `entrypoints/services/derive.py`, `classify_boundary` | Globs are not an interoperable boundary syntax. Recommend literal directories. |
| Worker envelope | `packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py`, `envelope_worker_cmd`; `models/envelope.py`, `Envelope`; `services/envelope/{model,authoring}.py` | The generic workflow feature owns typed fields, CLI input and persistence; devkit-spec only consumes it. |
| Existing field shapes | `models/envelope.py`, `Envelope.to_dict`; `services/envelope/authoring.py`, `_data` | Checks and assumptions carry text, findings carry review issues. None is a suitable existing typed extension record. |
| Reviewer wording | `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/SKILL.md.jinja`; `subagents/code-reviewer.md` | Skill and role contract both need the admission rule. |
| Existing ownership | `ARCH-05-2-components` | Feature roots and source-mirroring test tiers supply adjacency for this repository without a new registry. |
| Existing ADR | `ADR-orchestration-workers`, committed-result and write-scope clauses | New PADR partially supersedes strict unlisted-path rejection, preserving all remaining authorities and checks. |

## Options compared

| Option | Benefit | Cost or failure |
| --- | --- | --- |
| Keep strict scope and respawn | Smallest implementation | Preserves the operator round trip that this proposal addresses. |
| Generic machine ownership registry | Computes adjacency | Adds project configuration and cross-feature semantics for a reviewer decision; unnecessary for the agreed outcome. |
| Recorded adjacent extension with semantic review (selected) | Removes routine stop, retains explicit evidence and protected classes | Review must judge project ownership and necessity; inspect claims only structural and recognizable-tree checks. |
| Allow any necessary repository path | Minimal policy | Makes unrelated feature/config changes self-authorized; outside the requested adjacent-path hypothesis. |

## Verification plan

Reuse `packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py` fixtures and the workflow
envelope fixtures under `packages/devkit/tests/integration/features/workflow/`. Add tests beside their owners;
use parser unit tests under `packages/devkit-spec/tests/unit/features/entrypoints/` and role/content tests under
`packages/devkit-spec/tests/integration/bundles/spec/`. No production code or tests changed in Planning.

Cloud parity means shipped worker/reviewer rules. No autohub checkout or live Hub invocation was inspected; no
claim depends on Hub running inspect. No before/after performance or operator-cost measurement is claimed.

## Challenger disposition

The medium Challenger at `28cfdcc08058d7664c81584a329a7429eb4a1e96` found one P2 lifecycle contradiction:
the PADR required the typed record at first source write, while the existing worker record is written once at
turn end. The proposal and PADR now require only the annotation/reason at first source commit. Review reads
that annotation; the final/emergency record mirrors it and Host/inspect subsequently check agreement.

The optional exact-marker-only alternative was considered. Retaining the inline reason lets the pre-final code
review evaluate necessity without an extra provisional journal or early worker envelope. A one-line reason
without parentheses keeps the existing note grammar unambiguous; parser tests cover comma/colon text and reject
unsupported parentheses. No anti-bypass baseline or sealed boundary snapshot is introduced.
