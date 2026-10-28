# Baseline report template

Copy this shape into an ordinary material report and replace placeholders with observed facts.
Keep source identity and current conclusions; this report is not a Unit or an approval envelope.

# SDD baseline: <retained product>

## Identity and selected scope

- Repository and exact HEAD: <identity>
- Relevant dirty paths and their content identity: <paths and evidence, or none>
- Current approach/source and selected assets: <observed inspection>
- Retained goal, constraints and representative flows: <scope>
- Exclusions and reasons: <outside the user's selected adoption scope>
- Existing context and run instructions: <available locations; context is optional>

## Retained coverage

| Retained item | Current document or destination | Implementation citation | Check/usage evidence and source | Status | Gap or limitation |
| --- | --- | --- | --- | --- | --- |
| <behavior, structure, choice or verification method> | <location> | <file/symbol> | <observation> | <verified/gap/excluded> | <fact> |

## Executed verification

| Command or interaction | Revision/dirty source | Environment | Actual outcome | Coverage and limits |
| --- | --- | --- | --- | --- |
| <exact execution> | <identity> | <environment> | <pass/fail/skipped> | <bounded observation> |

## Gaps and dispositions

Record missing evidence and mismatches, their user-decided disposition and the affected recheck.
Required gaps block readiness. Exclusions do not count as verified coverage.

## Readiness and activation effects

State whether all selected retained items are verified and applicable required checks passed.
Identify the ready report/source, selected SDD assets, exact approach change and integration provider.
Preserve an existing spec provider; list project-to-spec as an explicit activation effect when necessary.
Without authority for that necessary effect, report a mismatch rather than successful adoption.
Name the existing explicit user authority for those same effects, or state that the decision is pending.
Record real versus simulated decisions in a test exercise.

## Observed final state or recovery

Record actual policy/asset inspection, sync/check outcomes and next SDD routing after activation.
For a partial failure, identify the failed command, current state, next supported recovery and stale evidence to recheck.
Do not claim rollback or successful adoption from an unverified expectation.
