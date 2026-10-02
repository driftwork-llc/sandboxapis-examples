# Pinned GitHub: Did the fix for the incident ship, and did anyone other than its author sign it off?

Every request in this directory goes to `https://gh-2026-03-g12.snap.sandboxapis.dev`, a pinned snapshot
host (`gh-2026-03-g12`). A pinned host answers the same way on every request, so these
assertions hold in CI indefinitely. The live host rolls forward daily; the pinned one does not.

## One request first

```bash
curl -s https://gh-2026-03-g12.snap.sandboxapis.dev/repos/olympus-labs/parthenon/pulls/53 \
  | python3 -c "import json,sys; p = json.load(sys.stdin); print(p['number'], p['title'], '| merged:', p['merged'], '|', p['head']['sha'])"
```

```
53 Fix the backfill job OOMing | merged: True | 94dd1fdf3b96e96c242a869801e448edeca9fd85
```

## Run the agent script

```bash
pip install requests
python3 github_agent.py
```

```
PR #53 Fix the backfill job OOMing -> {'shipped': True, 'approved_by': 'athena'}
ok
```

## The same claim as a test

```bash
pip install pytest requests && pytest test_github_agent.py
```

What each assertion pins down:

- Pull request 53 is merged, and its author is tiresias.
- Its one review is an APPROVED from athena, who is not the author, so the agent's verdict is decided rather than assumed.
- Its head branch is hotfix/backfill-job-ooming at 94dd1fdf3b96e96c242a869801e448edeca9fd85.
- GET /branches/hotfix/backfill-job-ooming returns that same SHA, so the ref on the pull request is a real, fetchable ref.

## Point the MCP server at the same host

```bash
export SANDBOXAPIS_BASE_URL_GITHUB=https://gh-2026-03-g12.snap.sandboxapis.dev
claude mcp add sandboxapis -- npx -y @sandboxapis/mcp
```

## Writes are refused, in the provider's own shape

```bash
curl -s -i -X POST https://gh-2026-03-g12.snap.sandboxapis.dev/repos/olympus-labs/parthenon/issues \
  -H "Content-Type: application/json" \
  -d '{"title":"opened by an agent under test"}'
```

```
HTTP 403
x-sandboxapis-read-only: true

{"message":"This universe is read-only. See what's covered at https://sandboxapis.dev/roadmap. (You tried to POST /repos/olympus-labs/parthenon/issues.) Tell us what you needed to write: https://sandboxapis.dev/feedback","documentation_url":"https://sandboxapis.dev/roadmap","status":"403"}
```

Full walkthrough: https://sandboxapis.dev/docs/tutorials/agent-github
