# Technical reading tool: initial research

Research only. No architecture, storage technology or implementation is approved.

## Product framing

The user keeps technical articles and notes for several personal projects and occasionally shares a reading list with one collaborator. Work is mostly offline. Maintenance must fit a small tool. Proposed value: easier project-oriented retrieval and sharing. Switching value over bookmarks and folders is unproven. These constraints come from [the idea](../../inputs/idea.md) and [architecture request](../../inputs/architecture.md).

## Evidence and limits

All vendor examples in [the source pack](../../inputs/sources.md) are fictional scenario evidence. They do not describe observed users or real products.

- Vendor A marketing claims fully offline use and effortless collaboration. Its technical note requires the hosted account service for initial sign-in and enabling sharing. It describes offline edits to cached personal notes only. This narrows the marketing claim; it does not verify concurrent shared edits.
- Vendor B stores Markdown locally and delegates sharing and conflict resolution to another application. Local storage alone therefore does not establish collaboration behavior.
- The described workaround is browser bookmarks plus project folders. Retrieval and sharing costs have not been measured. No interviews or usage measurements exist.

The source pack cannot establish demand, edit-overlap frequency, acceptable recovery burden, maintenance effort or offline article-body availability. Notes being editable offline does not establish that linked articles are available offline.

## Compared directions

| Direction | Potential value and cost (inference) | Conditions to investigate |
| --- | --- | --- |
| Local files | Could support offline personal work without hosted operations. Organizing material, sharing and reconciliation add adoption effort. | Continue if required content is available offline and participants accept explicit recovery. Reopen server coordination if overlapping edits make recovery unacceptable. |
| Server-backed | Shared authoritative state could coordinate edits. Accounts, hosting and availability add maintenance; offline caching, synchronization and conflicts still need defined behavior. | Continue if coordination needs justify upkeep and hosted dependencies are acceptable. Reopen local files if operations exceed the small-tool constraint. |
| Existing workaround | Avoids migration and build effort. Its retrieval and sharing limitations are unmeasured. | Retain it if observed benefit cannot justify switching and upkeep. |

Recommendation: preserve all three directions while gathering discriminating evidence. Neither fictional vendor settles feasibility. No storage technology follows from this comparison. This is a recommendation, not a user decision.

## Conditional initial roadmap

1. Learning: observe representative retrieval and sharing against the existing workaround. Establish acceptable maintenance, hosted dependence, offline content coverage and recovery effort with both participants.
2. Learning: investigate shared-edit overlap across actual usage and discuss a divergent offline-edit scenario. One session can expose recovery problems but cannot establish overlap frequency. No such observation or scenario exercise occurred in this run.
3. Decision: compare the directions against those findings. Keep the workaround if benefit remains insufficient. Investigate local files if manual reconciliation is acceptable; investigate server coordination if shared edits require it within maintenance limits. Architecture remains unresolved until that decision.
4. Conditional build: only after separate user authorization, define the smallest retrieval-and-sharing slice and acceptance checks. Evaluate storage after offline and collaboration expectations are clear. No dates or delivery commitments are assigned.

## Source identities

SHA-256 of the inspected raw inputs:

- `inputs/idea.md`: `7ce5d08f84508b2d716befd8d99c1be0e93dc022927fc2c85018c029a80f861c`
- `inputs/architecture.md`: `c89863fbd0b3bc895d8c8fd00bc2bb5a1b6ca0536075d3e632fecd9a94c8085b`
- `inputs/sources.md`: `660bfd64a9b4d1427a0a65d8f94f263eb84f06a05ce687d4d192c36819fa4899`

The selected synthesis stands alone with these inputs. No network research, experiments, prototype or implementation occurred.
