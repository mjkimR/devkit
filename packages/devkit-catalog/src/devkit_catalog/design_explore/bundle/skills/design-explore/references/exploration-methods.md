# Exploring mechanisms

1. Identify what actually produces the intended benefit before changing the proposed means.
2. Select only lenses that can change a useful direction for this problem:
   - Simplify: remove a component, state, coordination step or decision that the goal does not require.
   - Remove a premise: question when work happens, who owns it or whether the proposed subsystem must exist.
   - Transfer a mechanism: adapt ownership, batching, indirection, caching or reconciliation from another domain.
3. Preserve hard constraints in every viable candidate. If relaxing a preference reveals a useful mechanism, label
   the relaxed preference; a hard-constraint conflict is an infeasible sketch unless the user changes that constraint.
4. Explain how each mechanism works with one concrete example and the consequential cost it introduces.
5. Retain a familiar sufficient design when it best fits the problem; novelty alone earns no recommendation.

For cross-process status sharing, compare a single owner answering queries, an existing persistent store with
readers, and asynchronous events with reconciliation. Show ownership and stale/failure behavior for each.
Three database brands using the same coordination scheme are product choices, not three architectures.
Do not add distributed infrastructure solely to make an option unusual.

For a data model, question whether a stored field is authoritative state or a derivation; compare computing it on
read with maintaining it on writes when that changes consistency and ownership.
For a module boundary, compare moving responsibility to the state owner with introducing a coordination layer.
For a workflow, compare eliminating a handoff with batching it; preserve any required approval or audit constraint.
These examples illustrate exploration, not tested recommendations for a consumer project.
