---
license: mit
language:
- en
pretty_name: olympus-labs answer-key evals
size_categories:
- n<1K
task_categories:
- question-answering
- text-generation
tags:
- mcp
- agent-evaluation
- api
- deterministic
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.jsonl
dataset_info:
  features:
  - name: id
    dtype: string
  - name: provider
    dtype: string
  - name: question
    dtype: string
  - name: expected
    dtype: string
  - name: request_url
    dtype: string
  - name: request_method
    dtype: string
  - name: tool_calls
    dtype: string
  - name: difficulty
    dtype: string
  - name: guarded_by
    dtype: string
  - name: pin_host
    dtype: string
  splits:
  - name: train
    num_bytes: 42864
    num_examples: 53
---

# olympus-labs answer-key evals

Repository id: `sandboxapis/olympus-labs-evals`.

## Dataset Summary

53 questions an agent can answer by calling real API shapes: GitHub, GitLab, Jira, Linear and Slack. Each row carries the question, the request that answers it, and the value the answer must be. The requests go to [SandboxAPIs](https://sandboxapis.dev) pinned snapshot hosts, which are read-only replicas of those APIs preloaded with one simulated engineering company, `olympus-labs`. A pinned host returns the same bytes on every request, so a row's expected answer is as true next year as it is today.

All 53 rows follow one incident across the five services: the bug report in the tracker, the pull request that fixed it, its review, the branch it merged from, and the chat thread where it was called resolved. The identifiers agree from one service to the next, so some rows can only be answered by reading two responses and joining them.

This is version `olympus-labs-g12-2026-09`: generation `g12` of the data set, compiled from template `hello-20`, artifact sha256 `c27f762cc1d2656fca27e2a3ffc8c7742e41bca227cc7d36efc4cf0a8bf31d39`.

```python
from datasets import load_dataset
import json

rows = load_dataset("sandboxapis/olympus-labs-evals", split="train")
row = rows[0]
expected = json.loads(row["expected"])  # {"path": "number", "match": "equals", "value": 53}
```

## Supported Tasks

- **Tool-using agent evaluation.** Give the agent `question` and an HTTP tool (or the [SandboxAPIs MCP server](https://www.npmjs.com/package/@sandboxapis/mcp)), let it choose its own calls, and score its final answer against `expected`. The `tool_calls` column is one correct route to the answer, not the only one.
- **Answer extraction from API responses.** Fetch `tool_calls` yourself, hand the responses to the model with `question`, and score what it reads out of them. This isolates reading from planning.

Scoring is exact and needs no judge model. `expected.match` is one of:

| match | the answer is correct when |
| --- | --- |
| `equals` | it equals `expected.value` (a string, an integer or a boolean) |
| `count` | it is a list whose length is `expected.value` |
| `contains` | it is a string that contains `expected.value` |

`expected.path` is where the value sits in the response to `request_url`, as a dotted path in which numbers index arrays and `""` is the whole document.

`difficulty` grades the row: `read` is one field off one response, `join` means two responses have to agree and the second call is only reachable once the first has been read, and `reason` means the answer is computed from what came back rather than copied out of it.

Two zero-dependency harnesses that score either the data set or your model, `run.mjs` and `run.py`, are in [driftwork-llc/sandboxapis-examples](https://github.com/driftwork-llc/sandboxapis-examples/tree/main/evals).

## Dataset Structure

### Data Fields

| field | type | what it holds |
| --- | --- | --- |
| `id` | string | Stable row id, for example `gh-pull-number`. Never reused for a different question. |
| `provider` | string | `github`, `gitlab`, `jira`, `linear` or `slack`. |
| `question` | string | The question, in plain English, as an agent would be asked it. |
| `expected` | string | JSON: `{"path", "match", "value"}`, described above. A string because `value` changes type between rows. |
| `request_url` | string | The request whose response holds the answer. |
| `request_method` | string | `GET`, or `POST` for the Linear GraphQL rows. |
| `tool_calls` | string | JSON: every request the answer needs, in order, as `{"method", "url", "body"}`. `body` is the GraphQL document on Linear rows and `null` elsewhere. |
| `difficulty` | string | `read`, `join` or `reason`. |
| `guarded_by` | string | The test in the SandboxAPIs engine repository that fails if this answer changes. That repository is private; the citation shows that each answer is held by a test rather than typed from memory. |
| `pin_host` | string | The pinned snapshot host that `request_url` points at. |

### Example row

```json
{
  "id": "gh-pull-number",
  "provider": "github",
  "question": "Which pull request number in olympus-labs/parthenon carried the fix for the dropped-events incident?",
  "expected": "{\"path\":\"number\",\"match\":\"equals\",\"value\":53}",
  "request_url": "https://gh-2026-03-g12.snap.sandboxapis.dev/repos/olympus-labs/parthenon/pulls/53",
  "request_method": "GET",
  "tool_calls": "[{\"method\":\"GET\",\"url\":\"https://gh-2026-03-g12.snap.sandboxapis.dev/repos/olympus-labs/parthenon/pulls/53\",\"body\":null}]",
  "difficulty": "read",
  "guarded_by": "packages/conformance/src/parity/pinned-cross-category.test.ts#closed_by_pull resolves to the closing PR on the GITHUB host, via the tracker's branchName",
  "pin_host": "gh-2026-03-g12.snap.sandboxapis.dev"
}
```

## Data Splits

One split, `train`, with all 53 rows. There is no held-out split: every answer can be read from a public host, so a held-out split would not stay held out. Treat the set as an evaluation set and do not train on it.

| provider | rows | pinned host |
| --- | --- | --- |
| github | 12 | `gh-2026-03-g12.snap.sandboxapis.dev` |
| jira | 11 | `jira-v3-g12.snap.sandboxapis.dev` |
| slack | 14 | `slack-2026-08-g12.snap.sandboxapis.dev` |
| gitlab | 6 | `gl-v4-g12.snap.sandboxapis.dev` |
| linear | 10 | `linear-2026-08-g12.snap.sandboxapis.dev` |

## Dataset Creation

### Source data

The data is generated, not recorded. A deterministic simulation runs a fictional company's engineers over 90 days of simulated time, and a compiler renders the result in each provider's API shape. Nothing in it came from a real account, a real repository or a real person.

There is one fictional company, `olympus-labs`, and its people and projects carry Greek-mythology names (`athena`, `tiresias`, `parthenon`) so that nobody mistakes a row for a real organisation's data.

### Annotations

Each expected value was read off the pinned host and is held there by a test in the engine repository, named in `guarded_by`. A row nobody can cite does not go in the set.

## Considerations for Using the Data

- **Read-only hosts.** The pinned hosts accept reads only. A write returns the provider's own error status and body with a plain explanation, so an agent under test cannot change the answers for anyone else.
- **Rate limit.** Anonymous callers get 60 requests an hour per IP. Scoring every row with the reference `tool_calls` takes 12 requests, because rows share responses. A free key from [sandboxapis.dev/login](https://sandboxapis.dev/login) raises the limit to 600 an hour; send it as `Authorization: Bearer <key>`.
- **Every answer is checkable live.** Fetch `request_url` and read `expected.path` out of it. If the value differs, the row or the host is wrong, and we want to hear about it at [sandboxapis.dev/feedback](https://sandboxapis.dev/feedback).
- **Pinned, not live.** The `-g12` hosts are frozen snapshots. SandboxAPIs also serves live hosts that roll forward daily; do not point this set at them, because their answers move.
- **Contamination.** The rows and their answers are public. A model may have seen them, so report a score on this set alongside your own held-back tasks rather than instead of them.

## Licensing Information

MIT. The hosted service and the engine that generates the data set are separate and are not covered by this licence.

## Citation Information

```bibtex
@misc{sandboxapis_olympus_labs_evals_2026,
  author       = {{SandboxAPIs team, Driftwork LLC}},
  title        = {olympus-labs answer-key evals},
  year         = {2026},
  version      = {olympus-labs-g12-2026-09},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/sandboxapis/olympus-labs-evals}}
}
```
