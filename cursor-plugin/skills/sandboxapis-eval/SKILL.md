---
name: sandboxapis-eval
description: Score an agent run against the SandboxAPIs answer-key eval pack. Use when the user asks to evaluate, score or regression-test an agent that reads GitHub, GitLab, Jira, Linear or Slack, or asks whether the sandboxapis data set still answers the way it did.
---

# Run the SandboxAPIs eval pack and read the score

The eval pack is 53 known facts about the `olympus-labs` data set across five services. Each item carries the request that answers it and the value it must come back with, and every host it calls is a pinned snapshot, so the same question returns the same answer on every run.

## Steps

1. Get the pack. If the examples repository is open, it is already in `evals/`. Otherwise fetch the three files:

   ```bash
   mkdir -p sandboxapis-evals && cd sandboxapis-evals
   curl -O https://sandboxapis.dev/evals/olympus-labs-g12.json
   curl -O https://sandboxapis.dev/evals/run.mjs
   ```

2. Check the budget first. A full run makes 12 requests, which fits inside the anonymous 60 requests an hour; if `check_budget` shows fewer than 12 remaining, wait for the reset or set `SANDBOXAPIS_API_KEY` in the shell before running.

3. Run it with Node 22 and no dependencies:

   ```bash
   node run.mjs
   ```

   This scores the data set: the harness reads each answer straight out of the response. Every item should pass. A failing item here means the host or the pack changed, not the agent; report it as such and stop.

4. To score the agent instead, replace the body of `answer()` in `run.mjs` with the agent's own reasoning (a model call that reads the fetched rows and returns the value) and run `node run.mjs --agent`. Now a failing item is the agent reading the right rows wrongly.

5. Read the score as three numbers, one per difficulty: `read` (one field off one response), `join` (two responses have to agree) and `reason` (the value is computed from what came back). Report all three and name the failing items by id; do not summarise to a single percentage.

## Rules

- Keep every host in the pack as it is. The pack pins `-g12` snapshot hosts on purpose; swapping in a live host makes the answers move.
- Do not edit `expected` values to make a run pass. Each item names the test in the SandboxAPIs repository that guards its answer; if the answer looks wrong, that is the thing to report.
- Set `SANDBOXAPIS_RUN=<a name>` when the user has the flight recorder on for their key, so the whole run arrives in their dashboard as one timeline.
