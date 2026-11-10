# [RULE-decision-supersession] Decision supersession consistency

## Scope

The linter/error rule checks every targeted ADR, including superseded records, through the run's snapshot cache.
Materials and other document kinds are outside its scope. PADRs receive statement checks only. Aliases resolve through the document index's unique canonical
mapping. `supersedes` accepts one ADR ID or a list; `superseded_by` accepts one ADR ID.

## Findings and remediation

1. Keep `superseded_by` only on a wholly replaced ADR with `status: superseded`; name one resolving ADR there.
2. In that successor's `supersedes`, name the replaced ADR.
3. For every `supersedes` target, retain either `status: superseded` or a visible partial pointer naming the successor.
4. For partial replacements, keep the earlier ADR accepted and write `Superseded in part by` followed by the successor's
   backtick-quoted ADR ID. A later whole replacement may set the earlier ADR superseded while retaining its
   historical partial pointers. In that successor's `supersedes`, name the earlier ADR.
5. Correct missing, ambiguous, malformed or non-ADR metadata targets by hand.

Code fences, comments, indented code and struck-out text are masked for partial pointers. Checks do not interpret
which clauses a replacement covers, change the reference graph or rewrite files. `devkit rules fix` leaves these
findings unresolved; repair the recorded decision relationship and rerun `devkit rules check` until it passes.

6. Write one partial-supersession statement for each resolving non-superseded target of an ADR or PADR; a missing
   statement is reported at `supersedes`.
7. Remove stray statements, merge duplicates by canonical target, and fill empty statement text; findings point to
   the statement line. Aliases count as their canonical document.
8. Copy the statement's source text into one earlier ADR pointer. Whitespace and wrapping may differ; inline code
   and links must match. A mismatch is reported once per pair at the first pointer if its file is targeted, else
   at the statement. Missing pointers retain the metadata finding. PADRs and wholly superseded targets are exempt
   from pointer-text comparison. A whole target is exempt from missing-statement checks too.

## Example

An accepted ADR-example-old contains this body line:

```markdown
Superseded in part by `ADR-example-new`: the retry policy.
```

ADR-example-new records `supersedes: [ADR-example-old]` and this Decision Outcome statement:

```markdown
Supersedes in part `ADR-example-old`: the retry policy.
```

Each statement or pointer is a paragraph or list item; its text stops at a blank line, next item or heading.
Source text includes code spans. Keep statements free of trace, source citation, nested list and relative link.
The rule checks text, not meaning, and offers no fixer. After a repair, copy the statement into one pointer.
 A whole replacement instead sets the earlier ADR's
`status: superseded` and `superseded_by: ADR-example-new`.

## Configuration

No rule-specific settings. Standard targeting and exclusions apply; there are no inline suppressions.
