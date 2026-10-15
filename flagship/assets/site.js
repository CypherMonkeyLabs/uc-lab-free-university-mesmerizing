(function () {
  "use strict";

  var THEMES = ["neon", "holographic", "cyberpunk", "sunset", "light"];
  var root = document.documentElement;
  var I18N = {
    en: { skip: "Skip to content", brandSub: "Free University", greet: "Welcome to the lab", heroTitle: "Voice, UC, and contact center.", heroLede: "Fundamentals, then the edge, the cloud, and the systems around the agent.", startPath: "Start the path", openDiagrams: "Open diagrams", campus: "Deep campus", wall: "Signal wall", next: "Where to go next", audioTitle: "Architect conversation", searchPh: "Search", langLabel: "Language", mode: "Light", modeDark: "Dark", navHome: "Home", navDiagrams: "Diagrams", navFlows: "Flows", navCharts: "Charts", navCheats: "Cheat Codes", navPlay: "Play", navEco: "Ecosystem", navDownloads: "Downloads", navCareers: "Careers" },
    es: { skip: "Saltar al contenido", brandSub: "Universidad libre", greet: "Bienvenido al laboratorio", heroTitle: "Voz, UC y centro de contacto.", heroLede: "Primero lo fundamental, luego el borde, la nube y los sistemas junto al agente.", startPath: "Empezar la ruta", openDiagrams: "Abrir diagramas", campus: "Campus profundo", wall: "Muro de señal", next: "A dónde seguir", audioTitle: "Conversación de arquitectos", searchPh: "Buscar", langLabel: "Idioma", mode: "Claro", modeDark: "Oscuro", navHome: "Inicio", navDiagrams: "Diagramas", navFlows: "Flujos", navCharts: "Gráficos", navCheats: "Chuletas", navPlay: "Jugar", navEco: "Ecosistema", navDownloads: "Descargas", navCareers: "Carreras" },
    hi: { skip: "सामग्री पर जाएँ", brandSub: "मुक्त विश्वविद्यालय", greet: "प्रयोगशाला में स्वागत है", heroTitle: "वॉइस, यूसी और कॉन्टैक्ट सेंटर।", heroLede: "पहले मूल बातें, फिर एज, क्लाउड, और एजेंट के आसपास के सिस्टम।", startPath: "पथ शुरू करें", openDiagrams: "आरेख खोलें", campus: "गहरा परिसर", wall: "सिग्नल दीवार", next: "आगे कहाँ", audioTitle: "आर्किटेक्ट बातचीत", searchPh: "खोजें", langLabel: "भाषा", mode: "हल्का", modeDark: "गहरा", navHome: "होम", navDiagrams: "आरेख", navFlows: "प्रवाह", navCharts: "चार्ट", navCheats: "चीट कोड", navPlay: "खेल", navEco: "पारिस्थितिकी", navDownloads: "डाउनलोड", navCareers: "करियर" },
    te: { skip: "విషయానికి వెళ్లండి", brandSub: "ఉచిత విశ్వవిద్యాలయం", greet: "ప్రయోగశాలకు స్వాగతం", heroTitle: "వాయిస్, యూసీ, కాంటాక్ట్ సెంటర్.", heroLede: "ముందు మూలాలు, తర్వాత ఎడ్జ్, క్లౌడ్, ఏజెంట్ చుట్టూ ఉన్న వ్యవస్థలు.", startPath: "మార్గం ప్రారంభించండి", openDiagrams: "చిత్రాలు తెరవండి", campus: "లోతైన క్యాంపస్", wall: "సిగ్నల్ గోడ", next: "తర్వాత ఎక్కడ", audioTitle: "ఆర్కిటెక్ట్ సంభాషణ", searchPh: "వెతకండి", langLabel: "భాష", mode: "వెలుతురు", modeDark: "చీకటి", navHome: "హోమ్", navDiagrams: "చిత్రాలు", navFlows: "ప్రవాహాలు", navCharts: "చార్టులు", navCheats: "చీట్ కోడ్స్", navPlay: "ఆట", navEco: "పర్యావరణం", navDownloads: "డౌన్‌లోడ్", navCareers: "వృత్తి" },
    fr: { skip: "Aller au contenu", brandSub: "Université libre", greet: "Bienvenue dans le laboratoire", heroTitle: "Voix, UC et centre de contact.", heroLede: "D'abord les bases, puis la bordure, le cloud, et les systèmes autour de l'agent.", startPath: "Commencer le parcours", openDiagrams: "Ouvrir les schémas", campus: "Campus approfondi", wall: "Mur de signal", next: "Où aller ensuite", audioTitle: "Conversation d'architectes", searchPh: "Rechercher", langLabel: "Langue", mode: "Clair", modeDark: "Sombre", navHome: "Accueil", navDiagrams: "Schémas", navFlows: "Flux", navCharts: "Graphiques", navCheats: "Antisèches", navPlay: "Jouer", navEco: "Écosystème", navDownloads: "Téléchargements", navCareers: "Carrières" },
    de: { skip: "Zum Inhalt", brandSub: "Freie Universität", greet: "Willkommen im Labor", heroTitle: "Sprache, UC und Contact Center.", heroLede: "Zuerst die Grundlagen, dann der Rand, die Cloud und die Systeme um den Agenten.", startPath: "Pfad starten", openDiagrams: "Diagramme öffnen", campus: "Tiefer Campus", wall: "Signalwand", next: "Wohin als Nächstes", audioTitle: "Architekten-Gespräch", searchPh: "Suchen", langLabel: "Sprache", mode: "Hell", modeDark: "Dunkel", navHome: "Start", navDiagrams: "Diagramme", navFlows: "Abläufe", navCharts: "Balken", navCheats: "Spickzettel", navPlay: "Spielen", navEco: "Ökosystem", navDownloads: "Downloads", navCareers: "Beruf" },
    ja: { skip: "本文へ", brandSub: "フリー大学", greet: "ラボへようこそ", heroTitle: "音声、UC、コンタクトセンター。", heroLede: "基礎から、エッジ、クラウド、エージェント周りのシステムへ。", startPath: "経路を始める", openDiagrams: "図を開く", campus: "深いキャンパス", wall: "シグナルの壁", next: "次に行く場所", audioTitle: "アーキテクトの対話", searchPh: "検索", langLabel: "言語", mode: "ライト", modeDark: "ダーク", navHome: "ホーム", navDiagrams: "図", navFlows: "フロー", navCharts: "チャート", navCheats: "チート", navPlay: "プレイ", navEco: "エコシステム", navDownloads: "ダウンロード", navCareers: "キャリア" },
    ar: { skip: "انتقل إلى المحتوى", brandSub: "جامعة حرة", greet: "أهلًا بك في المختبر", heroTitle: "الصوت والاتصالات ومركز الاتصال.", heroLede: "الأساسيات أولًا، ثم الحافة والسحابة والأنظمة حول الوكيل.", startPath: "ابدأ المسار", openDiagrams: "افتح المخططات", campus: "الحرم العميق", wall: "جدار الإشارة", next: "إلى أين بعد ذلك", audioTitle: "حوار المهندسين", searchPh: "بحث", langLabel: "اللغة", mode: "فاتح", modeDark: "داكن", navHome: "الرئيسية", navDiagrams: "المخططات", navFlows: "التدفقات", navCharts: "الرسوم", navCheats: "أوراق المراجعة", navPlay: "العب", navEco: "المنظومة", navDownloads: "التنزيلات", navCareers: "المسار المهني" }
  };
  var lang = "en";
  function pack() { return I18N[lang] || I18N.en; }
  function label(key) { return pack()[key] || I18N.en[key] || key; }
  function applyLang() {
    $all("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (key === "mode") return;
      if (pack()[key]) el.textContent = pack()[key];
    });
    $all("[data-i18n-placeholder]").forEach(function (el) {
      el.setAttribute("placeholder", label(el.getAttribute("data-i18n-placeholder")));
    });
    root.lang = lang;
    root.dir = lang === "ar" ? "rtl" : "ltr";
    var sel = $("#langSwitch");
    if (sel) sel.value = lang;
    var modeBtn = $(".mode-btn");
    if (modeBtn) modeBtn.textContent = root.getAttribute("data-theme") === "light" ? label("modeDark") : label("mode");
  }

  function $(sel, base) { return (base || document).querySelector(sel); }
  function $all(sel, base) { return Array.prototype.slice.call((base || document).querySelectorAll(sel)); }

  var lastDark = "neon";
  function setTheme(name) {
    if (THEMES.indexOf(name) < 0) name = "neon";
    if (name !== "light") lastDark = name;
    root.setAttribute("data-theme", name);
    try { localStorage.setItem("uc_flagship_theme", name); } catch (err) { /* private mode */ }
    $all(".themes button").forEach(function (btn) {
      btn.setAttribute("aria-checked", btn.getAttribute("data-theme-set") === name ? "true" : "false");
    });
    var modeBtn = $(".mode-btn");
    if (modeBtn) modeBtn.textContent = name === "light" ? label("modeDark") : label("mode");
    if (window.UC_APPLY_THEME) window.UC_APPLY_THEME();
  }

  $all(".themes button").forEach(function (btn) {
    btn.addEventListener("click", function () { setTheme(btn.getAttribute("data-theme-set")); });
  });
  setTheme(root.getAttribute("data-theme") || "neon");
  var modeBtn = $(".mode-btn");
  if (modeBtn) {
    modeBtn.addEventListener("click", function () {
      setTheme(root.getAttribute("data-theme") === "light" ? lastDark : "light");
    });
  }
  try {
    var asked = new URLSearchParams(window.location.search).get("theme");
    if (asked) setTheme(asked);
  } catch (err) { /* no query */ }
  try { lang = localStorage.getItem("uc_flagship_lang") || root.lang || "en"; } catch (err) { lang = "en"; }
  if (!I18N[lang]) lang = "en";
  applyLang();
  var langSel = $("#langSwitch");
  if (langSel) {
    langSel.addEventListener("change", function () {
      lang = I18N[langSel.value] ? langSel.value : "en";
      try { localStorage.setItem("uc_flagship_lang", lang); } catch (err) { /* private */ }
      applyLang();
    });
  }

  var menu = $(".menu-btn");
  if (menu) {
    menu.addEventListener("click", function () {
      var open = document.querySelector(".topbar").classList.toggle("open");
      menu.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var motionBtn = $(".motion-btn");
  function motionNow() {
    return root.getAttribute("data-motion") || "system";
  }
  if (motionBtn) {
    motionBtn.addEventListener("click", function () {
      var next = motionNow() === "reduce" ? "allow" : "reduce";
      root.setAttribute("data-motion", next);
      try { localStorage.setItem("uc_flagship_motion", next); } catch (err) { /* private mode */ }
      motionBtn.textContent = next === "reduce" ? "Motion off" : "Motion on";
    });
  }

  function tick() {
    if (motionNow() === "reduce") return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches && motionNow() !== "allow") return;
    try {
      var ctx = new (window.AudioContext || window.webkitAudioContext)();
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.frequency.value = 660;
      gain.gain.value = 0.03;
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.04);
    } catch (err) { /* no audio */ }
  }

  function mountLadders() {
    $all("[data-ladder]").forEach(function (box) {
      var msgs = $all(".msg", box);
      if (!msgs.length) return;
      var i = 0;
      var timer = null;
      function show(n) {
        i = (n + msgs.length) % msgs.length;
        msgs.forEach(function (el, idx) { el.classList.toggle("is-on", idx === i); });
        var cap = $(".ladder-cap", box);
        if (cap) cap.textContent = msgs[i].getAttribute("data-cap") || "";
      }
      show(0);
      function stop() {
        if (timer) clearInterval(timer);
        timer = null;
      }
      $all("[data-act]", box).forEach(function (btn) {
        btn.addEventListener("click", function () {
          var act = btn.getAttribute("data-act");
          if (act === "prev") { stop(); show(i - 1); tick(); }
          if (act === "next") { stop(); show(i + 1); tick(); if (window.UC_FLAGSHIP) window.UC_FLAGSHIP.award("ladder"); }
          if (act === "play") {
            if (timer) { stop(); btn.textContent = "Play"; return; }
            btn.textContent = "Pause";
            timer = setInterval(function () { show(i + 1); }, 900);
          }
        });
      });
    });
  }

  function reduced() {
    if (motionNow() === "reduce") return true;
    if (motionNow() === "allow") return false;
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function mountFabric(canvas) {
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext("2d");
    var broken = {};
    var ang = 0.4;
    var nodes = [
      { id: "phone", x: -1.35, y: 0.35, z: 0.1, label: "Phone" },
      { id: "cucm", x: -0.25, y: -0.15, z: 0.35, label: "CUCM" },
      { id: "cube", x: 0.85, y: 0.25, z: -0.15, label: "CUBE" },
      { id: "pstn", x: 1.7, y: 0.05, z: 0.25, label: "PSTN" },
      { id: "webex", x: 0.15, y: -0.95, z: -0.2, label: "Webex" }
    ];
    var links = [
      ["phone", "cucm", "SIP"],
      ["cucm", "cube", "Trunk"],
      ["cube", "pstn", "ITSP"],
      ["cucm", "webex", "LGW"]
    ];
    function resize() {
      var rect = canvas.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
    }
    resize();
    window.addEventListener("resize", resize);
    $all("[data-break]").forEach(function (box) {
      box.addEventListener("change", function () {
        broken[box.getAttribute("data-break")] = box.checked;
      });
    });
    function byId(id) {
      for (var n = 0; n < nodes.length; n += 1) if (nodes[n].id === id) return nodes[n];
      return nodes[0];
    }
    function project(p, a) {
      var x = p.x * Math.cos(a) - p.z * Math.sin(a);
      var z = p.x * Math.sin(a) + p.z * Math.cos(a);
      var depth = z + 4.2;
      var scale = (canvas.width * 0.22) / depth;
      return {
        x: canvas.width / 2 + x * scale,
        y: canvas.height * 0.48 + p.y * scale,
        r: Math.max(16, scale * 0.28)
      };
    }
    function frame() {
      if (!reduced()) ang += 0.004;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      var placed = {};
      nodes.forEach(function (n) { placed[n.id] = project(n, ang); });
      links.forEach(function (link) {
        var a = placed[link[0]];
        var b = placed[link[1]];
        var down = broken[link[0] + "-" + link[1]];
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = down ? "#e11d48" : "rgba(244,239,230,0.75)";
        ctx.lineWidth = down ? 3 : 2;
        ctx.setLineDash(down ? [6, 6] : []);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = "rgba(244,239,230,0.8)";
        ctx.font = "12px Segoe UI, sans-serif";
        ctx.fillText(down ? "down" : link[2], (a.x + b.x) / 2, (a.y + b.y) / 2 - 8);
      });
      nodes.forEach(function (n) {
        var p = placed[n.id];
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "#0f6e62";
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#f4efe6";
        ctx.stroke();
        ctx.fillStyle = "#f4efe6";
        ctx.font = "bold 13px Segoe UI, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(n.label, p.x, p.y + p.r + 16);
      });
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function bank() { return window.UC_FLAGSHIP_BANK || { questions: [], cards: [], scenarios: [], pr2Cards: [] }; }

  function mountQuiz() {
    var host = $("#quiz");
    if (!host) return;
    var data = bank().questions || [];
    var totalEl = $("#quizTotal");
    if (totalEl) totalEl.textContent = String(data.length);
    var tracks = {};
    data.forEach(function (q) { tracks[q.track || "General"] = true; });
    var select = $("#quizTrack");
    if (select) {
      Object.keys(tracks).sort().forEach(function (name) {
        var opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
      });
    }
    var cursor = 0;
    var correct = 0;
    var answered = 0;
    var deck = data.slice();
    function filtered() {
      var name = select ? select.value : "all";
      deck = data.filter(function (q) { return name === "all" || q.track === name; });
      cursor = 0;
      render();
    }
    function render() {
      var q = deck[cursor];
      var box = $("#quizCard");
      if (box) box.removeAttribute("data-locked");
      if (!q) {
        box.innerHTML = "<p>This track has no questions in the bank.</p>";
        return;
      }
      var html = "<p class='kicker'>" + escapeHtml(q.track) + " · " + (cursor + 1) + " / " + deck.length + "</p>";
      html += "<h2>" + escapeHtml(q.q) + "</h2>";
      (q.choices || []).forEach(function (choice, idx) {
        html += "<button type='button' class='choice' data-i='" + idx + "'>" + escapeHtml(choice) + "</button>";
      });
      html += "<p id='quizWhy' class='muted'></p>";
      box.innerHTML = html;
      $("#quizScore").textContent = correct + " correct · " + answered + " answered · " + data.length + " in the bank";
      $all(".choice", box).forEach(function (btn) {
        btn.addEventListener("click", function () {
          if (box.getAttribute("data-locked") === "1") return;
          box.setAttribute("data-locked", "1");
          var pick = Number(btn.getAttribute("data-i"));
          answered += 1;
          var good = pick === q.answer;
          if (good) {
            correct += 1;
            if (window.confetti) window.confetti({ particleCount: 70, spread: 62, origin: { y: 0.65 } });
          }
          btn.classList.add(good ? "good" : "bad");
          $all(".choice", box)[q.answer].classList.add("good");
          $("#quizWhy").textContent = q.why ? ("Reason in the bank: " + q.why) : "";
          if (window.UC_FLAGSHIP) window.UC_FLAGSHIP.award("quiz");
          $("#quizScore").textContent = correct + " correct · " + answered + " answered · " + data.length + " in the bank";
          try { localStorage.setItem("uc_flagship_quiz", JSON.stringify({ correct: correct, answered: answered })); } catch (err) { /* private */ }
        });
      });
    }
    if (select) select.addEventListener("change", filtered);
    var next = $("#quizNext");
    if (next) next.addEventListener("click", function () {
      if (!deck.length) return;
      cursor = (cursor + 1) % deck.length;
      var box = $("#quizCard");
      if (box) box.removeAttribute("data-locked");
      render();
    });
    filtered();
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function mountCards() {
    var host = $("#cards");
    if (!host) return;
    var data = bank();
    var decks = {
      pool: data.cards || [],
      study: data.pr2Cards || []
    };
    var name = "pool";
    var index = 0;
    var revealed = false;
    var known = {};
    function key() { return "uc_flagship_cards_" + name; }
    function load() {
      try { known = JSON.parse(localStorage.getItem(key()) || "{}"); } catch (err) { known = {}; }
    }
    function save() {
      try { localStorage.setItem(key(), JSON.stringify(known)); } catch (err) { /* private */ }
    }
    function deck() { return decks[name] || []; }
    function counts() {
      var list = deck();
      var k = 0;
      list.forEach(function (card, i) { if (known[card.id || card.term || i]) k += 1; });
      var el = $("#cardCounts");
      if (el) el.textContent = "Known " + k + " · Remaining " + (list.length - k) + " · Deck " + list.length;
    }
    function render() {
      var list = deck();
      var card = list[index];
      var face = $("#cardFace");
      if (!card) { face.textContent = "This deck is empty."; return; }
      var front = card.q || card.term;
      var back = card.a || card.def;
      var cite = card.cite || card.track || "";
      face.innerHTML = revealed
        ? "<p class='kicker'>Answer</p><p class='term'>" + escapeHtml(back) + "</p><p>" + escapeHtml(card.why && card.why !== back ? card.why : "") + "</p><p class='muted'>" + escapeHtml(cite) + "</p>"
        : "<p class='kicker'>Card " + (index + 1) + " of " + list.length + "</p><p class='term'>" + escapeHtml(front) + "</p><p class='muted'>Click to flip</p>";
      counts();
    }
    load();
    $("#cardFace").addEventListener("click", function () { revealed = !revealed; render(); });
    $("#cardKnow").addEventListener("click", function () {
      var card = deck()[index];
      if (!card) return;
      known[card.id || card.term || index] = true;
      save();
      if (window.UC_FLAGSHIP) window.UC_FLAGSHIP.award("card");
      revealed = false;
      index = (index + 1) % deck().length;
      render();
    });
    $("#cardAgain").addEventListener("click", function () {
      var card = deck()[index];
      if (!card) return;
      delete known[card.id || card.term || index];
      save();
      revealed = false;
      index = (index + 1) % deck().length;
      render();
    });
    $("#cardDeck").addEventListener("change", function (ev) {
      name = ev.target.value;
      index = 0;
      revealed = false;
      load();
      render();
    });
    render();
  }

  function mountCases() {
    var host = $("#casePlayer");
    if (!host) return;
    var scenarios = bank().scenarios || [];
    var current = scenarios[0];
    var nodeId = current ? current.start : "";
    function find(id) {
      for (var i = 0; i < scenarios.length; i += 1) if (scenarios[i].id === id) return scenarios[i];
      return scenarios[0];
    }
    function render() {
      if (!current) { host.textContent = "No cases in the bank."; return; }
      var node = (current.nodes || {})[nodeId];
      if (!node) { host.textContent = "This case has no node."; return; }
      var html = "<p class='kicker'>" + escapeHtml(current.title) + "</p>";
      html += "<p>" + escapeHtml(node.text || "") + "</p>";
      if (node.solved) html += "<p class='callout mint'>Solved. Open the next case when you can say which leg moved.</p>";
      (node.choices || []).forEach(function (choice, idx) {
        html += "<button type='button' class='case-choice' data-i='" + idx + "'>" + escapeHtml(choice.label) + "</button>";
      });
      if (node.next && !node.choices) {
        html += "<button type='button' class='btn' id='caseBack'>Go back</button>";
      }
      host.innerHTML = html;
      $all(".case-choice", host).forEach(function (btn) {
        btn.addEventListener("click", function () {
          var choice = node.choices[Number(btn.getAttribute("data-i"))];
          btn.classList.add(choice.good ? "good" : "bad");
          if (window.UC_FLAGSHIP) window.UC_FLAGSHIP.award("case");
          var note = document.createElement("p");
          note.className = "muted";
          note.textContent = choice.note || "";
          host.appendChild(note);
          if (choice.next && current.nodes[choice.next]) nodeId = choice.next;
          setTimeout(render, 700);
        });
      });
      var back = $("#caseBack");
      if (back) back.addEventListener("click", function () { nodeId = node.next || current.start; render(); });
    }
    $all("[data-case]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        current = find(btn.getAttribute("data-case"));
        nodeId = current.start;
        render();
        host.scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "start" });
      });
    });
    render();
  }

  function mountGlossary() {
    var input = $("#glossQ");
    var out = $("#glossHits");
    if (!input || !out) return;
    var cards = (bank().cards || []).concat(bank().pr2Cards || []);
    var count = $("#glossCount");
    if (count) count.textContent = String(cards.length);
    function run() {
      var q = input.value.trim().toLowerCase();
      if (q.length < 2) { out.innerHTML = "<p class='muted'>Type at least two letters. " + cards.length + " entries are loaded.</p>"; return; }
      var hits = cards.filter(function (card) {
        var blob = ((card.term || card.q || "") + " " + (card.def || card.a || "")).toLowerCase();
        return blob.indexOf(q) >= 0;
      }).slice(0, 30);
      out.innerHTML = hits.map(function (card) {
        return "<article class='search-hit'><h3>" + escapeHtml(card.term || card.q) + "</h3><p>" + escapeHtml(card.def || card.a) + "</p><p class='muted'>" + escapeHtml(card.track || card.cite || "") + "</p></article>";
      }).join("") || "<p>No entry contains that text.</p>";
    }
    input.addEventListener("input", run);
    run();
  }

  function mountPorts() {
    var input = $("#portQ");
    var table = $("#portTable");
    if (!input || !table) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      $all("tbody tr", table).forEach(function (row) {
        row.hidden = q.length > 0 && row.textContent.toLowerCase().indexOf(q) < 0;
      });
      var shown = $all("tbody tr", table).filter(function (row) { return !row.hidden; }).length;
      var label = $("#portShown");
      if (label) label.textContent = String(shown);
    });
  }

  function mountCodec() {
    var form = $("#codecForm");
    if (!form) return;
    function calc() {
      var payload = Number($("#payload").value);
      var ptime = Number($("#ptime").value);
      var l2 = Number($("#l2").value);
      var l3 = (payload + 40) * 8 * (1000 / ptime) / 1000;
      var wire = (payload + 40 + l2) * 8 * (1000 / ptime) / 1000;
      $("#codecOut").textContent = l3.toFixed(1) + " kbit/s at layer 3, " + wire.toFixed(1) + " kbit/s with the layer-2 header you set.";
    }
    form.addEventListener("input", calc);
    calc();
  }

  function mountCssLab() {
    var list = $("#cssOrder");
    if (!list) return;
    var dial = $("#cssDial");
    var out = $("#cssOut");
    function judge() {
      var order = $all("li", list).map(function (li) { return li.getAttribute("data-part"); });
      var number = (dial.value || "").replace(/\s+/g, "");
      var emergencyFirst = order.indexOf("Emergency") < order.indexOf("PSTN");
      var hit = "";
      if (number === "911" || number === "933") {
        hit = emergencyFirst
          ? "911 matches the Emergency partition before 9.@ in PSTN. That is the order you want."
          : "911 is consumed by 9.@ in the PSTN partition because that partition is searched first. Emergency never gets a turn.";
      } else {
        hit = "A national number can use the PSTN partition. 911 is the pattern that must be ahead of it.";
      }
      out.textContent = "CSS order: " + order.join(" → ") + ". " + hit;
    }
    $all("[data-move]", list.parentElement).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var part = btn.getAttribute("data-move");
        var dir = Number(btn.getAttribute("data-dir"));
        var items = $all("li", list);
        var idx = items.findIndex(function (li) { return li.getAttribute("data-part") === part; });
        var swap = idx + dir;
        if (swap < 0 || swap >= items.length) return;
        if (dir < 0) list.insertBefore(items[idx], items[swap]);
        else list.insertBefore(items[swap], items[idx]);
        judge();
      });
    });
    dial.addEventListener("input", judge);
    judge();
  }

  function mountSip() {
    var input = $("#sipCode");
    var out = $("#sipOut");
    if (!input || !out) return;
    input.addEventListener("input", function () {
      var code = input.value.trim();
      var row = document.getElementById("sip-" + code);
      out.textContent = row ? row.getAttribute("data-mean") : "Type a response code that is in the table, such as 180, 183, 401, 407, 486, or 488.";
    });
  }

  mountLadders();
  mountFabric($("#fabric"));
  mountQuiz();
  mountCards();
  mountCases();
  mountGlossary();
  mountPorts();
  mountCodec();
  mountCssLab();
  mountSip();

  function award(id) {
    var got = {};
    try { got = JSON.parse(localStorage.getItem("uc_flagship_badges") || "{}"); } catch (err) { got = {}; }
    if (got[id]) return;
    got[id] = Date.now();
    try { localStorage.setItem("uc_flagship_badges", JSON.stringify(got)); } catch (err) { /* private */ }
    var note = document.createElement("p");
    note.className = "toast-note";
    var names = {
      ladder: "First step",
      quiz: "One honest answer",
      card: "Card turned",
      case: "Case opened",
      ports: "Port ear",
      daily: "Today's leg",
      sandbox: "Your ladder",
      map: "Map reader",
      konami: "Traversal zone",
      cheat: "Sheet in hand"
    };
    note.textContent = "Badge: " + (names[id] || id);
    document.body.appendChild(note);
    setTimeout(function () { note.remove(); }, 2200);
  }
  window.UC_FLAGSHIP = { award: award };

  function mountSearch() {
    var input = $("#siteSearch");
    var pop = $("#searchPop");
    if (!input || !pop) return;
    var items = window.UC_SEARCH || [];
    var prefix = (document.body && document.body.getAttribute("data-root")) || "";
    var cursor = -1;
    function close() { pop.hidden = true; cursor = -1; }
    function render(list) {
      pop.innerHTML = list.slice(0, 8).map(function (item, i) {
        var href = item.href.indexOf("http") === 0 ? item.href : prefix + item.href;
        return "<a href='" + href + "' data-i='" + i + "'" + (i === cursor ? " aria-selected='true'" : "") + ">" + item.title + "</a>";
      }).join("");
      pop.hidden = list.length === 0;
    }
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      cursor = 0;
      if (!q) { close(); return; }
      render(items.filter(function (item) {
        return (item.title + " " + item.text + " " + item.href).toLowerCase().indexOf(q) >= 0;
      }));
    });
    input.addEventListener("keydown", function (event) {
      var links = $all("a", pop);
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        if (!links.length) return;
        cursor = event.key === "ArrowDown" ? Math.min(links.length - 1, cursor + 1) : Math.max(0, cursor - 1);
        links.forEach(function (link, i) { link.setAttribute("aria-selected", i === cursor ? "true" : "false"); });
      } else if (event.key === "Enter" && links[cursor]) {
        event.preventDefault();
        window.location.href = links[cursor].getAttribute("href");
      } else if (event.key === "Escape") close();
    });
    document.addEventListener("keydown", function (event) {
      var tag = (event.target && event.target.tagName) || "";
      if (event.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") {
        event.preventDefault();
        input.focus();
      }
    });
  }
  function mountProgress() {
    var slot = $("#visitProgress");
    if (!slot) return;
    var id = "index.html";
    var path = location.pathname;
    var marker = "/flagship/";
    var at = path.indexOf(marker);
    if (at >= 0) id = path.slice(at + marker.length) || "index.html";
    else if (!(path.endsWith("/") || path.endsWith("/index.html"))) id = path.split("/").pop() || id;
    var seen = [];
    try { seen = JSON.parse(localStorage.getItem("uc_flagship_seen") || "[]"); } catch (err) { seen = []; }
    if (seen.indexOf(id) < 0) seen.push(id);
    try { localStorage.setItem("uc_flagship_seen", JSON.stringify(seen)); } catch (err) { /* private */ }
    var total = (window.UC_SEARCH || []).length || seen.length;
    slot.textContent = "Progress " + seen.length + " / " + total + " pages opened in this browser";
    var ring = $("#visitRing");
    if (ring) {
      var pct = Math.max(4, Math.min(100, Math.round(100 * seen.length / Math.max(total, 1))));
      ring.style.strokeDasharray = pct + " " + (100 - pct);
    }
  }
  function mountParallax() {
    var hosts = $all("[data-parallax]");
    if (!hosts.length) return;
    if (root.getAttribute("data-motion") === "reduce") return;
    window.addEventListener("scroll", function () {
      var y = window.scrollY || 0;
      hosts.forEach(function (host) {
        $all("[data-depth]", host).forEach(function (el) {
          var depth = Number(el.getAttribute("data-depth")) || 0.2;
          el.style.transform = "translate3d(0," + (-y * depth * 0.15) + "px,0)";
        });
      });
    }, { passive: true });
  }
  function mountLightbox() {
    var shots = $all(".shot");
    if (!shots.length) return;
    var box = document.createElement("div");
    box.className = "lightbox";
    box.hidden = true;
    box.innerHTML = '<div class="lightbox-card" role="dialog" aria-modal="true" aria-label="Diagram"><p class="kicker" id="lbTitle"></p><div id="lbStage"></div><p id="lbWhy"></p><p class="legend"><span><i style="background:#5eead4"></i>Request</span><span><i style="background:#fde047"></i>Provisional</span><span><i style="background:#86efac"></i>Success</span><span><i style="background:#fb7185"></i>Error or media</span></p><div class="actions"><button type="button" class="btn" data-lb="prev">Step back</button><button type="button" class="btn" data-lb="play">Play</button><button type="button" class="btn" data-lb="pause">Pause</button><button type="button" class="btn" data-lb="next">Step</button><button type="button" class="btn" data-lb="close">Close</button></div></div>';
    document.body.appendChild(box);
    var stage = $("#lbStage", box);
    var index = 0;
    var timer = null;
    function msgs() { return $all(".msg", stage); }
    function show(n) {
      var list = msgs();
      if (!list.length) return;
      index = (n + list.length) % list.length;
      list.forEach(function (el, i) { el.classList.toggle("is-on", i === index); });
    }
    function stop() { if (timer) clearInterval(timer); timer = null; }
    shots.forEach(function (shot) {
      shot.addEventListener("click", function () {
        stage.innerHTML = "";
        var graphic = shot.querySelector("svg, img");
        if (graphic) stage.appendChild(graphic.cloneNode(true));
        $("#lbTitle", box).textContent = (shot.getAttribute("aria-label") || (shot.querySelector("img") && shot.querySelector("img").alt) || "Diagram");
        $("#lbWhy", box).textContent = shot.getAttribute("data-why") || "";
        box.hidden = false;
        index = 0;
        show(0);
      });
    });
    box.addEventListener("click", function (event) {
      var act = event.target.getAttribute && event.target.getAttribute("data-lb");
      if (event.target === box) act = "close";
      if (act === "close") { stop(); box.hidden = true; stage.innerHTML = ""; }
      if (act === "prev") { stop(); show(index - 1); }
      if (act === "next") { stop(); show(index + 1); }
      if (act === "pause") {
        stop();
        $all("svg", stage).forEach(function (svg) { svg.style.animationPlayState = "paused"; svg.querySelectorAll("*").forEach(function (el) { el.style.animationPlayState = "paused"; }); });
      }
      if (act === "play") {
        $all("svg", stage).forEach(function (svg) { svg.style.animationPlayState = "running"; svg.querySelectorAll("*").forEach(function (el) { el.style.animationPlayState = "running"; }); });
        stop();
        if (msgs().length) timer = setInterval(function () { show(index + 1); }, 900);
      }
    });
    document.addEventListener("keydown", function (event) {
      if (box.hidden) return;
      if (event.key === "Escape") { stop(); box.hidden = true; }
    });
  }
  function mountChartTips() {
    var rows = $all(".bar-row");
    if (!rows.length) return;
    var tip = document.createElement("div");
    tip.className = "chart-tip";
    tip.hidden = true;
    document.body.appendChild(tip);
    rows.forEach(function (row) {
      function move(event) {
        var title = row.querySelector("title");
        tip.textContent = title ? title.textContent : "";
        tip.hidden = false;
        tip.style.left = (event.clientX + 12) + "px";
        tip.style.top = (event.clientY + 12) + "px";
      }
      row.addEventListener("pointerenter", move);
      row.addEventListener("pointermove", move);
      row.addEventListener("pointerleave", function () { tip.hidden = true; });
    });
  }
  function mountMascotCycle() {
    var variants = ["study", "alert", "celebrate", "night", "holo"];
    var step = 0;
    setInterval(function () {
      step = (step + 1) % variants.length;
      $all(".mascot").forEach(function (el, i) {
        el.setAttribute("data-variant", variants[(step + i) % variants.length]);
      });
    }, 180000);
  }
  mountSearch();
  mountProgress();
  mountParallax();
  mountLightbox();
  mountChartTips();
  mountMascotCycle();

  if ("serviceWorker" in navigator && location.protocol.indexOf("http") === 0) {
    var prefix = document.body.getAttribute("data-root") || "./";
    var script = new URL(prefix + "sw.js", window.location.href);
    navigator.serviceWorker.register(script.href).catch(function () { /* file or blocked */ });
  }
})();
