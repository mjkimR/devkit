# [RULE-advisory-unique-code] Advisory Code Uniqueness

## 1. Overview

Agents and `except` clauses branch on advisory codes, so a code names one condition. The rule refuses two unrelated
`AdvisoryError` classes that declare the same code.

- **Phase and severity**: `linter`, `error`; it runs in `devkit rules check` and the commit gate. Shipped by the
  `advisory` bundle's `python` preset (`devkit add advisory:python`).
- **What is checked**: every Python file of the workspace outside `exclude`, read statically and never imported.
  An *advisory class* derives, directly or through workspace classes, from a name in `bases`. Its code declarations
  are `code = "X"` (or `code: str = "X"`) in its body and `code="X"` keywords at calls of the class or of one of its
  classmethods (`MyError.blocked(..., code="X")`). A value is a string literal or a name bound to a module-level
  string literal.
- **Imports are resolved**, not matched by name: aliases (`import a.b as m`, `from x import Y as Z`), relative imports
  and re-exports through a package `__init__.py`. A module's name comes from its path below the last `src` directory,
  or from the workspace root; when two files give the same module name, the first path in sorted order is used.
- **Not checked**: codes defined in installed packages outside the workspace, codes passed to `super().__init__` or
  `cls(...)`, computed codes, and test files (default `exclude`).

## 2. Cause of Violation

For each code, the classes declaring it (its owners) must lie on one inheritance line: one owner is an ancestor of
every other. A subclass that redeclares its base's code is accepted. Otherwise every declaration of an owner that
derives from no other owner is reported, naming the others:

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
bases = ["devkit.advisory.AdvisoryError", "devkit.advisory.error.AdvisoryError", "devkit.core.DevkitCoreError"]
```

Patterns are workspace-relative; a standalone `**` matches zero or more path segments.

## 5. Exceptions

There is no per-code exception: two conditions sharing a code is the defect itself. Leave generated or vendored
sources out with `exclude`, with the reason in a comment directly above the setting.
