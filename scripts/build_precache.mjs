/* Check the service-worker shell against a 3.5 MB budget.
   The list in sw.js is the precache. This script fails if a file is missing
   or the total is over the budget. It does not fetch the network. */
import { readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const budget = 3_500_000;
const sw = readFileSync(join(root, "sw.js"), "utf8");
const block = sw.match(/var SHELL = \[([\s\S]*?)\];/);
if (!block) {
  console.error("SHELL array missing");
  process.exit(1);
}
const files = [...block[1].matchAll(/"\.\/([^"]+)"/g)].map((m) => m[1]).filter((name) => name && name !== "");
let total = 0;
const missing = [];
for (const rel of files) {
  const abs = join(root, rel);
  try {
    total += statSync(abs).size;
  } catch {
    missing.push(rel);
  }
}
console.log(`precache files ${files.length} bytes ${total} budget ${budget}`);
for (const rel of missing) console.log("MISSING", rel);
if (missing.length || total > budget) process.exit(1);
console.log("build_precache: ok");
