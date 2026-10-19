/* Mount the offline retriever inside the existing guide panel. */
import { createRetriever } from "../shared/pybot-chat/engine.js";
import { chatMarkup, paintChat } from "../shared/pybot-chat/ui.js";

const CHIPS = [
  "What can you help with",
  "Where should I start",
  "What is a SIP transaction",
  "What is a CUCM partition",
  "What is SRST",
  "What causes one-way audio",
];

export async function mountChat(host, base) {
  const prefix = base || "";
  const response = await fetch(`${prefix}js/content/ucbot-index.json`);
  if (!response.ok) throw new Error("index missing");
  const index = await response.json();
  const engine = createRetriever(index);
  host.innerHTML = chatMarkup(CHIPS);
  const root = host.querySelector("[data-py-chat]");
  const messages = [{
    role: "bot",
    text: "I quote this lab's pages. Ask about SIP, CUCM, CUBE, Expressway, QoS, UCCE, or Webex Calling. I am a simulation of a study guide, not a vendor system.",
  }];

  function show() {
    paintChat(root, messages, false);
    root.querySelectorAll(".py-msg-link").forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (href && !/^(https?:|#)/.test(href)) link.setAttribute("href", prefix + href);
    });
  }

  function ask(text) {
    const q = String(text || "").trim();
    if (!q) return;
    messages.push({ role: "user", text: q });
    const answer = engine.ask(q, {
      progress() {
        return { done: 0, total: index.lessons || 0, xpLevel: 1, nextHref: "start.html", nextTitle: "Learn" };
      },
    });
    messages.push({
      role: "bot",
      text: answer.example ? `${answer.text}\n${answer.example}` : answer.text,
      href: answer.href,
      link: answer.link,
      follow: answer.follow,
      followQ: answer.followQ,
    });
    show();
  }

  window.UC_ASK = ask;
  root.querySelector(".py-chat-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const field = root.querySelector("input");
    ask(field.value);
    field.value = "";
  });
  root.addEventListener("click", (event) => {
    const chip = event.target.closest("[data-py-ask]");
    if (chip) ask(chip.getAttribute("data-py-ask"));
    if (event.target.closest("[data-py-clear]")) {
      messages.splice(0, messages.length);
      engine.reset();
      show();
    }
    const follow = event.target.closest("[data-py-follow]");
    if (follow) ask(follow.getAttribute("data-py-follow"));
  });
  const mic = root.querySelector("[data-py-mic]");
  const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Rec) mic.hidden = true;
  else mic.addEventListener("click", () => {
    const rec = new Rec();
    rec.lang = "en-US";
    rec.onresult = (event) => ask(event.results[0][0].transcript);
    try { rec.start(); } catch (err) { /* mic blocked */ }
  });
  show();
}
