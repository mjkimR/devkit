---
reconcile_id: REC-repository-viewer
status: resolved
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: docs/development/reference/README.md
    resolution: modified
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/development/setup.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-viewer-distribution-and-frontend-build.md
    resolution: modified
  - file: docs/decisions/2026-10/20261019-read-only-local-server-over-git-refs.md
    resolution: modified
---

# Reconciliation

`CAP-VIEW-repository-viewer` is the new canonical contract of the `devkit-viewer` distribution: `devkit viewer serve`,
its registration and refusals, the GET-only JSON API over Git refs, the loopback and `Host` safety rules, the page's
tabs, the roadmap rules and the library autohub vendors. It states what review fixed: only files the bundle lists are
served, by decoded path; a ref is `HEAD` or the exact name of a local branch, listed by full name; the roadmap reads
the default branch plus local `plan-`/`dev-` branches whatever branch the page shows.

`ARCH-05-1-containers` adds the container and its edges (harness dependency on `devkit-agt`, the local viewer for
development environments, the vendored library for autohub). `ARCH-07-deployment` adds the release wheel and the Git
install line, names the viewer command among the release notes and states that the library is vendored, not
released. The module reference (`viewer.md`, indexed in the reference README) mirrors the command, codes, API and
frontend recipes; `ci-cd.md` describes the viewer CI job and smoke step, and `setup.md` the Node prerequisite for
frontend changes only and the `just viewer` commands.

The two ADRs were promoted from the proposal's PADRs by the handoff and are not edited afterwards. One sentence of
`ADR-read-only-local-server-over-git-refs` §4 names `git rev-parse --verify --end-of-options` as the ref mechanism;
the implementation narrows it to `HEAD` or `refs/heads/<exact name>` (`show-ref --verify`) so that tags,
remote-tracking branches, commit IDs and expressions are refused. The decision itself (local branches only, nothing
fetched) holds and is enforced more strictly; `CAP-VIEW-repository-viewer` §2 carries the exact rule.

No story is added: the user stories of `SPEC-repository-viewer` describe this one capability and no existing story
changes. No other capability's behavior changes; `CAP-DLV-human-interaction` and `CAP-INT-mcp-services` are unchanged,
since the viewer takes no part in approvals.

Deferred work: none retained in this repository. autohub's adoption of the vendored library is autohub's own change
(its `vendor/` tarball and the removal of its copy), outside this repository's proposals. Showing open workflow
requests and uncommitted working tree content stay non-goals with their reconsider triggers in the spec; no follow-up
is queued for them.
