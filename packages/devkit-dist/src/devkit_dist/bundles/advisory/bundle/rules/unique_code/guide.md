# [RULE-advisory-unique-code] Advisory Code Uniqueness

## 1. Overview

Agents and `except` clauses branch on advisory codes, so a code names one condition. The rule refuses two unrelated
`AdvisoryError` classes that declare the same code: a code is declared by one advisory class and its subclasses.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `advisory` bundle's `python` preset (`devkit add advisory:python`).
- **What is checked**: every Python file of the workspace outside `exclude`, read statically and never imported.
  An *advisory class* derives, directly or through workspace classes, from a name in `bases` (imports and aliases
  are resolved, not matched by name). Its code declarations are `code = "X"` in its body and `code="X"` keywords at
  calls of the class or its classmethods (`MyError.blocked(..., code="X")`), with a string literal or a name bound to
  a module-level one (`CODE = "X"`).
- **Inputs**: the rule reads Python files only and declares `inputs` `**/*.py`, so a run with explicit targets
  and no Python file among them, such as `lint-clean` on a documentation-only unit, skips it.
- **Not checked**: codes defined in installed packages outside the workspace, codes passed to `super().__init__` or
  `cls(...)`, computed codes, and test files (default `exclude`).

## 2. Cause of Violation

For each code, the classes declaring it (its owners) must be one class and its subclasses; a subclass that redeclares
its base's code, or raises with it, is accepted. A code declared only at calls (`raise Base(..., code="X")`) does not
cover subclasses declaring it in their bodies. Every declaration of an owner that no other owner covers is reported:

`Code "<CODE>" is also declared by <module.Class> (<file>:<line>); a code names one condition`

A run with explicit targets (a commit) reports only declarations in the targeted files but always compares them with
the whole workspace.

## 3. Remediation

- The two classes report different conditions: give one a code of its own and update whatever branches on it.
- One condition is a refinement of the other: derive the class from the class that owns the code.
- A call passes another class's code (`OtherError(..., code="OWNED")`): raise the class that owns the code instead.

There is no autofix: which condition keeps the code is a contract decision. The `agent-advisory-python` instruction
describes how codes are declared.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `bases` | list of dotted names | `["devkit.advisory.AdvisoryError", "devkit.advisory.error.AdvisoryError"]` | Classes whose subclasses are advisory classes, resolved like imports. |
| `exclude` | list of patterns | `["**/tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py"]` | Files left out of the analysis. |

```toml
# An application base imported from an installed package also roots advisory classes.
[rules.settings.RULE-advisory-unique-code]
bases = ["devkit.advisory.AdvisoryError", "devkit.advisory.error.AdvisoryError", "devkit_core.core.DevkitCoreError"]
```

Set `bases` globally unless one part of the workspace has its own error hierarchy (path overrides apply per file).
`[rules] exclude` limits only what is reported: excluded files are still analyzed. Patterns are workspace-relative;
a standalone `**` matches zero or more path segments.

## 5. Exceptions

There is no per-code exception: two conditions sharing a code is the defect itself. Leave generated or vendored
sources out with `exclude`, with the reason in a comment directly above the setting.

Per-file syntax extraction can reuse disposable facts under `.devkit/transient/rules/facts/` when a safe transient
directory exists. Every check rebuilds discovery, settings and cross-file judgment. Working-tree checks/fixes may
warm the memo after successful evaluation; snapshots and dry runs only read it. Missing or malformed memos cause
re-extraction without different findings or advisories. `CAP-GOV-rule-authoring` defines the descriptor contract.
