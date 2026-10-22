---
id: SPEC-advisory-unique-code
title: Advisory code uniqueness rule
summary: A Python rule in the advisory bundle that refuses two unrelated AdvisoryError classes declaring the same code, or a constructor code that a class already owns.
status: completed
created: 2026-10-19
related_capabilities:
  - CAP-ADV-agent-advisory-protocol
  - CAP-GOV-rule-authoring
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-advisory-unique-code] Advisory code uniqueness rule

## 1. Problem Statement & Motivation

`CAP-ADV-agent-advisory-protocol` makes codes the contract an agent branches on (principle 4, checklist item
"Headline"), but nothing checks that a code names one condition. Every repository that extends `AdvisoryError`
(devkit, devkit-spec, and any consumer of `devkit-advisory`) can declare the same code on two unrelated classes, and an
agent or an `except` clause then cannot tell them apart.

A check inside devkit's own test suite reaches devkit only. The check belongs where every Python consumer gets it: a
deterministic rule shipped by the `advisory` bundle's `python` preset, which `devkit rules check` and the commit gate run
in any project that selects it. The runtime distribution `devkit-advisory` stays unchanged: the bundle is built into
`devkit-agt` (`devkit.advisory_guide`), so a runtime environment never carries the rule.

## 2. User Stories

- **US-1**: As an agent or developer adding an `AdvisoryError` subclass, I want `devkit rules check` to refuse a code
  another unrelated class already declares, so that each code keeps one meaning.
- **US-2**: As a maintainer of a repository that consumes `devkit-advisory`, I want the same check by selecting
  `advisory:python`, without devkit's test suite.

## 3. Non-Goals

1. **Scope Excluded**: codes declared in installed packages outside the workspace (a consumer subclassing a devkit class
   does not see devkit's own codes).
   - **Rationale**: the rule reads workspace files statically; importing installed or project code would run it.
   - **When to Reconsider**: a consumer reports a collision with an upstream code that this rule could not see.
2. **Scope Excluded**: codes that are not literal: computed expressions, `code=` passed to `super().__init__` or to
   `cls(...)`, and codes set after construction.
3. **Scope Excluded**: advisory implementations in other languages; the `core` preset stays language-agnostic.
4. **Scope Excluded**: an autofix, and any change to existing codes in this repository.

## 4. Acceptance Criteria & Behavioral Contracts

An *advisory class* is a class defined in a checked workspace file that derives, directly or through workspace classes,
from a configured base (`bases`, default `devkit.advisory.AdvisoryError` and `devkit.advisory.error.AdvisoryError`). A
*code declaration* is either a class-body `code = "X"` / `code: str = "X"` on an advisory class (owned by that class) or
a `code="X"` keyword on a call to an advisory class or one of its classmethods (owned by the called class). The value
may be a string literal or a name bound to a module-level string literal, plain or annotated. Names resolve through
the module's imports, and inside a function through that function's own imports first. An owner *covers* an owner
derived from it, except that an owner declaring the code only at calls never covers one declaring it in its class
body. A code *collides* when more than one of its owners is covered by no other owner.

### [AC-01] Unrelated classes declaring one code are reported
- **Given** `a.py` defines `class A(AdvisoryError): code = "DUP"` and `b.py` defines `class B(AdvisoryError): code = "DUP"`
- **When** `RULE-advisory-unique-code` runs over the workspace
- **Then** it returns exactly two violations, one per declaration line, each message naming the code and the other
  owner's qualified name and location, with severity `error` in phase `linter`

### [AC-02] A subclass redeclaring its base's code is accepted
- **Given** `core.py` defines `class LockHeld(AdvisoryError): code = "LOCK_HELD"` and `dist.py` imports it as
  `CoreLockHeld` and defines `class LockHeld(Base, CoreLockHeld): code = "LOCK_HELD"`
- **When** the rule runs
- **Then** it returns no violation

### [AC-03] A constructor code owned by an unrelated class is reported
- **Given** `class A(AdvisoryError): code = "OWNED"` and, in another module, `raise B("msg", code="OWNED")` where `B`
  does not derive from `A`
- **When** the rule runs
- **Then** it returns a violation at the call's line naming `A` and a violation at `A`'s declaration naming `B`

### [AC-04] Constructor codes on one inheritance line are accepted
- **Given** `class Refused(AdvisoryError): code = "REFUSED"`, a call `Refused("m", code="REFUSED_X")`, a call
  `Refused.blocked("m", code="REFUSED_X")` in another module and a subclass of `Refused` declaring `code = "REFUSED"`
- **When** the rule runs
- **Then** it returns no violation

### [AC-05] Imports resolve to the defining module
- **Given** two unrelated classes both named `ConfigError` in different modules with different codes, a class deriving
  from one of them through `import pkg.mod as m` / `m.ConfigError`, a relative import (`from .errors import X`) and a
  re-export through a package `__init__.py`
- **When** the rule runs
- **Then** each subclass is attributed to the class its import names, and no violation is reported

### [AC-06] Bases outside the workspace are recognized; other classes are ignored
- **Given** a workspace without `devkit-advisory` sources whose `app.py` imports `AdvisoryError` from `devkit.advisory`
  and declares the same code on two unrelated subclasses, and whose `other.py` declares `code = "DUP"` on a class that
  derives from no configured base
- **When** the rule runs
- **Then** it reports the two subclasses and nothing in `other.py`

### [AC-07] Settings: excluded files and extra bases
- **Given** the default settings and a colliding declaration in `tests/test_x.py`, then `bases = ["lib.Base"]` with two
  unrelated subclasses of an external `lib.Base` declaring one code
- **When** the rule runs with each configuration
- **Then** the test file contributes no declaration (default `exclude`: `**/tests/**`, `**/test_*.py`, `**/*_test.py`,
  `**/conftest.py`), and the `lib.Base` subclasses are reported; an invalid `exclude` pattern is
  `RULES_SETTINGS_INVALID`

### [AC-08] Targets limit reporting, not analysis
- **Given** a collision between `a.py` and `b.py`
- **When** the rule runs with only `b.py` targeted
- **Then** it returns one violation, in `b.py`, naming the owner in `a.py`

### [AC-09] Unparseable files are skipped
- **Given** a `.py` file with a syntax error beside a valid collision
- **When** the rule runs
- **Then** the valid collision is reported and the run raises no error

### [AC-10] Shipped in the python preset and run in this repository
- **Given** the `advisory` bundle and this repository's `.devkit/config.toml`
- **When** `devkit sync` and `devkit rules check` run
- **Then** the rule asset belongs to the `python` preset only, this repository selects `advisory` at `python`, the
  rule is loaded, `devkit rules check` reports no `RULE-advisory-unique-code` violation, and
  `packages/devkit/tests/test_layering.py` passes with `advisory_guide` allowed to import `rules` only

### [AC-11] Lazy imports bind names in their function only
- **Given** `use.py` defines a class `ConfigError` and two functions that each import a different `ConfigError` and
  raise it with that class's own code, one of them from a nested function
- **When** the rule runs
- **Then** it returns no violation

### [AC-12] A code passed when raising a base does not cover its subclasses
- **Given** `class Base(AdvisoryError)`, subclasses `S1(Base)` and `S2(Base)` declaring `code = "DUP"`, and
  `raise Base("m", code="DUP")`; separately, `AdvisoryError.blocked("m", code="DUP")` on a base outside the workspace
  beside a subclass declaring `DUP`
- **When** the rule runs
- **Then** the first workspace reports three violations (both subclasses and the call), and the second reports two
  (the subclass and the factory call)

### [AC-13] Annotated module constants are codes
- **Given** `CODE: Final = "DUP"`, `class S1(AdvisoryError): code = CODE` and `class S2(AdvisoryError): code = "DUP"`
- **When** the rule runs
- **Then** it returns two violations

## 5. Assumptions

- Phase `linter`, severity `error`: a collision breaks the code contract, like other contract rules.
- Module names come from paths: below the last `src` directory segment when there is one, otherwise from the
  workspace root; `__init__.py` names its package. This covers `src` layouts and flat layouts.
- Each colliding root declaration is reported, and each owner reported names the other roots, so the agent sees every
  party without a second run.
- The import-based test drafted before this spec was never committed; the rule replaces it, so no test file is removed
  from the repository.
