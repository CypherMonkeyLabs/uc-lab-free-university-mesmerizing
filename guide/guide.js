/* UC guide. Big glowing monkey, first-open tour, read-along, voice input.
   Facts come from the page and assets/data/catalog.json. No cloud call. */
(function () {
  var root = document.documentElement;
  var KEY = "uc-guide-v1";

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || "{}"); }
    catch (err) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (err) { /* storage off */ }
  }
  var state = load();

  function prefix() {
    var nodes = document.querySelectorAll("script[src]");
    for (var i = 0; i < nodes.length; i++) {
      var src = nodes[i].getAttribute("src") || "";
      var at = src.indexOf("guide/guide.js");
      if (at !== -1) return src.slice(0, at);
    }
    return "";
  }
  var base = prefix();

  var dock = document.createElement("div");
  dock.className = "bot-dock";
  dock.innerHTML =
    '<div class="idle-note" data-idle hidden></div>' +
    '<button type="button" class="monkey-btn" data-tour="bot" data-pose="wave" aria-expanded="false" aria-controls="bot-panel" aria-label="UC guide monkey">' +
    monkeySvg() + "</button>" +
    '<section id="bot-panel" class="bot-panel" hidden>' +
    '<button type="button" class="sheet-handle" data-sheet-close aria-label="Close the guide"><span></span></button>' +
    '<div class="choice-row" data-choices></div>' +
    '<div class="bot-log" role="log" aria-live="polite"></div>' +
    '<label class="voice-pick">Voice <select data-voice-name aria-label="Speaking voice"></select></label>' +
    '<div class="choice-row">' +
    '<button type="button" data-read>Read along</button>' +
    '<button type="button" data-stop>Stop</button>' +
    "</div>" +
    '<details class="bot-extras"><summary>Voice and sound</summary>' +
    '<div class="voice-row">' +
    '<label>Rate <input data-rate type="range" min="0.7" max="1.3" step="0.05" value="0.95" aria-label="Speech rate"></label>' +
    '<label>Pitch <input data-pitch type="range" min="0.7" max="1.3" step="0.05" value="1" aria-label="Speech pitch"></label>' +
    '<button type="button" data-ambient aria-pressed="false">Ambient off</button>' +
    "</div></details>" +
    '<form class="bot-form"><button type="button" data-mic aria-label="Voice input">Mic</button>' +
    '<input type="text" aria-label="Type a question" placeholder="Type if the mic is unavailable" autocomplete="off">' +
    '<button type="submit">Send</button></form></section>';
  document.body.appendChild(dock);

  var monkey = dock.querySelector(".monkey-btn");
  var panel = dock.querySelector(".bot-panel");
  var log = dock.querySelector(".bot-log");
  var choices = dock.querySelector("[data-choices]");
  var voiceName = dock.querySelector("[data-voice-name]");
  var rate = dock.querySelector("[data-rate]");
  var pitch = dock.querySelector("[data-pitch]");
  var input = dock.querySelector(".bot-form input");
  var idleNote = dock.querySelector("[data-idle]");
  var suppressClick = false;
  var speaking = false;
  var readNodes = [];
  var readAt = 0;
  var ambient = null;
  var catalog = [];

  if (state.x != null && state.y != null && !isPhone()) {
    dock.style.left = state.x + "px";
    dock.style.top = state.y + "px";
    dock.style.right = "auto";
    dock.style.bottom = "auto";
  }
  if (state.rate) rate.value = state.rate;
  if (state.pitch) pitch.value = state.pitch;

  function isPhone() { return window.matchMedia("(max-width: 800px)").matches; }
  function pose(name) { monkey.setAttribute("data-pose", name); }

  function sayLocal(text) {
    var p = document.createElement("p");
    p.textContent = text;
    log.appendChild(p);
    log.scrollTop = log.scrollHeight;
  }
  function setChoices(items) {
    choices.innerHTML = "";
    items.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = item.label;
      btn.addEventListener("click", item.run);
      choices.appendChild(btn);
    });
  }

  function openPanel(flag) {
    panel.hidden = !flag;
    dock.classList.toggle("is-open", !!flag);
    monkey.setAttribute("aria-expanded", flag ? "true" : "false");
    if (flag) pose("cheer");
  }
  document.querySelectorAll("[data-open-guide]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      openPanel(panel.hidden);
      pose(panel.hidden ? "idle" : "wave");
    });
  });
  dock.querySelector("[data-sheet-close]").addEventListener("click", function () {
    openPanel(false);
    pose("idle");
  });
  monkey.addEventListener("click", function () {
    if (suppressClick) { suppressClick = false; return; }
    openPanel(panel.hidden);
  });

  function pages() { return catalog; }
  fetch(base + "assets/data/catalog.json").then(function (res) { return res.ok ? res.json() : null; }).then(function (data) {
    catalog = (data && data.pages) || [];
  }).catch(function () { catalog = []; });

  function go(href) { location.href = base + href; }
  function currentExport() {
    var box = document.querySelector(".room-downloads");
    if (box) {
      var link = box.querySelector("a");
      if (link) return link.getAttribute("href");
    }
    if (/downloads\.html$/.test(location.pathname)) return "downloads/uc-lab-university.zip";
    return "downloads.html";
  }
  function introCards() {
    setChoices([
      { label: "Finish in 10 minutes", run: function () { go("start.html#ten"); } },
      { label: "Full course", run: function () { go("start.html#path"); } },
      { label: "Just download", run: function () { go("downloads.html"); } },
      { label: "Read this page aloud", run: function () { dock.querySelector("[data-read]").click(); } },
      { label: "Export this section", run: function () { location.href = currentExport(); } }
    ]);
  }
  function greetCenter() {
    if (document.querySelector(".greet-modal")) return;
    openPanel(false);
    pose("wave");
    state.greeted = 1;
    save(state);
    var modal = document.createElement("div");
    modal.className = "greet-modal";
    modal.innerHTML =
      '<div class="greet-backdrop" data-greet-close></div>' +
      '<div class="greet-card" role="dialog" aria-modal="true" aria-labelledby="greet-title">' +
      '<div class="greet-mascot">' + monkeySvg() + "</div>" +
      '<h2 id="greet-title">Welcome to CypherMonkey Labs</h2>' +
      "<p>I am the UC guide for CUCM, SIP, gateways, and the path toward Webex Calling. I only repeat what these pages say.</p>" +
      '<div class="choice-row">' +
      '<button type="button" data-go="start.html#ten">Finish in 10 minutes</button>' +
      '<button type="button" data-go="start.html#path">Full course</button>' +
      '<button type="button" data-go="downloads.html">Just download</button>' +
      '<button type="button" data-greet-close>Continue on this page</button>' +
      "</div></div>";
    document.body.appendChild(modal);
    function closeGreet() {
      if (modal.parentNode) modal.parentNode.removeChild(modal);
      pose("idle");
      introCards();
      document.removeEventListener("keydown", onKey);
    }
    function onKey(event) {
      if (event.key === "Escape") closeGreet();
    }
    document.addEventListener("keydown", onKey);
    modal.querySelectorAll("[data-greet-close]").forEach(function (node) {
      node.addEventListener("click", closeGreet);
    });
    modal.querySelectorAll("[data-go]").forEach(function (node) {
      node.addEventListener("click", function () { go(node.getAttribute("data-go")); });
    });
    var first = modal.querySelector("button");
    if (first) first.focus();
  }

  function rankVoices(list) {
    return list.slice().sort(function (a, b) {
      return scoreVoice(b) - scoreVoice(a);
    });
  }
  function scoreVoice(voice) {
    var name = (voice.name + " " + voice.lang).toLowerCase();
    var score = 0;
    if (/en[-_]/.test(name) || voice.lang.toLowerCase().indexOf("en") === 0) score += 5;
    if (/natural|neural|aria|jenny|guy|enhanced|premium|samantha|google uk english female/.test(name)) score += 8;
    if (voice.localService) score += 1;
    return score;
  }
  function fillVoices() {
    if (!window.speechSynthesis) return;
    var list = rankVoices(window.speechSynthesis.getVoices() || []);
    voiceName.innerHTML = "";
    list.forEach(function (voice) {
      var opt = document.createElement("option");
      opt.value = voice.name;
      opt.textContent = voice.name + " (" + voice.lang + ")";
      voiceName.appendChild(opt);
    });
    if (state.voice) voiceName.value = state.voice;
    else if (list[0]) voiceName.value = list[0].name;
  }
  if (window.speechSynthesis) {
    fillVoices();
    window.speechSynthesis.addEventListener("voiceschanged", fillVoices);
  }
  function chosenVoice() {
    var list = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    for (var i = 0; i < list.length; i++) if (list[i].name === voiceName.value) return list[i];
    return rankVoices(list)[0] || null;
  }
  function speak(text, onend) {
    var done = false;
    var paced = 0;
    var started = Date.now();
    function finish() {
      if (done || !speaking) return;
      done = true;
      window.clearTimeout(paced);
      var wait = Math.max(0, 800 - (Date.now() - started));
      window.setTimeout(function () {
        if (onend && speaking) onend();
      }, wait);
    }
    if (!window.speechSynthesis) {
      paced = window.setTimeout(finish, 1400);
      return;
    }
    window.speechSynthesis.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    var voice = chosenVoice();
    if (voice) utter.voice = voice;
    utter.rate = Number(rate.value) || 0.95;
    utter.pitch = Number(pitch.value) || 1;
    paced = window.setTimeout(finish, Math.min(9000, 900 + text.length * 40));
    utter.onend = finish;
    utter.onerror = finish;
    speaking = true;
    pose("listen");
    root.classList.add("is-readalong");
    window.speechSynthesis.speak(utter);
  }
  function stopSpeak() {
    speaking = false;
    readAt = 0;
    root.classList.remove("is-readalong");
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    document.querySelectorAll(".is-spoken").forEach(function (el) { el.classList.remove("is-spoken"); });
    document.querySelectorAll(".is-reading").forEach(function (el) { el.classList.remove("is-reading"); });
    pose("idle");
  }
  dock.querySelector("[data-stop]").addEventListener("click", stopSpeak);
  rate.addEventListener("change", function () { state.rate = rate.value; save(state); });
  pitch.addEventListener("change", function () { state.pitch = pitch.value; save(state); });
  voiceName.addEventListener("change", function () { state.voice = voiceName.value; save(state); });

  function sentencesIn(section) {
    var nodes = [];
    section.querySelectorAll("p, li").forEach(function (el) {
      if (el.closest(".bot-dock, .site-footer, .quiz")) return;
      if (!el.querySelector(".read-sentence") && el.childNodes.length) {
        var text = el.textContent || "";
        var parts = text.split(/(?<=[.!?])\s+/).filter(Boolean);
        if (parts.length < 2) return;
        el.textContent = "";
        parts.forEach(function (part, index) {
          var span = document.createElement("span");
          span.className = "read-sentence";
          span.textContent = part;
          el.appendChild(span);
          if (index < parts.length - 1) el.appendChild(document.createTextNode(" "));
        });
      }
      el.querySelectorAll(".read-sentence").forEach(function (span) { nodes.push({ section: section, span: span }); });
      if (!el.querySelector(".read-sentence") && (el.textContent || "").trim()) nodes.push({ section: section, span: el });
    });
    return nodes;
  }
  function collectRead() {
    var nodes = [];
    document.querySelectorAll("main section, main article").forEach(function (section) {
      nodes = nodes.concat(sentencesIn(section));
    });
    if (!nodes.length) {
      document.querySelectorAll("main h1, main p").forEach(function (el) {
        nodes.push({ section: el.closest("section") || el, span: el });
      });
    }
    return nodes;
  }
  function readNext() {
    if (!speaking) return;
    if (readAt >= readNodes.length) { stopSpeak(); return; }
    var item = readNodes[readAt];
    document.querySelectorAll(".is-spoken").forEach(function (el) { el.classList.remove("is-spoken"); });
    document.querySelectorAll(".is-reading").forEach(function (el) { el.classList.remove("is-reading"); });
    item.span.classList.add("is-spoken");
    if (item.section && item.section.classList) item.section.classList.add("is-reading");
    root.classList.add("is-readalong");
    var reduce = root.dataset.motion === "reduce" || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    item.span.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" });
    var text = item.span.textContent || "";
    readAt += 1;
    speak(text, readNext);
  }
  dock.querySelector("[data-read]").addEventListener("click", function () {
    stopSpeak();
    readNodes = collectRead();
    readAt = 0;
    speaking = true;
    openPanel(true);
    sayLocal("Reading this page. The spoken sentence stays highlighted.");
    readNext();
  });
  document.querySelectorAll("[data-listen]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      dock.querySelector("[data-read]").click();
    });
  });

  var Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
  var mic = dock.querySelector("[data-mic]");
  if (!Rec) mic.hidden = false;
  mic.addEventListener("click", function () {
    if (!Rec) {
      sayLocal("This browser has no speech recognition. Type the question instead.");
      input.focus();
      return;
    }
    var rec = new Rec();
    rec.lang = "en-US";
    rec.onresult = function (event) {
      input.value = event.results[0][0].transcript;
      answer(input.value);
    };
    rec.onerror = function () {
      sayLocal("I could not hear that. Type the question instead.");
      input.focus();
    };
    try { rec.start(); pose("listen"); sayLocal("Listening."); }
    catch (err) { sayLocal("The mic did not start. Type the question instead."); input.focus(); }
  });

  function answer(text) {
    var q = (text || "").trim();
    if (!q) return;
    sayLocal("You: " + q);
    input.value = "";
    var lower = q.toLowerCase();
    pose("think");
    if (/download|export|sheet|zip/.test(lower)) {
      sayLocal("The export for this section is ready.");
      setChoices([{ label: "Open the export", run: function () { location.href = currentExport(); } }]);
      return;
    }
    if (/10 minute|ten minute|quick/.test(lower)) { go("start.html#ten"); return; }
    if (/full course|start here|learn/.test(lower)) { go("start.html#path"); return; }
    var hit = null;
    pages().forEach(function (row) {
      if (hit) return;
      if (lower.indexOf(row.title.toLowerCase()) !== -1 || (row.keys || []).some(function (key) { return lower.indexOf(key) !== -1; })) hit = row;
    });
    if (/diagram/.test(lower) && !hit) hit = { href: "diagrams.html", title: "Diagrams" };
    if (/flow/.test(lower) && !hit) hit = { href: "flows.html", title: "Flows" };
    if (/play|quiz/.test(lower) && !hit) hit = { href: "play.html", title: "Play" };
    if (/help|tour/.test(lower)) { sayLocal("Open Help to replay the tour."); setChoices([{ label: "Help", run: function () { go("help.html"); } }]); return; }
    if (hit) {
      sayLocal("Opening " + hit.title + ".");
      go(hit.href);
      return;
    }
    var section = document.querySelector("main h1");
    sayLocal("I do not have a separate note for that. On this page, start with " + (section ? section.textContent : "the first heading") + ". Confirm anything version-specific in the cited guide before you rely on it.");
    introCards();
  }
  dock.querySelector(".bot-form").addEventListener("submit", function (event) {
    event.preventDefault();
    answer(input.value);
  });

  dock.querySelector("[data-ambient]").addEventListener("click", function (event) {
    var on = event.currentTarget.getAttribute("aria-pressed") !== "true";
    event.currentTarget.setAttribute("aria-pressed", on ? "true" : "false");
    event.currentTarget.textContent = on ? "Ambient on" : "Ambient off";
    if (!on) {
      if (ambient) ambient.ctx.close();
      ambient = null;
      return;
    }
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    var ctx = new Ctx();
    var osc = ctx.createOscillator();
    var gain = ctx.createGain();
    osc.frequency.value = 174;
    osc.type = "sine";
    gain.gain.value = 0.015;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    ambient = { ctx: ctx };
  });

  var drag = null;
  monkey.addEventListener("pointerdown", function (event) {
    if (event.button !== 0 || isPhone()) return;
    drag = { x: event.clientX, y: event.clientY, left: dock.getBoundingClientRect().left, top: dock.getBoundingClientRect().top, moved: false };
    monkey.setPointerCapture(event.pointerId);
  });
  monkey.addEventListener("pointermove", function (event) {
    if (!drag) return;
    var dx = event.clientX - drag.x;
    var dy = event.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) < 6) return;
    drag.moved = true;
    var x = Math.max(8, drag.left + dx);
    var y = Math.max(8, drag.top + dy);
    dock.style.left = x + "px";
    dock.style.top = y + "px";
    dock.style.right = "auto";
    dock.style.bottom = "auto";
  });
  monkey.addEventListener("pointerup", function () {
    if (!drag) return;
    if (drag.moved) suppressClick = true;
    drag = null;
    var rect = dock.getBoundingClientRect();
    state.x = Math.round(rect.left);
    state.y = Math.round(rect.top);
    save(state);
  });

  var tour = document.createElement("div");
  tour.hidden = true;
  tour.className = "tour-layer";
  tour.innerHTML = '<div class="tour-hole" data-hole></div><div class="tour-card" role="dialog" aria-modal="true" aria-label="First visit tour"><p class="tour-kicker" data-kicker></p><p data-step></p><div class="tour-dots" role="group" aria-label="Steps 1 to 6"></div><div class="row"><button type="button" data-back>Back</button><button type="button" data-next>Next</button><button type="button" data-skip>Skip</button></div></div>';
  document.body.appendChild(tour);
  var hole = tour.querySelector("[data-hole]");
  var stepText = tour.querySelector("[data-step]");
  var kicker = tour.querySelector("[data-kicker]");
  var dots = tour.querySelector(".tour-dots");
  var steps = [
    { sel: "[data-tour='home']", n: "1 of 6", text: "Home is the front door. The eight tracks sit under this banner." },
    { sel: "[data-tour='menu']", n: "2 of 6", text: "Menu is at the top left. The drawer slides in. Esc or a tap outside closes it." },
    { sel: "[data-tour='learn']", n: "3 of 6", text: "Learn is the short path: ten minutes, or the full course." },
    { sel: "[data-tour='diagrams']", n: "4 of 6", text: "Diagrams are the still drawings. Flows are the ladders that move." },
    { sel: "[data-tour='play']", n: "5 of 6", text: "Play drills codes. Listen, on the phone bar and in the guide, reads the page aloud." },
    { sel: "[data-tour='downloads']", n: "6 of 6", text: "Downloads holds the sheets, cards, and the zip. Every room also has its own export buttons. The monkey can point at the file for this section." }
  ];
  var stepAt = 0;
  steps.forEach(function (step, index) {
    var dot = document.createElement("button");
    dot.type = "button";
    dot.className = "tour-dot";
    dot.setAttribute("data-dot", String(index));
    dot.setAttribute("aria-label", "Step " + (index + 1) + " of " + steps.length);
    dot.textContent = String(index + 1);
    dot.addEventListener("click", function () {
      stepAt = index;
      placeTour();
    });
    dots.appendChild(dot);
  });
  function fullyInside(node) {
    var rect = node.getBoundingClientRect();
    if (rect.width < 8 || rect.height < 8) return false;
    var margin = 6;
    return rect.top >= margin
      && rect.left >= margin
      && rect.bottom <= window.innerHeight - margin
      && rect.right <= window.innerWidth - margin;
  }
  function visibleTarget(sel) {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(sel));
    var found = null;
    nodes.forEach(function (node) {
      if (!found && fullyInside(node)) found = node;
    });
    if (found) return found;
    var pick = nodes[0] || monkey;
    if (pick && pick.scrollIntoView) {
      pick.scrollIntoView({ block: "nearest", inline: "center", behavior: "auto" });
    }
    return pick;
  }
  function band(selector) {
    var node = document.querySelector(selector);
    if (!node) return null;
    var rect = node.getBoundingClientRect();
    if (rect.width < 8 || rect.height < 8) return null;
    if (window.getComputedStyle(node).display === "none") return null;
    return rect;
  }
  function placeTour() {
    var target = visibleTarget(steps[stepAt].sel);
    var rect = target.getBoundingClientRect();
    var pad = 8;
    hole.style.left = (rect.left - pad) + "px";
    hole.style.top = (rect.top - pad) + "px";
    hole.style.width = (rect.width + pad * 2) + "px";
    hole.style.height = (rect.height + pad * 2) + "px";
    var card = tour.querySelector(".tour-card");
    kicker.textContent = steps[stepAt].n;
    stepText.textContent = steps[stepAt].text;
    tour.querySelectorAll(".tour-dot").forEach(function (dot, index) {
      var on = index === stepAt;
      dot.classList.toggle("is-on", on);
      dot.classList.toggle("is-done", index < stepAt);
      if (on) dot.setAttribute("aria-current", "step");
      else dot.removeAttribute("aria-current");
    });
    tour.querySelector("[data-back]").disabled = stepAt === 0;
    tour.querySelector("[data-next]").textContent = stepAt === steps.length - 1 ? "Done" : "Next";
    var header = band(".uc-top");
    var phone = band(".phone-bar");
    var headerBottom = header ? header.bottom : 8;
    var phoneTop = phone ? phone.top : window.innerHeight;
    var gap = 14;
    var cardH = card.offsetHeight;
    var roomTop = headerBottom + gap;
    var roomBottom = phoneTop - gap;
    var below = rect.bottom + gap;
    var above = rect.top - cardH - gap;
    var top = below;
    if (top < roomTop || top + cardH > roomBottom) {
      if (above >= roomTop && above + cardH <= roomBottom) top = above;
      else top = roomTop;
    }
    if (top + cardH > roomBottom) top = Math.max(roomTop, roomBottom - cardH);
    if (top < roomTop) top = roomTop;
    var hero = document.querySelector("main h1");
    if (hero && window.innerWidth <= 800) {
      var heroBottom = hero.getBoundingClientRect().bottom;
      var belowHero = heroBottom + gap;
      if (top < heroBottom - 8 && belowHero + cardH <= roomBottom) top = belowHero;
    }
    var width = card.offsetWidth;
    var left = Math.min(rect.left, window.innerWidth - width - 12);
    if (left < 12) left = 12;
    card.style.left = Math.round(left) + "px";
    card.style.top = Math.round(top) + "px";
  }
  function showTour() {
    tour.hidden = false;
    stepAt = 0;
    placeTour();
  }
  function endTour(skip) {
    tour.hidden = true;
    state.tour = 1;
    save(state);
    if (!state.greeted) greetCenter();
    else pose("idle");
  }
  tour.querySelector("[data-next]").addEventListener("click", function () {
    if (stepAt >= steps.length - 1) { endTour(false); return; }
    stepAt += 1;
    placeTour();
  });
  tour.querySelector("[data-back]").addEventListener("click", function () {
    if (stepAt === 0) return;
    stepAt -= 1;
    placeTour();
  });
  tour.querySelector("[data-skip]").addEventListener("click", function () { endTour(true); });
  window.addEventListener("resize", function () { if (!tour.hidden) placeTour(); });
  document.querySelectorAll("[data-tour-open]").forEach(function (btn) {
    btn.addEventListener("click", function () { showTour(); });
  });

  function offerIdle() {
    if (state.stopIdle) return;
    if ((state.offers || 0) >= 3) return;
    if (!panel.hidden) return;
    state.offers = (state.offers || 0) + 1;
    save(state);
    idleNote.hidden = false;
    idleNote.innerHTML = "<p>Need a hand with this page?</p>";
    var row = document.createElement("div");
    row.className = "row";
    var now = document.createElement("button");
    now.type = "button";
    now.textContent = "Not now";
    now.addEventListener("click", function () { idleNote.hidden = true; pose("idle"); });
    var stop = document.createElement("button");
    stop.type = "button";
    stop.textContent = "Stop offering";
    stop.addEventListener("click", function () {
      state.stopIdle = 1;
      save(state);
      idleNote.hidden = true;
    });
    row.appendChild(now);
    row.appendChild(stop);
    idleNote.appendChild(row);
    pose("wave");
  }
  if (!state.stopIdle && (state.offers || 0) < 3) {
    var wait = 120000 + Math.floor(Math.random() * 180000);
    window.setTimeout(offerIdle, wait);
  }

  if (!state.tour) showTour();
  else if (!state.greeted) greetCenter();
  else { pose("idle"); introCards(); }

  window.UC_GUIDE = { showTour: showTour, speak: speak, stop: stopSpeak };
})();

function monkeySvg() {
  return '<svg class="monkey-art" viewBox="0 0 240 280" aria-hidden="true">' +
    "<defs>" +
    '<radialGradient id="ucm-fur" cx="38%" cy="30%" r="72%"><stop offset="0" stop-color="#ffe7a3"/><stop offset=".48" stop-color="#f59e0b"/><stop offset="1" stop-color="#c2410c"/></radialGradient>' +
    '<radialGradient id="ucm-ear" cx="35%" cy="35%" r="75%"><stop offset="0" stop-color="#fda4af"/><stop offset="1" stop-color="#be123c"/></radialGradient>' +
    '<linearGradient id="ucm-vest" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#67e8f9"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>' +
    "</defs>" +
    '<circle cx="120" cy="132" r="108" fill="none" stroke="#fde047" stroke-width="4"/>' +
    '<circle cx="120" cy="132" r="100" fill="none" stroke="#22d3ee" stroke-width="5"/>' +
    '<circle cx="120" cy="132" r="92" fill="none" stroke="#f472b6" stroke-width="3"/>' +
    '<path class="tail" d="M168 198c30 6 42 34 24 50-14 12-32 2-32-14" fill="none" stroke="#ea580c" stroke-width="14" stroke-linecap="round"/>' +
    '<path class="tail" d="M168 198c30 6 42 34 24 50-14 12-32 2-32-14" fill="none" stroke="#fde68a" stroke-width="5" stroke-linecap="round"/>' +
    '<ellipse cx="118" cy="214" rx="54" ry="42" fill="url(#ucm-fur)" stroke="#9a3412" stroke-width="3"/>' +
    '<path d="M84 196h70c8 0 14 8 12 16l-8 24c-8 16-24 22-39 22s-31-6-39-22l-8-24c-2-8 4-16 12-16z" fill="url(#ucm-vest)" stroke="#1e1b4b" stroke-width="2"/>' +
    '<path class="arm-l" d="M76 198c-24 8-38 30-28 46 8 12 22 8 26-6 4-16 10-28 20-34z" fill="#f59e0b" stroke="#9a3412" stroke-width="2"/>' +
    '<circle cx="52" cy="240" r="11" fill="#fde68a" stroke="#9a3412" stroke-width="2"/>' +
    '<g class="arm-r"><path d="M160 186c24-6 42-30 36-46-6-14-22-10-26 4-4 16-8 28-18 36z" fill="#fbbf24" stroke="#9a3412" stroke-width="2"/>' +
    '<circle cx="198" cy="136" r="11" fill="#fde68a" stroke="#9a3412" stroke-width="2"/></g>' +
    '<circle class="ear-l" cx="46" cy="108" r="28" fill="url(#ucm-fur)" stroke="#9a3412" stroke-width="3"/>' +
    '<circle cx="46" cy="108" r="15" fill="url(#ucm-ear)"/>' +
    '<circle class="ear-r" cx="194" cy="108" r="28" fill="url(#ucm-fur)" stroke="#9a3412" stroke-width="3"/>' +
    '<circle cx="194" cy="108" r="15" fill="url(#ucm-ear)"/>' +
    '<circle cx="120" cy="112" r="64" fill="url(#ucm-fur)" stroke="#9a3412" stroke-width="3"/>' +
    '<ellipse cx="120" cy="136" rx="38" ry="30" fill="#fde68a" stroke="#d97706" stroke-width="2"/>' +
    '<g class="lid">' +
    '<ellipse cx="96" cy="104" rx="18" ry="20" fill="#fff" stroke="#1c1917" stroke-width="2.4"/>' +
    '<ellipse cx="144" cy="104" rx="18" ry="20" fill="#fff" stroke="#1c1917" stroke-width="2.4"/>' +
    '<circle cx="98" cy="106" r="9" fill="#06b6d4"/>' +
    '<circle cx="146" cy="106" r="9" fill="#8b5cf6"/>' +
    '<circle cx="98" cy="106" r="4.5" fill="#1c1917"/>' +
    '<circle cx="146" cy="106" r="4.5" fill="#1c1917"/>' +
    '<circle cx="102" cy="101" r="2.4" fill="#fff"/>' +
    '<circle cx="150" cy="101" r="2.4" fill="#fff"/>' +
    "</g>" +
    '<path class="brow" d="M78 80c12-10 24-8 32 2" fill="none" stroke="#7c2d12" stroke-width="3.5" stroke-linecap="round"/>' +
    '<path class="brow" d="M130 82c8-10 20-12 32-2" fill="none" stroke="#7c2d12" stroke-width="3.5" stroke-linecap="round"/>' +
    '<rect x="74" y="84" width="44" height="40" rx="14" fill="none" stroke="#facc15" stroke-width="3.5"/>' +
    '<rect x="122" y="84" width="44" height="40" rx="14" fill="none" stroke="#facc15" stroke-width="3.5"/>' +
    '<path d="M118 104h4M74 102H62M166 102h12" fill="none" stroke="#facc15" stroke-width="3.5" stroke-linecap="round"/>' +
    '<ellipse cx="120" cy="130" rx="8" ry="6" fill="#9a3412"/>' +
    '<ellipse cx="117" cy="128" rx="2.2" ry="1.4" fill="#fecdd3"/>' +
    '<path d="M98 146c10 14 34 14 44 0" fill="none" stroke="#7c2d12" stroke-width="3.5" stroke-linecap="round"/>' +
    '<path d="M110 150c5 5 15 5 20 0" fill="#fb7185"/>' +
    "</svg>";
}
