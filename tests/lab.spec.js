import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const shotDir = path.join("docs", "screenshots");
fs.mkdirSync(shotDir, { recursive: true });

const seen = () => {
  localStorage.setItem("uc-guide-v1", JSON.stringify({ tour: 1, greeted: 1, stopIdle: 1 }));
};

function watchErrors(page) {
  const errors = [];
  page.on("pageerror", (err) => errors.push(String(err)));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  return errors;
}

function quiet(errors) {
  return errors.filter((line) => !/favicon|Failed to load resource/i.test(line));
}

async function openBot(page) {
  await page.locator(".monkey-btn").click();
  await expect(page.locator("#bot-panel")).toBeVisible();
  await expect(page.locator("#py-chat-input")).toBeVisible();
}

async function ask(page, text) {
  const input = page.locator("#py-chat-input");
  await input.fill(text);
  await input.press("Enter");
  await expect(page.locator(".py-msg-user").last()).toContainText(text);
}

for (const viewport of [
  { width: 1440, height: 900, name: "1440" },
  { width: 390, height: 844, name: "390" },
]) {
  test(`home, guide, and a lesson at ${viewport.name}`, async ({ page }) => {
    await page.addInitScript(seen);
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    const errors = watchErrors(page);
    await page.goto("/index.html");
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.locator("#worlds")).toBeVisible();
    await expect(page.locator("body")).toContainText("lifelong student and AI builder");
    await page.screenshot({ path: path.join(shotDir, `wave-home-${viewport.name}.png`), fullPage: false });

    await openBot(page);
    await expect(page.locator("#bot-panel")).toContainText("I quote this lab's pages");
    await ask(page, "What is a SIP transaction");
    const answer = page.locator(".py-msg-bot").last();
    await expect(answer).toContainText(/SIP|transaction/i);
    await expect(answer.locator("a.py-msg-link")).toBeVisible();
    await page.screenshot({ path: path.join(shotDir, `wave-bot-${viewport.name}.png`), fullPage: false });

    await page.goto("/rooms/sip-transactions.html");
    await expect(page.locator("h1")).toBeVisible();
    await page.screenshot({ path: path.join(shotDir, `wave-lesson-${viewport.name}.png`), fullPage: false });
    expect(quiet(errors)).toEqual([]);
  });
}

test("service worker scope is this directory", async ({ page }) => {
  await page.addInitScript(seen);
  await page.goto("/index.html");
  const info = await page.evaluate(async () => {
    const reg = await navigator.serviceWorker.getRegistration("./");
    const worker = reg && (reg.active || reg.installing || reg.waiting);
    return {
      scope: reg ? reg.scope : "",
      script: worker ? worker.scriptURL : "",
      expected: new URL("./", location.href).href,
    };
  });
  expect(info.scope).toBe(info.expected);
  expect(info.script).toBe(new URL("./sw.js", info.expected).href);
});

test("offline reload still opens a lesson and the guide", async ({ page, context }) => {
  await page.addInitScript(seen);
  await page.setViewportSize({ width: 1440, height: 900 });
  const errors = watchErrors(page);
  await page.goto("/index.html");
  await page.waitForFunction(async () => {
    const ready = await navigator.serviceWorker.ready;
    if (!ready.active) return false;
    const cache = await caches.open("uc-university-r10");
    const index = await cache.match("./js/content/ucbot-index.json");
    const engine = await cache.match("./shared/pybot-chat/engine.js");
    const lesson = await cache.match("./rooms/sip-transactions.html");
    return !!(index && engine && lesson);
  }, null, { timeout: 20000 });
  await context.setOffline(true);
  await page.reload();
  await expect(page.locator("h1")).toBeVisible();
  await page.goto("/rooms/sip-transactions.html");
  await expect(page.locator("h1")).toBeVisible();
  await openBot(page);
  await ask(page, "What is a SIP transaction");
  await expect(page.locator(".py-msg-bot").last()).toContainText(/SIP|transaction/i);
  await expect(page.locator(".py-msg-bot").last().locator("a.py-msg-link")).toBeVisible();
  expect(quiet(errors)).toEqual([]);
});

test("dial-plan desk is labeled as a simulation", async ({ page }) => {
  await page.addInitScript(seen);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/sim.html");
  await expect(page.locator("h1")).toHaveText("Dial-plan desk");
  await expect(page.locator("[data-dial-sim]")).toContainText("Simulation only");
  await page.locator("[data-css]").selectOption("emergency");
  await page.locator("[data-digits]").fill("911");
  await page.locator("[data-sim-run]").click();
  await expect(page.locator("[data-sim-out]")).toContainText("No phone system was called");
  await expect(page.locator("[data-sim-out]")).toContainText("911 in the emergency partition is visible");
  await page.locator("[data-css]").selectOption("internal");
  await page.locator("[data-sim-run]").click();
  await expect(page.locator("[data-sim-out]")).toContainText("cannot see it");
});

test("reduced motion still shows the home page", async ({ page }) => {
  await page.addInitScript(seen);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/index.html");
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.locator("#worlds")).toBeVisible();
});
