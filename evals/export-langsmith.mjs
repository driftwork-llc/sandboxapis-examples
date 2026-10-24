#!/usr/bin/env node
// Writes exports/langsmith.jsonl: one LangSmith example per line, in the shape
// LangSmith's dataset importer reads, {"inputs": {...}, "outputs": {...}}, plus
// the documented per-example `metadata` map.
//
//     node evals/export-langsmith.mjs [out.jsonl]
//
// Then: LangSmith > Datasets > New dataset > upload the file. Node 22, no deps.
import { join } from "node:path";
import { here, rows, writeJsonl } from "./rows.mjs";

const out = process.argv[2] ?? join(here, "exports", "langsmith.jsonl");
const n = writeJsonl(out, rows().map((r) => ({
  inputs: { question: r.question, tool_calls: r.tool_calls },
  outputs: { answer: r.expected.value, match: r.expected.match, path: r.expected.path },
  metadata: {
    id: r.id, provider: r.provider, difficulty: r.difficulty, pin_host: r.pin_host,
    request_url: r.request_url, guarded_by: r.guarded_by, pack_version: r.pack_version,
  },
})));
console.log(`${n} examples -> ${out}`);
