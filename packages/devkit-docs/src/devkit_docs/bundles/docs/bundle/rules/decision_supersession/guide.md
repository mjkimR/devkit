# [RULE-decision-supersession] Decision supersession consistency

## Scope

The linter/error rule checks every targeted ADR, including superseded records, through the run's snapshot cache.
PADRs and other document kinds are outside its scope. Aliases resolve through the document index's unique canonical
mapping. `supersedes` accepts one ADR ID or a list; `superseded_by` accepts one ADR ID.

## Findings and remediation

1. Keep `superseded_by` only on a wholly replaced ADR with `status: superseded`; name one resolving ADR there.
2. In that successor's `supersedes`, name the replaced ADR.
3. For every `supersedes` target, retain either `status: superseded` or a visible partial pointer naming the successor.
4. For partial replacements, keep the earlier ADR accepted and write `Superseded in part by` followed by the successor's
   backtick-quoted ADR ID. In that successor's `supersedes`, name the earlier ADR.
5. Correct missing, ambiguous, malformed or non-ADR metadata targets by hand.

Code fences, comments, indented code and struck-out text are masked for partial pointers. Checks do not interpret
which clauses a replacement covers, change the reference graph or rewrite files. `devkit rules fix` leaves these
findings unresolved; repair the recorded decision relationship and rerun `devkit rules check` until it passes.

## Example

An accepted ADR-example-old contains this body line:

```markdown
Superseded in part by `ADR-example-new`: the retry policy.
```

ADR-example-new records `supersedes: [ADR-example-old]`. A whole replacement instead sets the earlier ADR's
`status: superseded` and `superseded_by: ADR-example-new`.

## Configuration

No rule-specific settings. Standard targeting and exclusions apply; there are no inline suppressions.
