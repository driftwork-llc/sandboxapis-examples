"""Agent task: how long did the incident take to close, and did it beat target?

Every request goes to a pinned SandboxAPIs snapshot host, so this file is a
test: the answer is the same today, in CI tonight, and in a year.
"""
import datetime
import requests

JIRA = "https://jira-v3-g12.snap.sandboxapis.dev"  # the only line that changes
KEY = "FATE-51"

http = requests.Session()
http.auth = ("you@example.com", "any-token")  # any pair is accepted


def get(path):
    res = http.get(JIRA + path, timeout=30)
    res.raise_for_status()
    return res.json()


# 1. FETCH. The same two calls your agent's Jira tools already make.
issue = get("/rest/api/3/issue/%s?fields=summary,status,issuetype,assignee,created,resolutiondate" % KEY)
project = get("/rest/api/3/project/FATE")
fields = issue["fields"]


def at(stamp):
    return datetime.datetime.strptime(stamp[:19], "%Y-%m-%dT%H:%M:%S")


# 2. REASON. The agent step: a pure function of the fetched data, so the same
# input always produces the same verdict. Swap in a model call here and the
# assertions below become an eval:
#   answer = json.loads(client.messages.create(model="claude-sonnet-4-5",
#            max_tokens=256, messages=[{"role": "user", "content": prompt}]) ...)
def cycle_time(issue_fields, target_hours=72):
    if issue_fields["resolutiondate"] is None:
        return {"closed": False}
    elapsed = at(issue_fields["resolutiondate"]) - at(issue_fields["created"])
    hours = round(elapsed.total_seconds() / 3600, 1)
    return {"closed": True, "hours": hours, "met_target": hours <= target_hours}


answer = cycle_time(fields)
print("%s %s -> %s" % (issue["key"], fields["summary"], answer))

# 3. ASSERT. Known facts of the olympus-labs data set, held still by this pin.
assert project["key"] == "FATE" and project["name"] == "Fates", project["name"]
assert fields["summary"] == "Postmortem follow-up: events dropped during a rebalance", fields["summary"]
assert fields["issuetype"]["name"] == "Incident", fields["issuetype"]["name"]
assert fields["status"]["name"] == "Done", fields["status"]["name"]
assert fields["assignee"]["displayName"] == "Tiresias", fields["assignee"]["displayName"]
assert answer == {"closed": True, "hours": 44.5, "met_target": True}, answer
print("ok")
