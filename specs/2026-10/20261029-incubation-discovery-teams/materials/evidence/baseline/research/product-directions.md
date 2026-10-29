# Reading tool: initial product directions

## Goal and boundary

The user keeps technical articles and notes across personal projects and occasionally shares a reading list with one collaborator. Work is mostly offline. Maintenance capacity fits a small tool. This research precedes development; no prototype, platform or storage technology has been selected.

A representative flow to investigate: save an article with a project and note, retrieve it for that project offline, prepare a shared reading list, let the collaborator change it, then reconcile both people's changes without losing intent. This is a proposed discovery scenario, not observed usage.

## Evidence and its limits

All evidence below comes from the supplied fictional `inputs/sources.md`; it describes no real products or measured users.

| Source identity | Observed statement | Decision implication |
| --- | --- | --- |
| Vendor A marketing, 2026-10-01 | Claims full offline operation and effortless collaboration. | Broad claims alone do not establish shared-edit behavior. |
| Vendor A technical note, 2026-10-20 | First sign-in and enabling sharing require a hosted account service. Cached personal notes support offline editing. Concurrent shared edits are unspecified. | The marketing claim is qualified. Fully offline setup and collaboration remain unproven. |
| Vendor B technical note, 2026-10-15 | Markdown resides in a local folder. Another application handles sharing and conflicts. | File ownership is documented; collaboration still has a dependency. Conflict safety is unverified. |
| Current workaround | Browser bookmarks and project folders. | No measured retrieval or sharing cost establishes a replacement's value. |

No interviews, usage measurements, overlap frequency, conflict experiments or maintenance estimates exist. Technical notes support narrower claims than marketing. Neither vendor supplies evidence of successful concurrent shared editing.

## Candidate directions

| Direction | Fit and tradeoffs | Evidence needed before selection |
| --- | --- | --- |
| Improve the existing workaround | Lowest additional tool maintenance; may leave retrieval and sharing friction unchanged. | Observe where the current flow fails or costs effort. |
| Small local-file tool | Plausible fit for offline personal work and user-controlled files. Sharing needs a transfer/sync process and explicit conflict handling; external tools add maintenance dependencies. | Offline retrieval needs, acceptable sharing delay, overlap and recovery expectations. |
| Server-backed tool | Could coordinate shared state and access when connected. Offline writes still need synchronization and conflict semantics. Hosting, accounts and operation may exceed the maintenance constraint. | Demonstrated collaboration need that justifies operating cost and disconnected behavior. |

**Agent recommendation:** investigate the workaround first, with a local-file direction as the leading hypothesis because offline work and small maintenance capacity are stated constraints. Keep the server direction open if observed sharing needs justify it. This is neither user approval nor a storage decision. A server alone does not resolve disconnected concurrent changes.

## Initial roadmap

1. **Observe before replacing.** The user and collaborator walk through the representative flow using their existing tools. Record retrieval attempts, sharing steps, elapsed effort, failed handoffs and overlapping edits. Include a deliberately overlapping edit as a discussion scenario if natural overlap is absent; label it simulated.
2. **Agree on usefulness and sharing expectations.** Set a concrete improvement target from that baseline. Decide acceptable delay, whether both people need offline shared edits, and what recovery from conflicting edits must preserve. These are unresolved user decisions.
3. **Compare a narrow first version.** Scope article references, project association, short notes, retrieval and one explicit shared-list workflow only if the baseline supports them. Estimate ongoing maintenance for local-file and server directions. Revisit the recommendation using the agreed criteria.
4. **Development gate.** Choose a direction and storage only after the user reviews those findings. Any future prototype needs separate authorization. Verify offline operation, the agreed sharing flow, conflict recovery and usefulness against the baseline before expanding scope.

This wave produced a document comparison only. It establishes neither product usefulness nor architecture feasibility.
