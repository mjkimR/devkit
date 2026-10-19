// A successful wrapper run covers its complete reusable CI, or reuses that same verified head.
module.exports = async ({ github, context, core }) => {
  if (context.eventName !== "schedule") {
    core.setOutput("run_ci", "true");
    return;
  }

  const { data } = await github.rest.actions.listWorkflowRuns({
    ...context.repo,
    workflow_id: "nightly.yml",
    branch: context.payload.repository.default_branch,
    status: "success",
    per_page: 1,
  });
  const [previous] = data.workflow_runs;
  core.setOutput("run_ci", String(previous?.head_sha !== context.sha));
};
