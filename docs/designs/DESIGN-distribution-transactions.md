---
id: DESIGN-distribution-transactions
title: "Journaled replacement of a file and directory"
status: active
summary: "Explains journaled file and directory replacement, its independent mechanism detail and authoritative distribution boundaries."
related_designs: [DESIGN-distribution-file-directory-replacement]
---

# [DESIGN-distribution-transactions] Journaled replacement of a file and directory

**Reader question:** How can one managed path become a directory or the reverse without losing rollback information?

This non-normative mechanism overview follows the distribution transaction implementation. Replacement is a
change-set problem: one deletion frees a path another write needs. Rollback also needs to distinguish prior file
content from directories created or replaced during that change set.

`CAP-DIST-sync-and-transactions` §3 owns safety guarantees and admissible replacements.
`ARCH-05-4-distribution-components` §3 locates the installation service that implements them.
`ARCH-06-runtime-view` §1 supplies system interaction context; it is not prerequisite reading for the mechanism.

Next read `DESIGN-distribution-file-directory-replacement`: it explains preflight, journal content, deletion ordering
and rollback, and links the implementing symbols. The detail is independently readable for a reader arriving at it
directly. Source links provide the implementing artifacts.

## Maintenance touchpoints

This maintained explanation follows the installation service's current transaction mechanism. Recheck the detail
when its source symbols change. Revisit architecture for changed system responsibilities and the capability for
changed guarantees; implementation explanation does not transfer either authority.
