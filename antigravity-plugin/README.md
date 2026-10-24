# SandboxAPIs for Antigravity

An Antigravity plugin that gives the agent a read-only, API-compatible replica of GitHub, GitLab, Jira, Slack and 17 more services to test itself and your integrations against. All of them are preloaded with one simulated data set, `olympus-labs`, whose references resolve across every service, and every write is refused with the provider's own error shape, so there is nothing to seed and nothing to clean up.

The plugin is two things:

| Part | File | What it does |
|---|---|---|
| MCP server | [`mcp_config.json`](mcp_config.json) | Registers the hosted server at `https://api.sandboxapis.dev/mcp` as `sandboxapis`. Nothing to install, nothing to run locally. Ten tools; `orient` first. |
| Skill | [`skills/sandboxapis-test/SKILL.md`](skills/sandboxapis-test/SKILL.md) | Teaches the agent to call `orient` first, `check_budget` before loops, pin a snapshot for assertions, swap only a base URL to test your code, and read a write refusal or a coverage 404 as an answer rather than an error to retry. |

## Install the plugin

From the Antigravity CLI, with a clone of this repository:

```bash
git clone https://github.com/driftwork-llc/sandboxapis-examples
agy plugin install ./sandboxapis-examples/antigravity-plugin
```

Or copy this directory by hand, to `~/.gemini/config/plugins/sandboxapis` for every workspace or to `.agents/plugins/sandboxapis` in one project.

## Or add only the server

Put this in `~/.gemini/config/mcp_config.json` for every workspace, or `.agents/mcp_config.json` for one project:

```json
{
  "mcpServers": {
    "sandboxapis": {
      "serverUrl": "https://api.sandboxapis.dev/mcp"
    }
  }
}
```

Antigravity names a remote server by `serverUrl`; it does not read `url`. After editing the file, reload the server from the MCP manager (`/mcp` in the CLI, the refresh button under Settings, Customizations, Installed MCP Servers in the app), or restart Antigravity. Every config, including the npm package form, is at [sandboxapis.dev/docs/mcp#antigravity](https://sandboxapis.dev/docs/mcp#antigravity).

## Your key, or a sign-in

With nothing else the server runs on the anonymous budget of 60 requests an hour. A free key from [sandboxapis.dev/login](https://sandboxapis.dev/login) raises that to 600, either as a header:

```json
{
  "mcpServers": {
    "sandboxapis": {
      "serverUrl": "https://api.sandboxapis.dev/mcp",
      "headers": { "Authorization": "Bearer sk_live_..." }
    }
  }
}
```

or with no key in the file at all, by signing in: use `https://api.sandboxapis.dev/mcp/auth` as the `serverUrl`, then choose Authenticate next to the server in Antigravity's settings. The authorization server takes dynamic client registration, so the entry needs no `oauth` block. The plugin ships the plain address on purpose, because it works for everyone the moment it is installed.

## Marketplace

This plugin is not listed on the Antigravity Marketplace yet; this README will link the listing when it is.

## Try it

Ask the agent:

> Call orient, then check_budget. Then use get_snapshot for a pinned GitHub host and fetch the parthenon repository from it with curl. Say which host answered.

The walkthrough is at [sandboxapis.dev/docs/tutorials/antigravity](https://sandboxapis.dev/docs/tutorials/antigravity).

## Versions

Antigravity's manifest takes only `name` and `description`, so the version lives here: this plugin tracks `@sandboxapis/mcp` 0.3.19, the same server the hosted URL runs. The tool list in the skill is checked against the server's source on every build of the SandboxAPIs site, so a renamed tool cannot leave the skill telling the agent to call something that no longer exists.
