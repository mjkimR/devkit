# ADRs kept outside the run

Read when an ADR kept outside the run partially supersedes a member, or a member partially supersedes it.

- Add `supersedes` to a replacement only for an ADR kept outside the run that a member partially superseded, listing
  that kept ADR.
- If a kept ADR names a member in `supersedes`, name the member's replacement instead and add the matching
  "Superseded in part by" line to that replacement.
- A kept ADR's own "Superseded in part by" line names the member's replacement, which lists it in `supersedes`.
