# Repository roadmap

Milestones are `MS-<slug>.md` documents with a word-led slug (for example `MS-release-1-0`) at the global roadmap root
or a registered namespace's roadmap root. Discover them with `devkit docs list milestone`, which follows the current
directory (`--all-namespaces` shows every root, `--history` adds done/dropped).

## Goal and membership

- Cite the goal in `ARCH-01-introduction-and-goals`.
- Milestones are loosely managed themes: user and agent jointly review a multi-unit phase, release or architectural
  theme and decompose it into direct PROP members. A theme may initially have one proposal while broader scope is
  unauthored; prefer a broader theme over a milestone that only sequences one proposal.
- Only direct PROP anchors declare membership, through `milestone`; milestone bodies list no work. Unit `depends_on`
  holds PROP/SPEC prerequisites; milestone `depends_on` is MS-only.
- Handoff does not carry milestone metadata to SPEC and historical SPEC metadata is ignored; no delivery lineage is
  stored, so inspect downstream code/Git on demand.

## Exit condition

Exit conditions are recommended to state capability boundaries and prefer observable phase-level outcomes over CLI
flags, branch names, file layouts and scenario tests, which belong in proposals/specs.

## Lifecycle

Creation, placement, status changes, close, drop, reopen and merge follow [Backlog](backlog.md) Milestones and
[milestone completion](milestone-completion.md).
