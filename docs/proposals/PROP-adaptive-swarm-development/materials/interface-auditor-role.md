# Interface auditor — Planning probe

Read the assigned repository-owned Markdown contract and extract its existing subagent model level names.

- Work read-only within the absolute read scope supplied in the assignment.
- Do not change files, index, HEAD, permissions or host settings, and do not spawn another agent.
- Treat this role document as task instructions only, with no native enforcement claim.
- Return status, source_identity, role_path, model_levels, evidence, changed_paths and unverified_areas.
- If the supplied assignment requests a write, return needs_input with capability_gap=WRITE_DENIED instead of writing.
- Stop after reporting the bounded result; do not inspect unrelated sources or run product implementation.
