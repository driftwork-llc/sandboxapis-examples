# Pinned Slack: Is the incident thread resolved, who called it, and how many people were in it?

Every request in this directory goes to `https://slack-2026-08-g12.snap.sandboxapis.dev`, a pinned snapshot
host (`slack-2026-08-g12`). A pinned host answers the same way on every request, so these
assertions hold in CI indefinitely. The live host rolls forward daily; the pinned one does not.

## One request first

```bash
curl -s "https://slack-2026-08-g12.snap.sandboxapis.dev/api/conversations.history?channel=CF1UPUMGC8Q&limit=1" \
  | python3 -c "import json,sys; m = json.load(sys.stdin)['messages'][0]; print(m['ts'], '|', m['reply_count'], 'replies |', m['text'])"
```

```
1781726237.230977 | 11 replies | we have a live one: events dropped during a rebalance. filed the incident issue, details there.
```

## Run the agent script

```bash
pip install requests
python3 slack_agent.py
```

```
12 messages in #incident-bridge -> {'resolved': True, 'closed_by': 'tiresias', 'people': 6}
ok
```

## The same claim as a test

```bash
pip install pytest requests && pytest test_slack_agent.py
```

What each assertion pins down:

- The thread in #incident-bridge was opened by cassandra and carries 11 replies.
- conversations.replies returns 12 messages: the parent leads, then the burst.
- Their timestamps run forward, so nobody replies before the thread was opened.
- Six people speak in it, and the last word is tiresias calling the all clear, so the agent's verdict is decided rather than assumed.

## Point the MCP server at the same host

```bash
export SANDBOXAPIS_BASE_URL_SLACK=https://slack-2026-08-g12.snap.sandboxapis.dev
claude mcp add sandboxapis -- npx -y @sandboxapis/mcp
```

## Writes are refused, in the provider's own shape

```bash
curl -s -i -X POST https://slack-2026-08-g12.snap.sandboxapis.dev/api/chat.postMessage \
  -H "Content-Type: application/json" \
  -d '{"channel":"CF1UPUMGC8Q","text":"posted by an agent under test"}'
```

```
HTTP 200
x-sandboxapis-read-only: true
x-sandboxapis-reason: This universe is read-only. See what's covered at https://sandboxapis.dev/roadmap. (You tried to call chat.postMessage.) Tell us what you needed to write: https://sandboxapis.dev/feedback

{"ok":false,"error":"read_only_universe","req_method":"chat.postMessage"}
```

Full walkthrough: https://sandboxapis.dev/docs/tutorials/agent-slack
