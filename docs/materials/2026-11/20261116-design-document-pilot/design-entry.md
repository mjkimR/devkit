# Journaled replacement of a file and directory

**Reader question:** How can one managed path become a directory or the reverse without losing rollback information?

This non-normative mechanism overview follows the distribution transaction implementation. Replacement is a
change-set problem: one deletion frees a path another write needs. Rollback also needs to distinguish prior file
content from directories created or replaced during that change set.

`CAP-DIST-sync-and-transactions` §3 owns safety guarantees and admissible replacements.
`ARCH-05-4-distribution-components` §3 locates the installation service that implements them.
`ARCH-06-runtime-view` §1 supplies system interaction context; it is not prerequisite reading for the mechanism.

Next read [replacement detail](replacement-detail.md): it explains preflight, journal content, deletion ordering
and rollback, and links the implementing symbols. The detail is independently readable for a reader arriving at it
directly. Source links provide actual artifacts; an illustrative datasheet or additional diagram is unnecessary for
this small sequence.

## Evidence boundary

This entry locates a cohesive mechanism below the system architecture view. The linked detail explains present
code rather than adding an observable guarantee. The capability remains the normative owner. No source or
architecture change is selected by this pilot, and no contract-to-draft discovery path is implied by this entry.
