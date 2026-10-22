# Use Cases

A directory managing how each actor reaches a goal through the system: the main success scenario, its extensions,
postconditions and concrete acceptance criteria.

---

## 1. Directory Structure & File Naming

Use cases reside in subdirectories partitioned by goal area. The area represents a categorizing shelf and does not need to match `capabilities/` areas.

```text
usecases/
├── README.md
├── <area-1>/                  # e.g., onboarding, checkout, operations
│   └── UC-<slug>.md
└── <area-2>/
    └── UC-<slug>.md
```

- File name is `UC-<slug>.md` and frontmatter `id` matches the file stem without sequence numbers.
- Frontmatter `area` must match the parent directory name. Only `README.md` resides directly under `usecases/`.
- Create a new area once 3 or more use cases cluster around the same goal area; before that, place use cases in the closest existing area. Moving a use case between areas only requires moving the file and updating `area`; the `id` remains unchanged.
- Conventions are checked by `RULE-id-convention`, and `devkit rules fix` aligns `id`, `area`, and H1 heading token to the path.

## 2. Authoring Principles

1. **One Actor, One Goal**: A use case follows one primary actor to one goal through a numbered main success scenario.
2. **Extensions**: Every refusal, failure or alternative path branches from a step, names its stable code and states where the use case resumes or ends.
3. **Acceptance Criteria**: Specify verifiable scenarios using `Given-When-Then` format, each naming the flow or extension it covers.
4. **M:N Association with Capabilities**: Reference underpinning capabilities in the frontmatter `capabilities:` list using `CAP-<AREA>-<slug>` identifiers; capabilities list the use cases they serve in `usecases:`. Detailed contracts stay in the capability.

---

## 3. Template & CLI Discovery
- **Authoring a New Use Case**: Copy and adapt `.devkit/managed/spec/templates/usecase.md`.
- **Listing Registered Use Cases**: Dynamically discover use cases via CLI frontmatter parsing grouped by area:
  ```bash
  devkit spec list usecase
  devkit spec list usecase --area <area>
  ```
