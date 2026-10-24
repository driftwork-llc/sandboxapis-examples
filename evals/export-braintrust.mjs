#!/usr/bin/env node
// Writes exports/braintrust.jsonl: one Braintrust dataset record per line, with
// the top-level fields Braintrust accepts: id, input, expected, metadata, tags.
//
//     node evals/export-braintrust.mjs [out.jsonl]
//
// Then: bt datasets create olympus-labs-evals --file exports/braintrust.jsonl
// A record keeps its pack id, so re-importing updates rows instead of duplicating them.
import { join } from "node:path";
import { here, rows, writeJsonl } from "./rows.mjs";

const out = process.argv[2] ?? join(here, "exports", "braintrust.jsonl");
const n = writeJsonl(out, rows().map((r) => ({
  id: r.id,
  input: { question: r.question, tool_calls: r.tool_calls },
  expected: { answer: r.expected.value, match: r.expected.match, path: r.expected.path },
  metadata: {
    provider: r.provider, difficulty: r.difficulty, pin_host: r.pin_host,
    request_url: r.request_url, guarded_by: r.guarded_by, pack_version: r.pack_version,
  },
  tags: [r.provider, r.difficulty],
})));
console.log(`${n} records -> ${out}`);
