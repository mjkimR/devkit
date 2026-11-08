# Evidence and recovery walkthroughs

Source: guidance at commit `cbb4c82b85edac460ef0588838591e39e089ec0c`, reviewed against `56e614f858a0f0dca8bd509d452468c6e7a36057`. Reviewer: Development worker. These are contract walkthroughs, not live model execution; installed packaging tests do not establish agent decisions.

| Input | Expected action | Observation and limit |
| --- | --- | --- |
| Stateful saved operation with duplicate request and partial write | Choose normal, duplicate and partial-failure probes; retain expected signal and actual source-specific outcomes | Evidence guidance selects relevant stateful probes and records interaction, source, outcome and limit. No product probe was run. |
| Fixture import fails before the product starts; cause not established | Keep cause unknown and product unverified | Guidance requires evidence for classification and a valid subsequent product probe. The import example describes diagnosis rather than an observed failure. |
| Same import error twice without a new causal observation, no supplied bound | Change strategy before repeating | Guidance triggers diagnosis after two identical no-progress attempts; materially new evidence is defined. No agent retry was observed. |
| Interrupted failed approach with an active owner and surviving hypothesis | Host retains reason, identity, owner, hypothesis, retry condition and recovery action; resume rechecks applicability | Current-context and orchestration guidance retain these fields and protect work. No interruption was executed. |
| Stateless formatting change with no relevant failure edge | Omit irrelevant adversarial probes and old history | Evidence guidance scopes probes by behavior and consequence; current context keeps only useful facts. No live agent was observed. |
