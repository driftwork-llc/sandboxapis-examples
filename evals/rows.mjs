// One row per eval item, with field names that do not change between releases.
// export-hf.mjs, export-langsmith.mjs and export-braintrust.mjs all read this,
// so the three files always describe the same 53 items.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const here = dirname(fileURLToPath(import.meta.url));
export const pack = JSON.parse(readFileSync(join(here, "olympus-labs-g12.json"), "utf8"));

// The kind of check: "equals" (the value at path), "count" (the length of the
// array at path) or "contains" (a substring of the value at path).
const matchOf = (expected) => ["equals", "count", "contains"].find((k) => k in expected);

export function rows() {
  return pack.items.map((item) => {
    const last = item.tool_calls.at(-1); // the response expected.path reads
    const match = matchOf(item.expected);
    return {
      id: item.id,
      provider: item.service,
      question: item.question,
      expected: { path: item.expected.path, match, value: item.expected[match] },
      request_url: `https://${last.host}${last.path}`,
      request_method: last.method,
      tool_calls: item.tool_calls.map((c) => ({ method: c.method, url: `https://${c.host}${c.path}`, body: c.body ?? null })),
      difficulty: item.difficulty,
      guarded_by: item.guarded_by,
      pin_host: last.host,
      pack_version: pack.version,
    };
  });
}

// Writes one JSON object per line and returns the row count.
export function writeJsonl(path, objects) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, objects.map((o) => JSON.stringify(o)).join("\n") + "\n");
  return objects.length;
}
