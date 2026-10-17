# User Stories

A directory managing developer and agent-centric value journeys and concrete acceptance criteria.

---

## 1. Directory Structure & File Naming

Stories reside in subdirectories partitioned by journey area:

```text
stories/
├── README.md
├── <area-1>/
│   └── US-<slug>.md
└── <area-2>/
    └── US-<slug>.md
```

- File name is `US-<slug>.md` and frontmatter `id` matches the file stem without sequence numbers.
- Frontmatter `area` matches the parent directory name.
- First heading opens with the token `[US-<slug>]`.

## 2. Authoring Principles

1. **Actor Value Centric**: Describe stories from the perspective of actor value ("As an actor, I want to ..., so that ...").
2. **Acceptance Criteria**: Specify verifiable scenarios using Given-When-Then criteria.
3. **M:N Association with Capabilities**: Reference underpinning capabilities in the frontmatter `capabilities:` list using `CAP-<AREA>-<slug>` identifiers.
