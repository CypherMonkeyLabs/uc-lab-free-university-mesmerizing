/* Teaching labs from the v23 shell. Loaded only when a lab route opens. */
(function () {
  "use strict";

  var QUIZ_KEY = "uc_app_quiz";
  var CARD_KEY = "uc_app_cards";
  var LAB_KEY = "uc_app_labs";
  var TRACKS = [
    "Start here",
    "SIP and media",
    "CUCM and CUBE",
    "Webex Calling and Teams Phone",
    "Contact center — UCCE and PCCE",
    "CCaaS and UCaaS platforms",
    "Emergency calling",
    "Voice network and QoS",
    "Migrations",
    "Troubleshooting",
    "Evidence habits",
    "Design notes",
    "Practice",
    "Reference"
  ].map(function (group) { return { group: group }; });

  var LAB_MENU = [
    ["simulator", "Call-flow player"],
    ["dial-plan", "Dial-plan builder"],
    ["ivr", "IVR sandbox"],
    ["sipdec", "SIP message decoder"],
    ["codec", "Codec and bandwidth"],
    ["jitter", "RTP jitter and loss"],
    ["route", "CUCM routing tracer"],
    ["webex", "Webex Calling location"],
    ["ucce", "UCCE router"],
    ["finesse", "Finesse agent states"],
    ["e911", "E911 and RedSky"],
    ["qos", "QoS marking game"],
    ["srtp", "SRTP and TLS flight"],
    ["erlang-c", "Erlang-C staffing"],
    ["fault", "Find the fault"],
    ["dialpeer", "CUBE dial-peer match"],
    ["nat", "One-way audio"],
    ["record", "Recording fork"],
    ["quiz", "Quiz"],
    ["cards", "Flashcards"],
    ["boss", "Boss exam"]
  ];

  var ENGINE = {
    sipdec: "sipdec",
    codec: "codec",
    jitter: "jitter",
    route: "route",
    webex: "webex",
    ucce: "ucce",
    finesse: "finesse",
    e911: "e911",
    qos: "qos",
    srtp: "srtp",
    "erlang-c": "erlang",
    fault: "fault",
    dialpeer: "dialpeer",
    nat: "nat",
    record: "record"
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function readJson(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return fallback;
      var parsed = JSON.parse(raw);
      return parsed == null ? fallback : parsed;
    } catch (err) {
      return fallback;
    }
  }

  function writeJson(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (err) { /* private mode */ }
  }

  function markLab(name) {
    var state = readJson(LAB_KEY, {});
    if (!state || typeof state !== "object" || Array.isArray(state)) state = {};
    state[name] = 1;
    writeJson(LAB_KEY, state);
  }

  window.UCApp = window.UCApp || {};
  window.UCApp.markLab = markLab;

  function drills() {
    return window.UC_DRILLS || { questions: [], cards: [], boss: [], counts: {} };
  }

  function quizStore() {
    var raw = readJson(QUIZ_KEY, {});
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) raw = {};
    if (!raw.tracks || typeof raw.tracks !== "object") raw.tracks = {};
    if (!raw.boss || typeof raw.boss !== "object") raw.boss = {};
    return raw;
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[data-src="' + src + '"]');
      if (existing) {
        if (existing.getAttribute("data-loaded") === "1") resolve();
        else existing.addEventListener("load", function () { resolve(); }, { once: true });
        return;
      }
      var script = document.createElement("script");
      script.src = src;
      script.dataset.src = src;
      script.onload = function () {
        script.setAttribute("data-loaded", "1");
        resolve();
      };
      script.onerror = function () { reject(new Error("Could not load " + src)); };
      document.head.appendChild(script);
    });
  }

  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  var DIAL_SLOTS = [
    { id: "css", label: "1 · Line CSS", why: "The line can only dial patterns in partitions this CSS lists. The device CSS is appended after it." },
    { id: "pt", label: "2 · Partition", why: "The route pattern is invisible unless its partition is in that CSS." },
    { id: "pattern", label: "3 · Route pattern", why: "This is the digit match. It should point at a route list, not at a guess." },
    { id: "list", label: "4 · Route list", why: "The list is how you order groups and fail over without editing every phone." },
    { id: "group", label: "5 · Route group", why: "The group holds the devices that can take the call." },
    { id: "trunk", label: "6 · SIP trunk", why: "The trunk is what sends the INVITE to CUBE." }
  ];
  var DIAL_CHIPS = [
    { id: "css-local", fit: "css", label: "CSS_Line_Local", why: "Lists PT_PSTN, so the outside pattern is visible to this line." },
    { id: "css-int", fit: "", label: "CSS_Internal_Only", why: "Internal partitions only. The PSTN pattern never runs." },
    { id: "pt-pstn", fit: "pt", label: "PT_PSTN", why: "Holds the outside route pattern." },
    { id: "pt-int", fit: "", label: "PT_Internal", why: "Holds directory numbers, not the PSTN pattern." },
    { id: "pat", fit: "pattern", label: "9.@", why: "Access code plus the NANP macro. Your plan may be more specific. The point is the match." },
    { id: "ext", fit: "", label: "1XXX", why: "An internal extension pattern. It will not carry a PSTN number." },
    { id: "rl", fit: "list", label: "RL_PSTN", why: "The list the outside pattern points at." },
    { id: "rg", fit: "group", label: "RG_CUBE", why: "Members are the trunks toward CUBE." },
    { id: "rg-fax", fit: "", label: "RG_FAX", why: "Fax devices. A voice call would leave on the wrong member." },
    { id: "trunk", fit: "trunk", label: "Trunk_to_CUBE", why: "The SIP trunk that sends the INVITE to the border." },
    { id: "vm", fit: "", label: "Trunk_Unity", why: "Voicemail. The carrier never sees this INVITE." }
  ];
  function chipById(id) {
    for (var i = 0; i < DIAL_CHIPS.length; i++) if (DIAL_CHIPS[i].id === id) return DIAL_CHIPS[i];
    return null;
  }
  function renderDial(root) {
    var placed = {};
    var armed = "";
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> A phone that looks idle can still have no outside route. If the partition is missing from the CSS, the pattern does not exist for that line.</p>' +
      '<div class="uc-app-toolbar"><button type="button" class="uc-app-btn primary" id="ucDialCheck">Check plan</button><button type="button" class="uc-app-btn" id="ucDialReset">Reset</button><span class="uc-app-score">Click a block, then a slot. Or drag it.</span></div>' +
      '<div class="uc-app-dial"><div class="uc-app-tray"><h2>Blocks</h2><div id="ucDialTray"></div></div><div class="uc-app-slots"><h2>Outbound order</h2><div id="ucDialSlots"></div></div></div>' +
      '<p class="uc-app-status" id="ucDialStatus" aria-live="polite">Place CSS_Line_Local through Trunk_to_CUBE, in that order. The other blocks are traps.</p>';
    function paint() {
      var tray = root.querySelector("#ucDialTray");
      var slots = root.querySelector("#ucDialSlots");
      tray.innerHTML = DIAL_CHIPS.filter(function (chip) {
        return Object.keys(placed).every(function (key) { return placed[key] !== chip.id; });
      }).map(function (chip) {
        return '<button type="button" class="uc-app-chip' + (armed === chip.id ? " is-armed" : "") + '" draggable="true" data-chip="' + chip.id + '" aria-pressed="' + (armed === chip.id ? "true" : "false") + '">' + esc(chip.label) + "<small>" + esc(chip.why) + "</small></button>";
      }).join("") || '<p class="uc-app-score">All blocks are placed.</p>';
      slots.innerHTML = DIAL_SLOTS.map(function (slot) {
        var chip = chipById(placed[slot.id]);
        return '<div class="uc-app-slot" data-slot="' + slot.id + '" tabindex="0" aria-label="' + esc(slot.label) + '"><b>' + esc(slot.label) + "</b>" +
          (chip ? '<button type="button" class="uc-app-chip" draggable="true" data-chip="' + chip.id + '">' + esc(chip.label) + "<small>" + esc(chip.why) + "</small></button>" : "<small>Empty. " + esc(slot.why) + "</small>") +
          "</div>";
      }).join("");
    }
    function place(chipId, slotId) {
      if (!chipById(chipId) || !DIAL_SLOTS.some(function (s) { return s.id === slotId; })) return;
      Object.keys(placed).forEach(function (key) { if (placed[key] === chipId) delete placed[key]; });
      placed[slotId] = chipId;
      armed = "";
      paint();
      var status = root.querySelector("#ucDialStatus");
      status.className = "uc-app-status";
      status.textContent = chipById(chipId).label + " is in " + slotId + ". Check the plan when the order looks right.";
    }
    root.addEventListener("click", function (e) {
      var chip = e.target.closest("[data-chip]");
      var slot = e.target.closest("[data-slot]");
      if (chip && slot && !armed) {
        delete placed[slot.getAttribute("data-slot")];
        paint();
        var status = root.querySelector("#ucDialStatus");
        status.className = "uc-app-status";
        status.textContent = "Block returned to the tray.";
        return;
      }
      if (chip && !slot) {
        armed = chip.getAttribute("data-chip");
        paint();
        return;
      }
      if (slot && armed) place(armed, slot.getAttribute("data-slot"));
    });
    root.addEventListener("dragstart", function (e) {
      var chip = e.target.closest("[data-chip]");
      if (!chip || !e.dataTransfer) return;
      e.dataTransfer.setData("text/plain", chip.getAttribute("data-chip"));
      e.dataTransfer.effectAllowed = "move";
    });
    root.addEventListener("dragover", function (e) {
      var slot = e.target.closest("[data-slot]");
      if (!slot) return;
      e.preventDefault();
      slot.classList.add("is-over");
    });
    root.addEventListener("dragleave", function (e) {
      var slot = e.target.closest("[data-slot]");
      if (slot) slot.classList.remove("is-over");
    });
    root.addEventListener("drop", function (e) {
      var slot = e.target.closest("[data-slot]");
      if (!slot || !e.dataTransfer) return;
      e.preventDefault();
      slot.classList.remove("is-over");
      place(e.dataTransfer.getData("text/plain"), slot.getAttribute("data-slot"));
    });
    root.querySelector("#ucDialReset").addEventListener("click", function () {
      placed = {};
      armed = "";
      paint();
    });
    root.querySelector("#ucDialCheck").addEventListener("click", function () {
      var bad = null;
      var missing = false;
      DIAL_SLOTS.forEach(function (slot) {
        var node = root.querySelector('[data-slot="' + slot.id + '"]');
        var chip = chipById(placed[slot.id]);
        var good = chip && chip.fit === slot.id;
        if (node) {
          node.classList.toggle("is-good", !!good);
          node.classList.toggle("is-bad", !good);
        }
        if (!chip) missing = true;
        else if (!good && !bad) bad = chip;
      });
      var status = root.querySelector("#ucDialStatus");
      if (!bad && !missing) {
        status.className = "uc-app-status is-ok";
        status.textContent = "The line can see PT_PSTN, 9.@ matches, and the route list lands on the CUBE trunk. Prove it with digit analysis before you change production.";
        markLab("dial");
      } else if (bad) {
        status.className = "uc-app-status is-bad";
        status.textContent = bad.label + " does not belong in that slot. " + bad.why;
      } else {
        status.className = "uc-app-status is-bad";
        status.textContent = "The chain is incomplete. An empty slot means the INVITE has nowhere to go.";
      }
    });
    paint();
  }

  function starterIvr() {
    return {
      nodes: [
        { id: "start", title: "Start", sub: "Entry", x: 6, y: 38, why: "Every contact needs an entry. Without it the caller never reaches a menu." },
        { id: "greet", title: "Greeting", sub: "Prompt", x: 28, y: 38, why: "The greeting tells the caller they reached the company. It is not the queue." },
        { id: "menu", title: "Menu", sub: "1 sales · 2 support", x: 50, y: 38, why: "A digit is useful only when a branch exists for it." },
        { id: "sales", title: "Queue · Sales", sub: "Queue", x: 74, y: 14, why: "The queue is what the report counts. Wait time starts here, not at the prompt." },
        { id: "support", title: "Queue · Support", sub: "Queue", x: 74, y: 62, why: "A second queue keeps the skill and the wait separate." }
      ],
      edges: [
        { f: "start", t: "greet" },
        { f: "greet", t: "menu" },
        { f: "menu", t: "sales", digit: "1" },
        { f: "menu", t: "support", digit: "2" }
      ]
    };
  }
  function renderIvr(root) {
    var model = starterIvr();
    var connect = false;
    var from = "";
    var seq = 1;
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> The caller can hear a menu and still never enter a queue. The report will not show a contact that died in the prompt.</p>' +
      '<div class="uc-app-ivr">' +
        '<div class="uc-app-palette"><h2>Build</h2>' +
          '<div class="uc-app-field"><label for="ucIvrDigit">Digit</label><select id="ucIvrDigit"><option>1</option><option>2</option><option>3</option><option>0</option></select></div>' +
          '<div class="uc-app-toolbar">' +
            '<button type="button" class="uc-app-btn primary" id="ucIvrRun">Call</button>' +
            '<button type="button" class="uc-app-btn" id="ucIvrConnect" aria-pressed="false">Connect</button>' +
            '<button type="button" class="uc-app-btn" id="ucIvrAdd">Add transfer</button>' +
            '<button type="button" class="uc-app-btn" id="ucIvrReset">Reset</button>' +
          '</div>' +
          '<p class="uc-app-score">Drag a node. Connect joins the selected digit when you leave the menu.</p>' +
        '</div>' +
        '<div class="uc-app-board" id="ucIvrBoard"><svg aria-hidden="true"></svg></div>' +
      '</div>' +
      '<p class="uc-app-status" id="ucIvrStatus" aria-live="polite">Press Call. Digit 1 should land in Sales. Digit 3 has no branch until you add one.</p>';
    var board = root.querySelector("#ucIvrBoard");
    function nodeById(id) {
      for (var i = 0; i < model.nodes.length; i++) if (model.nodes[i].id === id) return model.nodes[i];
      return null;
    }
    function drawEdges() {
      var svg = board.querySelector("svg");
      var bounds = board.getBoundingClientRect();
      svg.setAttribute("viewBox", "0 0 " + bounds.width + " " + bounds.height);
      svg.innerHTML = model.edges.map(function (edge) {
        var a = board.querySelector('[data-node="' + edge.f + '"]');
        var b = board.querySelector('[data-node="' + edge.t + '"]');
        if (!a || !b) return "";
        var ar = a.getBoundingClientRect();
        var br = b.getBoundingClientRect();
        var x1 = ar.left + ar.width / 2 - bounds.left;
        var y1 = ar.top + ar.height / 2 - bounds.top;
        var x2 = br.left + br.width / 2 - bounds.left;
        var y2 = br.top + br.height / 2 - bounds.top;
        var label = edge.digit ? '<text x="' + ((x1 + x2) / 2) + '" y="' + ((y1 + y2) / 2 - 6) + '">' + esc(edge.digit) + "</text>" : "";
        return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '"/>' + label;
      }).join("");
    }
    function paint(path) {
      board.querySelectorAll(".uc-app-node").forEach(function (n) { n.remove(); });
      model.nodes.forEach(function (node) {
        var el = document.createElement("button");
        el.type = "button";
        el.className = "uc-app-node";
        el.setAttribute("data-node", node.id);
        el.style.left = node.x + "%";
        el.style.top = node.y + "%";
        var hot = path && path[path.length - 1] === node.id;
        var on = path && path.indexOf(node.id) !== -1;
        if (on) el.classList.add("is-on");
        if (hot) el.classList.add("is-hot");
        el.innerHTML = esc(node.title) + "<small>" + esc(node.sub) + "</small>";
        el.setAttribute("aria-label", node.title + ". " + node.why);
        board.appendChild(el);
      });
      drawEdges();
    }
    function trace(digit) {
      var path = ["start"];
      var at = "start";
      for (var guard = 0; guard < 12; guard++) {
        var outs = model.edges.filter(function (edge) { return edge.f === at; });
        var next = null;
        if (at === "menu") next = outs.filter(function (edge) { return edge.digit === digit; })[0];
        else next = outs[0];
        if (!next) {
          return { path: path, stuck: at === "menu" ? "No branch for digit " + digit + ". The caller stays in the menu, and no queue starts." : "The flow ends at " + at + "." };
        }
        path.push(next.t);
        at = next.t;
        if (/queue|transfer|xfer/i.test((nodeById(at) || {}).sub || "") || /Queue|Transfer/.test((nodeById(at) || {}).title || "")) break;
      }
      return { path: path, stuck: "" };
    }
    board.addEventListener("pointerdown", function (e) {
      var el = e.target.closest(".uc-app-node");
      if (!el) return;
      var id = el.getAttribute("data-node");
      if (connect) {
        var status = root.querySelector("#ucIvrStatus");
        if (!from) {
          from = id;
          status.textContent = "Connect " + id + " to the next node.";
          return;
        }
        if (from !== id && !model.edges.some(function (edge) { return edge.f === from && edge.t === id; })) {
          var edge = { f: from, t: id };
          if (from === "menu") edge.digit = root.querySelector("#ucIvrDigit").value;
          model.edges.push(edge);
        }
        from = "";
        status.textContent = "Branch saved. Press Call to see whether the digit reaches a queue.";
        paint();
        return;
      }
      var node = nodeById(id);
      var startX = e.clientX;
      var startY = e.clientY;
      var ox = node.x;
      var oy = node.y;
      function move(ev) {
        var bounds = board.getBoundingClientRect();
        node.x = Math.max(2, Math.min(78, ox + (ev.clientX - startX) / bounds.width * 100));
        node.y = Math.max(4, Math.min(78, oy + (ev.clientY - startY) / bounds.height * 100));
        el.style.left = node.x + "%";
        el.style.top = node.y + "%";
        drawEdges();
      }
      function up() {
        el.removeEventListener("pointermove", move);
        el.removeEventListener("pointerup", up);
      }
      el.addEventListener("pointermove", move);
      el.addEventListener("pointerup", up);
    });
    root.querySelector("#ucIvrConnect").addEventListener("click", function (e) {
      connect = !connect;
      from = "";
      e.currentTarget.setAttribute("aria-pressed", connect ? "true" : "false");
      root.querySelector("#ucIvrStatus").textContent = connect ? "Connect is on. Choose the source node, then the destination." : "Connect is off. Drag nodes, then place a call.";
    });
    root.querySelector("#ucIvrAdd").addEventListener("click", function () {
      var id = "xfer" + seq++;
      model.nodes.push({ id: id, title: "Transfer", sub: "Transfer", x: 40, y: 74, why: "A transfer leaves the queue. The report should show where the contact went." });
      paint();
    });
    root.querySelector("#ucIvrReset").addEventListener("click", function () {
      model = starterIvr();
      connect = false;
      from = "";
      root.querySelector("#ucIvrConnect").setAttribute("aria-pressed", "false");
      paint();
    });
    root.querySelector("#ucIvrRun").addEventListener("click", function () {
      var digit = root.querySelector("#ucIvrDigit").value;
      var result = trace(digit);
      paint(result.path);
      var last = nodeById(result.path[result.path.length - 1]);
      var status = root.querySelector("#ucIvrStatus");
      if (result.stuck) {
        status.className = "uc-app-status is-bad";
        status.textContent = result.stuck;
      } else {
        status.className = "uc-app-status is-ok";
        status.textContent = "Digit " + digit + " reached " + (last ? last.title : "the end") + ". " + (last ? last.why : "");
        markLab("ivr");
      }
    });
    paint();
  }

  function trackQuestions(track) {
    return (drills().questions || []).filter(function (item) { return item.track === track; });
  }
  function renderQuiz(root) {
    var bank = drills();
    var store = quizStore();
    function save() { writeJson(QUIZ_KEY, store); }
    function picker() {
      root.innerHTML =
        '<p class="uc-app-note"><b>Why it matters.</b> Each track keeps its own score. A drill is ten questions from that bank. The line under the answer is the point.</p>' +
        '<div class="uc-app-stack" id="ucQuizTracks"></div>';
      var host = root.querySelector("#ucQuizTracks");
      TRACKS.forEach(function (track) {
        var count = (bank.counts && bank.counts[track.group]) || trackQuestions(track.group).length;
        var row = store.tracks[track.group] || { ok: 0, n: 0, best: 0, bestN: 0 };
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "uc-app-choice";
        btn.textContent = track.group + " · " + count + " questions · " + (row.ok || 0) + "/" + (row.n || 0) + " scored · best drill " + (row.best || 0) + "/" + (row.bestN || 0);
        btn.addEventListener("click", function () { start(track.group); });
        host.appendChild(btn);
      });
    }
    function start(track) {
      var items = trackQuestions(track);
      if (!items.length) { picker(); return; }
      if (!store.tracks[track]) store.tracks[track] = { ok: 0, n: 0, best: 0, bestN: 0, seen: {}, cursor: 0 };
      var row = store.tracks[track];
      var cursor = Number(row.cursor) || 0;
      var session = [];
      var i;
      for (i = 0; i < 10; i++) {
        session.push(items[cursor % items.length]);
        cursor += 1;
      }
      var index = 0;
      var score = 0;
      var locked = false;
      function paint() {
        if (index >= session.length) {
          row.cursor = cursor % items.length;
          if (!row.bestN || score / session.length >= (row.best || 0) / row.bestN) {
            row.best = score;
            row.bestN = session.length;
          }
          save();
          markLab("quiz");
          root.innerHTML =
            '<p class="uc-app-note"><b>Why it matters.</b> A drill score is practice. The sentence under each answer is what you keep.</p>' +
            '<h2 class="uc-app-q">' + score + " / " + session.length + " on " + esc(track) + "</h2>" +
            '<p class="uc-app-score">Bank size ' + items.length + ". Cumulative " + row.ok + " / " + row.n + ". Best drill " + row.best + " / " + row.bestN + ".</p>" +
            '<div class="uc-app-toolbar"><button type="button" class="uc-app-btn primary" id="ucQuizAgain">Another ten</button><button type="button" class="uc-app-btn" id="ucQuizTracksBtn">All tracks</button></div>';
          root.querySelector("#ucQuizAgain").addEventListener("click", function () { start(track); });
          root.querySelector("#ucQuizTracksBtn").addEventListener("click", picker);
          return;
        }
        var item = session[index];
        root.innerHTML =
          '<p class="uc-app-score">' + esc(track) + " · " + items.length + " in the bank · question " + (index + 1) + " of " + session.length + " · " + score + " correct this drill</p>" +
          '<h2 class="uc-app-q">' + esc(item.q) + "</h2>" +
          item.choices.map(function (choice, choiceIndex) {
            return '<button type="button" class="uc-app-choice" data-choice="' + choiceIndex + '">' + esc(choice) + "</button>";
          }).join("") +
          '<p class="uc-app-status" id="ucQuizWhy" aria-live="polite">Choose an answer. The reason appears here.</p>' +
          '<button type="button" class="uc-app-btn" id="ucQuizNext" disabled>Next</button>';
        root.querySelector("#ucQuizNext").addEventListener("click", function () {
          if (!locked) return;
          index += 1;
          locked = false;
          paint();
        });
        root.querySelectorAll("[data-choice]").forEach(function (btn) {
          btn.addEventListener("click", function () {
            if (locked) return;
            locked = true;
            var pick = Number(btn.getAttribute("data-choice"));
            root.querySelectorAll("[data-choice]").forEach(function (choice) {
              var n = Number(choice.getAttribute("data-choice"));
              choice.disabled = true;
              if (n === item.answer) choice.classList.add("is-good");
              else if (n === pick) choice.classList.add("is-bad");
            });
            row.n = (row.n || 0) + 1;
            row.seen = row.seen || {};
            row.seen[item.id] = 1;
            if (pick === item.answer) {
              score += 1;
              row.ok = (row.ok || 0) + 1;
            }
            save();
            var why = root.querySelector("#ucQuizWhy");
            why.className = "uc-app-status " + (pick === item.answer ? "is-ok" : "is-bad");
            why.textContent = (pick === item.answer ? "Correct. " : "Not that one. ") + "Why it matters. " + item.why;
            var next = root.querySelector("#ucQuizNext");
            if (next) next.disabled = false;
          });
        });
      }
      paint();
    }
    picker();
  }

  function renderCards(root) {
    var bank = drills().cards || [];
    var known = readJson(CARD_KEY, {}).known || {};
    var index = 0;
    var flipped = false;
    var track = "";
    function visible() {
      if (!track) return bank;
      return bank.filter(function (card) { return card.track === track; });
    }
    function countKnown() { return Object.keys(known).length; }
    function cardKey(card) { return card.track + "|" + card.term; }
    function paint() {
      var list = visible();
      if (!list.length) {
        root.innerHTML = '<p class="uc-app-note">This track has no cards yet.</p>';
        return;
      }
      if (index >= list.length) index = 0;
      var card = list[index];
      var options = '<option value="">All tracks (' + bank.length + ")</option>" +
        TRACKS.map(function (item) {
          var n = bank.filter(function (entry) { return entry.track === item.group; }).length;
          return '<option value="' + esc(item.group) + '"' + (track === item.group ? " selected" : "") + ">" + esc(item.group) + " (" + n + ")</option>";
        }).join("");
      root.innerHTML =
        '<p class="uc-app-note"><b>Why it matters.</b> A definition you cannot use on a bridge is trivia. The back of the card is the reason you keep the term.</p>' +
        '<div class="uc-app-field"><label for="ucCardTrack">Track</label><select id="ucCardTrack">' + options + "</select></div>" +
        '<p class="uc-app-score">' + (index + 1) + " of " + list.length + " · " + countKnown() + " marked known in this browser</p>" +
        '<div class="uc-app-flip' + (flipped ? " is-flipped" : "") + '" id="ucFlip">' +
          '<div class="uc-app-flip-inner">' +
            '<div class="uc-app-face front" aria-hidden="' + (flipped ? "true" : "false") + '"><button type="button" class="uc-app-flip-hit" id="ucFlipBtn" aria-label="Flip card"></button><p class="uc-app-kicker">Term</p><h2>' + esc(card.term) + '</h2><p>Flip for the definition and why it matters.</p></div>' +
            '<div class="uc-app-face back" tabindex="-1" aria-hidden="' + (flipped ? "false" : "true") + '"><p class="uc-app-kicker">Definition</p><h2>' + esc(card.term) + '</h2><p>' + esc(card.def) + '</p><p style="margin-top:8px"><b>Why it matters.</b> ' + esc(card.why) + "</p></div>" +
          "</div></div>" +
        '<div class="uc-app-toolbar">' +
          '<button type="button" class="uc-app-btn" id="ucCardPrev">Previous</button>' +
          '<button type="button" class="uc-app-btn" id="ucCardFlip">Flip</button>' +
          '<button type="button" class="uc-app-btn" id="ucCardAgain">Again</button>' +
          '<button type="button" class="uc-app-btn primary" id="ucCardKnow">Know it</button>' +
        "</div>";
      function flip() { flipped = !flipped; paint(); }
      root.querySelector("#ucCardTrack").addEventListener("change", function (e) {
        track = e.target.value;
        index = 0;
        flipped = false;
        paint();
      });
      root.querySelector("#ucFlipBtn").addEventListener("click", flip);
      root.querySelector("#ucCardFlip").addEventListener("click", flip);
      root.querySelector("#ucCardPrev").addEventListener("click", function () {
        index = (index - 1 + list.length) % list.length;
        flipped = false;
        paint();
      });
      root.querySelector("#ucCardAgain").addEventListener("click", function () {
        delete known[cardKey(card)];
        writeJson(CARD_KEY, { known: known });
        index = (index + 1) % list.length;
        flipped = false;
        paint();
      });
      root.querySelector("#ucCardKnow").addEventListener("click", function () {
        known[cardKey(card)] = 1;
        writeJson(CARD_KEY, { known: known });
        if (countKnown() >= 5) markLab("cards");
        index = (index + 1) % list.length;
        flipped = false;
        paint();
      });
    }
    root.addEventListener("keydown", function (e) {
      var list = visible();
      var tag = e.target && e.target.tagName;
      if (!list.length || tag === "SELECT" || tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.key === " " && tag !== "BUTTON") {
        e.preventDefault();
        flipped = !flipped;
        paint();
      }
      if (e.key === "ArrowRight") { index = (index + 1) % list.length; flipped = false; paint(); }
      if (e.key === "ArrowLeft") { index = (index - 1 + list.length) % list.length; flipped = false; paint(); }
    });
    paint();
  }

  function renderBoss(root) {
    var items = drills().boss || [];
    var index = 0;
    var score = 0;
    var locked = false;
    function paint() {
      if (!items.length) {
        root.innerHTML = '<p class="uc-app-note">The boss exam is not loaded.</p>';
        return;
      }
      if (index >= items.length) {
        var store = quizStore();
        var passed = score / items.length >= 0.8;
        var best = Math.max(Number(store.boss.best) || 0, score);
        store.boss = {
          best: best,
          last: score,
          n: items.length,
          passed: !!(store.boss.passed || passed)
        };
        writeJson(QUIZ_KEY, store);
        markLab("boss");
        root.innerHTML =
          '<p class="uc-app-note"><b>Why it matters.</b> The boss exam crosses the tracks. Eighty percent is the pass line for this teaching set.</p>' +
          '<h2 class="uc-app-q">' + score + " / " + items.length + (passed ? " · passed" : " · below the pass line") + "</h2>" +
          '<p class="uc-app-score">Best in this browser: ' + best + " / " + items.length + ".</p>" +
          '<button type="button" class="uc-app-btn primary" id="ucBossAgain">Sit it again</button>';
        root.querySelector("#ucBossAgain").addEventListener("click", function () {
          index = 0;
          score = 0;
          locked = false;
          paint();
        });
        return;
      }
      var item = items[index];
      root.innerHTML =
        '<p class="uc-app-score">Boss exam · question ' + (index + 1) + " of " + items.length + " · " + score + " correct · pass at 80%</p>" +
        '<h2 class="uc-app-q">' + esc(item.q) + "</h2>" +
        item.choices.map(function (choice, choiceIndex) {
          return '<button type="button" class="uc-app-choice" data-choice="' + choiceIndex + '">' + esc(choice) + "</button>";
        }).join("") +
        '<p class="uc-app-status" id="ucBossWhy" aria-live="polite">Choose an answer. The reason appears here.</p>' +
        '<button type="button" class="uc-app-btn" id="ucBossNext" disabled>Next</button>';
      root.querySelector("#ucBossNext").addEventListener("click", function () {
        if (!locked) return;
        index += 1;
        locked = false;
        paint();
      });
      root.querySelectorAll("[data-choice]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          if (locked) return;
          locked = true;
          var pick = Number(btn.getAttribute("data-choice"));
          root.querySelectorAll("[data-choice]").forEach(function (choice) {
            var n = Number(choice.getAttribute("data-choice"));
            choice.disabled = true;
            if (n === item.answer) choice.classList.add("is-good");
            else if (n === pick) choice.classList.add("is-bad");
          });
          if (pick === item.answer) score += 1;
          var why = root.querySelector("#ucBossWhy");
          why.className = "uc-app-status " + (pick === item.answer ? "is-ok" : "is-bad");
          why.textContent = (pick === item.answer ? "Correct. " : "Not that one. ") + "Why it matters. " + item.why;
          var next = root.querySelector("#ucBossNext");
          if (next) next.disabled = false;
        });
      });
    }
    paint();
  }


  function ladderSvg(flow, index) {
    var actors = flow.actors;
    var steps = flow.steps;
    var n = actors.length;
    var w = Math.max(720, n * 168);
    var top = 78;
    var row = 52;
    var h = top + steps.length * row + 24;
    var col = (w - 40) / n;
    function cx(i) { return 20 + col * i + col / 2; }
    var currentStep = steps[index] || {};
    var out = ['<svg class="ladder" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(flow.title) + ' call ladder">'];
    actors.forEach(function (name, a) {
      var x = cx(a);
      var hot = a === currentStep.f || a === currentStep.t;
      out.push('<rect x="' + (x - 70) + '" y="12" width="140" height="32" rx="16" fill="' + (hot ? "#4338ca" : "#131d31") + '"></rect>');
      out.push('<text class="actor-name" x="' + x + '" y="33" text-anchor="middle" fill="#f8fafc" font-size="13" font-family="ui-sans-serif,system-ui" font-weight="700">' + esc(name) + "</text>");
      out.push('<path d="M' + x + " 48 V" + (h - 10) + '" stroke="' + (hot ? "#818cf8" : "#94a3b8") + '" stroke-width="' + (hot ? 2.4 : 1.2) + '"></path>');
    });
    steps.forEach(function (step, i) {
      var y = top + i * row;
      var x1 = cx(step.f);
      var x2 = cx(step.t);
      var on = i === index;
      var color = on ? "#4338ca" : i < index ? "#0f766e" : "#64748b";
      var dash = step.kind === "media" ? ' stroke-dasharray="7 5"' : "";
      if (on) out.push('<rect x="12" y="' + (y - 18) + '" width="' + (w - 24) + '" height="36" rx="10" fill="#818cf8" fill-opacity="0.16"></rect>');
      if (Math.abs(x1 - x2) < 2) {
        out.push('<path d="M' + x1 + " " + y + ' q22 -18 0 -32" fill="none" stroke="' + color + '" stroke-width="' + (on ? 3 : 1.6) + '"' + dash + "></path>");
      } else {
        out.push('<path d="M' + x1 + " " + y + " H" + x2 + '" fill="none" stroke="' + color + '" stroke-width="' + (on ? 3 : 1.6) + '"' + dash + "></path>");
        var dir = x2 > x1 ? 1 : -1;
        out.push('<path d="M' + x2 + " " + y + " l" + (-dir * 8) + " -4 v8 z\" fill=\"" + color + "\"></path>");
      }
      out.push('<text class="step-label" x="' + ((x1 + x2) / 2) + '" y="' + (y - 8) + '" text-anchor="middle" font-size="12" font-weight="700" font-family="ui-sans-serif,system-ui">' + (i + 1) + " " + esc(step.label) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }

  function renderSimulator(root, scenarioId) {
    var walks = window.UC_RESTORED_WALKS || [];
    var order = ["hold", "blind", "consult", "hunt", "mra", "ivr-agent", "e911", "teams-dr", "wxcc"];
    var restored = order.map(function (id) {
      for (var i = 0; i < walks.length; i++) if (walks[i].id === id) return walks[i];
      return null;
    }).filter(Boolean);
    var rest = walks.filter(function (item) { return order.indexOf(item.id) < 0; });
    var playable = restored.concat(rest);
    var selected = 0;
    playable.forEach(function (item, i) { if (item.id === scenarioId) selected = i; });
    var step = 0;
    var playing = false;
    var timer = null;
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> <span data-why></span></p>' +
      '<div class="uc-app-field"><label for="ucFlowPick">Scenario, ' + playable.length + ' ladders</label>' +
      '<select id="ucFlowPick"></select></div>' +
      '<p class="uc-app-score">Solid arrows are signaling. Dashed arrows are media. A self loop stays on that hop.</p>' +
      '<div class="ladder-scroll" data-svg></div>' +
      '<p class="uc-app-status" data-cap role="status"></p>' +
      '<div class="uc-app-toolbar">' +
      '<button type="button" class="uc-app-btn primary" data-act="play" aria-pressed="false">Play</button>' +
      '<button type="button" class="uc-app-btn" data-act="back">Step back</button>' +
      '<button type="button" class="uc-app-btn" data-act="next">Step forward</button>' +
      "</div>";
    var pick = root.querySelector("#ucFlowPick");
    function options(list, label) {
      if (!list.length) return "";
      return '<optgroup label="' + esc(label) + '">' + list.map(function (item) {
        var at = playable.indexOf(item);
        return '<option value="' + at + '">' + esc(item.title) + "</option>";
      }).join("") + "</optgroup>";
    }
    pick.innerHTML = options(restored, "Restored ladders") + options(rest, "Other call flows");
    pick.value = String(selected);
    var svgHost = root.querySelector("[data-svg]");
    var cap = root.querySelector("[data-cap]");
    var why = root.querySelector("[data-why]");
    var playBtn = root.querySelector('[data-act="play"]');

    function stop() {
      playing = false;
      if (timer) clearTimeout(timer);
      timer = null;
      playBtn.textContent = "Play";
      playBtn.setAttribute("aria-pressed", "false");
    }

    function flow() { return playable[selected]; }

    function draw() {
      var item = flow();
      if (!item) {
        cap.textContent = "No call flows loaded.";
        return;
      }
      if (step >= item.steps.length) step = item.steps.length - 1;
      if (step < 0) step = 0;
      svgHost.innerHTML = ladderSvg(item, step);
      var current = item.steps[step];
      why.textContent = item.why;
      cap.textContent = "Step " + (step + 1) + " of " + item.steps.length + ". " + current.label + ". " + current.cap;
    }

    function tick() {
      if (!playing) return;
      var item = flow();
      if (!item || step >= item.steps.length - 1) {
        stop();
        if (item) markLab("simulator");
        return;
      }
      timer = setTimeout(function () {
        step += 1;
        draw();
        tick();
      }, 1100);
    }

    pick.addEventListener("change", function () {
      stop();
      selected = Number(pick.value) || 0;
      step = 0;
      draw();
    });
    root.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-act]");
      if (!btn) return;
      var act = btn.getAttribute("data-act");
      var item = flow();
      if (!item) return;
      if (act === "play") {
        if (playing) stop();
        else if (!reducedMotion()) {
          if (step >= item.steps.length - 1) step = 0;
          playing = true;
          playBtn.textContent = "Pause";
          playBtn.setAttribute("aria-pressed", "true");
          draw();
          tick();
        }
      }
      if (act === "back" || act === "next") {
        stop();
        step = Math.max(0, Math.min(item.steps.length - 1, step + (act === "next" ? 1 : -1)));
        draw();
        if (step === item.steps.length - 1) markLab("simulator");
      }
    });
    root.tabIndex = 0;
    root.addEventListener("keydown", function (event) {
      var tag = event.target && event.target.tagName;
      if (tag === "SELECT" || tag === "INPUT" || tag === "TEXTAREA") return;
      var item = flow();
      if (!item) return;
      if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
        event.preventDefault();
        stop();
        step = Math.max(0, Math.min(item.steps.length - 1, step + (event.key === "ArrowRight" ? 1 : -1)));
        draw();
      }
    });
    draw();
    return { destroy: stop };
  }

  function callEngine(name, stage) {
    if (!window.UCLabs || !window.UCLabs[name]) {
      stage.innerHTML = '<p class="uc-app-note">This lab did not load. Keep the assets folder beside the HTML file.</p>';
      return { destroy: function () {} };
    }
    window.UCLabs[name](stage);
    return { destroy: function () {} };
  }

  var RUN = {
    simulator: function (stage, opts) { return renderSimulator(stage, (opts && opts.scenario) || ""); },
    "dial-plan": function (stage) { renderDial(stage); },
    ivr: function (stage) { renderIvr(stage); },
    quiz: function (stage) { renderQuiz(stage); },
    cards: function (stage) { renderCards(stage); },
    boss: function (stage) { renderBoss(stage); }
  };
  Object.keys(ENGINE).forEach(function (route) {
    RUN[route] = function (stage) { return callEngine(ENGINE[route], stage); };
  });

  function jumpBar(route) {
    return '<div class="uc-app-field uc-app-jump"><label for="ucLabJump">Teaching lab</label><select id="ucLabJump">' +
      LAB_MENU.map(function (item) {
        return '<option value="' + item[0] + '"' + (item[0] === route ? " selected" : "") + ">" + esc(item[1]) + "</option>";
      }).join("") +
      "</select></div>";
  }

  function mount(route, root, opts) {
    opts = opts || {};
    if (!RUN[route]) {
      root.innerHTML = '<p class="uc-app-note">That lab is not in this campus.</p>';
      return Promise.resolve({ destroy: function () { root.innerHTML = ""; } });
    }
    var jobs = [];
    if (route === "simulator") jobs.push(loadScript("assets/labs/restored-walks.js"));
    if (route === "quiz" || route === "cards" || route === "boss") jobs.push(loadScript("assets/app-drills.js"));
    if (ENGINE[route]) jobs.push(loadScript("assets/app-labs.js"));
    return Promise.all(jobs).then(function () {
      root.innerHTML = jumpBar(route);
      var stage = document.createElement("div");
      stage.setAttribute("data-stage", "");
      root.appendChild(stage);
      var handle = RUN[route](stage, opts) || { destroy: function () {} };
      root.querySelector("#ucLabJump").addEventListener("change", function (event) {
        var next = event.target.value;
        if (next && next !== route) location.hash = "#/lab/" + next;
      });
      return {
        destroy: function () {
          if (handle.destroy) handle.destroy();
          root.innerHTML = "";
        }
      };
    });
  }

  window.UCLabShell = {
    mount: mount,
    routes: LAB_MENU.map(function (item) { return item[0]; })
  };
})();
