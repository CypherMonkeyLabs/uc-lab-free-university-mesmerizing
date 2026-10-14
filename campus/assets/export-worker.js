/* Off-thread Markdown and question CSV. The page sends raw module source. */
"use strict";

function readValue(text, start) {
  var i = start;
  while (i < text.length && /\s/.test(text.charAt(i))) i += 1;
  var open = text.charAt(i);
  if (open !== "{" && open !== "[") throw new Error("expected JSON");
  var depth = 0;
  var inStr = false;
  var esc = false;
  for (var j = i; j < text.length; j += 1) {
    var ch = text.charAt(j);
    if (inStr) {
      if (esc) esc = false;
      else if (ch === "\\") esc = true;
      else if (ch === '"') inStr = false;
      continue;
    }
    if (ch === '"') {
      inStr = true;
      continue;
    }
    if (ch === "{" || ch === "[") depth += 1;
    else if (ch === "}" || ch === "]") {
      depth -= 1;
      if (depth === 0) return { value: JSON.parse(text.slice(i, j + 1)), end: j + 1 };
    }
  }
  throw new Error("unclosed JSON");
}

function sectionFromModule(text) {
  var at = text.indexOf("UC.pack(");
  if (at < 0) return null;
  return readValue(text, at + "UC.pack(".length).value;
}

function plain(html) {
  return String(html || "")
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(p|div|li|h1|h2|h3|tr|summary)>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

function csvCell(value) {
  var text = String(value == null ? "" : value).replace(/\r?\n/g, " ").trim();
  if (/[",]/.test(text)) return '"' + text.replace(/"/g, '""') + '"';
  return text;
}

function cardsFromSection(section) {
  var body = section.body || "";
  var rows = [];
  var re = /<details\b([^>]*)>([\s\S]*?)<\/details>/gi;
  var match;
  var n = 0;
  while ((match = re.exec(body))) {
    n += 1;
    var summary = "";
    var sum = /<summary\b[^>]*>([\s\S]*?)<\/summary>/i.exec(match[2]);
    if (sum) summary = plain(sum[1]);
    var rest = match[2].replace(/<summary\b[^>]*>[\s\S]*?<\/summary>/i, " ");
    var answer = plain(rest);
    var kind = /class="[^"]*\bq\b/.test(match[1]) || /^Q\d+\b/.test(summary) ? "question" : "card";
    rows.push([section.id, section.group || "", section.title || "", String(n), kind, summary, answer]);
  }
  return rows;
}

self.onmessage = function (event) {
  var msg = event.data || {};
  try {
    var texts = msg.texts || [];
    if (msg.type === "csv") {
      var lines = [];
      texts.forEach(function (text) {
        var section = sectionFromModule(text);
        if (!section) return;
        cardsFromSection(section).forEach(function (row) {
          lines.push(row.map(csvCell).join(","));
        });
      });
      self.postMessage({ id: msg.id, csv: lines.join("\n") });
      return;
    }
    if (msg.type === "md") {
      var parts = [];
      texts.forEach(function (text) {
        var section = sectionFromModule(text);
        if (!section) return;
        parts.push("# " + (section.title || section.id));
        parts.push("");
        parts.push("- Id: " + section.id);
        parts.push("- Group: " + (section.group || ""));
        parts.push("- " + (section.sub || ""));
        parts.push("");
        parts.push(plain(section.body || ""));
        parts.push("");
      });
      self.postMessage({ id: msg.id, md: parts.join("\n") });
      return;
    }
    self.postMessage({ id: msg.id, error: "Unknown export" });
  } catch (err) {
    self.postMessage({ id: msg.id, error: String(err && err.message ? err.message : err) });
  }
};
