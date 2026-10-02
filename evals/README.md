# The olympus-labs answer-key eval pack

53 known facts about the olympus-labs data set, across 5 services, with the
request that answers each one and the value it must come back with. Point an
agent at these hosts and the same question returns the same answer every run,
because every host below is a pinned snapshot rather than a live account.

Version `olympus-labs-g12-2026-09` reads generation `g12` of the data set,
compiled from template `hello-20`. Every one of those hosts serves the
artifact `c27f762cc1d2656fca27e2a3ffc8c7742e41bca227cc7d36efc4cf0a8bf31d39`,
and `packages/compiler/src/snapshot.test.ts` asserts that today's compiler still
reproduces exactly those bytes. That is what "the same answer every run" rests on.

## Run it

    curl -O https://sandboxapis.dev/evals/olympus-labs-g12.json
    curl -O https://sandboxapis.dev/evals/run.py
    pip install requests && python3 run.py

Or with Node 22 and nothing else:

    curl -O https://sandboxapis.dev/evals/run.mjs && node run.mjs

A full run makes 12 requests, because items that read the same response share
it. Anonymous access is 60 requests an hour, so it fits without a key; set
`SANDBOXAPIS_API_KEY` and it rides your own budget instead.

## Put a model in it

Both harnesses read the answer straight out of the response, which scores the
DATA SET and proves the pack is correct. The `answer()` function in each is the
one place to change: it already receives the question, the fetched responses and
an `agent` flag, and the commented model call inside it shows the shape. Put
yours there, run with `--agent`, and the same expectations now score your agent
instead of the data set.

## What is in it

| service | items | host |
| --- | --- | --- |
| github | 12 | `gh-2026-03-g12.snap.sandboxapis.dev` |
| jira | 11 | `jira-v3-g12.snap.sandboxapis.dev` |
| slack | 14 | `slack-2026-08-g12.snap.sandboxapis.dev` |
| gitlab | 6 | `gl-v4-g12.snap.sandboxapis.dev` |
| linear | 10 | `linear-2026-08-g12.snap.sandboxapis.dev` |

Each item carries a `difficulty`: `read` is one field off one response, `join`
means two responses have to agree and the second call is only reachable once the
first has been read, and `reason` means the answer is computed from what came
back rather than copied out of it.

Each item also carries `guarded_by`, naming the test in this repository that
would fail if the answer changed. An item nobody can cite does not go in the
pack.

## More items

The pack covers one incident told by 5 services. Ask for more, or for a
different corner of the data set, at https://sandboxapis.dev/feedback.
