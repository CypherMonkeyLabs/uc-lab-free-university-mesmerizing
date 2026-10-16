(function () {
  "use strict";

  var rootAttr = (document.body && document.body.getAttribute("data-root")) || "";
  var panel;
  var log;
  var chips;
  var form;
  var input;
  var typing = false;
  var kb = null;
  var quizIndex = 0;
  var quizScore = 0;
  var quizAnswered = false;

  function reduced() {
    var mode = document.documentElement.getAttribute("data-motion");
    if (mode === "reduce") return true;
    if (mode === "allow") return false;
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function pageHref(href) {
    if (!href) return "";
    if (/^https?:/.test(href)) return href;
    return rootAttr + href.replace(/^\.\//, "");
  }

  function hereFile() {
    var path = location.pathname || "";
    var marker = "/flagship/";
    var at = path.indexOf(marker);
    if (at >= 0) return path.slice(at + marker.length) || "index.html";
    if (path.endsWith("/") || path.endsWith("/index.html")) return "index.html";
    return path.split("/").pop() || "index.html";
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function build() {
    panel = el("section", "guide-bot");
    panel.id = "guideBot";
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "false");
    panel.setAttribute("aria-labelledby", "guideTitle");
    panel.innerHTML = [
      '<header class="guide-bar">',
      '<h2 id="guideTitle">Guide Bot</h2>',
      '<button type="button" class="btn guide-close">Close</button>',
      "</header>",
      '<div class="guide-log" role="log" aria-live="polite"></div>',
      '<div class="guide-chips"></div>',
      '<form class="guide-form">',
      '<label class="sr" for="guideInput">Ask the lab</label>',
      '<input id="guideInput" type="text" autocomplete="off" placeholder="Ask about a page in this lab">',
      '<button type="submit" class="btn">Send</button>',
      "</form>"
    ].join("");
    document.body.appendChild(panel);
    log = panel.querySelector(".guide-log");
    chips = panel.querySelector(".guide-chips");
    form = panel.querySelector(".guide-form");
    input = panel.querySelector("#guideInput");
    panel.querySelector(".guide-close").addEventListener("click", close);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      input.value = "";
      ask(text);
    });
  }

  function setOpen(open) {
    panel.hidden = !open;
    var launch = document.getElementById("guideLaunch");
    if (launch) launch.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("guide-open", open);
    if (open) input.focus();
  }

  function open() {
    ensure().then(function () {
      setOpen(true);
      if (!log.childNodes.length) greet();
    });
  }

  function close() { setOpen(false); }

  function toggle() {
    if (!panel || panel.hidden) open();
    else close();
  }

  function ensure() {
    if (kb) return Promise.resolve(kb);
    return fetch(rootAttr + "assets/guide-kb.json")
      .then(function (res) { if (!res.ok) throw new Error("kb"); return res.json(); })
      .catch(function () { return { entries: [], tours: [], quiz: [], synonyms: {}, fallback: "The guide notes did not load. I will not invent an answer.", greeting: "Guide notes did not load." }; })
      .then(function (data) { kb = data; return kb; });
  }

  function bubble(role, text, href, source) {
    var item = el("div", "guide-bubble " + role);
    var body = el("p", "", "");
    item.appendChild(body);
    if (href) {
      var link = el("a", "guide-link", "Open the page");
      link.href = pageHref(href);
      item.appendChild(link);
    }
    if (source) item.appendChild(el("p", "guide-source", source));
    log.appendChild(item);
    log.scrollTop = log.scrollHeight;
    return typeInto(body, text);
  }

  function typeInto(node, text) {
    typing = true;
    if (reduced() || text.length < 2) {
      node.textContent = text;
      typing = false;
      return Promise.resolve();
    }
    var i = 0;
    return new Promise(function (resolve) {
      var timer = setInterval(function () {
        i += 1;
        node.textContent = text.slice(0, i);
        log.scrollTop = log.scrollHeight;
        if (i >= text.length) {
          clearInterval(timer);
          typing = false;
          resolve();
        }
      }, 12);
    });
  }

  function setChips(list) {
    chips.innerHTML = "";
    list.forEach(function (chip) {
      var btn = el("button", "guide-chip", chip.label);
      btn.type = "button";
      btn.addEventListener("click", function () { chip.run(); });
      chips.appendChild(btn);
    });
  }

  function homeChips() {
    setChips([
      { label: "Start here", run: function () { startTour("start"); } },
      { label: "Diagrams", run: function () { ask("diagrams"); } },
      { label: "Flows", run: function () { ask("flows"); } },
      { label: "Charts", run: function () { ask("charts"); } },
      { label: "Cheat codes", run: function () { ask("cheat codes"); } },
      { label: "Ecosystem", run: function () { ask("ecosystem"); } },
      { label: "SIP tour", run: function () { startTour("sip"); } },
      { label: "Quiz me", run: startQuiz }
    ]);
  }

  function greet() {
    bubble("bot", kb.greeting || "Ask me about a page in this lab.").then(homeChips);
  }

  function norm(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9.+#\s-]/g, " ").replace(/\s+/g, " ").trim();
  }

  var STOP = { where: 1, do: 1, does: 1, is: 1, the: 1, a: 1, an: 1, to: 1, of: 1, my: 1, me: 1, in: 1, on: 1, for: 1, and: 1, or: 1, how: 1, what: 1, when: 1, why: 1, can: 1, you: 1, i: 1, it: 1, this: 1, that: 1, lab: 1 };

  function tokens(value) {
    return norm(value).split(" ").filter(function (word) { return word.length > 1 && !STOP[word]; });
  }

  function expand(words) {
    var out = words.slice();
    var map = kb.synonyms || {};
    words.forEach(function (word) {
      Object.keys(map).forEach(function (key) {
        var group = [key].concat(map[key] || []);
        if (group.indexOf(word) >= 0) out = out.concat(group);
      });
    });
    return out;
  }

  function scoreEntry(query, entry) {
    var q = expand(tokens(query));
    var hay = expand(tokens((entry.keywords || []).concat([entry.title, entry.answer]).join(" ")));
    if (!q.length) return 0;
    var hits = 0;
    q.forEach(function (word) { if (hay.indexOf(word) >= 0) hits += 1; });
    if (norm(entry.title) && norm(query).indexOf(norm(entry.title)) >= 0) hits += 2;
    return hits / q.length;
  }

  function bestEntry(query) {
    var best = null;
    var bestScore = 0;
    (kb.entries || []).forEach(function (entry) {
      var value = scoreEntry(query, entry);
      if (value > bestScore) {
        best = entry;
        bestScore = value;
      }
    });
    return bestScore >= 0.34 ? best : null;
  }

  function searchHit(query) {
    var q = norm(query);
    if (!q || !window.UC_SEARCH) return null;
    var hit = null;
    window.UC_SEARCH.some(function (item) {
      var blob = norm(item.title + " " + item.text + " " + item.href);
      if (blob.indexOf(q) >= 0 || q.split(" ").every(function (word) { return word.length < 3 || blob.indexOf(word) >= 0; })) {
        hit = item;
        return true;
      }
      return false;
    });
    return hit;
  }

  function localAnswer(query) {
    var entry = bestEntry(query);
    if (entry) return { answer: entry.answer, href: entry.href, source: entry.source };
    var hit = searchHit(query);
    if (hit) {
      return {
        answer: "This lab has a page named “" + hit.title + "”. I can open it. I don't have an extra fact to add beyond that page.",
        href: hit.href,
        source: "Search index of this lab."
      };
    }
    return { answer: kb.fallback, href: "", source: "" };
  }

  function cloudAnswer(query) {
    var endpoint = window.UC_GUIDE_ENDPOINT || "";
    if (!endpoint) return Promise.resolve(null);
    return fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({ message: query, page: location.pathname, knowledge: "local-lab-only" })
    }).then(function (res) {
      if (!res.ok) throw new Error("agent");
      return res.json();
    }).then(function (data) {
      if (!data || typeof data.answer !== "string" || !data.answer.trim()) return null;
      return {
        answer: data.answer.trim(),
        href: typeof data.href === "string" ? data.href : "",
        source: data.source ? String(data.source) : "Configured cloud agent"
      };
    }).catch(function () { return null; });
  }

  function ask(query) {
    bubble("user", query);
    chips.innerHTML = "";
    ensure().then(function () {
      var local = localAnswer(query);
      if (local.href || local.answer !== kb.fallback) {
        return bubble("bot", local.answer, local.href, local.source).then(homeChips);
      }
      return cloudAnswer(query).then(function (remote) {
        var pick = remote || local;
        return bubble("bot", pick.answer, pick.href, pick.source).then(homeChips);
      });
    });
  }

  function tourState() {
    try { return JSON.parse(sessionStorage.getItem("uc_guide_tour") || "null"); }
    catch (err) { return null; }
  }

  function saveTour(state) {
    try { sessionStorage.setItem("uc_guide_tour", JSON.stringify(state)); }
    catch (err) { /* private mode */ }
  }

  function findTour(id) {
    var found = null;
    (kb.tours || []).some(function (tour) {
      if (tour.id === id) { found = tour; return true; }
      return false;
    });
    return found;
  }

  function startTour(id) {
    ensure().then(function () {
      var tour = findTour(id);
      if (!tour) {
        bubble("bot", kb.fallback).then(homeChips);
        return;
      }
      saveTour({ id: tour.id, step: 0 });
      showTourStep();
    });
  }

  function showTourStep() {
    var state = tourState();
    var tour = state && findTour(state.id);
    if (!tour) return;
    var step = tour.steps[state.step];
    if (!step) {
      bubble("bot", "That tour is finished. The notes stay on the pages you opened.").then(function () {
        saveTour(null);
        homeChips();
      });
      return;
    }
    var onPage = hereFile() === step.href || location.pathname.endsWith(step.href);
    var prefix = onPage ? "You are on this step. " : "Next stop. ";
    bubble("bot", prefix + step.text, step.href, tour.title + " · step " + (state.step + 1) + " of " + tour.steps.length).then(function () {
      var next = [];
      if (state.step < tour.steps.length - 1) {
        next.push({ label: "Next step", run: function () { saveTour({ id: tour.id, step: state.step + 1 }); showTourStep(); } });
      } else {
        next.push({ label: "Finish tour", run: function () { saveTour({ id: tour.id, step: tour.steps.length }); showTourStep(); } });
      }
      next.push({ label: "Leave tour", run: function () { saveTour(null); bubble("bot", "Tour closed.").then(homeChips); } });
      setChips(next);
    });
  }

  function startQuiz() {
    ensure().then(function () {
      quizIndex = 0;
      quizScore = 0;
      quizAnswered = false;
      if (!(kb.quiz || []).length) {
        bubble("bot", kb.fallback).then(homeChips);
        return;
      }
      bubble("bot", "Five questions from this lab's notes. I will score only those.").then(showQuiz);
    });
  }

  function showQuiz() {
    var item = kb.quiz[quizIndex];
    if (!item) {
      var total = kb.quiz.length;
      bubble("bot", "Score: " + quizScore + " of " + total + ". The reasons are the ones on the lab pages, not a new fact.").then(homeChips);
      return;
    }
    quizAnswered = false;
    bubble("bot", "Question " + (quizIndex + 1) + " of " + kb.quiz.length + ". " + item.q).then(function () {
      setChips(item.choices.map(function (choice, index) {
        return { label: choice, run: function () { chooseQuiz(index); } };
      }));
    });
  }

  function chooseQuiz(index) {
    if (quizAnswered) return;
    quizAnswered = true;
    var item = kb.quiz[quizIndex];
    var good = index === item.answer;
    if (good) quizScore += 1;
    bubble("bot", (good ? "Yes. " : "Not that one. ") + item.why, "", "Quiz score " + quizScore + " so far").then(function () {
      quizIndex += 1;
      setChips([{ label: quizIndex >= kb.quiz.length ? "See score" : "Next question", run: showQuiz }]);
    });
  }

  build();
  window.UC_GUIDE = { open: open, close: close, toggle: toggle };
})();
