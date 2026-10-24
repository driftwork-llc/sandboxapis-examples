# One agent task, in two agent frameworks

Both examples run the task from [`tutorials/github`](../tutorials/github): did the fix for the incident, pull request 53 in `olympus-labs/parthenon`, ship, and did someone other than its author approve it? Both send their tool calls to the pinned GitHub replica `https://gh-2026-03-g12.snap.sandboxapis.dev`, which needs no key and answers the same way on every run. Both score the agent's answer against the [eval pack](../evals)'s answer key, items `gh-pull-merged` and `gh-independent-approval`, and print `ok` only when it matches.

| Directory | Framework | The agent | Model key |
| --- | --- | --- | --- |
| [`langgraph/`](langgraph) | LangGraph | A two-node graph: `fetch_github`, a tool node that calls the pinned host with `requests`, then `reason`, an LLM node | `ANTHROPIC_API_KEY` |
| [`openai-agents/`](openai-agents) | OpenAI Agents SDK | One `Agent` with one function tool, `github_get`, and a typed `Verdict` output | `OPENAI_API_KEY` |

Python 3.10 or newer.

## `--dry-run`: verify it without a model key

`--dry-run` replaces the model with a fixed rule (merged, and the first approver who is not the author) and runs everything else for real: the tool calls go to the live pinned host, and the result is scored against the eval pack. A reviewer with no model key can check that the tool, the host and the scorer all work:

```bash
cd langgraph && pip install -r requirements.txt && python github_eval_graph.py --dry-run
cd openai-agents && pip install -r requirements.txt && python github_eval_agent.py --dry-run
```

Without `--dry-run` the model answers, and the same scorer checks it. `MODEL` overrides the default model in either example.

## Budget

Each run makes two requests to the pinned host (plus one to `sandboxapis.dev` for the answer key when the file is not beside it). Anonymous callers get 60 requests an hour; set `SANDBOXAPIS_API_KEY` to a free key from [sandboxapis.dev/login](https://sandboxapis.dev/login) to ride 600 an hour instead.
