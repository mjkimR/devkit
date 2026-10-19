const assert = require("node:assert/strict");
const { test } = require("node:test");
const gate = require("./nightly-ci.cjs");

function fixture(eventName = "schedule", runs = []) {
  const queries = [];
  const outputs = [];
  const input = {
    context: {
      eventName,
      repo: { owner: "owner", repo: "repo" },
      payload: { repository: { default_branch: "main" } },
      sha: "current",
    },
    github: {
      rest: { actions: { listWorkflowRuns: async (query) => {
        queries.push(query);
        return { data: { workflow_runs: runs } };
      } } },
    },
    core: { setOutput: (key, value) => outputs.push([key, value]) },
  };
  return { input, queries, outputs };
}

test("first nightly runs the complete CI and queries only successful default-branch wrapper runs", async () => {
  const { input, queries, outputs } = fixture();
  await gate(input);
  assert.deepEqual(queries, [{
    owner: "owner", repo: "repo", workflow_id: "nightly.yml", branch: "main", status: "success", per_page: 1,
  }]);
  assert.deepEqual(outputs, [["run_ci", "true"]]);
});

test("a successfully verified head skips the heavy CI", async () => {
  const { input, outputs } = fixture("schedule", [{ head_sha: "current" }]);
  await gate(input);
  assert.deepEqual(outputs, [["run_ci", "false"]]);
});

test("changes since the last success run even after a failed or cancelled attempt", async () => {
  // The API success filter omits unsuccessful attempts at the current head.
  const { input, outputs } = fixture("schedule", [{ head_sha: "older-success" }]);
  await gate(input);
  assert.deepEqual(outputs, [["run_ci", "true"]]);
});

test("manual invocation always runs and does not depend on the history API", async () => {
  const { input, queries, outputs } = fixture("workflow_dispatch", [{ head_sha: "current" }]);
  await gate(input);
  assert.deepEqual(queries, []);
  assert.deepEqual(outputs, [["run_ci", "true"]]);
});

test("history permission and network failures cannot produce a successful skip", async () => {
  const { input, outputs } = fixture();
  input.github.rest.actions.listWorkflowRuns = async () => { throw new Error("API unavailable"); };
  await assert.rejects(gate(input), /API unavailable/);
  assert.deepEqual(outputs, []);
});

test("malformed run history fails closed", async () => {
  const { input, outputs } = fixture();
  input.github.rest.actions.listWorkflowRuns = async () => ({ data: {} });
  await assert.rejects(gate(input), TypeError);
  assert.deepEqual(outputs, []);
});
