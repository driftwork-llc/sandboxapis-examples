# SandboxAPIs examples

Testing an agent that reads GitHub, Jira or Slack means keeping a test account alive, seeding it with data that looks nothing like production, and watching the suite flake when somebody changes it. SandboxAPIs replaces that with read-only, API-compatible replicas of 21 developer and SaaS APIs, all preloaded with one simulated engineering company whose references resolve across every provider. Point your client's base URL at us and your read code works unchanged, with no signup and no seed scripts.

This repository holds the runnable parts: an answer-key eval pack, three agent tutorials you can execute, and the MCP server's install recipes. The service itself lives at [sandboxapis.dev](https://sandboxapis.dev).

## The MCP server

```bash
claude mcp add sandboxapis -- npx -y @sandboxapis/mcp
```

Then have the agent call `orient` first. It comes back with the API surfaces and their base URLs, the simulated company and its teams, notable entry points each with a ready-to-run request, how to pin a reproducible snapshot, where the coverage manifest lives, and an `access` block saying what the server may spend. That is enough to make a correct call with no docs reading.

### Claude Desktop

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sandboxapis": {
      "command": "npx",
      "args": ["-y", "@sandboxapis/mcp"]
    }
  }
}
```

### Cursor

One click installs the server with no key: [Add to Cursor](https://sandboxapis.dev/docs/mcp#cursor)

Copy this into the address bar if the button does not open Cursor:

```
cursor://anysphere.cursor-deeplink/mcp/install?name=sandboxapis&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBzYW5kYm94YXBpcy9tY3AiXX0=
```

The link carries only `{ "command": "npx", "args": ["-y", "@sandboxapis/mcp"] }`, and Cursor shows it to you before installing. Or add this to `.cursor/mcp.json` in your project, or to `~/.cursor/mcp.json` for every project:

```json
{
  "mcpServers": {
    "sandboxapis": {
      "command": "npx",
      "args": ["-y", "@sandboxapis/mcp"]
    }
  }
}
```

### An API key is optional

Everything works with no configuration. A free key lifts the anonymous limit of 60 requests an hour to 600, which an agent in a loop will want:

```json
{
  "mcpServers": {
    "sandboxapis": {
      "command": "npx",
      "args": ["-y", "@sandboxapis/mcp"],
      "env": { "SANDBOXAPIS_API_KEY": "sk_live_..." }
    }
  }
}
```

Keys are free at [sandboxapis.dev/login](https://sandboxapis.dev/login).

### The Cursor plugin

[`cursor-plugin/`](cursor-plugin) is the same server as a Cursor plugin, with a rule that teaches the agent to call `orient` first and `check_budget` before loops, and a skill that runs the eval pack below. Opening this repository in Cursor applies the rule on its own, from [`.cursor/rules/sandboxapis.mdc`](.cursor/rules/sandboxapis.mdc). The walkthrough is at [sandboxapis.dev/docs/tutorials/cursor](https://sandboxapis.dev/docs/tutorials/cursor).

### Tools

| Tool | What it does |
|---|---|
| `orient` | Start here. Full self-orientation, no docs required, including an `access` block: keyed or not, requests left this hour, and where to raise the limit. |
| `check_budget` | Costs nothing. Call it before any loop of more than a handful of requests: limit, remaining, when the window resets. |
| `list_repositories` / `get_repository` | Repositories, provider-shaped, with provider-form ids. |
| `list_pull_requests` / `get_pull_request` | Pull requests and merge requests with their reviews or approvals. |
| `list_issues` | Issues. REST on the git hosts and Jira, GraphQL on Linear. |
| `get_user` | A user by login or username. |
| `search_commits_by_author` | Commits by author, with SHAs that cross-reference across hosts. |
| `get_snapshot` | The pinned hostname for drift-free CI. |

Results come from the same public API a human would point a client at, so anything an agent learns here transfers directly to a `curl` or an Octokit call.

### Writes are refused on purpose

Everything is read-only. A mutation returns the provider's own error shape with a plain explanation, so an agent that tries one learns something instead of breaking something. An uncovered REST endpoint returns a real `404` plus an `X-SandboxAPIs-Coverage` header pointing at the [coverage manifest](https://sandboxapis.dev/coverage); an uncovered GraphQL field returns an explicit coverage error rather than a silent `null`. You will never get a plausible-looking invented value.

## What is in this repository

### `evals/`: the answer-key eval pack

53 known facts about the `olympus-labs` data set across 5 services, each with the request that answers it and the value it must come back with. Every host in the pack is a pinned snapshot, so the same question returns the same answer on every run.

```bash
cd evals
node run.mjs              # Node 22, no dependencies
# or
pip install requests && python3 run.py
```

A full run makes 12 requests, which fits inside the anonymous hourly budget. Both harnesses read the answer straight out of the response, which scores the data set. The `answer()` function in each is the one place to change: put your model call there, run with `--agent`, and the same expectations now score your agent instead.

Each item carries `guarded_by`, naming the test that would fail if the answer changed. Those tests live in the SandboxAPIs engine repository, which is private; the citation is there so you can see that every answer is pinned by a test rather than typed from memory.

### `tutorials/`: three agent tasks, as runnable files

One provider from each of the three categories an agent-evaluation harness reaches for first: a git host, a tracker and a chat log. Each directory holds the agent script, the same claim as a five-line pytest file, and a README with the captured output.

| Directory | The question the scripted agent answers |
|---|---|
| [`tutorials/github`](tutorials/github) | Did the fix for the incident ship, and did anyone other than its author sign it off? |
| [`tutorials/jira`](tutorials/jira) | How long did the incident take to close, and did it beat the team's 72 hour target? |
| [`tutorials/slack`](tutorials/slack) | Is the incident thread resolved, who called it, and how many people were in it? |

```bash
cd tutorials/github
pip install requests && python3 github_agent.py
```

All three read the same incident from three different APIs, and they agree with each other. That is the point of the data set.

### `cursor-plugin/`: the Cursor plugin

The MCP server, a rule and a skill in Cursor's plugin format, installable as a local plugin today. See its [README](cursor-plugin/README.md).

### `mcp/`: directory metadata and a container recipe

Notes on what the MCP server needs for each distribution channel, and a `Dockerfile` for running it in a container.

## Links

- Docs: [sandboxapis.dev/docs](https://sandboxapis.dev/docs)
- MCP server docs: [sandboxapis.dev/docs/mcp](https://sandboxapis.dev/docs/mcp)
- Coverage manifest, every endpoint and its status: [sandboxapis.dev/coverage](https://sandboxapis.dev/coverage)
- Try it in one request, no signup: [sandboxapis.dev/try](https://sandboxapis.dev/try)
- Registry listing: `dev.sandboxapis/mcp` in the [official MCP registry](https://registry.modelcontextprotocol.io/v0/servers?search=sandboxapis)
- npm: [@sandboxapis/mcp](https://www.npmjs.com/package/@sandboxapis/mcp)

## Licence

Everything in this repository is MIT licensed. See [LICENSE](LICENSE). The hosted service and the engine that generates the data set are separate and are not covered by it.

## Issues welcome here

File them here rather than emailing. Two things are especially useful:

- **A coverage request.** An endpoint or field you need that returns a coverage `404` today. Say which client you are driving and what it calls.
- **A wrong response.** Something that does not match what the real provider returns. Include the request, what came back, and what the real API returns instead.

Templates for both are in the issue form. The coverage manifest at [sandboxapis.dev/coverage](https://sandboxapis.dev/coverage) is the current answer for what is served.
