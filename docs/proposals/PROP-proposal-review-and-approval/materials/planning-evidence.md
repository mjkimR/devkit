# Planning evidence

The assigned worktree was read at the status-transition commit `a4914c6`; the initial Host comparison point is
`0269cd9b103c5f3dc2633f8119528fc64890ed56`. This is a documentation-only Planning run, not an implementation proof.

| Evidence | Observation and implication |
| --- | --- |
| `packages/devkit-spec/src/devkit_spec/handoff_mcp.py`, `prepare`, `HandoffService._execute` | Accepted base, clean tree, source/policy snapshot, form validation and setup recovery already exist; reuse their domain guards. |
| `packages/devkit/src/devkit/integration/mcp.py` and `CAP-INT-mcp-services` | Native authority is request-scoped and integration owns readiness and cleanup; composing approval needs a typed internal seam, not another tool invocation with forged approval. |
| `CAP-VIEW-repository-viewer`, `ADR-read-only-local-server-over-git-refs` | Git-only reads exclude ignored reports. A restricted exact-artifact read is an intentional ADR exception, while all writes and approvals remain outside viewer. |
| `ADR-shared-language-preference-with-bounded-approval-content` | Owned static form text can be bilingual; source prose and host chrome are separate. An agent-authored report needs semantic review, not an invented translation service. |
| Host dependency snapshot | Shared storage is provisional: immutable Markdown, 1 MiB envelope, full source SHA, ko/en, UUID generations, fixed 7-day expiry and read-only get/list. No production remote backend is promised. |

No filesystem probe or live form was required for choosing the design. Protocol tests and real host rendering are
separate Development evidence. No source code or Living Spec was changed in Planning. Active spec discovery returned
only completed spec statuses in this checkout; concurrent work is governed by the Host handoff, not by stale branch discovery.
