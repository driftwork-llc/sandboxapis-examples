# LangGraph: a two-node agent scored by the eval pack

`github_eval_graph.py` builds a `StateGraph` with two nodes:

1. `fetch_github`, the tool node. Two GitHub REST reads with `requests`, against the pinned read-only replica `https://gh-2026-03-g12.snap.sandboxapis.dev`: the pull request and its reviews.
2. `reason`, the LLM node. Claude reads the two responses and answers `{"shipped": ..., "approved_by": ...}`.

The answer is then scored against items `gh-pull-merged` and `gh-independent-approval` from the [eval pack](../../evals).

```bash
pip install -r requirements.txt
python github_eval_graph.py --dry-run              # no model key needed
ANTHROPIC_API_KEY=sk-ant-... python github_eval_graph.py
```

The model key is read from **`ANTHROPIC_API_KEY`**. `MODEL` overrides the model. The default, `claude-sonnet-5`, is the current Sonnet at the time of writing (2026-10-08). `SANDBOXAPIS_API_KEY` is optional and raises the replica's rate limit.

`--dry-run` swaps the LLM node for a fixed rule and leaves the graph, the tool node and the scorer as they are. Captured output, 2026-10-08:

```
$ python github_eval_graph.py --dry-run
PR #53 Fix the backfill job OOMing -> {'shipped': True, 'approved_by': 'athena'}
pass  shipped      wanted True, got True
pass  approved_by  wanted 'athena', got 'athena'
ok
```
