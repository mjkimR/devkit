# Baseline report template

Copy this shape into the material report, replace placeholders with observed facts and keep source identity and
current conclusions; the report is not a Unit or an approval envelope.

Recovery rules, not part of the report:

- If installation, policy update or sync fails, record the failed command and the actual partial policy, asset and
  file state in the report, and report the next supported recovery action; claim neither successful adoption nor
  automatic rollback.
- Resume from the existing report after revalidating source and affected evidence, without duplicating baseline
  documents.

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

Record missing evidence and mismatches, their user-decided disposition and the affected recheck. Required gaps block
readiness.

## Readiness and activation effects

- State whether all selected retained items are verified and applicable required checks passed.
- Identify the ready report/source, selected SDD assets and exact approach change; invent no provider activation
  effects or separate approval for them.
- Name the existing explicit user authority for those same effects, or state that the decision is pending.
- In a test exercise, record real versus simulated decisions.

## Observed final state or recovery

Record actual policy/asset inspection, sync/check outcomes and next SDD routing after activation. For a partial
failure, identify the failed command, current state, next supported recovery and stale evidence to recheck.
