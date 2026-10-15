(function () {
  "use strict";

  function award(id) {
    if (window.UC_FLAGSHIP && window.UC_FLAGSHIP.award) window.UC_FLAGSHIP.award(id);
  }
  function $(sel, base) { return (base || document).querySelector(sel); }
  function $all(sel, base) { return Array.prototype.slice.call((base || document).querySelectorAll(sel)); }

  var BADGES = [
    ["ladder", "First step", "Step a call ladder"],
    ["quiz", "One honest answer", "Answer a quiz question"],
    ["card", "Card turned", "Mark a flashcard known"],
    ["case", "Case opened", "Choose a branch in a case"],
    ["ports", "Port ear", "Score 6 of 8 on the ports game"],
    ["daily", "Today's leg", "Finish the daily question"],
    ["sandbox", "Your ladder", "Add three messages in the sandbox"],
    ["map", "Map reader", "Open three nodes on the flow map"],
    ["konami", "Traversal zone", "Enter the old joystick code"],
    ["cheat", "Sheet in hand", "Open the cheat-code hub"]
  ];

  if (/cheats\/index\.html$/.test(location.pathname) || /cheats\/$/.test(location.pathname)) award("cheat");

  function drawShare(title, line) {
    var canvas = $("#shareCanvas");
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext("2d");
    ctx.fillStyle = "#172033";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#7dcec4";
    ctx.font = "700 14px Segoe UI, sans-serif";
    ctx.fillText("UC LAB FREE UNIVERSITY", 28, 42);
    ctx.fillStyle = "#f4efe6";
    ctx.font = "700 32px Georgia, serif";
    wrap(ctx, title, 28, 96, 580, 36);
    ctx.font = "18px Segoe UI, sans-serif";
    ctx.fillStyle = "#f0b429";
    wrap(ctx, line, 28, 180, 580, 26);
    ctx.fillStyle = "#d7e2f0";
    ctx.font = "16px Segoe UI, sans-serif";
    ctx.fillText("cyphermonkeylabs.com", 28, 320);
  }
  function wrap(ctx, text, x, y, max, lh) {
    var words = String(text || "").split(/\s+/);
    var line = "";
    words.forEach(function (word) {
      var trial = line ? line + " " + word : word;
      if (ctx.measureText(trial).width > max) {
        ctx.fillText(line, x, y);
        y += lh;
        line = word;
      } else line = trial;
    });
    if (line) ctx.fillText(line, x, y);
  }
  var shareBtn = $("#shareBtn");
  if (shareBtn) {
    shareBtn.addEventListener("click", function () {
      drawShare(shareBtn.getAttribute("data-title") || "UC Lab", shareBtn.getAttribute("data-line") || "A teaching result. Not a vendor score.");
      var canvas = $("#shareCanvas");
      var link = document.createElement("a");
      link.href = canvas.toDataURL("image/png");
      link.download = "uc-lab-result.png";
      link.click();
    });
  }
  if ($("#shareCanvas") && shareBtn) {
    drawShare(shareBtn.getAttribute("data-title") || "UC Lab", shareBtn.getAttribute("data-line") || "Study card from the flagship lab.");
  }

  var quiz = $("#quiz");
  if (quiz && !$("#shareCanvas")) {
    var block = document.createElement("div");
    block.innerHTML = '<h2>Shareable result</h2><canvas id="shareCanvas" class="share-card" width="640" height="360"></canvas><div class="actions"><button type="button" class="btn" id="shareBtn" data-title="Quiz bank" data-line="468 questions in the idea-pool bank.">Download result card</button></div>';
    quiz.appendChild(block);
    $("#shareBtn").addEventListener("click", function () {
      var line = ($("#quizScore") && $("#quizScore").textContent) || "Quiz in progress";
      drawShare("Quiz bank", line + " · cyphermonkeylabs.com");
      var a = document.createElement("a");
      a.href = $("#shareCanvas").toDataURL("image/png");
      a.download = "uc-lab-quiz.png";
      a.click();
    });
    drawShare("Quiz bank", "468 questions in the idea-pool bank.");
  }

  function mountPortsGame() {
    var host = $("#portsGame");
    var raw = $("#portDeck");
    if (!host || !raw) return;
    var deck = JSON.parse(raw.textContent);
    var order = deck.slice();
    var cursor = 0;
    var correct = 0;
    function render() {
      if (cursor >= 8 || cursor >= order.length) {
        host.innerHTML = "<p class='num'>" + correct + " / " + cursor + "</p><p>8 rounds or the end of the deck. A score of 6 or more earns the Port ear badge.</p>";
        if (correct >= 6) award("ports");
        return;
      }
      var item = order[cursor];
      var choices = [item.port].concat(item.decoys);
      choices.sort(function () { return Math.random() - 0.5; });
      host.innerHTML = "<p class='kicker'>Round " + (cursor + 1) + " of 8</p><h2>" + item.ask + "</h2>" +
        choices.map(function (choice) {
          return "<button type='button' class='choice' data-port='" + choice + "'>" + choice + "</button>";
        }).join("") + "<p id='portWhy' class='muted'></p><p class='num'>" + correct + " correct</p>";
      $all(".choice", host).forEach(function (btn) {
        btn.addEventListener("click", function () {
          var good = btn.getAttribute("data-port") === item.port;
          if (good) correct += 1;
          btn.classList.add(good ? "good" : "bad");
          $("#portWhy").textContent = item.why;
          cursor += 1;
          setTimeout(render, 700);
        });
      });
    }
    render();
  }

  function mountMap() {
    var detail = $("#mapDetail");
    if (!detail) return;
    var seen = {};
    $all("[data-map]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        detail.innerHTML = "<h2>" + btn.getAttribute("data-map") + "</h2><p>" + btn.getAttribute("data-blurb") + "</p><p><a href='" + btn.getAttribute("data-href") + "'>Open the page</a></p>";
        seen[btn.getAttribute("data-map")] = true;
        if (Object.keys(seen).length >= 3) award("map");
      });
    });
  }

  function mountSandbox() {
    var board = $("#sbBoard");
    if (!board) return;
    var steps = [];
    function draw() {
      var actors = ["Phone", "CUCM", "CUBE", "PSTN"];
      var width = 760;
      var cols = actors.map(function (_, i) { return (i + 0.5) * width / actors.length; });
      var height = 80 + steps.length * 42;
      var svg = "<svg viewBox='0 0 " + width + " " + Math.max(height, 120) + "'><rect width='" + width + "' height='" + Math.max(height, 120) + "' fill='#fffdf8'/>";
      actors.forEach(function (name, i) {
        svg += "<text x='" + cols[i] + "' y='28' text-anchor='middle' font-size='14'>" + name + "</text>";
        svg += "<line x1='" + cols[i] + "' y1='40' x2='" + cols[i] + "' y2='" + (Math.max(height, 120) - 10) + "' stroke='#e3d7c6'/>";
      });
      steps.forEach(function (step, i) {
        var y = 64 + i * 42;
        var x1 = cols[actors.indexOf(step.from)];
        var x2 = cols[actors.indexOf(step.to)];
        svg += "<line x1='" + x1 + "' y1='" + y + "' x2='" + x2 + "' y2='" + y + "' stroke='#0f6e62' stroke-width='2'/>";
        svg += "<text x='" + ((x1 + x2) / 2) + "' y='" + (y - 6) + "' text-anchor='middle' font-size='12'>" + escapeHtml(step.label) + "</text>";
      });
      svg += "</svg>";
      $("#sbSvg").innerHTML = svg;
      board.textContent = steps.length + " messages";
      if (steps.length >= 3) award("sandbox");
    }
    $("#sbAdd").addEventListener("click", function () {
      steps.push({
        from: $("#sbFrom").value,
        to: $("#sbTo").value,
        label: ($("#sbLabel").value || "INVITE").slice(0, 24)
      });
      draw();
    });
    draw();
  }

  function mountDaily() {
    var host = $("#dailyHost");
    if (!host) return;
    var bank = window.UC_FLAGSHIP_BANK || { questions: [] };
    var list = bank.questions || [];
    if (!list.length) { host.textContent = "The question bank did not load."; return; }
    var now = new Date();
    var key = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
    var index = key % list.length;
    var q = list[index];
    host.innerHTML = "<p class='kicker'>UTC " + now.toISOString().slice(0, 10) + " · question " + (index + 1) + " of " + list.length + "</p><h2>" + escapeHtml(q.q) + "</h2>" +
      (q.choices || []).map(function (choice, i) {
        return "<button type='button' class='choice' data-i='" + i + "'>" + escapeHtml(choice) + "</button>";
      }).join("") + "<p id='dailyWhy' class='muted'></p>";
    $all(".choice", host).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var good = Number(btn.getAttribute("data-i")) === q.answer;
        btn.classList.add(good ? "good" : "bad");
        $all(".choice", host)[q.answer].classList.add("good");
        $("#dailyWhy").textContent = "Reason in the bank: " + (q.why || "");
        award("daily");
      });
    });
  }
  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function mountBadges() {
    var list = $("#badgeList");
    if (!list) return;
    var got = {};
    try { got = JSON.parse(localStorage.getItem("uc_flagship_badges") || "{}"); } catch (err) { got = {}; }
    var earned = Object.keys(got).length;
    list.innerHTML = "<p class='num'>" + earned + " / " + BADGES.length + "</p>" + BADGES.map(function (row) {
      var on = got[row[0]] ? "Earned" : "Not yet";
      return "<article class='paper'><h2>" + row[1] + "</h2><p>" + row[2] + "</p><p class='muted'>" + on + "</p></article>";
    }).join("");
  }

  function mountErlang() {
    var form = $("#erlangForm");
    if (!form) return;
    function erlangB(agents, offered) {
      var b = 1;
      for (var n = 1; n <= agents; n += 1) b = (offered * b) / (n + offered * b);
      return b;
    }
    function calc() {
      var calls = Number($("#erlangCalls").value);
      var aht = Number($("#erlangAht").value);
      var agents = Number($("#erlangAgents").value);
      var offered = (calls / 3600) * aht;
      var out = $("#erlangOut");
      if (!(offered > 0) || !(agents > 0)) { out.textContent = "Enter calls per hour, handle time, and agents."; return; }
      var b = erlangB(Math.round(agents), offered);
      var wait = agents > offered ? (agents * b) / (agents - offered * (1 - b)) : 1;
      out.textContent = "Offered load " + offered.toFixed(2) + " erlangs. Teaching Erlang C probability of waiting about " + Math.min(1, Math.max(0, wait)).toFixed(3) + ". This is not a vendor forecast.";
    }
    form.addEventListener("input", calc);
    calc();
  }

  var egg = document.createElement("div");
  egg.className = "egg";
  egg.id = "egg";
  egg.hidden = true;
  egg.innerHTML = "<div class='egg-card'><p class='kicker'>Traversal zone</p><h2>You found the joystick code.</h2><p>The lab still does not touch a live system. The badge is stored in this browser only.</p><p><a href='https://cyphermonkeylabs.com'>cyphermonkeylabs.com</a></p><button type='button' class='btn' id='eggClose'>Close</button></div>";
  document.body.appendChild(egg);
  $("#eggClose").addEventListener("click", function () { egg.hidden = true; });
  var konami = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"];
  var progress = 0;
  document.addEventListener("keydown", function (event) {
    var tag = (event.target && event.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    var key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    if (key === konami[progress]) {
      progress += 1;
      if (progress === konami.length) {
        progress = 0;
        egg.hidden = false;
        award("konami");
      }
    } else {
      progress = key === konami[0] ? 1 : 0;
    }
  });

  mountPortsGame();
  mountMap();
  mountSandbox();
  mountDaily();
  mountBadges();
  mountErlang();
})();
