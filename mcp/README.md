# Distribution metadata for `@sandboxapis/mcp`

What each distribution channel needs from this repository, and what it does not.

## The server, in one line

```bash
claude mcp add sandboxapis -- npx -y @sandboxapis/mcp
```

It is an npm package that speaks MCP over **stdio** and reads the hosted
SandboxAPIs service over HTTPS. It holds no data of its own and runs no server of
its own. That one fact decides what every directory below can and cannot do with
it.

| | |
|---|---|
| npm package | `@sandboxapis/mcp` |
| Official registry name | `dev.sandboxapis/mcp` |
| Transport | stdio, over `npx` |
| Licence | MIT |
| Homepage | https://sandboxapis.dev/docs/mcp |

## `../glama.json`

Glama indexes servers from a public GitHub repository and will infer a display
name, description and category if you let it. `glama.json` at the repository root
sets them instead. Its published schema
(`https://glama.ai/mcp/schemas/server.json`, read 2026-10-02) declares exactly one
property, `maintainers`, a list of GitHub usernames allowed to maintain the
listing. Glama's own FAQ says the file can also carry the display name,
description, category, environment variables and build spec, so those keys are
accepted but are not in the published schema. Keep the file minimal and set the
name and description on the submission form, which is the path the schema
actually guarantees.

Editing `glama.json` later means re-running Glama's claim flow, so do not add keys
speculatively.

## There is no `smithery.yaml`, and that is current

Smithery's publishing documentation (`https://smithery.ai/docs/build/publish`,
read 2026-10-02) describes two inputs and neither is a repository manifest:

1. **A public HTTPS URL** speaking streamable HTTP, entered at `smithery.ai/new`
   or with `smithery mcp publish "https://your-server/mcp" -n @org/name`.
2. **An `.mcpb` bundle**, uploaded through the same flow.

Metadata comes from an automated scan of the running server, or from a static card
the server serves at `/.well-known/mcp/server-card.json` when the scan cannot
reach it. `smithery.yaml` is no longer part of that process, so shipping one here
would be a file that nothing reads.

An npm stdio package is neither of Smithery's two inputs. Listing there needs
either a hosted streamable-HTTP endpoint or an `.mcpb` bundle built from the
package. Both are real pieces of work rather than a manifest, and neither is
needed by any other channel.

## `Dockerfile`

For the Docker MCP Catalog, and for anyone who would rather run the server in a
container than through `npx`. It installs the published npm package at a pinned
version and runs it over stdio.

```bash
docker build -t sandboxapis-mcp -f mcp/Dockerfile .
docker run -i --rm sandboxapis-mcp
```

Docker's catalog build path expects the `Dockerfile` at the **root** of the
repository it is pointed at. This one is under `mcp/` because this repository is
examples first and a server distribution second. A catalog submission therefore
uses Docker's pre-built-image option, or points at a repository whose root is this
file. Nothing else in this repository depends on where it sits.

## Configuration, for any form that asks

Every variable is optional. The server works with none of them set.

| Variable | Effect |
|---|---|
| `SANDBOXAPIS_API_KEY` | Lifts the anonymous limit of 60 requests an hour to 600. Free at https://sandboxapis.dev/login |
| `SANDBOXAPIS_BASE_URL_GITHUB` and the same for `_GITLAB`, `_BITBUCKET`, `_ADO`, `_JIRA`, `_LINEAR`, `_SLACK`, `_TEAMS`, `_SENTRY`, `_PAGERDUTY`, `_STATUSPAGE`, `_SALESFORCE`, `_HUBSPOT`, `_ZENDESK`, `_CIRCLECI`, `_BUILDKITE`, `_ANTHROPIC`, `_OPENAI`, `_CHATGPT`, `_CURSOR`, `_DEVIN` | Point one surface at a pinned snapshot host, so assertions against it do not drift |

No secrets, no OAuth, no credentials of any kind. A directory's security scan will
find nothing to flag, because there is nothing to steal: every request the server
makes is a read of a public, simulated data set.
