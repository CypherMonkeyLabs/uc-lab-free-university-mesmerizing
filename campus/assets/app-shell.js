/* UC Lab app shell. Offline. Keeps the existing curriculum and adds the dashboard, labs, and player. */
(function () {
  "use strict";

  var LAB_KEY = "uc_app_labs";
  var QUIZ_KEY = "uc_app_quiz";
  var CARD_KEY = "uc_app_cards";
  var LAST_KEY = "uc_app_last";
  var STREAK_KEY = "uc_app_streak";
  var badgeSnap = {};
  var simRAF = 0;
  var waveRAF = 0;
  var palIndex = 0;
  var returnFocus = null;
  var labKind = "simulator";
  var openedLabFromQuery = false;

  function reduced() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function fmt(n) {
    return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  function svg(body) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + body + "</svg>";
  }
  var ICONS = {
    start: svg('<path d="M12 3 4 7.5V12c0 4.5 3.2 7 8 8.5 4.8-1.5 8-4 8-8.5V7.5z"/><path d="m9 12 2 2 4-4"/>'),
    sip: svg('<path d="M4 7h16M4 12h10M4 17h16"/><path d="m14 10 4 2-4 2"/>'),
    cube: svg('<rect x="3" y="7" width="7" height="10" rx="1.5"/><rect x="14" y="7" width="7" height="10" rx="1.5"/><path d="M10 12h4"/>'),
    cloud: svg('<path d="M7 17h10a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.8-1.2A3 3 0 0 0 7 17z"/>'),
    queue: svg('<circle cx="7" cy="8" r="2"/><circle cx="17" cy="16" r="2"/><path d="M9 8h4a3 3 0 0 1 3 3v3"/>'),
    emergency: svg('<path d="M12 3 3 20h18z"/><path d="M12 9v5"/><path d="M12 17h.01"/>'),
    qos: svg('<path d="M4 17h16M7 17V9M12 17V6M17 17v-5"/>'),
    move: svg('<path d="M4 8h12M4 16h12M14 5l3 3-3 3M8 13l-3 3 3 3"/>'),
    tree: svg('<path d="M12 4v6M12 10H7v4M12 10h5v4"/><circle cx="12" cy="4" r="1.4"/>'),
    proof: svg('<path d="m5 12 4 4 10-10"/>'),
    design: svg('<circle cx="6" cy="12" r="2"/><circle cx="18" cy="7" r="2"/><circle cx="18" cy="17" r="2"/><path d="M8 12h6M14 12l2-4M14 12l2 4"/>'),
    book: svg('<path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H20v16H7.5A2.5 2.5 0 0 0 5 21.5z"/><path d="M5 5.5A2.5 2.5 0 0 1 7.5 8H20"/>'),
    phone: svg('<path d="M8 4h3l1 3-2 1a8 8 0 0 0 4 4l1-2 3 1v3a2 2 0 0 1-2 2A12 12 0 0 1 6 6a2 2 0 0 1 2-2z"/>'),
    sun: svg('<circle cx="12" cy="12" r="3.5"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/>'),
    moon: svg('<path d="M16 3.5A8.5 8.5 0 1 0 20.5 14 7 7 0 0 1 16 3.5z"/>'),
    labs: svg('<path d="M9 3h6M10 3v6L5 19a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-10V3"/>')
  };

  var TRACKS = [
    { group: "Start here", id: "home", icon: "start", color: "#0F9B8E", why: "You cannot troubleshoot a call you cannot name. LICC is the habit the rest of the campus assumes." },
    { group: "SIP and media", id: "proto-sip-master", icon: "sip", color: "#6366F1", why: "Signaling can succeed while the caller hears nothing. Separate the ladder from RTP." },
    { group: "CUCM and CUBE", id: "prod-cube", icon: "cube", color: "#159947", why: "Digit analysis and the border decide whether the call leaves the campus, and on which Call-ID." },
    { group: "Webex Calling and Teams Phone", id: "vd-webex-calling-call-flow", icon: "cloud", color: "#0891B2", why: "The PSTN still lands on a gateway you can prove. The cloud name does not remove the dial plan." },
    { group: "Contact center — UCCE and PCCE", id: "hub-icm-ucce", icon: "queue", color: "#7C3AED", why: "The contact is a script, a queue, and a desktop. The report sits beside that path." },
    { group: "CCaaS and UCaaS platforms", id: "prod-wxcc", icon: "cloud", color: "#4F46E5", why: "Every platform has an entry, a flow, a queue, and an agent id. Learn the shape, then the vendor names." },
    { group: "Emergency calling", id: "found-11", icon: "emergency", color: "#E11D48", why: "A connected call with the wrong location is a failed emergency call." },
    { group: "Voice network and QoS", id: "hub-qos", icon: "qos", color: "#0F766E", why: "Voice bearer needs a measured delay budget. Marking EF is not the same as proving the WAN kept it." },
    { group: "Migrations", id: "hub-migrations", icon: "move", color: "#E08A00", why: "Two systems will own the number for a while. Rollback has to be rehearsed before the window." },
    { group: "Troubleshooting", id: "trick-0", icon: "tree", color: "#B45309", why: "One hypothesis, one change, one evidence pack. Everything else is noise on the bridge." },
    { group: "Evidence habits", id: "mm-licc", icon: "proof", color: "#047857", why: "The person who was not on the call has to be able to read what you captured." },
    { group: "Design notes", id: "arch-capacity", icon: "design", color: "#1D4ED8", why: "Capacity, identity, recording, and failure domains decide the design before the product name does." },
    { group: "Practice", id: "drill-sip-dialplan-licc", icon: "proof", color: "#BE185D", why: "Drill the fault before a customer is waiting on the line." },
    { group: "Reference", id: "glossary", icon: "book", color: "#64748B", why: "Names drift. The glossary gets you to the current vendor document." }
  ];

  function trackFor(group) {
    for (var i = 0; i < TRACKS.length; i++) if (TRACKS[i].group === group) return TRACKS[i];
    return TRACKS[0];
  }
  function sections() { return window.SECTIONS || []; }
  function findSection(id) {
    var list = sections();
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }
  function inGroup(group) {
    var out = [];
    sections().forEach(function (s) { if (s.group === group) out.push(s); });
    return out;
  }
  function readJson(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || "") || fallback; } catch (e) { return fallback; }
  }
  function writeJson(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }
  function progressIds() {
    var ids = {};
    var studied = readJson("uc_studied_sections", {});
    Object.keys(studied).forEach(function (k) { if (studied[k]) ids[k] = 1; });
    if (window.UCProgress && window.UCProgress.load) {
      var state = window.UCProgress.load();
      Object.keys(state.seen || {}).forEach(function (k) { ids[k] = 1; });
    }
    return ids;
  }
  function labState() { return readJson(LAB_KEY, {}); }
  function markLab(name) {
    var state = labState();
    state[name] = 1;
    writeJson(LAB_KEY, state);
    announceNewBadges();
  }
  function liveCounts() {
    var c = window.UC_VISUAL_COUNTS || {};
    return {
      sections: c.sections || sections().length || 476,
      flows: c.flowDefinitions || (window.UC_FLOW_CATALOG || []).length || 978,
      illustrations: c.illustrations || 2772,
      tracks: c.trackHubs || TRACKS.length
    };
  }
  function tween(el, to) {
    if (!el) return;
    if (reduced()) { el.textContent = fmt(to); return; }
    var start = performance.now();
    function tick(now) {
      var p = Math.min(1, (now - start) / 680);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(to * eased);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  function go(id) {
    if (window.openSection) window.openSection(id);
  }


  var LABS = [
    { id: "simulator", short: "Call flow", title: "Call-flow simulator", icon: "phone", color: "#0F9B8E", blurb: "Place a call and watch SIP move apart from RTP." },
    { id: "dial", short: "Dial plan", title: "Dial-plan builder", icon: "design", color: "#6366F1", blurb: "Build the path from CSS to the CUBE trunk." },
    { id: "ivr", short: "IVR", title: "IVR sandbox", icon: "queue", color: "#7C3AED", blurb: "Send a digit into a queue, or show where it dies." },
    { id: "sipdec", short: "SIP decode", title: "SIP message decoder", icon: "sip", color: "#4F46E5", blurb: "Paste a message or click a header and read the job." },
    { id: "codec", short: "Codec", title: "Codec and bandwidth", icon: "qos", color: "#0F766E", blurb: "Turn payload and headers into kbit/s." },
    { id: "jitter", short: "Jitter", title: "RTP jitter and loss", icon: "qos", color: "#0891B2", blurb: "See late and missing packets on a teaching chart." },
    { id: "route", short: "Route", title: "CUCM routing tracer", icon: "cube", color: "#159947", blurb: "Watch CSS order and the partition that wins." },
    { id: "webex", short: "Webex PSTN", title: "Webex Calling location", icon: "cloud", color: "#0891B2", blurb: "Build a location and name the PSTN path." },
    { id: "ucce", short: "UCCE", title: "UCCE router", icon: "queue", color: "#7C3AED", blurb: "Follow a dialed number into a call type and skill group." },
    { id: "finesse", short: "Finesse", title: "Finesse agent states", icon: "phone", color: "#BE185D", blurb: "Walk the desktop states the router can see." },
    { id: "e911", short: "E911", title: "E911 and RedSky", icon: "emergency", color: "#E11D48", blurb: "Order discovery, location, callback, and proof." },
    { id: "qos", short: "QoS", title: "QoS marking game", icon: "qos", color: "#0F766E", blurb: "Mark the class, then give it a real queue." },
    { id: "srtp", short: "SRTP", title: "SRTP and TLS flight", icon: "proof", color: "#1D4ED8", blurb: "Step the teaching handshake. Signaling is not media." },
    { id: "erlang", short: "Erlang", title: "Erlang-C staffing", icon: "design", color: "#B45309", blurb: "Turn calls and handle time into a teaching staff count." },
    { id: "fault", short: "Find fault", title: "Find the fault", icon: "tree", color: "#B45309", blurb: "Name the next proof, not a second guess." },
    { id: "dialpeer", short: "Dial-peer", title: "CUBE dial-peer match", icon: "cube", color: "#159947", blurb: "Longest match, then the lowest preference." },
    { id: "nat", short: "One-way", title: "One-way audio", icon: "sip", color: "#E08A00", blurb: "The ladder is up. The SDP address is not reachable." },
    { id: "record", short: "Record", title: "Recording fork", icon: "proof", color: "#047857", blurb: "Fork the media where the PSTN audio actually is." },
    { id: "quiz", short: "Quiz", title: "Quiz", icon: "proof", color: "#E08A00", blurb: "A scored drill from the track bank, with the reason." },
    { id: "cards", short: "Cards", title: "Flashcards", icon: "book", color: "#0891B2", blurb: "Flip a term, then say why you would use it." },
    { id: "boss", short: "Boss", title: "Boss exam", icon: "start", color: "#E11D48", blurb: "One sitting across the tracks. Eighty percent to pass." }
  ];

  function labById(id) {
    for (var i = 0; i < LABS.length; i++) if (LABS[i].id === id) return LABS[i];
    return LABS[0];
  }
  function knownLab(id) {
    for (var i = 0; i < LABS.length; i++) if (LABS[i].id === id) return true;
    return false;
  }
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
  function dayKey(date) {
    return date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
  }
  function streakState() {
    return readJson(STREAK_KEY, { last: "", n: 0 });
  }
  function touchStreak() {
    var row = streakState();
    var today = new Date();
    var key = dayKey(today);
    if (row.last === key) return row;
    var prior = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1);
    row.n = row.last === dayKey(prior) ? (Number(row.n) || 0) + 1 : 1;
    row.last = key;
    writeJson(STREAK_KEY, row);
    return row;
  }
  function earnedBadges() {
    var labs = labState();
    var tried = 0;
    var all = true;
    LABS.forEach(function (lab) {
      if (labs[lab.id]) tried += 1;
      else all = false;
    });
    var opened = Object.keys(progressIds()).length;
    var streak = Number(streakState().n) || 0;
    var quiz = quizStore();
    var sharp = false;
    Object.keys(quiz.tracks || {}).forEach(function (name) {
      var row = quiz.tracks[name];
      if (row && row.bestN && row.best / row.bestN >= 0.8) sharp = true;
    });
    var out = {};
    if (labs.simulator) out["first-call"] = "First call";
    if (labs.dial) out["dial-plan"] = "Dial plan";
    if (tried >= 5) out["five-labs"] = "Five labs";
    if (all) out["full-bench"] = "Full bench";
    if (opened >= 10) out.listener = "Listener";
    if (opened >= 50) out.cartographer = "Cartographer";
    if (streak >= 3) out["streak-3"] = "Three-day streak";
    if (streak >= 7) out["streak-7"] = "Seven-day streak";
    if (sharp) out["track-sharp"] = "Track sharp";
    if (quiz.boss && quiz.boss.passed) out.boss = "Boss exam";
    return out;
  }
  function ensureLive() {
    var el = document.getElementById("ucAppLive");
    if (el) return el;
    el = document.createElement("div");
    el.id = "ucAppLive";
    el.className = "uc-app-sr";
    el.setAttribute("aria-live", "polite");
    document.body.appendChild(el);
    return el;
  }
  function celebrate(name) {
    var live = ensureLive();
    live.textContent = "Badge earned: " + name + ".";
    if (reduced()) return;
    var layer = document.createElement("div");
    layer.className = "uc-app-confetti";
    layer.setAttribute("aria-hidden", "true");
    var colors = ["#0F9B8E", "#6366F1", "#F5B942", "#E11D48", "#22C55E"];
    for (var i = 0; i < 24; i++) {
      var bit = document.createElement("i");
      bit.style.left = (4 + Math.random() * 92) + "%";
      bit.style.background = colors[i % colors.length];
      bit.style.animationDelay = (Math.random() * 0.25) + "s";
      layer.appendChild(bit);
    }
    document.body.appendChild(layer);
    setTimeout(function () {
      if (layer.parentNode) layer.parentNode.removeChild(layer);
    }, 1700);
  }
  function announceNewBadges() {
    var now = earnedBadges();
    Object.keys(now).forEach(function (key) {
      if (!badgeSnap[key]) celebrate(now[key]);
    });
    badgeSnap = now;
  }
  function badgeRow() {
    var earned = earnedBadges();
    var catalog = [
      ["first-call", "First call"],
      ["dial-plan", "Dial plan"],
      ["five-labs", "Five labs"],
      ["full-bench", "Full bench"],
      ["listener", "Listener"],
      ["cartographer", "Cartographer"],
      ["streak-3", "3-day"],
      ["streak-7", "7-day"],
      ["track-sharp", "Track sharp"],
      ["boss", "Boss"]
    ];
    return catalog.map(function (item) {
      var on = !!earned[item[0]];
      return '<span class="uc-app-badge' + (on ? " is-on" : "") + '">' + esc(item[1]) + "</span>";
    }).join("");
  }
  function globeMarkup() {
    return '<div class="uc-app-globe" aria-hidden="true"><div class="uc-app-globe-spin">' +
      '<div class="uc-app-sphere"></div><span class="uc-app-orbit o1"></span><span class="uc-app-orbit o2"></span>' +
      '<span class="uc-app-nodelet n1"></span><span class="uc-app-nodelet n2"></span>' +
      '<span class="uc-app-nodelet n3"></span><span class="uc-app-nodelet n4"></span>' +
      "</div></div>";
  }
  function matchLab(section) {
    if (!section || section.id === "home") return null;
    var blob = (section.title + " " + section.id + " " + (section.sub || "")).toLowerCase();
    function hit(re) { return re.test(blob); }
    if (hit(/jitter|packet loss/)) return { lab: "jitter" };
    if (hit(/dscp|\bqos\b|\bllq\b|expedited|marking/)) return { lab: "qos" };
    if (hit(/srtp|dtls|\btls\b|certificate/)) return { lab: "srtp" };
    if (hit(/erlang|staffing|shrinkage/)) return { lab: "erlang" };
    if (hit(/finesse|agent state/)) return { lab: "finesse" };
    if (hit(/e911|redsky|\belin\b|kari|baum|dispatchable/)) return { lab: "e911" };
    if (hit(/local gateway|webex calling/)) return { lab: "webex" };
    if (hit(/direct routing|operator connect|teams phone/)) return { lab: "webex" };
    if (hit(/skill group|call type|precision queue|\bucce\b|\bpcce\b|\bcvp\b|\bicm\b/)) return { lab: "ucce" };
    if (hit(/dial-peer|dial peer|\bcube\b/)) return { lab: "dialpeer" };
    if (hit(/one-way|nat traversal|\bnat\b/)) return { lab: "nat" };
    if (hit(/recording|built-in bridge|\bbib\b/)) return { lab: "record" };
    if (hit(/codec|bandwidth|g\.711|g\.729|opus/)) return { lab: "codec" };
    if (hit(/hunt group|line group|hunt pilot/)) return { lab: "simulator", scenario: "hunt" };
    if (hit(/blind transfer/)) return { lab: "simulator", scenario: "blind" };
    if (hit(/\bconsult\b/)) return { lab: "simulator", scenario: "consult" };
    if (hit(/\btransfer\b/)) return { lab: "simulator", scenario: "consult" };
    if (hit(/conference/)) return { lab: "simulator", scenario: "conference" };
    if (hit(/expressway|\bmra\b/)) return { lab: "simulator", scenario: "mra" };
    if (hit(/callback/)) return { lab: "simulator", scenario: "callback" };
    if (hit(/failover/)) return { lab: "simulator", scenario: "failover" };
    if (hit(/\bivr\b|\bdtmf\b|prompt/)) return { lab: "ivr" };
    if (hit(/partition|calling search space|route pattern|\bcss\b/)) return { lab: "route" };
    if (hit(/via header|call-id|sip header|invite transaction/)) return { lab: "sipdec" };
    var group = section.group;
    if (group === "Start here") return { lab: "simulator", scenario: "station" };
    if (group === "SIP and media") return { lab: "sipdec" };
    if (group === "CUCM and CUBE") return { lab: "route" };
    if (group === "Webex Calling and Teams Phone") return { lab: "webex" };
    if (group === "Contact center — UCCE and PCCE") return { lab: "ucce" };
    if (group === "CCaaS and UCaaS platforms") return { lab: "erlang" };
    if (group === "Emergency calling") return { lab: "e911" };
    if (group === "Voice network and QoS") return { lab: "qos" };
    if (group === "Migrations") return { lab: "simulator", scenario: "failover" };
    if (group === "Troubleshooting" || group === "Evidence habits" || group === "Practice") return { lab: "fault" };
    if (group === "Design notes") return { lab: "codec" };
    if (group === "Reference") return { lab: "quiz" };
    return { lab: "fault" };
  }

  function mountDash() {
    var main = document.getElementById("main");
    var host = main && main.querySelector(".sec-container");
    if (!host) return;
    var prior = document.getElementById("ucAppDash");
    if (prior) prior.remove();
    var counts = liveCounts();
    var ids = progressIds();
    var total = Math.max(1, sections().length);
    var opened = 0;
    sections().forEach(function (s) { if (ids[s.id]) opened += 1; });
    var ratio = Math.max(0, Math.min(1, opened / total));
    var ring = 2 * Math.PI * 32;
    var labs = labState();
    var last = "";
    try { last = localStorage.getItem(LAST_KEY) || ""; } catch (e) {}
    var contId = last && last !== "home" && findSection(last) ? last : "proto-sip-master";
    var cont = findSection(contId);
    var dash = document.createElement("section");
    dash.id = "ucAppDash";
    dash.className = "uc-app-dash";
    dash.setAttribute("aria-label", "Campus dashboard");
    var streak = streakState();
    var streakText = (Number(streak.n) || 1) <= 1
      ? "Day 1 in this browser. Open the campus again tomorrow to start a streak."
      : streak.n + " day streak in this browser. It stays on this device.";
    dash.innerHTML =
      '<div class="uc-app-hero">' +
        '<div class="uc-app-hero-layout">' +
          '<div>' +
            '<p class="uc-app-kicker">UC Lab · offline campus</p>' +
            '<h1>Voice, UC, and contact center</h1>' +
            '<p class="uc-app-lead"><b>Why it matters.</b> The call, the border, the queue, and the proof have to stay separable. This file is the campus: open a track, or prove a path in a lab before you change anything real.</p>' +
            '<p class="uc-app-streak" id="ucAppStreak">' + esc(streakText) + '</p>' +
            '<div class="uc-app-badges" aria-label="Achievements">' + badgeRow() + '</div>' +
            '<div class="uc-app-counters">' +
              '<div class="uc-app-counter"><strong data-n="' + counts.sections + '">0</strong><span>Sections</span></div>' +
              '<div class="uc-app-counter"><strong data-n="' + counts.flows + '">0</strong><span>Flows</span></div>' +
              '<div class="uc-app-counter"><strong data-n="' + counts.illustrations + '">0</strong><span>Illustrations</span></div>' +
              '<div class="uc-app-counter"><strong data-n="' + counts.tracks + '">0</strong><span>Tracks</span></div>' +
            '</div>' +
          '</div>' +
          globeMarkup() +
        '</div>' +
        '<div class="uc-app-row">' +
          '<div class="uc-app-progress">' +
            '<div class="uc-app-ring" role="img" aria-label="' + opened + ' of ' + total + ' sections opened in this browser">' +
              '<svg viewBox="0 0 84 84"><g transform="rotate(-90 42 42)"><circle cx="42" cy="42" r="32" fill="none" stroke="currentColor" stroke-opacity=".15" stroke-width="8"/>' +
              '<circle cx="42" cy="42" r="32" fill="none" stroke="#0F9B8E" stroke-width="8" stroke-linecap="round" stroke-dasharray="' + ring.toFixed(2) + '" stroke-dashoffset="' + ((1 - ratio) * ring).toFixed(2) + '"/></g>' +
              '<text x="42" y="46" text-anchor="middle" fill="currentColor" font-size="14" font-weight="800" font-family="ui-sans-serif,system-ui">' + Math.round(ratio * 100) + '%</text></svg>' +
            '</div>' +
            '<div><h2>Progress stays in this browser</h2>' +
            '<p>' + opened + ' of ' + total + ' sections opened. Nothing is uploaded.</p>' +
            '<div class="uc-app-actions"><button type="button" class="uc-app-btn primary" data-go="' + esc(contId) + '" aria-label="Continue with ' + esc(cont ? cont.title : "SIP") + '">Continue</button></div></div>' +
          '</div>' +
          '<div class="uc-app-labs"><h2>Labs</h2><p>' + LABS.length + ' teaching models. They do not change a live system.</p><div class="uc-app-lab-grid">' +
            LABS.map(function (item) {
              return '<button type="button" class="uc-app-lab-launch" data-lab="' + item.id + '" style="--accent:' + item.color + '">' +
                (ICONS[item.icon] || "") + '<strong>' + esc(item.short) + '</strong><span>' + esc(item.blurb) + '</span>' +
                (labs[item.id] ? '<span class="uc-app-done">Tried</span>' : '') + '</button>';
            }).join("") +
          '</div></div>' +
        '</div>' +
      '</div>' +
      '<div class="uc-app-stage3d"><div class="uc-app-cards" role="list"></div></div>';
    var grid = dash.querySelector(".uc-app-cards");
    TRACKS.forEach(function (track) {
      var group = inGroup(track.group);
      var seen = 0;
      group.forEach(function (s) { if (ids[s.id]) seen += 1; });
      var width = group.length ? Math.round(seen / group.length * 100) : 0;
      var card = document.createElement("button");
      card.type = "button";
      card.className = "uc-app-card";
      card.setAttribute("role", "listitem");
      card.style.setProperty("--track", track.color);
      card.setAttribute("data-go", track.id);
      card.setAttribute("aria-label", track.group + ". " + track.why);
      card.innerHTML =
        '<span class="uc-app-shine" aria-hidden="true"></span>' +
        '<span class="uc-app-card-top"><span class="uc-app-ico">' + (ICONS[track.icon] || ICONS.proof) + '</span>' +
        '<span class="uc-app-card-count">' + seen + " / " + group.length + '</span></span>' +
        '<strong>' + esc(track.group) + '</strong><em>Why it matters</em>' +
        '<span class="uc-app-card-why">' + esc(track.why) + '</span>' +
        '<span class="uc-app-meter" aria-hidden="true"><span style="width:' + width + '%"></span></span>';
      if (!reduced()) {
        card.addEventListener("pointermove", function (e) {
          var rect = card.getBoundingClientRect();
          var px = (e.clientX - rect.left) / rect.width;
          var py = (e.clientY - rect.top) / rect.height;
          card.style.setProperty("--rx", ((0.5 - py) * 8).toFixed(2) + "deg");
          card.style.setProperty("--ry", ((px - 0.5) * 10).toFixed(2) + "deg");
          card.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
          card.style.setProperty("--my", (py * 100).toFixed(1) + "%");
        });
        card.addEventListener("pointerleave", function () {
          card.style.setProperty("--rx", "0deg");
          card.style.setProperty("--ry", "0deg");
        });
      }
      grid.appendChild(card);
    });
    host.insertBefore(dash, host.firstChild);
    dash.querySelectorAll("[data-n]").forEach(function (el) { tween(el, Number(el.getAttribute("data-n")) || 0); });
    dash.addEventListener("click", function (e) {
      var goBtn = e.target.closest("[data-go]");
      if (goBtn) { go(goBtn.getAttribute("data-go")); return; }
      var labBtn = e.target.closest("[data-lab]");
      if (labBtn) openLab(labBtn.getAttribute("data-lab"), labBtn);
    });
  }

  function lessonWhy(section) {
    if (!section || section.id === "home") return;
    var main = document.getElementById("main");
    var host = main && main.querySelector(".sec-container");
    if (!host || host.querySelector(".uc-app-why")) return;
    var track = trackFor(section.group);
    var sub = section.sub ? " This section covers " + section.sub.replace(/\.$/, "") + "." : "";
    var match = matchLab(section);
    var lab = match ? labById(match.lab) : null;
    var bar = document.createElement("div");
    bar.className = "uc-app-why";
    bar.innerHTML = "<div><b>Why it matters.</b> " + esc(track.why + sub) + "</div>" +
      (lab ? '<button type="button" class="uc-app-btn primary" id="ucAppTry">Try it</button>' : "");
    var tryBtn = bar.querySelector("#ucAppTry");
    if (tryBtn && match) {
      tryBtn.setAttribute("aria-label", "Try it in the " + lab.title + " lab");
      tryBtn.addEventListener("click", function () {
        openLab(match.lab, tryBtn, match.scenario || "");
      });
    }
    var hero = host.querySelector(".sec-head");
    if (hero && hero.nextSibling) host.insertBefore(bar, hero.nextSibling);
    else host.appendChild(bar);
  }

  function refreshProg() {
    var btn = document.getElementById("ucAppProg");
    if (!btn) return;
    var ids = progressIds();
    var total = sections().length || 0;
    var n = 0;
    sections().forEach(function (s) { if (ids[s.id]) n += 1; });
    btn.textContent = n + " / " + total;
    btn.setAttribute("aria-label", "Study progress, " + n + " of " + total + " sections opened in this browser");
  }
  function fillProgPop() {
    var pop = document.getElementById("ucAppProgPop");
    if (!pop) return;
    var ids = progressIds();
    var rows = TRACKS.map(function (track) {
      var group = inGroup(track.group);
      var seen = 0;
      group.forEach(function (s) { if (ids[s.id]) seen += 1; });
      var width = group.length ? Math.round(seen / group.length * 100) : 0;
      return '<div class="uc-app-track"><span>' + esc(track.group.replace("Contact center — ", "").replace("CCaaS and UCaaS platforms", "CCaaS").replace("Webex Calling and Teams Phone", "Cloud calling").replace("Voice network and QoS", "QoS")) + '</span><i><span style="width:' + width + '%"></span></i><b>' + seen + "/" + group.length + "</b></div>";
    }).join("");
    pop.innerHTML = "<h2>Opened in this browser</h2><p>Section ids only. No name, number, or capture is stored.</p>" + rows;
  }
  function toggleProg(force) {
    var pop = document.getElementById("ucAppProgPop");
    if (!pop) return;
    var open = force === true ? true : force === false ? false : pop.hasAttribute("hidden");
    if (open) { fillProgPop(); pop.removeAttribute("hidden"); }
    else pop.setAttribute("hidden", "");
  }

  function installChrome() {
    if (document.getElementById("ucAppSkip")) return;
    var skip = document.createElement("a");
    skip.id = "ucAppSkip";
    skip.className = "uc-app-skip";
    skip.href = "#main";
    skip.textContent = "Skip to content";
    document.body.insertBefore(skip, document.body.firstChild);

    var theme = document.getElementById("theme");
    if (theme && !document.getElementById("ucAppLabsBtn")) {
      var labs = document.createElement("button");
      labs.id = "ucAppLabsBtn";
      labs.type = "button";
      labs.className = "uc-app-labs-btn";
      labs.innerHTML = ICONS.labs + " Labs";
      labs.setAttribute("aria-label", "Open interactive labs");
      labs.addEventListener("click", function () { openLab("simulator", labs); });
      theme.parentNode.insertBefore(labs, theme);

      var mode = document.createElement("button");
      mode.id = "ucAppThemeBtn";
      mode.type = "button";
      mode.className = "uc-app-theme-btn";
      mode.setAttribute("aria-label", "Toggle light and dark theme");
      function paintMode() {
        var dark = document.documentElement.getAttribute("data-theme") === "dark";
        mode.innerHTML = dark ? ICONS.sun : ICONS.moon;
        mode.setAttribute("aria-pressed", dark ? "true" : "false");
      }
      paintMode();
      mode.addEventListener("click", function () {
        var cur = document.documentElement.getAttribute("data-theme") || "light";
        var next = cur === "dark" ? "light" : "dark";
        if (window.setAppTheme) window.setAppTheme(next);
        else {
          document.documentElement.setAttribute("data-theme", next);
          try { localStorage.setItem("uc_theme", next); localStorage.setItem("uc-theme", next); } catch (e) {}
          if (theme.querySelector('option[value="' + next + '"]')) theme.value = next;
        }
        paintMode();
      });
      var obs = new MutationObserver(paintMode);
      obs.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
      theme.parentNode.insertBefore(mode, theme.nextSibling);
    }
    var prog = document.getElementById("prog");
    if (prog && !document.getElementById("ucAppProg")) {
      var btn = document.createElement("button");
      btn.id = "ucAppProg";
      btn.type = "button";
      btn.className = "uc-app-prog";
      btn.addEventListener("click", function () { toggleProg(); });
      prog.parentNode.insertBefore(btn, prog.nextSibling);
      var pop = document.createElement("div");
      pop.id = "ucAppProgPop";
      pop.className = "uc-app-pop";
      pop.setAttribute("hidden", "");
      pop.setAttribute("role", "dialog");
      pop.setAttribute("aria-label", "Progress by track");
      document.body.appendChild(pop);
      document.addEventListener("click", function (e) {
        if (pop.hasAttribute("hidden")) return;
        if (e.target === btn || btn.contains(e.target) || pop.contains(e.target)) return;
        toggleProg(false);
      });
    }
    refreshProg();
  }

  function installPlayer() {
    if (document.getElementById("ucAppPlayer")) return;
    var bar = document.createElement("div");
    bar.id = "ucAppPlayer";
    bar.className = "uc-app-player";
    bar.setAttribute("hidden", "");
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Tone player");
    bar.innerHTML =
      '<canvas width="224" height="72" aria-hidden="true"></canvas>' +
      '<div class="uc-app-player-copy"><b id="ucAppPlayerName">Tone</b><p id="ucAppPlayerWhy"></p></div>' +
      '<button type="button" class="uc-app-btn" id="ucAppPlayerNext">Next</button>' +
      '<button type="button" class="uc-app-btn primary" id="ucAppPlayerStop">Stop</button>';
    document.body.appendChild(bar);
    var canvas = bar.querySelector("canvas");
    var ctx = canvas.getContext("2d");
    var playing = false;
    var clipIndex = 0;
    function drawWave() {
      if (!ctx) return;
      var analyser = window.UCAudio && window.UCAudio.analyser && window.UCAudio.analyser();
      var w = canvas.width;
      var h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#0B1220";
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = "#2DD4BF";
      ctx.lineWidth = 2;
      ctx.beginPath();
      if (analyser && playing && !reduced()) {
        var data = new Uint8Array(analyser.fftSize);
        analyser.getByteTimeDomainData(data);
        for (var i = 0; i < data.length; i++) {
          var x = i / data.length * w;
          var y = data[i] / 255 * h;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
      } else {
        ctx.moveTo(0, h / 2);
        ctx.lineTo(w, h / 2);
      }
      ctx.stroke();
    }
    function loop() {
      drawWave();
      if (playing && !reduced()) waveRAF = requestAnimationFrame(loop);
    }
    function show(payload) {
      if (!payload) {
        playing = false;
        if (waveRAF) cancelAnimationFrame(waveRAF);
        bar.setAttribute("hidden", "");
        return;
      }
      playing = true;
      clipIndex = payload.index || 0;
      document.getElementById("ucAppPlayerName").textContent = payload.name || "Tone";
      document.getElementById("ucAppPlayerWhy").textContent = payload.text || "";
      bar.removeAttribute("hidden");
      if (waveRAF) cancelAnimationFrame(waveRAF);
      loop();
    }
    if (window.UCAudio && window.UCAudio.subscribe) window.UCAudio.subscribe(show);
    document.getElementById("ucAppPlayerStop").addEventListener("click", function () {
      if (window.UCAudio && window.UCAudio.stop) window.UCAudio.stop();
      else show(null);
    });
    document.getElementById("ucAppPlayerNext").addEventListener("click", function () {
      var clips = (window.UCAudio && window.UCAudio.clips) || [];
      if (!clips.length || !window.UCAudio.play) return;
      window.UCAudio.play((clipIndex + 1) % clips.length);
    });
  }

  function installPalette() {
    var palq = document.getElementById("palq");
    var hits = document.getElementById("palhits");
    var pal = document.querySelector(".pal");
    if (!palq || !hits || palq.dataset.ucApp) return;
    palq.dataset.ucApp = "1";
    palq.setAttribute("aria-label", "Search every lesson");
    palq.setAttribute("aria-controls", "palhits");
    palq.setAttribute("aria-autocomplete", "list");
    hits.setAttribute("role", "listbox");
    hits.setAttribute("aria-label", "Lesson results");
    if (pal && !pal.querySelector(".uc-app-pal-foot")) {
      var foot = document.createElement("div");
      foot.className = "uc-app-pal-foot";
      foot.innerHTML = "<span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>Enter</kbd> open</span><span><kbd>Esc</kbd> close</span><span>Searches every lesson</span>";
      pal.appendChild(foot);
    }
    function items() { return hits.querySelectorAll("button"); }
    function setActive(index) {
      var list = items();
      if (!list.length) { palIndex = 0; palq.removeAttribute("aria-activedescendant"); return; }
      palIndex = (index + list.length) % list.length;
      for (var i = 0; i < list.length; i++) {
        var on = i === palIndex;
        list[i].classList.toggle("is-active", on);
        list[i].setAttribute("role", "option");
        list[i].id = "uc-pal-opt-" + i;
        if (on) list[i].setAttribute("aria-selected", "true");
        else list[i].removeAttribute("aria-selected");
      }
      palq.setAttribute("aria-activedescendant", list[palIndex].id);
      if (list[palIndex].scrollIntoView) list[palIndex].scrollIntoView({ block: "nearest" });
    }
    new MutationObserver(function () { setActive(0); }).observe(hits, { childList: true });
    palq.addEventListener("keydown", function (e) {
      var list = items();
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        e.stopImmediatePropagation();
        setActive(palIndex + (e.key === "ArrowDown" ? 1 : -1));
      } else if (e.key === "Enter" && list[palIndex]) {
        e.preventDefault();
        e.stopImmediatePropagation();
        list[palIndex].click();
      }
    }, true);
  }

  var SCENARIOS = [
    {
      id: "station",
      title: "Station to station",
      why: "Two phones on one cluster. CUCM does the signaling. RTP goes phone to phone unless a media resource is inserted.",
      nodes: [
        { id: "a", label: "Phone A", sub: "SIP" },
        { id: "cucm", label: "CUCM", sub: "signaling" },
        { id: "b", label: "Phone B", sub: "SIP" }
      ],
      steps: [
        { f: "a", t: "cucm", kind: "sip", label: "INVITE", note: "Phone A sends the INVITE to the subscriber that holds its registration." },
        { f: "cucm", t: "a", kind: "sip", label: "100 Trying", note: "CUCM has the INVITE and is doing digit analysis." },
        { f: "cucm", t: "b", kind: "sip", label: "INVITE", note: "The called CSS and partition resolved to Phone B." },
        { f: "b", t: "cucm", kind: "sip", label: "180 Ringing", note: "Phone B is alerting. This is still signaling, not audio." },
        { f: "cucm", t: "a", kind: "sip", label: "180 Ringing", note: "CUCM relays alerting to the caller." },
        { f: "b", t: "cucm", kind: "sip", label: "200 OK", note: "Phone B answered. SDP names the phone's own media address." },
        { f: "a", t: "b", kind: "rtp", label: "RTP", note: "Audio goes phone to phone. It does not hairpin through CUCM." }
      ]
    },
    {
      id: "cube",
      title: "PSTN through CUBE",
      why: "CUBE is a B2BUA. The Call-ID changes there. A 200 OK on the trunk does not prove the phone has audio.",
      nodes: [
        { id: "phone", label: "Phone", sub: "SIP" },
        { id: "cucm", label: "CUCM", sub: "CSS / pattern" },
        { id: "cube", label: "CUBE", sub: "B2BUA" },
        { id: "pstn", label: "PSTN", sub: "ITSP" }
      ],
      steps: [
        { f: "phone", t: "cucm", kind: "sip", label: "INVITE", note: "The line CSS must contain the partition of the route pattern, or this number does not exist." },
        { f: "cucm", t: "cube", kind: "sip", label: "INVITE", note: "The pattern points at a route list, then a route group, then the SIP trunk. This Call-ID is the CUCM leg." },
        { f: "cube", t: "pstn", kind: "sip", label: "INVITE", note: "A dial-peer matches. CUBE starts a new Call-ID toward the carrier." },
        { f: "pstn", t: "cube", kind: "sip", label: "180", note: "Ringing on the carrier leg. Relay it back only after you know which leg you are looking at." },
        { f: "cube", t: "cucm", kind: "sip", label: "180", note: "CUBE notifies CUCM. Still no audio." },
        { f: "pstn", t: "cube", kind: "sip", label: "200 OK", note: "The carrier answered. SDP is the carrier media address." },
        { f: "phone", t: "cube", kind: "rtp", label: "RTP", note: "Phone media goes to CUBE, not through CUCM, unless an MTP or transcoder is actually invoked." },
        { f: "cube", t: "pstn", kind: "rtp", label: "RTP", note: "CUBE anchors or relays media toward the carrier. Prove both RTP legs." }
      ]
    },
    {
      id: "webex",
      title: "Webex Calling local gateway",
      why: "Webex Calling still needs a premises border for your own PSTN. Calling Plan has no local gateway. This path does.",
      nodes: [
        { id: "app", label: "Webex app", sub: "client" },
        { id: "wx", label: "Webex Calling", sub: "cloud" },
        { id: "lgw", label: "Local Gateway", sub: "CUBE" },
        { id: "pstn", label: "PSTN", sub: "carrier" }
      ],
      steps: [
        { f: "app", t: "wx", kind: "sip", label: "INVITE", note: "The client signals Webex Calling, not your old subscriber." },
        { f: "wx", t: "lgw", kind: "sip", label: "INVITE", note: "Outbound PSTN uses the local gateway trunk or registration, on the ports that design chose." },
        { f: "lgw", t: "pstn", kind: "sip", label: "INVITE", note: "Dial-peers on the gateway decide the carrier leg." },
        { f: "pstn", t: "lgw", kind: "sip", label: "200 OK", note: "Answer is on the carrier leg. Check that SDP before you blame the app." },
        { f: "lgw", t: "wx", kind: "sip", label: "200 OK", note: "The gateway completes the Webex leg." },
        { f: "app", t: "lgw", kind: "rtp", label: "RTP", note: "Media for this PSTN call anchors at the local gateway. The cloud signaling path is not the audio path." }
      ]
    },
    {
      id: "ucce",
      title: "UCCE comprehensive",
      why: "Ingress, prompt, script, queue, and agent are the contact. CUIC is the report beside that path, not the audio.",
      nodes: [
        { id: "caller", label: "Caller", sub: "PSTN" },
        { id: "cube", label: "CUBE", sub: "ingress" },
        { id: "cvp", label: "CVP", sub: "VVB prompt" },
        { id: "icm", label: "ICM", sub: "script" },
        { id: "cucm", label: "CUCM", sub: "agent phone" },
        { id: "agent", label: "Agent", sub: "Finesse" },
        { id: "cuic", label: "CUIC", sub: "report", lane: "side" }
      ],
      steps: [
        { f: "caller", t: "cube", kind: "sip", label: "INVITE", note: "The carrier hits the border. This leg has its own Call-ID." },
        { f: "cube", t: "cvp", kind: "sip", label: "INVITE", note: "CVP takes the call for treatment." },
        { f: "cvp", t: "icm", kind: "sip", label: "New call", note: "ICM runs the script. The route request is not RTP." },
        { f: "cvp", t: "cvp", kind: "sip", label: "Prompt", note: "VVB plays the menu. A prompt is not a queue." },
        { f: "icm", t: "cvp", kind: "sip", label: "Label", note: "The script returns a label for an agent or a queue." },
        { f: "cvp", t: "cucm", kind: "sip", label: "INVITE", note: "The agent phone is a CUCM destination." },
        { f: "cucm", t: "agent", kind: "sip", label: "INVITE", note: "If the phone rings and Finesse does not, look at PG, CTI, and Finesse." },
        { f: "caller", t: "agent", kind: "rtp", label: "RTP", note: "Audio is between the caller path and the agent phone. CUIC never carries it." },
        { f: "icm", t: "cuic", kind: "report", label: "Interval", note: "Join the report with RouterCallKey and matching time. A skill rename can break history while calls still connect." }
      ]
    }
  ];
  if (window.UC_EXTRA_SCENARIOS && window.UC_EXTRA_SCENARIOS.length) {
    SCENARIOS = SCENARIOS.concat(window.UC_EXTRA_SCENARIOS);
  }

  var sim = { scenario: 0, i: 2, preview: 0.62, running: false, t0: 0, dur: 1100 };

  function stopSim() {
    sim.running = false;
    if (simRAF) cancelAnimationFrame(simRAF);
    simRAF = 0;
  }
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  function layoutNodes(nodes, w, h) {
    var main = nodes.filter(function (n) { return n.lane !== "side"; });
    var side = nodes.filter(function (n) { return n.lane === "side"; });
    var nw = Math.max(78, Math.min(132, (w - 36) / Math.max(main.length, 1) - 16));
    var placed = [];
    main.forEach(function (n, i) {
      var x = ((i + 0.5) / main.length) * (w - 24) + 12;
      placed.push({ id: n.id, label: n.label, sub: n.sub, x: x, y: h * 0.42, w: nw, h: 58 });
    });
    side.forEach(function (n, i) {
      placed.push({ id: n.id, label: n.label, sub: n.sub, x: w * 0.5, y: h * 0.78, w: nw, h: 58, side: true });
    });
    return placed;
  }
  function drawSim(progress) {
    var canvas = document.getElementById("ucAppCanvas");
    if (!canvas) return;
    var rect = canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.max(320, rect.width || canvas.clientWidth || 640);
    var h = Math.max(240, rect.height || 420);
    if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
    }
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var contrast = document.documentElement.getAttribute("data-theme") === "contrast";
    var board = contrast ? "#000" : "#0B1220";
    var sip = contrast ? "#5EEAD4" : "#2DD4BF";
    var rtp = contrast ? "#FFE14A" : "#F5B942";
    var report = contrast ? "#fff" : "#C4B5FD";
    var scenario = SCENARIOS[sim.scenario];
    ctx.clearRect(0, 0, w, h);
    var g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0, board);
    g.addColorStop(1, contrast ? "#000" : "#151b38");
    roundRect(ctx, 0, 0, w, h, 18);
    ctx.fillStyle = g;
    ctx.fill();
    ctx.fillStyle = contrast ? "#333" : "rgba(45,212,191,.18)";
    for (var gx = 18; gx < w; gx += 26) {
      for (var gy = 18; gy < h; gy += 26) ctx.fillRect(gx, gy, 1.4, 1.4);
    }
    var nodes = layoutNodes(scenario.nodes, w, h);
    var map = {};
    nodes.forEach(function (n) { map[n.id] = n; });
    function colorOf(step) {
      if (step.kind === "rtp") return rtp;
      if (step.kind === "report") return report;
      return sip;
    }
    function edge(step, p, done) {
      var a = map[step.f];
      var b = map[step.t];
      if (!a || !b) return;
      ctx.save();
      ctx.strokeStyle = colorOf(step);
      ctx.globalAlpha = done ? 0.35 : 0.95;
      ctx.lineWidth = step.kind === "rtp" ? 2 : 2.5;
      ctx.setLineDash(step.kind === "sip" ? [] : [7, 6]);
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      if (a.id === b.id) ctx.arc(a.x + 36, a.y - 28, 22, 0.4, 2.4);
      else ctx.lineTo(b.x, b.y);
      ctx.stroke();
      ctx.restore();
      if (done || p <= 0) return;
      var eased = 1 - Math.pow(1 - p, 3);
      var x = a.id === b.id ? a.x + 36 : a.x + (b.x - a.x) * eased;
      var y = a.id === b.id ? a.y - 46 : a.y + (b.y - a.y) * eased;
      ctx.beginPath();
      ctx.fillStyle = colorOf(step);
      ctx.globalAlpha = 0.25;
      ctx.arc(x, y, 16, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.beginPath();
      ctx.fillStyle = "#fff";
      ctx.strokeStyle = colorOf(step);
      ctx.lineWidth = 3;
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.font = "700 12px ui-sans-serif, system-ui, sans-serif";
      ctx.fillStyle = "#F8FAFC";
      ctx.fillText(step.label, x + 12, y - 10);
    }
    var current = scenario.steps[sim.i];
    var shown = sim.running ? progress : sim.preview;
    for (var i = 0; i < sim.i && i < scenario.steps.length; i++) edge(scenario.steps[i], 1, true);
    if (current && sim.i < scenario.steps.length) edge(current, shown, false);
    nodes.forEach(function (n) {
      var hot = current && (current.f === n.id || current.t === n.id) && sim.i < scenario.steps.length;
      ctx.save();
      roundRect(ctx, n.x - n.w / 2, n.y - n.h / 2, n.w, n.h, 14);
      ctx.fillStyle = contrast ? "#000" : "#121A2F";
      ctx.fill();
      ctx.lineWidth = hot ? 2.5 : 1.5;
      ctx.strokeStyle = hot ? "#6366F1" : (contrast ? "#fff" : "rgba(248,250,252,.45)");
      ctx.stroke();
      ctx.fillStyle = "#F8FAFC";
      ctx.font = "800 13px ui-sans-serif, system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(n.label, n.x, n.y - 2);
      ctx.fillStyle = contrast ? "#fff" : "#99F6E4";
      ctx.font = "700 10px ui-sans-serif, system-ui, sans-serif";
      ctx.fillText(n.sub, n.x, n.y + 14);
      ctx.restore();
    });
  }
  function simNote() {
    var scenario = SCENARIOS[sim.scenario];
    var step = scenario.steps[Math.min(sim.i, scenario.steps.length - 1)];
    var el = document.getElementById("ucAppSimNote");
    if (el && step) el.textContent = (sim.i >= scenario.steps.length ? "Call placed. " : "") + step.note;
    var log = document.getElementById("ucAppSimLog");
    if (!log) return;
    log.innerHTML = scenario.steps.map(function (stepItem, idx) {
      var cls = idx < sim.i ? "done" : idx === sim.i ? "on" : "";
      return '<button type="button" class="' + cls + '" data-step="' + idx + '">' + (idx + 1) + " " + esc(stepItem.label) + "</button>";
    }).join("");
  }
  function simFrame(now) {
    if (!sim.running) return;
    var p = Math.min(1, (now - sim.t0) / sim.dur);
    drawSim(p);
    if (p < 1) {
      simRAF = requestAnimationFrame(simFrame);
      return;
    }
    sim.i += 1;
    simNote();
    if (sim.i >= SCENARIOS[sim.scenario].steps.length) {
      stopSim();
      sim.preview = 1;
      drawSim(1);
      markLab("simulator");
      var el = document.getElementById("ucAppSimNote");
      if (el) el.textContent = "Call placed. Read the RTP step again: signaling success is not two-way audio.";
      return;
    }
    sim.t0 = now;
    simRAF = requestAnimationFrame(simFrame);
  }
  function placeCall() {
    stopSim();
    sim.i = 0;
    sim.preview = 0;
    simNote();
    if (reduced()) {
      sim.i = SCENARIOS[sim.scenario].steps.length;
      sim.preview = 1;
      drawSim(1);
      simNote();
      markLab("simulator");
      return;
    }
    sim.running = true;
    sim.t0 = performance.now();
    simRAF = requestAnimationFrame(simFrame);
  }
  function renderSimulator(root) {
    if (!SCENARIOS[sim.scenario]) sim.scenario = 0;
    var scenario = SCENARIOS[sim.scenario];
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> ' + esc(scenario.why) + '</p>' +
      '<div class="uc-app-field"><label for="ucAppScenario">Scenario, ' + SCENARIOS.length + ' paths</label>' +
        '<select id="ucAppScenario">' +
          SCENARIOS.map(function (item, idx) {
            return '<option value="' + idx + '"' + (idx === sim.scenario ? " selected" : "") + ">" + esc(item.title) + "</option>";
          }).join("") +
        "</select></div>" +
      '<div class="uc-app-legend"><span><i class="sip"></i>SIP signaling</span><span><i class="rtp"></i>RTP or a report, not the same path</span></div>' +
      '<canvas id="ucAppCanvas" class="uc-app-canvas" role="img" aria-label="Animated call flow"></canvas>' +
      '<div class="uc-app-toolbar">' +
        '<button type="button" class="uc-app-btn primary" id="ucAppPlace">Place call</button>' +
        '<button type="button" class="uc-app-btn" id="ucAppStep">Step</button>' +
        '<button type="button" class="uc-app-btn" id="ucAppResetSim">Reset</button>' +
      '</div>' +
      '<p class="uc-app-status" id="ucAppSimNote" aria-live="polite"></p>' +
      '<div class="uc-app-log" id="ucAppSimLog" aria-label="Messages in this call"></div>';
    sim.i = Math.min(2, scenario.steps.length - 1);
    sim.preview = 0.62;
    sim.running = false;
    root.querySelector("#ucAppPlace").addEventListener("click", placeCall);
    root.querySelector("#ucAppStep").addEventListener("click", function () {
      stopSim();
      if (sim.i < scenario.steps.length) sim.i += 1;
      sim.preview = 1;
      if (sim.i >= scenario.steps.length) markLab("simulator");
      simNote();
      drawSim(1);
    });
    root.querySelector("#ucAppResetSim").addEventListener("click", function () {
      stopSim();
      sim.i = 0;
      sim.preview = 0;
      simNote();
      drawSim(0);
    });
    root.querySelector("#ucAppScenario").addEventListener("change", function (e) {
      stopSim();
      sim.scenario = Number(e.target.value) || 0;
      renderSimulator(root);
    });
    root.onclick = function (e) {
      var stepBtn = e.target.closest("[data-step]");
      if (stepBtn) {
        stopSim();
        sim.i = Number(stepBtn.getAttribute("data-step"));
        sim.preview = 0.7;
        simNote();
        drawSim(0.7);
      }
    };
    simNote();
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { drawSim(sim.preview); });
    });
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
      '<div class="uc-app-dial"><div class="uc-app-tray"><h3>Blocks</h3><div id="ucDialTray"></div></div><div class="uc-app-slots"><h3>Outbound order</h3><div id="ucDialSlots"></div></div></div>' +
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
        '<div class="uc-app-palette"><h3>Build</h3>' +
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
            '<h3 class="uc-app-q">' + score + " / " + session.length + " on " + esc(track) + "</h3>" +
            '<p class="uc-app-score">Bank size ' + items.length + ". Cumulative " + row.ok + " / " + row.n + ". Best drill " + row.best + " / " + row.bestN + ".</p>" +
            '<div class="uc-app-toolbar"><button type="button" class="uc-app-btn primary" id="ucQuizAgain">Another ten</button><button type="button" class="uc-app-btn" id="ucQuizTracksBtn">All tracks</button></div>';
          root.querySelector("#ucQuizAgain").addEventListener("click", function () { start(track); });
          root.querySelector("#ucQuizTracksBtn").addEventListener("click", picker);
          return;
        }
        var item = session[index];
        root.innerHTML =
          '<p class="uc-app-score">' + esc(track) + " · " + items.length + " in the bank · question " + (index + 1) + " of " + session.length + " · " + score + " correct this drill</p>" +
          '<h3 class="uc-app-q">' + esc(item.q) + "</h3>" +
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
            '<div class="uc-app-face front"><button type="button" class="uc-app-flip-hit" id="ucFlipBtn" aria-label="Flip card"></button><p class="uc-app-kicker">Term</p><h3>' + esc(card.term) + '</h3><p>Flip for the definition and why it matters.</p></div>' +
            '<div class="uc-app-face back"><p class="uc-app-kicker">Definition</p><h3>' + esc(card.term) + '</h3><p>' + esc(card.def) + '</p><p style="margin-top:8px"><b>Why it matters.</b> ' + esc(card.why) + "</p></div>" +
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
          '<h3 class="uc-app-q">' + score + " / " + items.length + (passed ? " · passed" : " · below the pass line") + "</h3>" +
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
        '<h3 class="uc-app-q">' + esc(item.q) + "</h3>" +
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

  function renderLab(kind) {
    var body = document.getElementById("ucAppLabBody");
    var title = document.getElementById("ucAppLabTitle");
    if (!body || !title) return;
    var fresh = document.createElement("div");
    fresh.id = "ucAppLabBody";
    body.parentNode.replaceChild(fresh, body);
    body = fresh;
    if (!knownLab(kind)) kind = "simulator";
    labKind = kind;
    stopSim();
    title.textContent = labById(kind).title;
    document.querySelectorAll(".uc-app-tab[data-lab]").forEach(function (tab) {
      var on = tab.getAttribute("data-lab") === kind;
      tab.setAttribute("aria-selected", on ? "true" : "false");
      tab.tabIndex = on ? 0 : -1;
    });
    if (kind === "simulator") renderSimulator(body);
    else if (kind === "dial") renderDial(body);
    else if (kind === "ivr") renderIvr(body);
    else if (kind === "quiz") renderQuiz(body);
    else if (kind === "cards") renderCards(body);
    else if (kind === "boss") renderBoss(body);
    else if (window.UCLabs && window.UCLabs[kind]) window.UCLabs[kind](body);
    else renderSimulator(body);
  }
  function ensureLab() {
    if (document.getElementById("ucAppLab")) return;
    var lab = document.createElement("div");
    lab.id = "ucAppLab";
    lab.className = "uc-app-lab";
    lab.setAttribute("hidden", "");
    lab.setAttribute("role", "dialog");
    lab.setAttribute("aria-modal", "true");
    lab.setAttribute("aria-labelledby", "ucAppLabTitle");
    lab.innerHTML =
      '<div class="uc-app-lab-panel">' +
        '<div class="uc-app-lab-head"><div><p class="uc-app-kicker">Interactive lab</p><h2 id="ucAppLabTitle">Call-flow simulator</h2></div>' +
        '<button type="button" class="uc-app-btn" id="ucAppLabClose">Close</button></div>' +
        '<div class="uc-app-tabs uc-app-lab-tabs" role="tablist" aria-label="Labs">' +
          LABS.map(function (item) {
            return '<button type="button" class="uc-app-tab" data-lab="' + item.id + '" role="tab">' + esc(item.short) + "</button>";
          }).join("") +
        '</div>' +
        '<div id="ucAppLabBody"></div>' +
      '</div>';
    document.body.appendChild(lab);
    lab.querySelector("#ucAppLabClose").addEventListener("click", closeLab);
    lab.addEventListener("click", function (e) {
      if (e.target === lab) closeLab();
      var tab = e.target.closest(".uc-app-tab[data-lab]");
      if (tab && tab.parentNode.classList.contains("uc-app-tabs")) renderLab(tab.getAttribute("data-lab"));
    });
    lab.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); closeLab(); return; }
      if (e.key !== "Tab") return;
      var items = lab.querySelectorAll("button, select, input, textarea, [href], [tabindex]:not([tabindex='-1'])");
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    window.addEventListener("resize", function () {
      if (!lab.hasAttribute("hidden") && labKind === "simulator") drawSim(sim.running ? 0 : sim.preview);
    });
  }
  function openLab(kind, trigger, scenarioId) {
    if (scenarioId) {
      for (var i = 0; i < SCENARIOS.length; i++) {
        if (SCENARIOS[i].id === scenarioId) { sim.scenario = i; break; }
      }
    }
    ensureLab();
    var lab = document.getElementById("ucAppLab");
    returnFocus = trigger || document.activeElement;
    lab.removeAttribute("hidden");
    document.body.classList.add("uc-app-lock");
    renderLab(kind || "simulator");
    var close = document.getElementById("ucAppLabClose");
    if (close) close.focus();
  }
  function closeLab() {
    stopSim();
    var lab = document.getElementById("ucAppLab");
    if (!lab || lab.hasAttribute("hidden")) return;
    var trigger = returnFocus;
    lab.setAttribute("hidden", "");
    document.body.classList.remove("uc-app-lock");
    if (document.getElementById("ucAppDash")) mountDash();
    if (trigger && document.body.contains(trigger) && trigger.focus) trigger.focus();
    else {
      var fallback = document.getElementById("ucAppLabsBtn");
      if (fallback && fallback.focus) fallback.focus();
    }
  }
  function maybeLab() {
    if (openedLabFromQuery) return;
    var params;
    try { params = new URLSearchParams(window.location.search); } catch (e) { return; }
    var kind = params.get("lab");
    if (!kind || !knownLab(kind)) return;
    openedLabFromQuery = true;
    openLab(kind, null, params.get("scenario") || "");
  }

  var lastSection = "";
  function onOpen(section) {
    if (!section) return;
    if (lastSection && lastSection !== section.id) closeLab();
    lastSection = section.id;
    try { localStorage.setItem(LAST_KEY, section.id); } catch (e) {}
    refreshProg();
    var main = document.getElementById("main");
    var sec = main && main.querySelector(".sec-container");
    if (sec && !reduced()) {
      requestAnimationFrame(function () { sec.classList.add("uc-app-in"); });
    }
    if (section.id === "home") mountDash();
    else lessonWhy(section);
    maybeLab();
  }

  function wrap() {
    if (window.openSection && !window.__ucAppOpen) {
      window.__ucAppOpen = true;
      var orig = window.openSection;
      window.openSection = function (id) {
        var main = document.getElementById("main");
        var sec = main && main.querySelector(".sec-container");
        if (sec) sec.classList.remove("uc-app-in");
        return orig.apply(this, arguments);
      };
    }
    if (window.ucAfterOpen && !window.__ucAppWrapped) {
      window.__ucAppWrapped = true;
      var after = window.ucAfterOpen;
      window.ucAfterOpen = function (s) {
        try { after(s); } catch (e) {}
        try { onOpen(s); } catch (err) { if (window.console) console.error(err); }
      };
    } else if (!window.ucAfterOpen) {
      window.ucAfterOpen = onOpen;
      window.__ucAppWrapped = true;
    }
  }

  function boot() {
    badgeSnap = earnedBadges();
    touchStreak();
    installChrome();
    installPlayer();
    installPalette();
    wrap();
    var current = window.getCurrentSectionId && window.getCurrentSectionId();
    var section = findSection(current);
    if (section) onOpen(section);
    else setTimeout(function () {
      var again = findSection(window.getCurrentSectionId && window.getCurrentSectionId());
      if (again) onOpen(again);
      announceNewBadges();
    }, 90);
    if (section) announceNewBadges();
  }

  window.UCApp = { openLab: openLab, closeLab: closeLab, markLab: markLab, celebrate: celebrate };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
