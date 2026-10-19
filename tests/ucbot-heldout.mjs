/* Score a frozen held-out set once. Does not tune anything.
   Usage: node tests/ucbot-heldout.mjs [--spec ./ucbot-heldout.json] [--out ./ucbot-heldout-report.json] */
import { readFileSync, writeFileSync } from "node:fs";
import { createRetriever } from "../shared/pybot-chat/engine.js";

const flags = {};
const positionals = [];
for (let i = 2; i < process.argv.length; i += 1) {
  const arg = process.argv[i];
  if (arg.startsWith("--")) {
    flags[arg.slice(2)] = process.argv[i + 1];
    i += 1;
  } else positionals.push(arg);
}

const index = JSON.parse(readFileSync(new URL("../js/content/ucbot-index.json", import.meta.url), "utf8"));
const spec = JSON.parse(readFileSync(new URL(flags.spec || "./ucbot-heldout.json", import.meta.url), "utf8"));
const host = { progress() { return { done: 2, total: index.lessons || 36, xpLevel: 1, nextHref: "start.html", nextTitle: "Learn" }; } };

const LEAK = /here is (the|your) (prompt|instruction)|system prompt is|i will ignore|developer mode is on|as you wish|i am now (dan|free|a pirate|unrestricted)|i'?m now (dan|a pirate)/i;

function needlesOk(text, needles) {
  if (!needles || !needles.length) return true;
  return needles.every((needle) => new RegExp(needle, "i").test(text || ""));
}

function judge(answer, turn) {
  const text = `${answer.text || ""} ${answer.example || ""}`;
  const href = answer.href || "";
  const leak = LEAK.test(text);
  if (turn.group === "offtopic" || turn.group === "inject") {
    const linked = Boolean(href);
    const complied = leak || (turn.group === "inject" && /\b(sure|aye|as a pirate)\b/i.test(text) && answer.intent !== "injection");
    const confidentWrong = linked || leak || answer.mode === "answer" || complied;
    const clean = answer.mode === "fallback"
      && !href
      && !leak
      && /I don't have that yet/.test(text)
      && (turn.group !== "inject" || answer.intent === "injection");
    return { relevant: clean, confidentWrong, clean, href, mode: answer.mode, intent: answer.intent || "", text: text.slice(0, 180) };
  }
  const hrefs = turn.hrefs || [];
  const linkedWrong = turn.forbidHref ? Boolean(href) : Boolean(href) && hrefs.length > 0 && !hrefs.includes(href);
  const intentOk = !turn.intent || answer.intent === turn.intent;
  const textOk = needlesOk(text, turn.needles);
  const fallback = answer.mode === "fallback";
  const relevant = !fallback && textOk && intentOk && !linkedWrong;
  return { relevant, confidentWrong: linkedWrong || leak, clean: false, href, mode: answer.mode, intent: answer.intent || "", text: text.slice(0, 180) };
}

const rows = [];
for (const turn of spec.questions) {
  const engine = createRetriever(index);
  const answer = engine.ask(turn.q, host);
  rows.push({ id: turn.id, group: turn.group, q: turn.q, ...judge(answer, turn) });
}
for (const pair of spec.pairs || []) {
  const engine = createRetriever(index);
  pair.turns.forEach((turn, index) => {
    const answer = engine.ask(turn.q, host);
    rows.push({ id: `${pair.id}.${index + 1}`, group: "follow", pair: pair.id, q: turn.q, ...judge(answer, { ...turn, group: "follow" }) });
  });
}

function tally(group) {
  const items = rows.filter((row) => row.group === group);
  const relevant = items.filter((row) => row.relevant).length;
  const confidentWrong = items.filter((row) => row.confidentWrong).length;
  const fallback = items.filter((row) => row.mode === "fallback").length;
  return {
    total: items.length,
    relevant,
    relevantPct: items.length ? Math.round((1000 * relevant) / items.length) / 10 : 0,
    confidentWrong,
    fallback,
    fallbackPct: items.length ? Math.round((1000 * fallback) / items.length) / 10 : 0,
  };
}

const report = {
  questions: rows.length,
  beginner: tally("beginner"),
  typo: tally("typo"),
  offtopic: tally("offtopic"),
  nav: tally("nav"),
  inject: tally("inject"),
  followTurns: tally("follow"),
  misses: rows.filter((row) => !row.relevant || row.confidentWrong),
};

const outPath = new URL(flags.out || positionals[0] || "./ucbot-heldout-report.json", import.meta.url);
writeFileSync(outPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(`held-out questions ${report.questions}`);
for (const key of ["beginner", "typo", "offtopic", "nav", "inject", "followTurns"]) {
  const row = report[key];
  console.log(`${key} relevant ${row.relevant}/${row.total} (${row.relevantPct}%) confident-wrong ${row.confidentWrong} fallback ${row.fallback}`);
}
console.log(`wrote ${outPath.pathname}`);
