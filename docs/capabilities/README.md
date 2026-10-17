# Capabilities

A directory managing the durable system capabilities (Living Spec) provided by devkit.

---

## 1. Directory Structure & File Naming

Capabilities are partitioned into subdirectories by functional area:

```text
capabilities/
├── README.md
├── distribution/
│   └── CAP-DIST-<slug>.md
├── governance/
│   └── CAP-GOV-<slug>.md
├── delivery/
│   └── CAP-DLV-<slug>.md
├── worktree/
│   └── CAP-WT-<slug>.md
├── gate/
│   └── CAP-GATE-<slug>.md
├── compact/
│   └── CAP-CMP-<slug>.md
├── search/
│   └── CAP-SRCH-<slug>.md
├── host/
│   └── CAP-HOST-<slug>.md
├── integration/
│   └── CAP-INT-<slug>.md
├── generated/
│   └── CAP-GEN-<slug>.md
└── advisory/
    └── CAP-ADV-<slug>.md
```

- File name is `CAP-<AREA>-<slug>.md` and frontmatter `id` matches the file stem without sequence numbers.
- Frontmatter `area` matches the parent directory name.
- First heading opens with the token `[CAP-<AREA>-<slug>]`.

## 2. Authoring Principles

1. **Durable Functional Specification**: Define permanent system capabilities and responsibilities, not transient tickets.
2. **M:N Association with Stories**: Reference associated user stories using `US-<slug>` identifiers in the frontmatter `stories:` list.
3. **Normative Force**: Express contracts explicitly using RFC 2119 keywords (`MUST`, `SHOULD`, `MAY`).
4. **Summary**: Provide a 1-2 sentence English summary in frontmatter (embedded by document search).

## 3. Module References

Capabilities define behavior and contracts. System structure belongs in `../architecture/`; CLI/API usage,
configuration tables, and executable examples live in [Module References](../development/reference/README.md).
