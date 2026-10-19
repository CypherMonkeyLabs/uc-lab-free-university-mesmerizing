/* Write data/lesson-map.json, data/lesson-schema.json, and data/sources.json
   from the room pages and their sources files. */
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const catalog = JSON.parse(readFileSync(join(root, "assets/data/catalog.json"), "utf8"));
const trackOf = new Map();
for (const page of catalog.pages || []) {
  const key = (page.keys || []).find((item) => /^t\d+-r\d+$/i.test(item));
  if (!key) continue;
  const level = Math.min(10, Number(key.slice(1).split("-")[0]));
  trackOf.set(page.href, level);
}

function decode(text) {
  return String(text || "")
    .replace(/&#x27;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function sourceId(src) {
  const url = src.url || "";
  const rfc = url.match(/rfc(\d+)/i);
  if (rfc) return `rfc-${rfc[1]}`;
  const slug = `${src.kind || "src"}-${src.title || url}`
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 72);
  return slug || "source";
}

const sources = new Map();
const lessons = [];
const rooms = readdirSync(join(root, "rooms")).filter((name) => name.endsWith(".html")).sort();

for (const name of rooms) {
  const id = name.replace(/\.html$/, "");
  const html = readFileSync(join(root, "rooms", name), "utf8");
  const title = decode((html.match(/<h1>([\s\S]*?)<\/h1>/) || [, id])[1].replace(/<[^>]+>/g, " "));
  const bullet = decode(((html.match(/<section id="five"[\s\S]*?<li>([\s\S]*?)<\/li>/) || [])[1] || title).replace(/<[^>]+>/g, " "));
  const outcome = bullet.length >= 8 ? bullet : `Explain ${title} from this room.`;
  const href = `rooms/${name}`;
  const srcPath = join(root, "rooms/sources", id, "sources.json");
  let ids = [];
  try {
    const file = JSON.parse(readFileSync(srcPath, "utf8"));
    ids = (file.sources || []).filter((src) => src.url).map((src) => {
      const sid = sourceId(src);
      if (!sources.has(sid)) {
        sources.set(sid, {
          id: sid,
          title: src.title || sid,
          url: src.url,
          kind: src.kind || "",
          status: src.status || "unconfirmed",
          last_checked: src.last_checked || null,
        });
      }
      return sid;
    });
  } catch {
    ids = [];
  }
  if (!ids.length) ids = ["lab-room-unconfirmed"];
  lessons.push({
    key: id,
    title,
    level: trackOf.get(href) || 0,
    outcomes: [outcome.slice(0, 240)],
    sources: ids,
    href,
    last_verified: null,
  });
}

if (!sources.has("lab-room-unconfirmed")) {
  sources.set("lab-room-unconfirmed", {
    id: "lab-room-unconfirmed",
    title: "Room has no verified source URL",
    url: "",
    kind: "lab",
    status: "unconfirmed",
    last_checked: null,
  });
}

const schema = {
  required: ["key", "title", "level", "outcomes", "sources", "href", "last_verified"],
  level: { min: 0, max: 10 },
  last_verified: "null or YYYY-MM-DD",
};

writeFileSync(join(root, "data/lesson-schema.json"), `${JSON.stringify(schema, null, 2)}\n`);
writeFileSync(join(root, "data/sources.json"), `${JSON.stringify({ sources: [...sources.values()] }, null, 2)}\n`);
writeFileSync(join(root, "data/lesson-map.json"), `${JSON.stringify({ lessons }, null, 2)}\n`);
console.log(`lesson map: ${lessons.length} lessons, ${sources.size} sources`);
