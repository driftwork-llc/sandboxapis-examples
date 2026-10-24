"""A two-node LangGraph agent, scored by the SandboxAPIs answer-key eval pack.

Task: did the fix for the incident (pull request 53 in olympus-labs/parthenon) ship,
and did someone other than its author approve it? The tool node reads a pinned,
read-only GitHub replica with no key; the LLM node answers; the eval pack scores it.

    pip install -r requirements.txt
    python github_eval_graph.py --dry-run    # no model key: tool call + scorer only
    ANTHROPIC_API_KEY=... python github_eval_graph.py
"""
import json, os, pathlib, sys
from typing import TypedDict

import requests
from langgraph.graph import END, START, StateGraph

GITHUB = "https://gh-2026-03-g12.snap.sandboxapis.dev"  # pinned: same answer every run
REPO = "olympus-labs/parthenon"
PACK = pathlib.Path(__file__).resolve().parents[2] / "evals" / "olympus-labs-g12.json"
PACK_URL = "https://sandboxapis.dev/evals/olympus-labs-g12.json"
HTTP = requests.Session()  # a free key raises 60 requests/hour to 600; none is needed
HTTP.headers["Authorization"] = "Bearer " + os.environ.get("SANDBOXAPIS_API_KEY", "any-token")
QUESTION = ("Did pull request 53 ship, and who other than its author approved it? Reply with only "
            'JSON: {"shipped": true or false, "approved_by": "<login>" or null}.')


class State(TypedDict, total=False):
    pull: dict
    reviews: list
    answer: dict


def get(path):
    res = HTTP.get(GITHUB + path, timeout=30)
    res.raise_for_status()
    return res.json()


def fetch_github(state: State) -> State:  # the tool node: two plain REST reads
    return {"pull": get(f"/repos/{REPO}/pulls/53"), "reviews": get(f"/repos/{REPO}/pulls/53/reviews")}


def rule(pull, reviews):  # what --dry-run uses in place of the model
    others = [r["user"]["login"] for r in reviews if r["state"] == "APPROVED" and r["user"]["login"] != pull["user"]["login"]]
    return {"shipped": pull["merged"], "approved_by": others[0] if others else None}


def reason(state: State) -> State:  # the LLM node
    if "--dry-run" in sys.argv:
        return {"answer": rule(state["pull"], state["reviews"])}
    from langchain_anthropic import ChatAnthropic
    model = ChatAnthropic(model=os.environ.get("MODEL", "claude-sonnet-5"), max_tokens=256)
    facts = json.dumps({"pull": {k: state["pull"][k] for k in ("number", "title", "merged", "user")},
                        "reviews": [{"user": r["user"], "state": r["state"]} for r in state["reviews"]]})
    text = model.invoke(QUESTION + "\n\n" + facts).content
    return {"answer": json.loads(text[text.index("{"): text.rindex("}") + 1])}


def expected():  # the eval pack's answer key, from this repo or from sandboxapis.dev
    pack = json.loads(PACK.read_text()) if PACK.exists() else requests.get(PACK_URL, timeout=30).json()
    items = {i["id"]: i["expected"] for i in pack["items"]}
    return {"shipped": items["gh-pull-merged"]["equals"], "approved_by": items["gh-independent-approval"]["equals"]}


graph = StateGraph(State)
graph.add_node("fetch_github", fetch_github)
graph.add_node("reason", reason)
graph.add_edge(START, "fetch_github")
graph.add_edge("fetch_github", "reason")
graph.add_edge("reason", END)

if __name__ == "__main__":
    result = graph.compile().invoke({})
    want = expected()
    print("PR #%d %s -> %s" % (result["pull"]["number"], result["pull"]["title"], result["answer"]))
    for key, value in want.items():
        print("%s  %-12s wanted %r, got %r" % ("pass" if result["answer"].get(key) == value else "FAIL", key, value, result["answer"].get(key)))
    assert result["answer"] == want, result["answer"]
    print("ok")
