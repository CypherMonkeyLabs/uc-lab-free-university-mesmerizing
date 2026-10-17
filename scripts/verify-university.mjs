import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const need = [
  "index.html",
  "start.html",
  "diagrams.html",
  "flows.html",
  "downloads.html",
  "help.html",
  "legal.html",
  "play.html",
  "listen.html",
  "ecosystem.html",
  "sw.js",
  "manifest.webmanifest",
  "assets/js/frame.js",
  "assets/js/university.js",
  "assets/css/frame.css",
  "assets/css/wow.css",
  "assets/css/footer.css",
  "assets/css/uc.css",
  "guide/guide.js",
  "guide/guide.css",
  "guide/dragbot.js",
  "docs/KIT.md",
  "docs/PUBLISHING.md",
  "downloads/flashcards.json",
  "downloads/uc-lab-deck.pptx",
  "downloads/uc-lab-university.zip",
];
const missing = need.filter((path) => !existsSync(join(root, path)));
if (missing.length) {
  console.error("missing", missing);
  process.exit(1);
}

const diagramDir = join(root, "assets/diagrams/university");
const diagrams = readdirSync(diagramDir).filter((name) => name.endsWith(".svg"));
const animated = diagrams.filter((name) => readFileSync(join(diagramDir, name), "utf8").includes("animateMotion"));
if (diagrams.length < 60) throw new Error("need 60 diagrams, have " + diagrams.length);
if (animated.length < 30) throw new Error("need 30 flows, have " + animated.length);

const sheets = readdirSync(join(root, "downloads/sheets")).filter((name) => name.endsWith(".html"));
for (const name of sheets) {
  const stem = name.replace(/\.html$/, "");
  for (const ext of [".pdf", ".png"]) {
    if (!existsSync(join(root, "downloads/sheets", stem + ext))) throw new Error("missing " + stem + ext);
  }
  const sheet = readFileSync(join(root, "downloads/sheets", name), "utf8");
  for (const bit of ["learning-only", "cyphermonkeylabs.com/#contact", "github.com/CypherMonkeyLabs", "linktr.ee/cypherMonkey"]) {
    if (!sheet.includes(bit)) throw new Error(name + " missing " + bit);
  }
}
const cards = JSON.parse(readFileSync(join(root, "downloads/flashcards.json"), "utf8")).cards;
if (cards.length < 100) throw new Error("need 100 cards, have " + cards.length);
if (cards.some((card) => !card.front || !card.back || !card.source)) throw new Error("empty flashcard");

const downloads = readFileSync(join(root, "downloads.html"), "utf8");
if (!downloads.includes("Headless test table")) throw new Error("downloads missing test table");
const charts = readFileSync(join(root, "charts.html"), "utf8");
if ((charts.match(/data-chart=/g) || []).length < 6) throw new Error("need 6 charts");

const frame = readFileSync(join(root, "assets/js/frame.js"), "utf8");
const guide = readFileSync(join(root, "guide/guide.js"), "utf8");
for (const bit of ["data-menu-open", "data-ink", "data-font-set"]) {
  if (!readFileSync(join(root, "index.html"), "utf8").includes(bit) && !frame.includes(bit)) {
    /* baked in HTML */
  }
}
if (!guide.includes("Read along") || !guide.includes("SpeechRecognition") && !guide.includes("webkitSpeechRecognition")) {
  throw new Error("guide missing read-along or voice input");
}
if (!guide.includes("Finish in 10 minutes")) throw new Error("guide missing intro choices");

const allowedBrand = [
  /^https:\/\/cyphermonkeylabs\.com(\/|$|#)/,
  /^https:\/\/github\.com\/CypherMonkeyLabs(\/|$)/,
  /^https:\/\/linktr\.ee\/cypherMonkey$/,
];
const citationHosts = new Set([
  "www.rfc-editor.org",
  "www.cisco.com",
  "help.webex.com",
  "www.itu.int",
  "datatracker.ietf.org",
  "www.iana.org",
  "en.wikipedia.org",
  "community.cisco.com",
  "www.fcc.gov",
  "docs.asterisk.org",
  "developer.signalwire.com",
  "www.sipforum.org",
  "www.w3.org",
]);
const banned = /(?:^|[^a-z0-9.])(?:x\.com|linkedin\.com|huggingface\.co)|github\.com\/cipher0x9|mailto:/i;
const email = /[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}/;

function walk(dir, out) {
  for (const name of readdirSync(dir)) {
    if (name === ".git" || name === "node_modules" || name === "vendor") continue;
    const path = join(dir, name);
    const stat = statSync(path);
    if (stat.isDirectory()) walk(path, out);
    else if (name.endsWith(".html")) out.push(path);
  }
  return out;
}

const htmlFiles = walk(root, []);
const broken = [];
const hrefRe = /(?:href|src)="([^"]+)"/g;
for (const file of htmlFiles) {
  const text = readFileSync(file, "utf8");
  const rel = file.slice(root.length + 1);
  if (banned.test(text)) broken.push(rel + " banned brand link");
  const university = rel.startsWith("rooms/") || rel.startsWith("tracks/") || rel.startsWith("downloads/") || ["index.html", "start.html", "help.html", "legal.html", "downloads.html", "diagrams.html", "flows.html", "play.html", "listen.html", "ecosystem.html", "quizzes.html", "flashcards.html", "charts.html"].includes(rel);
  if (university) {
    if (email.test(text.replace(/<script[\s\S]*?<\/script>/g, ""))) broken.push(rel + " email-shaped text");
    for (const bit of ["learning-only student project", "© 2026 CypherMonkeyLabs 🐒", "data-canon-footer", "linktr.ee/cypherMonkey"]) {
      if (!text.includes(bit)) broken.push(rel + " missing " + bit);
    }
  }
  if (rel.startsWith("rooms/")) {
    for (const bit of ["Learn it in 5 minutes", "Worked example", "Ecosystem", "room-downloads", "data-quiz"]) {
      if (!text.includes(bit)) broken.push(rel + " missing " + bit);
    }
  }
  let match;
  hrefRe.lastIndex = 0;
  while ((match = hrefRe.exec(text))) {
    const href = match[1];
    if (!href || href.startsWith("#") || href.startsWith("data:")) continue;
    if (href.startsWith("http:") || href.startsWith("https:")) {
      if (banned.test(href)) broken.push(rel + " -> " + href);
      const host = href.split("/")[2];
      const brandOk = allowedBrand.some((re) => re.test(href));
      const citeOk = citationHosts.has(host);
      const sameSite = host === "cyphermonkeylabs.com" || host.endsWith(".cyphermonkeylabs.com");
      if (university && !brandOk && !citeOk && !sameSite) broken.push(rel + " host " + host);
      continue;
    }
    const clean = href.split("#")[0].split("?")[0];
    if (!clean) continue;
    const target = resolve(dirname(file), clean);
    if (!existsSync(target)) broken.push(rel + " -> " + href);
  }
}
if (broken.length) {
  console.error(broken.slice(0, 40).join("\n"));
  console.error("broken", broken.length);
  process.exit(1);
}
console.log("ok", htmlFiles.length, "html", diagrams.length, "diagrams", animated.length, "flows", sheets.length, "sheets", cards.length, "cards");
