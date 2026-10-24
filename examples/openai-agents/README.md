# OpenAI Agents SDK: one function tool, scored by the eval pack

`github_eval_agent.py` defines one `Agent` with one function tool, `github_get`, which calls the pinned read-only GitHub replica `https://gh-2026-03-g12.snap.sandboxapis.dev` with `requests`. The agent's typed output, `Verdict(shipped, approved_by)`, is scored against items `gh-pull-merged` and `gh-independent-approval` from the [eval pack](../../evals).

```bash
pip install -r requirements.txt
python github_eval_agent.py --dry-run              # no model key needed
OPENAI_API_KEY=sk-... python github_eval_agent.py
```

The model key is read from **`OPENAI_API_KEY`**, which the Agents SDK reads by default. `MODEL` overrides the model. The default, `gpt-4.1-mini`, was chosen at the time of writing (2026-10-08); set `MODEL` to use a newer one. `SANDBOXAPIS_API_KEY` is optional and raises the replica's rate limit.

`--dry-run` calls the same `github_get` function the agent's tool wraps, puts a fixed rule where the model would be, and runs the scorer. Captured output, 2026-10-08:

```
$ python github_eval_agent.py --dry-run
PR #53 -> {'shipped': True, 'approved_by': 'athena'}
pass  shipped      wanted True, got True
pass  approved_by  wanted 'athena', got 'athena'
ok
```
