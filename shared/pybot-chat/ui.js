/* Chat log for a lab bot panel. The host owns the answers.
   This file only paints messages and reports what the visitor typed. */

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

export function chatMarkup(examples) {
  const chips = (examples || []).map((item) => (
    `<button type="button" class="bp-chip" data-py-ask="${escapeAttr(item)}">${escapeText(item)}</button>`
  )).join("");
  return `<div class="py-chat" data-py-chat>
    <p class="py-chat-beta"><span class="py-beta-badge">Beta</span> Beta: scripted offline helper, may miss questions</p>
    <div class="py-chat-log" role="log" aria-live="polite" aria-relevant="additions" tabindex="0" aria-label="Chat with the UC guide"></div>
    <p class="py-chat-try">Try asking</p>
    <div class="py-chat-examples">${chips}</div>
    <div class="py-chat-chips" role="group" aria-label="Suggestion"></div>
    <form class="py-chat-form">
      <label class="visually-hidden" for="py-chat-input">Ask the UC guide about this lab</label>
      <button type="button" class="py-mic" data-py-mic aria-label="Voice input">Mic</button>
      <input id="py-chat-input" type="text" name="q" autocomplete="off" enterkeyhint="send" maxlength="400" placeholder="Ask about a lesson" spellcheck="true">
      <button type="submit">Send</button>
    </form>
    <button type="button" class="bp-link" data-py-clear>Clear chat</button>
  </div>`;
}

function escapeText(value) {
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}

function escapeAttr(value) {
  return escapeText(value).replace(/`/g, "&#96;");
}

export function paintChat(root, messages, busy) {
  if (!root) return;
  const log = root.querySelector(".py-chat-log");
  const chips = root.querySelector(".py-chat-chips");
  if (!log || !chips) return;
  log.replaceChildren();
  messages.forEach((msg, index) => {
    const item = el("article", `py-msg py-msg-${msg.role}`);
    item.appendChild(el("p", "py-msg-text", msg.text));
    if (msg.example) {
      const pre = el("pre", "py-msg-code");
      pre.appendChild(el("code", "", msg.example));
      item.appendChild(pre);
    }
    if (msg.href) {
      const link = el("a", "py-msg-link", msg.link || "Open this page");
      link.href = msg.href;
      if (msg.act) link.dataset.pyAct = msg.act;
      item.appendChild(link);
    }
    if (msg.closest) {
      msg.closest.forEach((hit) => {
        const link = el("a", "py-msg-link py-msg-near", hit.title);
        link.href = hit.href;
        item.appendChild(link);
      });
    }
    if (msg.role === "bot" && msg.text) {
      const read = el("button", "bp-link py-read", "Read aloud");
      read.type = "button";
      read.dataset.pyRead = String(index);
      read.title = "Read this answer with the browser voice. Recorded voices are the fixed audio lessons.";
      item.appendChild(read);
    }
    log.appendChild(item);
  });
  if (busy) log.appendChild(el("p", "py-msg py-msg-bot py-msg-wait", "Looking through the lab…"));
  log.scrollTop = log.scrollHeight;
  const last = [...messages].reverse().find((msg) => msg.role === "bot" && msg.follow);
  chips.replaceChildren();
  if (last && last.follow) {
    const btn = el("button", "bp-chip", last.follow);
    btn.type = "button";
    btn.dataset.pyAsk = last.followQ || last.follow;
    chips.appendChild(btn);
  }
}

export function chatInput(root) {
  return root ? root.querySelector("#py-chat-input") : null;
}
