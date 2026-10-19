/* Validate data/lesson-map.json against room pages and data/sources.json.
   Exit 1 on any problem. */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const map = JSON.parse(readFileSync(join(root, "data/lesson-map.json"), "utf8"));
const schema = JSON.parse(readFileSync(join(root, "data/lesson-schema.json"), "utf8"));
const sources = JSON.parse(readFileSync(join(root, "data/sources.json"), "utf8"));
const sourceIds = new Set((sources.sources || []).map((src) => src.id));
const problems = [];
const seen = new Set();

function decode(text) {
  return String(text || "")
    .replace(/&#x27;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

for (const lesson of map.lessons || []) {
  seen.add(lesson.key);
  for (const field of schema.required) {
    if (!(field in lesson)) problems.push(`${lesson.key}: missing field ${field}`);
  }
  if (!Number.isInteger(lesson.level) || lesson.level < 0 || lesson.level > 10) {
    problems.push(`${lesson.key}: level must be 0-10`);
  }
  if (!Array.isArray(lesson.outcomes) || lesson.outcomes.length < 1 || lesson.outcomes.some((item) => typeof item !== "string" || item.length < 8)) {
    problems.push(`${lesson.key}: needs at least one outcome`);
  }
  if (!Array.isArray(lesson.sources) || lesson.sources.length < 1) {
    problems.push(`${lesson.key}: needs at least one source`);
  }
  for (const id of lesson.sources || []) {
    if (!sourceIds.has(id)) problems.push(`${lesson.key}: unknown source id ${id}`);
  }
  if (lesson.last_verified !== null && !/^\d{4}-\d{2}-\d{2}$/.test(lesson.last_verified)) {
    problems.push(`${lesson.key}: last_verified must be null or YYYY-MM-DD`);
  }
  const file = join(root, lesson.href || "");
  if (!lesson.href || !existsSync(file)) {
    problems.push(`${lesson.key}: missing page ${lesson.href}`);
    continue;
  }
  const html = readFileSync(file, "utf8");
  const title = decode((html.match(/<h1>([\s\S]*?)<\/h1>/) || [, ""])[1]);
  if (title !== lesson.title) problems.push(`${lesson.key}: title differs from the page ("${lesson.title}" vs "${title}")`);
}

const perLevel = {};
for (const lesson of map.lessons) perLevel[lesson.level] = (perLevel[lesson.level] || 0) + 1;
for (const problem of problems) console.log("FAIL", problem);
console.log("lessons:", seen.size, "mapped:", (map.lessons || []).length, "per level:", JSON.stringify(perLevel));
console.log("validate_lessons:", problems.length, "problems");
process.exit(problems.length ? 1 : 0);
