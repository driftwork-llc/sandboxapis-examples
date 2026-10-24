"""An OpenAI Agents SDK agent with one function tool, scored by the SandboxAPIs eval pack.

Task: did the fix for the incident (pull request 53 in olympus-labs/parthenon) ship,
and did someone other than its author approve it? The tool reads a pinned, read-only
GitHub replica with no key; the agent answers; the eval pack's answer key scores it.

    pip install -r requirements.txt
    python github_eval_agent.py --dry-run    # no model key: tool call + scorer only
    OPENAI_API_KEY=... python github_eval_agent.py
"""
import json, os, pathlib, sys
from typing import Optional

import requests
from agents import Agent, Runner, function_tool
from pydantic import BaseModel

GITHUB = "https://gh-2026-03-g12.snap.sandboxapis.dev"  # pinned: same answer every run
PACK = pathlib.Path(__file__).resolve().parents[2] / "evals" / "olympus-labs-g12.json"
PACK_URL = "https://sandboxapis.dev/evals/olympus-labs-g12.json"
HTTP = requests.Session()  # a free key raises 60 requests/hour to 600; none is needed
HTTP.headers["Authorization"] = "Bearer " + os.environ.get("SANDBOXAPIS_API_KEY", "any-token")


def github_get(path: str) -> str:
    """GET a GitHub REST path, for example /repos/olympus-labs/parthenon/pulls/53, and return the JSON."""
    res = HTTP.get(GITHUB + path, timeout=30)
    res.raise_for_status()
    return res.text


class Verdict(BaseModel):
    shipped: bool
    approved_by: Optional[str]


agent = Agent(
    name="Release checker",
    instructions="Answer from GitHub data only. Call github_get for the pull request and its /reviews.",
    tools=[function_tool(github_get)],
    output_type=Verdict,
    model=os.environ.get("MODEL", "gpt-4.1-mini"),
)
QUESTION = ("Did pull request 53 in olympus-labs/parthenon merge, and which user other than "
            "its author approved it? approved_by is null if nobody did.")


def dry_run():  # the same tool function, with a rule standing in for the model
    pull = json.loads(github_get("/repos/olympus-labs/parthenon/pulls/53"))
    reviews = json.loads(github_get("/repos/olympus-labs/parthenon/pulls/53/reviews"))
    others = [r["user"]["login"] for r in reviews if r["state"] == "APPROVED" and r["user"]["login"] != pull["user"]["login"]]
    return Verdict(shipped=pull["merged"], approved_by=others[0] if others else None)


def expected():  # the eval pack's answer key, from this repo or from sandboxapis.dev
    pack = json.loads(PACK.read_text()) if PACK.exists() else requests.get(PACK_URL, timeout=30).json()
    items = {i["id"]: i["expected"] for i in pack["items"]}
    return {"shipped": items["gh-pull-merged"]["equals"], "approved_by": items["gh-independent-approval"]["equals"]}


if __name__ == "__main__":
    verdict = dry_run() if "--dry-run" in sys.argv else Runner.run_sync(agent, QUESTION).final_output
    got, want = verdict.model_dump(), expected()
    print("PR #53 ->", got)
    for key, value in want.items():
        print("%s  %-12s wanted %r, got %r" % ("pass" if got.get(key) == value else "FAIL", key, value, got.get(key)))
    assert got == want, got
    print("ok")
