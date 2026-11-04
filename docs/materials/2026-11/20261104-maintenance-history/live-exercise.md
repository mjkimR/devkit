# Maintenance history live exercise

Status: not executed. Injected-model results are not live GitHub evidence. `SPEC-maintenance-history` AC-10 remains required.

The operator selects an existing nonempty throwaway GitHub repository and one dedicated branch named devkit-history-exercise-<suffix>. Explicit authority must cover creating its immutable history root, sanitized run/report/amendment commits and non-forced ref-update probes. The script retains the branch; it performs no repository creation, remote deletion, force update, code-history update or publication of actual project content.

Run after obtaining that exact destination and authority:

```sh
uv run python docs/materials/2026-11/20261104-maintenance-history/live-exercise.py \
  --repository <owner/throwaway-repository> \
  --branch devkit-history-exercise-<suffix> \
  --authority "<user authority for this exercise destination>"
```

The script checks deterministic initialization, repeated blob/tree/commit POSTs, duplicate publication, amendment, same-SHA reference updates, non-fast-forward rejection, missing file/ref responses and retrieval. It prints sanitized JSON observations for retention as live-results.json after successful execution. No credentials or real project evidence enter the fixture. It does not infer access-denied private-repository behavior or simulate service rate limits as live evidence; injected integration tests cover those response classes.

A failed exercise remains failed evidence: retain its observed status, fix the implementation within the agreed contract and rerun only the affected probes. After successful completion, confirm the documented root/error facts against the observations, mark AC-10's task complete and promote the capability/use cases from draft/proposed to active.
