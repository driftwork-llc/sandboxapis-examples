"""Agent task: is the incident thread resolved, who closed it, who was in it?

Every request goes to a pinned SandboxAPIs snapshot host, so this file is a
test: the answer is the same today, in CI tonight, and in a year.
"""
import requests

SLACK = "https://slack-2026-08-g12.snap.sandboxapis.dev"  # the only line that changes
CHANNEL = "CF1UPUMGC8Q"  # #incident-bridge

http = requests.Session()
http.headers["Authorization"] = "Bearer xoxb-any-token"  # any token is accepted


def call(method, **params):
    res = http.get("%s/api/%s" % (SLACK, method), params=params, timeout=30)
    body = res.json()
    if not body.get("ok"):  # Slack reports failure in the body, not the status
        raise RuntimeError("%s: %s" % (method, body.get("error")))
    return body


# 1. FETCH. The same three calls your agent's Slack tools already make.
opener = call("conversations.history", channel=CHANNEL, limit=1)["messages"][0]
thread = call("conversations.replies", channel=CHANNEL, ts=opener["ts"], limit=999)["messages"]
names = {u["id"]: u["name"] for u in call("users.list", limit=200)["members"]}


# 2. REASON. The agent step: a pure function of the fetched data, so the same
# input always produces the same verdict. Swap in a model call here and the
# assertions below become an eval:
#   answer = json.loads(client.messages.create(model="claude-sonnet-4-5",
#            max_tokens=256, messages=[{"role": "user", "content": prompt}]) ...)
def triage(messages):
    closing = [m for m in messages if "all clear" in m["text"].lower()]
    return {
        "resolved": len(closing) > 0,
        "closed_by": names[closing[-1]["user"]] if closing else None,
        "people": len({m["user"] for m in messages}),
    }


answer = triage(thread)
print("%d messages in #incident-bridge -> %s" % (len(thread), answer))

# 3. ASSERT. Known facts of the olympus-labs data set, held still by this pin.
assert names[opener["user"]] == "cassandra", names[opener["user"]]
assert opener["reply_count"] == 11, opener["reply_count"]
assert len(thread) == opener["reply_count"] + 1, len(thread)
# The parent leads and the burst runs forward: nobody replies before the thread
# was opened.
assert thread == sorted(thread, key=lambda m: float(m["ts"]))
assert answer == {"resolved": True, "closed_by": "tiresias", "people": 6}, answer
print("ok")
