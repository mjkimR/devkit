# Planning evidence

Source baseline: ff28b456b5f6ec170fd58e8a95f9565b3c0bf308. This is source inspection, not implementation verification.

| Question | Source | Decision |
| --- | --- | --- |
| Field eligibility | packages/devkit-spec/src/devkit_spec/documents/parse.py:63 | Extend depends_on to unit anchors |
| Graph validation | packages/devkit-spec/src/devkit_spec/rules/document_reference.py:136 | Separate live unit graph; completed targets terminal |
| Historical rewrite | packages/devkit-spec/src/devkit_spec/rules/document_reference.py:274 | Preserve no automatic history rewrite |
| Handoff carry | packages/devkit-spec/src/devkit_spec/proposals/specs.py:134 | Carry direct depends_on, omit milestone |
| Mutation point | packages/devkit-spec/src/devkit_spec/proposals/handoff.py:385 | Validate projected replacement before writes |
| Direct relocation | packages/devkit-spec/src/devkit_spec/proposals/handoff.py:435 | Reuse exact PROP-to-SPEC rewrite, no lineage traversal |
| Critical priority | packages/devkit-spec/src/devkit_spec/bundle/skills/spec-next/references/next-work.md:10-24 | Preserve milestone exception, filter unit prerequisites first |

The explicit product correction chooses PROP-only milestone ownership and rejects persistent delivery lineage.
The separately simplified closure proposal was inspected read-only from commit
3d95572f1064b512e0d1dc0f67b22ca501fb82fc via git show. It uses collaborative direct-proposal confirmations
and focused code/Git inspection; this Planning assumes no completion API or persistent lineage from that draft.

Alternatives: milestone-only ordering retains the present single-unit grouping pressure; a new scheduling CLI or
lineage resolver adds mechanisms not required by direct ordering. Optional frontmatter with existing refs/rules
and decision guidance is the smallest supported extension. No runtime probes or temporary repositories were
needed; Development will exercise projected handoff and base-state cases with isolated Git fixtures.
