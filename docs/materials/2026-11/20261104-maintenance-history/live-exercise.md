# Maintenance history live exercise

Status: passed against `mjkimR/test-sandbox` branch `devkit-history-exercise-20261104-c94eb4fc`. The user supplied the test-sandbox destination and authorized the sanitized exercise; `answer-01.yaml` records the decision. `live-results.json` is the retained live observation. `live-attempt-01.json` preserves the failed first lookup and its demonstrated fix.

```sh
uv run python docs/materials/2026-11/20261104-maintenance-history/live-exercise.py \
  --repository mjkimR/test-sandbox \
  --branch devkit-history-exercise-20261104-c94eb4fc \
  --authority "<explicit destination-specific user authority>"
```

The exercise initialized the frozen parentless root, published one sanitized weekly-report run and appended an integration amendment. It retained the dedicated remote branch at `39c0a871ff5bc4d04f5f50fdd87c44c77a586b2d`. It deleted no remote resource, forced no update and published no real project content. It did not touch the supplied local test-sandbox checkout. Authored local fixture/run files remain under the maintenance worktree's ignored `tmp/` directory.

| Probe | Observed result |
| --- | --- |
| Frozen root | `96eb369a841a26ca7094eb2bea25bbf8ccb5d95a` |
| Repeated blob/tree/commit POSTs | Identical SHA for each repeated object |
| Duplicate publication | Original history commit returned |
| Amendment, index listing and report retrieval | Passed |
| Non-forced same-SHA reference update | HTTP 200 |
| Non-forced stale reference update | HTTP 422; head unchanged |
| Missing file and absent reference in readable repository | HTTP 404 for each |

The first attempt failed before mutation: `GET repos/mjkimR/test-sandbox/` returned 404 while the canonical endpoint without a trailing slash returned 200. The strict regression failed before the endpoint fix and the integration suite passed afterward. The injected GitHub model now reproduces that distinction.

Private-repository access denial and service rate-limit responses were not exercised live; injected tests cover their response classes. These observations describe the selected fixture, without inferring undocumented error messages. Live success verifies AC-10 independently of playbook composition. Canonical activation and completion also require the user-refined opt-in contracts and their review.
