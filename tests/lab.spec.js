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
    const cache = await caches.open("uc-university-r12");
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

test("chat input is at least 180px wide on a phone", async ({ browser }) => {
  for (const viewport of [
    { width: 390, height: 844 },
    { width: 390, height: 430 },
  ]) {
    const context = await browser.newContext({ viewport, hasTouch: true, isMobile: true });
    await context.addInitScript(seen);
    const page = await context.newPage();
    await page.goto("/index.html");
    await page.locator(".monkey-btn").click();
    const input = page.locator("#py-chat-input");
    await expect(input).toBeVisible();
    const width = await input.evaluate((el) => el.getBoundingClientRect().width);
    expect(width, `input width at ${viewport.width}x${viewport.height}`).toBeGreaterThanOrEqual(180);
    await expect(page.locator(".py-chat-form button[type=submit]")).toBeVisible();
    await context.close();
  }
});

test("chat input and Send stay on screen at 390x430", async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 390, height: 430 },
    hasTouch: true,
    isMobile: true,
  });
  await context.addInitScript(seen);
  const page = await context.newPage();
  await page.goto("/index.html");
  await page.locator(".monkey-btn").click();
  const input = page.locator("#py-chat-input");
  const send = page.locator(".py-chat-form button[type=submit]");
  await expect(input).toBeVisible();
  await expect(send).toBeVisible();
  const box = await page.evaluate(() => {
    function place(el) {
      const rect = el.getBoundingClientRect();
      const x = Math.min(window.innerWidth - 2, Math.max(2, rect.left + rect.width / 2));
      const y = Math.min(window.innerHeight - 2, Math.max(2, rect.top + rect.height / 2));
      const top = document.elementFromPoint(x, y);
      return {
        inView: rect.top >= -1 && rect.bottom <= window.innerHeight + 1 && rect.left >= -1 && rect.right <= window.innerWidth + 1 && rect.height > 8,
        hit: !!(top && (top === el || el.contains(top))),
      };
    }
    const log = document.querySelector(".py-chat-log");
    return {
      input: place(document.querySelector("#py-chat-input")),
      send: place(document.querySelector(".py-chat-form button[type=submit]")),
      log: log.getBoundingClientRect().height,
    };
  });
  expect(box.input.inView, "input is outside the 430px viewport").toBe(true);
  expect(box.input.hit, "input is covered").toBe(true);
  expect(box.send.inView, "Send is outside the 430px viewport").toBe(true);
  expect(box.send.hit, "Send is covered").toBe(true);
  expect(box.log, "answer area is under 120px").toBeGreaterThanOrEqual(120);
  await context.close();
});

test("reduced motion still shows the home page", async ({ page }) => {
  await page.addInitScript(seen);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/index.html");
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.locator("#worlds")).toBeVisible();
});
