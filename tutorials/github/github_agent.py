"""Agent task: did the fix for the incident ship, and did anyone sign it off?

Every request goes to a pinned SandboxAPIs snapshot host, so this file is a
test: the answer is the same today, in CI tonight, and in a year.
"""
import requests

GITHUB = "https://gh-2026-03-g12.snap.sandboxapis.dev"  # the only line that changes
REPO = "olympus-labs/parthenon"

http = requests.Session()
http.headers["Authorization"] = "token any-token"  # any token is accepted


def get(path):
    res = http.get(GITHUB + path, timeout=30)
    res.raise_for_status()
    return res.json()


# 1. FETCH. The same three calls your agent's GitHub tools already make.
pull = get("/repos/%s/pulls/53" % REPO)
reviews = get("/repos/%s/pulls/53/reviews" % REPO)
branch = get("/repos/%s/branches/%s" % (REPO, pull["head"]["ref"]))


# 2. REASON. The agent step: a pure function of the fetched data, so the same
# input always produces the same verdict. Swap in a model call here and the
# assertions below become an eval:
#   answer = json.loads(client.messages.create(model="claude-sonnet-4-5",
#            max_tokens=256, messages=[{"role": "user", "content": prompt}]) ...)
def verdict(pr, pr_reviews):
    author = pr["user"]["login"]
    approvals = [r for r in pr_reviews if r["state"] == "APPROVED" and r["user"]["login"] != author]
    if not pr["merged"]:
        return {"shipped": False, "reason": "closed without merging"}
    if not approvals:
        return {"shipped": True, "reason": "merged with no independent approval"}
    return {"shipped": True, "approved_by": approvals[0]["user"]["login"]}


answer = verdict(pull, reviews)
print("PR #%d %s -> %s" % (pull["number"], pull["title"], answer))

# 3. ASSERT. Known facts of the olympus-labs data set, held still by this pin.
assert pull["user"]["login"] == "tiresias", pull["user"]["login"]
assert answer == {"shipped": True, "approved_by": "athena"}, answer
assert pull["head"]["ref"] == "hotfix/backfill-job-ooming", pull["head"]["ref"]
assert pull["head"]["sha"] == "94dd1fdf3b96e96c242a869801e448edeca9fd85", pull["head"]["sha"]
# The branch is a real, fetchable ref at that exact commit, not a string on the
# pull request. Every reference in this data set resolves like this.
assert branch["commit"]["sha"] == pull["head"]["sha"], branch["commit"]["sha"]
print("ok")
