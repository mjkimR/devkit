# Adaptive Development

Develop the agreed product through the next useful discovery, research, implementation or verification action.
Adaptive development can remain the project's approach; product size or elapsed time never forces graduation.

- Read this context once per agent context; use `/adaptive-dev` for iterative product work and resume.
- Selecting this bundle changes assets only; never implicitly switch approach, remove SDD assets or reopen existing SDD history.
- Before document authoring, read `uv run devkit get-context docs` and the relevant writing instructions.
- Keep independent build, lint, test and actual-usage checks; report skipped or unavailable evidence as unverified.
- Only the Host writes current facts to project-owned `.devkit/adaptive-dev.md`, when useful and before pausing or handing off; product-support roles return evidence and never commit.
- Make implementation choices inside the agreed goal autonomously; return changes to that goal or its constraints to the user.
- Reusable swarm agents follow their caller's workflow and authority, including under SDD; selecting them grants no approach or host-setting change.
- Give swarm workers commit authority only through an explicit assignment; keep product-support roles' index and HEAD unchanged.
- Use the project's ordinary Git and host permissions; adaptive development requires no per-change SDD Unit, approval, envelope or immutable experiment history.

- The delegating agent SHOULD record assignments and verify returns with `uv run devkit adaptive assignment`; if a command cannot record, keep the manual procedure and report assignments as unrecorded.
