#!/usr/bin/env node
// The SandboxAPIs answer-key eval pack, scored against pinned hosts.
//
//     node run.mjs             // score the data set
//     node run.mjs --agent     // score a model: see answer() below
// Node 22, no deps. Hosts are pinned snapshots, so this scores the same in a year. SANDBOXAPIS_RUN names the run in your flight trace.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const pack = JSON.parse(readFileSync(join(here, "olympus-labs-g12.json"), "utf8"));
const auth = `Bearer ${process.env.SANDBOXAPIS_API_KEY ?? "any-token"}`, run = process.env.SANDBOXAPIS_RUN ?? "eval-pack";
const cache = new Map();
const agent = process.argv.includes("--agent");
// One tool call, cached: items sharing a response cost one request.
async function call({ method, host, path, body }) {
  const url = `https://${host}${path}`;
  const key = `${url} ${body ?? ""}`;
  if (!cache.has(key)) {
    const headers = { authorization: auth, "x-sandboxapis-run": run, ...(body ? { "content-type": "application/json" } : {}) };
    const res = await fetch(url, { method, headers, body });
    if (!res.ok) throw new Error(`${res.status} ${method} ${url}`);
    cache.set(key, await res.json());
  }
  return cache.get(key);
}

// A dotted path: numbers index arrays, "" is the whole document.
const at = (doc, path) => path.split(".").filter(Boolean).reduce((d, part) => d[part], doc);

function scores(expected, value) {
  if ("equals" in expected) return [JSON.stringify(value) === JSON.stringify(expected.equals), expected.equals];
  if ("count" in expected) return [value?.length === expected.count, expected.count];
  return [String(value).includes(expected.contains), expected.contains];
}

// THE AGENT HOOK. With no flag this reads the answer out of the response, which scores the DATA
// SET. Put your model call under "if (agent)" and the same expectations score the MODEL instead:
//   if (agent) { const reply = await new Anthropic().messages.create({ model: "claude-sonnet-4-5",
//     max_tokens: 256, messages: [{ role: "user", content: item.question + JSON.stringify(responses) }] });
//     return JSON.parse(reply.content[0].text).answer; }
const answer = async (item, responses, agent) => at(responses.at(-1), item.expected.path);

const results = [];
for (const item of pack.items) {
  let ok = false, want = item.expected, value;
  try {
    const responses = [];
    for (const c of item.tool_calls) responses.push(await call(c));
    value = await answer(item, responses, agent);
    [ok, want] = scores(item.expected, value);
  } catch (err) { value = String(err); }
  results.push(ok);
  console.log(`${ok ? "pass" : "FAIL"}  ${item.id.padEnd(32)} ${item.difficulty.padEnd(6)} ${item.question.slice(0, 56)}`);
  if (!ok) console.log(`        wanted ${JSON.stringify(want)}, got ${JSON.stringify(value)}`);
}
const passed = results.filter(Boolean).length, total = results.length;
console.log(`\n${passed}/${total}  ${passed === total ? "all correct" : "SOME WRONG"}  (${pack.version}, ${cache.size} requests)`);
process.exit(passed === total ? 0 : 1);
