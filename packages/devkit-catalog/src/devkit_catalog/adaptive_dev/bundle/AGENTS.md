# Adaptive Development

Develop the agreed product through the next useful discovery, research, implementation or verification action.
Adaptive development can remain the project's approach; product size or elapsed time never forces graduation.

- Read this context once per agent context; use `/adaptive-dev` for iterative product work and resume.
- Before product work, require the effective `configuration.development.approach` from `uv run devkit config show` to be `adaptive-dev`; if inspection fails or the approach is SDD, stop product work and report the shared configuration action.
- Selecting this bundle changes assets only; never implicitly switch approach, remove SDD assets or reopen existing SDD history.
- Before document authoring, read `uv run devkit get-context docs` and the relevant writing instructions.
- Keep independent build, lint, test and actual-usage checks; report skipped or unavailable evidence as unverified.
- Only the coordinator writes current facts to project-owned `.devkit/adaptive-dev.md`, when useful and before pausing or handing off; optional roles return evidence and never commit.
- Make implementation choices inside the agreed goal autonomously; return changes to that goal or its constraints to the user.
- Use the project's ordinary Git and host permissions; adaptive development requires no per-change SDD Unit, approval, envelope or immutable experiment history.
