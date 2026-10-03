# SandboxAPIs for Cursor

A Cursor plugin that gives Cursor's agent a read-only, API-compatible replica of GitHub, GitLab, Jira, Slack and 17 more services to test itself against. All of them are preloaded with one simulated data set, `olympus-labs`, whose references resolve across every service, and every write is refused with the provider's own error shape, so there is nothing to seed and nothing to clean up.

The plugin is three things:

| Part | File | What it does |
|---|---|---|
| MCP server | [`mcp.json`](mcp.json) | Registers `@sandboxapis/mcp` as a stdio server named `sandboxapis`. Ten tools; `orient` first. |
| Rule | [`rules/sandboxapis.mdc`](rules/sandboxapis.mdc) | Teaches the agent to call `orient` first, `check_budget` before loops, pin a snapshot for assertions, and read a write refusal or a coverage 404 as an answer rather than an error to retry. |
| Skill | [`skills/sandboxapis-eval/SKILL.md`](skills/sandboxapis-eval/SKILL.md) | Runs the answer-key eval pack from this repository and reads the score. |

## Install the server in one click

[Add to Cursor](https://sandboxapis.dev/docs/mcp#cursor)

GitHub does not render `cursor://` links, so the button above opens the install page on sandboxapis.dev, which has the one-click link. Copy this into the address bar if the button does not open Cursor:

```
cursor://anysphere.cursor-deeplink/mcp/install?name=sandboxapis&config=eyJjb21tYW5kIjoibnB4IiwiYXJncyI6WyIteSIsIkBzYW5kYm94YXBpcy9tY3AiXX0=
```

The link installs the MCP server with no key. It carries this configuration and nothing else:

```json
{ "command": "npx", "args": ["-y", "@sandboxapis/mcp"] }
```

Cursor shows you the config and asks before it installs anything. With no key the server runs on the anonymous budget of 60 requests an hour; a free key from [sandboxapis.dev/login](https://sandboxapis.dev/login) raises that to 600. Add it to the server entry in Cursor Settings > MCP as an `env` value named `SANDBOXAPIS_API_KEY`. The link deliberately carries no key: a link cannot hold your key, and a placeholder would install a broken server for anyone who clicks it and never edits it.

## Install the whole plugin, rule and skill included

The install link registers the server only. The rule and the skill arrive one of two ways:

**As a local plugin.** Copy this directory to `~/.cursor/plugins/local/sandboxapis` and restart Cursor:

```bash
git clone https://github.com/driftwork-llc/sandboxapis-examples
mkdir -p ~/.cursor/plugins/local
cp -r sandboxapis-examples/cursor-plugin ~/.cursor/plugins/local/sandboxapis
```

**By opening this repository.** The same rule is checked in at [`.cursor/rules/sandboxapis.mdc`](../.cursor/rules/sandboxapis.mdc) at the repository root, so opening `sandboxapis-examples` in Cursor applies it with no plugin install. Add the server with the link above or with `.cursor/mcp.json`.

**Manually.** Put the contents of [`mcp.json`](mcp.json) in `.cursor/mcp.json` for one project or `~/.cursor/mcp.json` for every project, and copy `rules/sandboxapis.mdc` into `.cursor/rules/`.

## Marketplace

Cursor reviews every plugin before listing it and requires it to be open source, which this is (MIT, see [LICENSE](../LICENSE)). This plugin is not listed on the Cursor marketplace yet; this README will link the listing when it is.

## Try it

Open this repository in Cursor and ask the agent:

> Call orient, then find the incident the agent tutorials read: the Jira issue, the pull request that fixed it, and whether anyone other than its author approved it. Use the pinned -g12 hosts.

Then ask it to run the eval pack:

> Use the sandboxapis-eval skill to score the data set.

The walkthrough with expected answers is at [sandboxapis.dev/docs/tutorials/cursor](https://sandboxapis.dev/docs/tutorials/cursor).

## Versions

`version` in [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) tracks the npm package `@sandboxapis/mcp`. The tool list in the rule is checked against the server's source on every build of the SandboxAPIs site, so a renamed tool cannot leave the rule telling the agent to call something that no longer exists.
