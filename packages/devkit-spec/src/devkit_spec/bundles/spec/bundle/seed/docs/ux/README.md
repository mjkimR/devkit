# UX Documents

A directory managing what a person sees and operates: one document per screen, modal or panel, with its purpose,
content, states and interactions. A use case step cites the screen it happens on; each interaction names the step
it serves. Projects without a user interface leave this directory empty.

---

## 1. Directory Structure & File Naming

UX documents reside in subdirectories partitioned by area, like use cases.

```text
ux/
├── README.md
└── <area>/                    # e.g., account, checkout
    └── UX-<slug>.md
```

- File name is `UX-<slug>.md` and frontmatter `id` matches the file stem without sequence numbers.
- Frontmatter `area` must match the parent directory name; `element` is `screen`, `modal` or `panel`.
- Conventions are checked by `RULE-id-convention`; links to use case steps by `RULE-ux-links` and
  `RULE-ux-coverage`.

## 2. Authoring Principles

1. **One element per document**: the use case carries the task flow; the Interactions table's targets give the
   transitions.
2. **Text contract**: content is written as prose regions and a content tree, never as a character-cell layout; the
   wireframe medium stays the project's, linked from the optional Evidence section.
3. **Objects**: name objects by glossary terms; their representations and calls to action per role live in the
   steering file `docs/steering/ux-objects.md`, created with the first UX document.

---

## 3. Template & CLI Discovery
- **Authoring a New UX Document**: Copy and adapt `.devkit/managed/spec/templates/ux.md`, following the `ux-writing`
  instruction.
- **Listing Registered UX Documents**:
  ```bash
  devkit docs list ux
  devkit docs list ux --area <area>
  ```
