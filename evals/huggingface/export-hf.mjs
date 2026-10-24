#!/usr/bin/env node
// Writes data/train.jsonl for the Hugging Face dataset sandboxapis/olympus-labs-evals.
//
//     node evals/huggingface/export-hf.mjs
//
// Node 22, no dependencies. `expected` and `tool_calls` are JSON-encoded strings
// because `expected.value` is a string, an integer or a boolean depending on the
// item, and Arrow, which `datasets` loads into, needs one type per column.
import { readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { here as evals, pack, rows, writeJsonl } from "../rows.mjs";

const out = join(evals, "huggingface", "data", "train.jsonl");
const n = writeJsonl(out, rows().map((r) => ({
  id: r.id,
  provider: r.provider,
  question: r.question,
  expected: JSON.stringify(r.expected),
  request_url: r.request_url,
  request_method: r.request_method,
  tool_calls: JSON.stringify(r.tool_calls),
  difficulty: r.difficulty,
  guarded_by: r.guarded_by,
  pin_host: r.pin_host,
})));
if (n !== pack.items.length) throw new Error(`wrote ${n} rows for ${pack.items.length} items`);

// Keep the card's dataset_info split note in step with the file just written. num_bytes is
// the JSONL file's size; `datasets` reports the Arrow size instead, and only the count is checked.
const card = join(evals, "huggingface", "README.md"), bytes = statSync(out).size;
writeFileSync(card, readFileSync(card, "utf8")
  .replace(/(- name: train\n\s+num_bytes: )\d+(\n\s+num_examples: )\d+/, `$1${bytes}$2${n}`));
console.log(`${n} rows, ${bytes} bytes -> ${out} (split: train, ${pack.version})`);
