# Use Cases

A directory managing how developers and agents reach their goals through devkit: the main success scenario, its
extensions, postconditions and concrete acceptance criteria.

---

## 1. Directory Structure & File Naming

Use cases reside in subdirectories partitioned by goal area:

```text
usecases/
├── README.md
├── <area-1>/
│   └── UC-<slug>.md
└── <area-2>/
    └── UC-<slug>.md
```

- File name is `UC-<slug>.md` and frontmatter `id` matches the file stem without sequence numbers.
- Frontmatter `area` matches the parent directory name.
- First heading opens with the token `[UC-<slug>]`.

## 2. Authoring Principles

1. **One Actor, One Goal**: A use case follows one primary actor to one goal through a numbered main success scenario (`usecase-writing`).
2. **Extensions**: Every refusal, failure or alternative path branches from a step, names its stable code and states where the use case resumes or ends.
3. **Acceptance Criteria**: Specify verifiable scenarios using Given-When-Then criteria, each naming the flow or extension it covers.
4. **M:N Association with Capabilities**: Reference underpinning capabilities in the frontmatter `capabilities:` list using `CAP-<AREA>-<slug>` identifiers; capabilities list the use cases they serve in `usecases:`. Detailed contracts stay in the capability.
