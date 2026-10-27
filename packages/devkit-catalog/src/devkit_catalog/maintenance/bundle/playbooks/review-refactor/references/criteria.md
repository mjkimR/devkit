# Review criteria and evidence

Read at the review step of a batch and again when you record a change's evidence. Every question needs a location
and a named maintenance cost before it becomes a finding; reviewers, you included, over-report, and acting on every
gap adds abstraction and defensive code.

## 1. Review questions

### Code

- Duplicated behavior: do two or more places implement the same behavior, so a change to one must be repeated in the
  others? Count behavior, not lines that look alike; deliberate parallel structure (test arrangements, command
  boilerplate) is not duplication.
- Repeated technical helpers: is the same small technical operation (path handling, parsing, formatting) written in
  several modules instead of one utility?
- Unnecessary abstraction: does a helper, base class, protocol, factory or configuration option have one caller or
  one implementation, or exist "for later"?
- Speculative compatibility: does a shim, legacy reader, version branch or migration path serve no current consumer?
- Unused code: are functions, classes, parameters, imports or commented-out blocks unreached?
- Unused parameters and flags: does no caller vary a parameter, or does a boolean flag switch between two behaviors?
- Boilerplate without a purpose: does a catch-all handler, silent fallback or validation guard a state internal code
  cannot reach?

### Guidance (skills, playbooks, root agent guides, instructions)

- Derivable content: can the agent derive it from the repository (overviews, directory trees, file-by-file
  descriptions, standard language conventions, the README)?
- Duplication: is the same rule stated in several always-loaded or co-loaded files, where the copies can drift?
- Conflicts: can two directives not both hold, or is precedence between nested guides unclear?
- Obsolete exceptions: does a carve-out name removed code, a retired command or a temporary state?
- Always-loaded context: does content load on every turn that only some tasks need, or sit where critical
  directives get buried?
- Keep: repository-specific operational constraints, decision criteria and examples the agent cannot infer. A
  removal of one needs a ground from §3.

### CLI

- Inventory the commands and subcommands of the roots first.
- Overlap: do two commands or options serve the same purpose, or does a catch-all default hide one?
- Unneeded: is a command or option unused by documented workflows and callers?
- Fragmented operations: does one user goal need several commands in a fixed sequence?
- Grouping and naming: do the same concepts use different flag names or ordering across commands?
- Help: do help text and its source docstrings describe actual behavior, lead with the common usage and name a useful
  next step?

## 2. Consolidation and reduction

- Merge duplicated logic into a shared module, fold repeated technical helpers into a utility, and remove unneeded
  code, guidance, options and commands.
- Introduce a shared implementation only for demonstrated repeated behavior: at least two current callers with the
  same behavior, where a change to one must be repeated in the others.
- If the implementations to consolidate do not behave identically, list each difference (accepted input, output,
  error or side effect) with the behavior the consolidation keeps. The decision round presents the list and the
  user's decision covers each difference; an approved difference is a behavior change of the report.
- Treat removing a compatibility path (shim, legacy reader, version branch) as a contract change, unless the
  repository's declared compatibility policy states that no external consumer exists for that package. Either way,
  name the inputs or callers no longer accepted. In-repository reachability never proves the absence of external
  consumers.
- Treat a removal, rename or consolidation of a command, option or public interface as a contract change, never as
  behavior-preserving refactoring.

## 3. Reduction grounds

Accept a reduction only on one of these grounds, and record which:

1. Derivable: the removed content is derivable from the repository.
2. Duplicated: a named canonical copy is kept.
3. Enforced: a check, rule or hook enforces it mechanically elsewhere.
4. Shown unnecessary by a recorded check: for code, the verification command and its result plus reachability
   evidence; for guidance, a recorded representative-task run with and without the text. Without that record this
   ground is unavailable.

Report the line or token delta, never as the justification.

## 4. Preservation evidence

Record per consolidation or removal:

- Reachability: static references and the repository's dynamic reach (entry points, plugin registries,
  configuration, documentation, string dispatch). Name each search (command, registry or configuration read) and its
  result.
- Verification: the relevant verification passing before and after the change, both results recorded.
- Differential comparison: for a change that consolidates or replaces a parser, scanner, matcher, file listing,
  serialized format or other function whose inputs can be enumerated or generated, run the old and new code on the
  same inputs: the repository's own corpus plus edge cases of the input domain (for example empty, malformed or
  unclosed input and symbolic link loops). Record the input count and the result. Fix each difference unless it is
  an approved behavior change.
  - Run the old code side by side from an extracted copy of the previous revision (for example `git archive`) or a
    separate checkout. Never stash to run it, because the stash list is shared by every worktree of the repository.
- Characterization test: add one only when some merged caller is exercised by no existing test.
- Guidance: a retained-constraint map, listing each constraint of the removed or merged text and where it remains,
  plus the representative-task run when the removal relies on ground 4.

## 5. Helper placement

Place a consolidated helper at the lowest common owner every caller may already depend on under the repository's
declared layering. Make a new cross-package or foundation module, or any placement in a repository without declared
layering, a decision in the round.

Example order for a layered monorepo: feature-local first, then a package-level `utils` (technical helpers) or `base`
(contracts), then the shared foundation package only for generic primitives with no application dependency.

## 6. Recurrence prevention

First delete, consolidate or correct the existing code and guidance. Propose a new rule only for an evidenced
recurring failure with a stated benefit, through the repository's rule-authoring process; never adopt a rule as part
of the run.
