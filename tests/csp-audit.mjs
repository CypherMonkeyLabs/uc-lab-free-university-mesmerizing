import { chromium } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const repoName = process.env.CSP_REPO || "uc-lab-free-university-mesmerizing";
const base = process.env.CSP_BASE || `http://127.0.0.1:41741/${repoName}`;
const rootDir = process.env.CSP_ROOT || "/tmp/uc-baseline";
const outFile = process.env.CSP_OUT || "/tmp/csp-baseline.json";
const interact = process.env.CSP_INTERACT !== "0";

function listHtml(dir) {
  const found = [];
  const walk = (current) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (entry.name === ".git" || entry.name === "node_modules") continue;
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith(".html")) found.push(path.relative(dir, full).split(path.sep).join("/"));
    }
  };
  walk(dir);
  return found.sort();
}

function isNoise(text) {
  return /favicon|Failed to load resource: the server responded with a status of 404/i.test(text);
}

async function clickIf(page, selector) {
  const loc = page.locator(selector).first();
  if (!(await loc.count())) return false;
  try {
    await loc.click({ timeout: 4000 });
    return true;
  } catch (err) {
    return false;
  }
}

async function interactWith(page, rel) {
  const notes = [];
  if (rel === "index.html" || rel === "start.html" || rel === "quizzes.html" || rel === "play.html" || rel === "listen.html" || rel === "sim.html" || rel === "diagrams.html") {
    if (await clickIf(page, "header [data-menu-open], .menu-btn")) notes.push("menu");
    if (await clickIf(page, "header [data-menu-open], .menu-btn")) notes.push("menu-close");
    const search = page.locator("[data-nav-search]").first();
    if (await search.count()) {
      await search.fill("sip");
      notes.push("search");
    }
    if (await clickIf(page, ".display-btn")) notes.push("display");
    if (await clickIf(page, "[data-set-theme='aurora']")) notes.push("theme");
    if (await clickIf(page, "[data-set-theme='bloom']")) notes.push("theme-back");
    if (await clickIf(page, ".choice")) notes.push("quiz");
    if (rel === "listen.html") {
      const played = await page.evaluate(async () => {
        const audio = document.querySelector("audio");
        if (!audio) return "none";
        try {
          await audio.play();
          return "played";
        } catch (err) {
          return "play-blocked:" + (err && err.name ? err.name : "error");
        }
      });
      notes.push(played);
      if (await clickIf(page, "[data-listen]")) notes.push("listen-btn");
    }
    if (rel === "sim.html") {
      const css = page.locator("[data-css]");
      if (await css.count()) {
        await css.selectOption("emergency");
        await page.locator("[data-digits]").fill("911");
        await clickIf(page, "[data-sim-run]");
        notes.push("sim");
      }
    }
  }
  if (rel === "flagship/index.html") {
    if (await clickIf(page, "[data-theme-set='light']")) notes.push("flag-theme");
    const search = page.locator(".js-search").first();
    if (await search.count()) {
      await search.fill("sip");
      notes.push("flag-search");
    }
    if (await clickIf(page, "[data-open='menu']")) notes.push("flag-menu");
    const played = await page.evaluate(async () => {
      const audio = document.querySelector("audio");
      if (!audio) return "none";
      try {
        await audio.play();
        return "played";
      } catch (err) {
        return "play-blocked:" + (err && err.name ? err.name : "error");
      }
    });
    notes.push(played);
  }
  if (rel === "flagship/quiz.html") {
    await page.waitForSelector("#quizCard .choice", { timeout: 8000 }).catch(() => {});
    if (await clickIf(page, "#quizCard .choice")) notes.push("flag-quiz");
    const confetti = await page.evaluate(() => {
      if (typeof window.confetti !== "function") return "no-confetti";
      try {
        window.confetti({ particleCount: 12, spread: 40, origin: { y: 0.6 } });
        return "fired";
      } catch (err) {
        return "confetti-error:" + (err && err.message ? err.message : "error");
      }
    });
    notes.push(confetti);
    await page.waitForTimeout(300);
  }
  if (rel === "flagship/ecosystem/mindmap.html") {
    await page.waitForTimeout(1200);
    notes.push("mindmap-wait");
  }
  if (rel === "campus/uc-lab-free-university.html") {
    if (await clickIf(page, "#searchBtn")) notes.push("campus-search");
    const theme = page.locator("[data-theme], [data-set-theme], button[aria-label='Theme']").first();
    if (await theme.count()) {
      await theme.click({ timeout: 4000 }).catch(() => {});
      notes.push("campus-theme-try");
    }
  }
  return notes;
}

const only = new Set((process.env.CSP_ONLY || "").split(",").map((item) => item.trim()).filter(Boolean));
const pages = listHtml(rootDir).filter((rel) => only.size === 0 || only.has(rel));
const browser = await chromium.launch({
  executablePath: process.env.PW_CHROME || "/usr/local/bin/google-chrome",
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
const context = await browser.newContext();
await context.addInitScript(() => {
  try {
    localStorage.setItem("uc-guide-v1", JSON.stringify({ tour: 1, greeted: 1, stopIdle: 1 }));
  } catch (err) {
    /* private */
  }
  window.__cspViolations = [];
  document.addEventListener("securitypolicyviolation", (event) => {
    window.__cspViolations.push({
      directive: event.violatedDirective,
      blocked: event.blockedURI,
      sample: event.sample || "",
      source: event.sourceFile || "",
      line: event.lineNumber || 0,
    });
  });
});

const results = [];
let index = 0;
for (const rel of pages) {
  index += 1;
  const url = `${base}/${rel}`;
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => pageErrors.push(String(err)));
  let status = 0;
  let navError = "";
  try {
    const response = await page.goto(url, { waitUntil: "load", timeout: 25000 });
    status = response ? response.status() : 0;
    await page.waitForTimeout(rel.includes("mindmap") || rel.includes("uc-lab-free-university") ? 800 : 250);
  } catch (err) {
    navError = String(err).split("\n")[0];
  }
  let notes = [];
  if (interact && !navError) {
    try {
      notes = await interactWith(page, rel);
    } catch (err) {
      notes = ["interact-error:" + String(err).split("\n")[0]];
    }
  }
  const csp = navError ? [] : await page.evaluate(() => window.__cspViolations || []).catch(() => []);
  const meaningfulConsole = consoleErrors.filter((line) => !isNoise(line));
  results.push({ rel, status, navError, csp, consoleErrors: meaningfulConsole, pageErrors, notes });
  const bad = csp.length || meaningfulConsole.length || pageErrors.length || navError;
  if (bad || index % 40 === 0) {
    console.log(`${index}/${pages.length} ${rel} csp=${csp.length} console=${meaningfulConsole.length} page=${pageErrors.length} ${navError ? "NAV" : ""}`);
  }
  await page.close();
}
await browser.close();

const summary = {
  pages: results.length,
  cspPages: results.filter((row) => row.csp.length).length,
  cspEvents: results.reduce((sum, row) => sum + row.csp.length, 0),
  consolePages: results.filter((row) => row.consoleErrors.length).length,
  pageErrorPages: results.filter((row) => row.pageErrors.length).length,
  navErrors: results.filter((row) => row.navError).length,
};
fs.writeFileSync(outFile, JSON.stringify({ summary, results }, null, 2));
console.log(JSON.stringify(summary, null, 2));
console.log("wrote", outFile);
