---
name: sandboxapis-test
description: Tests an agent or an integration against SandboxAPIs, read-only API-compatible replicas of GitHub, GitLab, Jira, Slack and other developer and SaaS APIs that share one simulated data set. Use when the user asks to test, evaluate or debug code or an agent that reads one of those services, calls a sandboxapis.dev host, or uses any of the sandboxapis tools.
---

# Test against SandboxAPIs replicas

The `sandboxapis` MCP server answers through API-compatible, read-only replicas of GitHub, GitLab, Jira, Slack and other developer and SaaS APIs. Underneath all of them is one simulated data set, `olympus-labs`, so a pull request on the GitHub host, the issue it closes on the Jira host and the thread about it on the Slack host are the same incident. Use it to test an agent or an integration against data that never moves and can never be damaged.

## Steps

1. Call `orient` first, before any other tool or any HTTP request. It returns the base URLs, the data set and its teams, ready-to-run entry points, how to pin a snapshot, where the coverage manifest lives, and an `access` block saying whether a key is set and how many requests are left this hour. Do not read docs or guess hostnames; `orient` is cheaper and correct.
2. Call `check_budget` before any loop of more than a few requests. It costs nothing against the budget and reads the real window: limit, remaining, and when it resets. If `remaining` is small, do fewer requests or ask the user for a key rather than running into a refusal.
3. For anything that will be asserted in a test or an eval, ask `get_snapshot` for a pinned host and send the requests there. The live hosts roll their data forward daily; a pinned host never changes under the test. When the user runs the npm package instead of the hosted URL, the matching `SANDBOXAPIS_BASE_URL_<PROVIDER>` variable in the server's `env` points the tools themselves at the pin (for example `SANDBOXAPIS_BASE_URL_GITHUB` set to the GitHub host `get_snapshot` returned).
4. To test the user's own code, change only its base URL to the host `orient` or `get_snapshot` gave, and leave its client library, auth and request code as they are. Run the code, then compare what it printed with what the matching tool returns for the same request.
5. Report what was asserted, which host answered it, and whether that host is pinned or live.

## Budget

Anonymous callers get 60 requests an hour, shared by every caller on the same address across every host. A free key from https://sandboxapis.dev/login raises that to 600 requests an hour on the user's own account. On the hosted URL the key is an `Authorization: Bearer` header in the server entry's `headers`, or the user signs in instead; with the npm package it is the `SANDBOXAPIS_API_KEY` environment variable. A refusal for budget keeps the provider's own error body and adds an `upgrade` field with `tier`, `url` and `retryAfterSeconds`; read the field, do not parse the sentence, and do not retry in a tight loop.

## What a response means

- Every host is read-only. A write (POST, PUT, PATCH, DELETE, or a GraphQL mutation) returns the provider's own error status and body with a plain message saying the data set is read-only and naming what was attempted. That is the designed answer. Do not retry it, do not try a different endpoint to achieve the same write, and do not report it as an outage. The one exception is the scratch layer: a key the user has turned it on for may create, edit, close and comment on GitHub issues, comment on and transition Jira issues, and post messages into existing Slack channels and threads; those writes last 24 hours and are visible only to that key. Do not assume it is on.
- A `404` carrying an `X-SandboxAPIs-Coverage` header means the endpoint is outside published coverage. It is a real answer, not a missing row and not a transient error. Do not retry it; report it, and point the user at https://sandboxapis.dev/coverage if they need that endpoint.
- A GraphQL field outside coverage returns an explicit error in `errors`, never a silent `null`. Treat it the same way.
- Values are never placeholders. If a field is present it is a real value from the data set, and ids are in the provider's own form, so a SHA, an issue key or a login from one tool can be passed straight to another tool or to a `curl`.

## The tools

- `orient`: start here. Base URLs, the data set and its teams, entry points, pinning, coverage, and the `access` block.
- `check_budget`: the real hourly window, free to call. Call it before loops.
- `list_repositories`: repositories on a host, provider-shaped, with provider-form ids.
- `get_repository`: one repository by owner and name.
- `list_pull_requests`: pull requests or merge requests on a repository.
- `get_pull_request`: one pull request or merge request, with its reviews or approvals.
- `list_issues`: issues. REST on the git hosts and Jira, GraphQL on Linear.
- `get_user`: a user by login or username; every author and reviewer in the data set resolves here.
- `search_commits_by_author`: commits by author, with SHAs that match across the git hosts.
- `get_snapshot`: the pinned hostname to use when a result must be the same on every run.

Results come from the same public API a person would point a client at, so anything learned through a tool transfers directly to an HTTP call against the same base URL.
