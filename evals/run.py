#!/usr/bin/env python3
"""The SandboxAPIs answer-key eval pack, scored against pinned hosts.

    pip install requests && python3 run.py     # score the data set
    python3 run.py --agent                     # score a model: see answer()
Every host is a pinned snapshot, so this scores the same in a year. SANDBOXAPIS_API_KEY
is optional (it raises the rate limit); SANDBOXAPIS_RUN names this run in your flight trace.
"""
import json, os, sys
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = json.load(open(os.path.join(HERE, "olympus-labs-g12.json")))
HTTP = requests.Session()
HTTP.headers.update({"Authorization": "Bearer %s" % (os.environ.get("SANDBOXAPIS_API_KEY") or "any-token"), "X-SandboxAPIs-Run": os.environ.get("SANDBOXAPIS_RUN") or "eval-pack"})
CACHE, AGENT = {}, "--agent" in sys.argv

def call(tc):  # one tool call, cached: items sharing a response cost one request
    url, body = "https://%s%s" % (tc["host"], tc["path"]), tc.get("body")
    if (url, body) not in CACHE:
        res = HTTP.request(tc["method"], url, data=body, timeout=30,
                           headers={"Content-Type": "application/json"} if body else None)
        res.raise_for_status()
        CACHE[(url, body)] = res.json()
    return CACHE[(url, body)]

def at(doc, path):  # a dotted path: numbers index arrays, "" is the document
    for part in [p for p in path.split(".") if p]:
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc

def scores(expected, value):
    if "equals" in expected: return value == expected["equals"], expected["equals"]
    if "count" in expected: return len(value) == expected["count"], expected["count"]
    return expected["contains"] in value, expected["contains"]

def answer(item, responses, agent):
    """THE AGENT HOOK. With no flag this reads the answer out of the response, which
    scores the DATA SET. Put your model call under "if agent:" and the same
    expectations score the MODEL instead, which is what makes this an eval:
        if agent:
            reply = anthropic.Anthropic().messages.create(model="claude-sonnet-4-5",
                max_tokens=256, messages=[{"role": "user", "content": item["question"] + json.dumps(responses)}])
            return json.loads(reply.content[0].text)["answer"]
    """
    return at(responses[-1], item["expected"]["path"])

results = []
for item in PACK["items"]:
    try:
        value = answer(item, [call(c) for c in item["tool_calls"]], AGENT)
        ok, want = scores(item["expected"], value)
    except Exception as err:
        ok, want, value = False, item["expected"], err
    results.append(ok)
    print("%s  %-32s %-6s %s" % ("pass" if ok else "FAIL", item["id"], item["difficulty"], item["question"][:56]))
    if not ok: print("        wanted %r, got %r" % (want, value))
passed, total = results.count(True), len(results)
print("\n%d/%d  %s  (%s, %d requests)" % (passed, total, "all correct" if passed == total else "SOME WRONG", PACK["version"], len(CACHE)))
sys.exit(0 if passed == total else 1)
