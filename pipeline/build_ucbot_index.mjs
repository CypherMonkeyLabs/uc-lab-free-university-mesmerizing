/* Build the offline UC chat index from this lab's own pages.
   Usage: node pipeline/build_ucbot_index.mjs
   Writes js/content/ucbot-index.json. Do not edit that file by hand. */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tokens } from "../shared/pybot-chat/engine.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const outPath = join(root, "js/content/ucbot-index.json");

const SYN = {
  transactions: "transaction",
  transaction: "transaction",
  transacton: "transaction",
  dialogs: "dialog",
  dialogue: "dialog",
  partitions: "partition",
  partiton: "partition",
  partition: "partition",
  expresway: "expressway",
  expressways: "expressway",
  gatewy: "gateway",
  gateway: "gateway",
  gateways: "gateway",
  caling: "calling",
  codecs: "codec",
  recording: "recording",
  recordng: "recording",
  recordings: "recording",
  emergncy: "emergency",
  emergency: "emergency",
  audoi: "audio",
  erly: "early",
  pattrn: "pattern",
  patterns: "pattern",
  rout: "route",
  routes: "route",
  carrir: "carrier",
  carrier: "carrier",
  serch: "search",
  peers: "dialpeer",
  peer: "dialpeer",
  srst: "srst",
  srts: "srst",
  eln: "elin",
  elins: "elin",
  erls: "erl",
  webrtc: "webrtc",
  asterisk: "asterisk",
  freeswitch: "freeswitch",
  siprec: "siprec",
  qos: "qos",
  dscp: "dscp",
  ucce: "ucce",
  cucm: "cucm",
  webex: "webex",
  mra: "mra",
  prack: "prack",
  llq: "llq",
};

const PAGES = [
  ["index.html", "Home", "page", "The front door for the eleven tracks."],
  ["start.html", "Learn", "page", "Ten minutes, or the full course."],
  ["diagrams.html", "Diagrams", "diagram", "Still drawings you can export."],
  ["flows.html", "Flows", "page", "Ladders with a moving packet."],
  ["play.html", "Play", "game", "Short drills in this browser. The dial-plan desk is a simulation."],
  ["listen.html", "Listen", "media", "Spoken notes, then read-along."],
  ["downloads.html", "Downloads", "download", "Sheets, cards, and the zip."],
  ["help.html", "Help", "guide", "How the menu, course, bot, and downloads work."],
  ["ecosystem.html", "Ecosystem", "glossary", "Glossary, bridges, and the systems beside CUCM."],
  ["quizzes.html", "Quizzes", "quiz", "Short checks with the answer written under the question."],
  ["sim.html", "Dial-plan desk", "game", "A simulation of a calling search space and a route pattern. No phone system is called."],
];

const TRACKS = [
  ["tracks/T1.html", "SIP", 1],
  ["tracks/T2.html", "CUCM dial plan", 2],
  ["tracks/T3.html", "CUBE and SRST", 3],
  ["tracks/T4.html", "Expressway", 4],
  ["tracks/T5.html", "Voice QoS", 5],
  ["tracks/T6.html", "UCCE bridges", 6],
  ["tracks/T7.html", "Webex Calling migration", 7],
  ["tracks/T8.html", "Troubleshooting", 8],
  ["tracks/T9.html", "Emergency calling", 9],
  ["tracks/T10.html", "Call recording", 10],
  ["tracks/T11.html", "Open telephony bridges", 11],
];

function decode(text) {
  return String(text || "")
    .replace(/&#x27;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function strip(html) {
  return decode(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
}

function section(html, id) {
  const re = new RegExp(`<section id="${id}"[\\s\\S]*?</section>`);
  const match = html.match(re);
  return match ? match[0] : "";
}

function bullets(html) {
  const block = section(html, "five");
  return [...block.matchAll(/<li>([\s\S]*?)<\/li>/g)].map((m) => strip(m[1])).filter(Boolean);
}

function paragraph(html, id) {
  const block = section(html, id);
  const match = block.match(/<p>([\s\S]*?)<\/p>/);
  return match ? strip(match[1]) : "";
}

function h1(html) {
  const match = html.match(/<h1>([\s\S]*?)<\/h1>/);
  return match ? strip(match[1]) : "";
}

const docs = [];
const seeds = [];

function add(doc) {
  const ex = String(doc.ex || "").replace(/\s+/g, " ").trim();
  const body = `${doc.ti} ${doc.body || ex}`;
  docs.push({
    i: doc.i,
    k: doc.k,
    ti: doc.ti,
    h: doc.h,
    s: doc.s || "",
    ex,
    eg: doc.eg || "",
    w: tokens(body, SYN),
    tw: tokens(doc.ti, SYN),
  });
}

for (const [href, title, kind, blurb] of PAGES) {
  let extra = blurb;
  try {
    const html = readFileSync(join(root, href), "utf8");
    const lead = html.match(/<p class="lede">([\s\S]*?)<\/p>/);
    if (lead) extra = `${blurb} ${strip(lead[1])}`;
  } catch {
    extra = blurb;
  }
  add({
    i: `page:${href.replace(/\.html$/, "").replace(/\//g, "-")}`,
    k: kind === "media" ? "media" : kind,
    ti: title,
    h: href,
    s: "shell",
    ex: extra,
    body: extra,
    eg: "",
  });
}

for (const [href, fallback, n] of TRACKS) {
  const html = readFileSync(join(root, href), "utf8");
  const title = h1(html) || fallback;
  const lede = html.match(/<p class="lede">([\s\S]*?)<\/p>/);
  const ex = lede ? strip(lede[1]) : fallback;
  add({
    i: `level:T${n}`,
    k: "level",
    ti: title,
    h: href,
    s: `T${n}`,
    ex,
    body: `${title} ${ex}`,
  });
}

const rooms = readdirSync(join(root, "rooms")).filter((name) => name.endsWith(".html")).sort();
for (const name of rooms) {
  const html = readFileSync(join(root, "rooms", name), "utf8");
  const title = h1(html) || name;
  const points = bullets(html);
  const core = paragraph(html, "core");
  const example = paragraph(html, "example");
  const opened = /Opened 2026-10/.test(html) ? "Opened 2026-10. " : "";
  const caution = /class="confirm"/.test(html) ? "Confirm before relying. " : "";
  const ex = `${opened}${caution}${core || points.join(" ")}`.trim();
  const gloss = [...html.matchAll(/<li><strong>([^<]+)<\/strong>\s*[—-]\s*([^<]+)<\/li>/g)]
    .map((m) => `${strip(m[1])}: ${strip(m[2])}`);
  add({
    i: `lesson:${name.replace(/\.html$/, "")}`,
    k: "lesson",
    ti: title,
    h: `rooms/${name}`,
    s: name.replace(/\.html$/, ""),
    ex,
    eg: example,
    body: `${title} ${points.join(" ")} ${core} ${example} ${gloss.join(" ")}`,
  });
  for (const point of points) {
    const any = tokens(point, SYN).filter((term) => term.length >= 4).slice(0, 3);
    if (!any.length) continue;
    seeds.push({
      i: `seed:point:${name}:${any[0]}`,
      h: `rooms/${name}`,
      ti: title,
      k: "lesson",
      topic: any[0],
      any: any.slice(0, 2),
      allow: tokens(`${title} ${point}`, SYN).filter((term) => term.length >= 3).slice(0, 12),
      rank: 4,
      how: false,
      ex: point,
      eg: example,
    });
  }
  for (const row of gloss) {
    const [term, meaning] = row.split(": ");
    const any = tokens(term, SYN).filter((termWord) => termWord.length >= 3).slice(0, 2);
    if (!any.length || !meaning) continue;
    seeds.push({
      i: `seed:gloss:${name}:${any[0]}`,
      h: `rooms/${name}`,
      ti: title,
      k: "glossary",
      topic: any[0],
      all: any,
      any,
      allow: tokens(`${term} ${meaning}`, SYN).slice(0, 12),
      rank: 8,
      how: false,
      ex: `${term}. ${meaning}`,
      eg: example,
    });
  }
}

const GENERATED_SKIP = new Set("this that with from have into about will each when what your page lesson room".split(" "));
for (const doc of docs) {
  if (doc.k !== "lesson") continue;
  const titleTerms = doc.tw.filter((term) => term.length >= 4 && !GENERATED_SKIP.has(term));
  if (!titleTerms.length) continue;
  const excerptTerms = tokens(doc.ex, SYN).filter((term) => term.length >= 4 && !GENERATED_SKIP.has(term)).slice(0, 8);
  seeds.push({
    i: `seed:gen:${doc.i}`,
    h: doc.h,
    ti: doc.ti,
    k: "lesson",
    topic: titleTerms[0],
    all: titleTerms.slice(0, 6),
    any: titleTerms.slice(0, 6),
    allow: [...new Set([...titleTerms, ...excerptTerms])],
    rank: 30,
    how: false,
    ex: doc.ex,
    eg: doc.eg || "",
  });
}

const payload = {
  v: 2,
  note: "Generated by pipeline/build_ucbot_index.mjs from this lab's rooms, tracks, and shell pages. Excerpts are sentences already on those pages. Do not edit by hand.",
  lessons: docs.filter((doc) => doc.k === "lesson").length,
  topics: [
    "SIP signaling",
    "CUCM dial plan",
    "CUBE and SRST",
    "Expressway and MRA",
    "voice QoS",
    "UCCE",
    "Webex Calling",
    "emergency calling",
    "recording",
    "troubleshooting",
  ],
  syn: SYN,
  seeds,
  docs: docs.map((doc) => {
    const row = {
      i: doc.i,
      k: doc.k,
      ti: doc.ti,
      h: doc.h,
      s: doc.s,
      ex: doc.ex,
      w: doc.w,
      tw: doc.tw,
    };
    if (doc.eg) row.eg = doc.eg;
    return row;
  }),
};

writeFileSync(outPath, `${JSON.stringify(payload)}\n`);
console.log(`ucbot index: ${payload.docs.length} docs, ${payload.lessons} lessons, ${payload.seeds.length} seeds`);
