# Pinned Jira: How long did the incident take to close, and did it beat the team's 72 hour target?

Every request in this directory goes to `https://jira-v3-g12.snap.sandboxapis.dev`, a pinned snapshot
host (`jira-v3-g12`). A pinned host answers the same way on every request, so these
assertions hold in CI indefinitely. The live host rolls forward daily; the pinned one does not.

## One request first

```bash
curl -s "https://jira-v3-g12.snap.sandboxapis.dev/rest/api/3/issue/FATE-51?fields=summary,status" \
  | python3 -c "import json,sys; d = json.load(sys.stdin); print(d['key'], '|', d['fields']['summary'], '|', d['fields']['status']['name'])"
```

```
FATE-51 | Postmortem follow-up: events dropped during a rebalance | Done
```

## Run the agent script

```bash
pip install requests
python3 jira_agent.py
```

```
FATE-51 Postmortem follow-up: events dropped during a rebalance -> {'closed': True, 'hours': 44.5, 'met_target': True}
ok
```

## The same claim as a test

```bash
pip install pytest requests && pytest test_jira_agent.py
```

What each assertion pins down:

- FATE-51 belongs to project FATE, whose name is Fates.
- Its summary is the incident's own title, its issue type is Incident, and its assignee is Tiresias.
- It was created at 2026-06-17T19:51:17 and resolved at 2026-06-19T16:21:17, so the computed cycle time is 44.5 hours and the 72 hour verdict is decided rather than assumed.
- Its status is Done, which is the same terminal status the Linear host reports for the same key.

## Point the MCP server at the same host

```bash
export SANDBOXAPIS_BASE_URL_JIRA=https://jira-v3-g12.snap.sandboxapis.dev
claude mcp add sandboxapis -- npx -y @sandboxapis/mcp
```

## Writes are refused, in the provider's own shape

```bash
curl -s -i -X POST https://jira-v3-g12.snap.sandboxapis.dev/rest/api/3/issue \
  -H "Content-Type: application/json" \
  -d '{"fields":{"project":{"key":"FATE"},"summary":"opened by an agent under test"}}'
```

```
HTTP 403
x-sandboxapis-read-only: true

{"errorMessages":["This universe is read-only. See what's covered at https://sandboxapis.dev/roadmap. (You tried to POST /rest/api/3/issue.) Tell us what you needed to write: https://sandboxapis.dev/feedback"],"errors":{}}
```

Full walkthrough: https://sandboxapis.dev/docs/tutorials/agent-jira
