/* UC Lab shell. One lesson in the DOM. Modules load on demand. */
(function () {
  "use strict";

  var PROGRESS_KEY = "uc_lab_progress_v21";
  var titleEl = document.getElementById("viewTitle");
  var view = document.getElementById("view");
  var side = document.getElementById("side");
  var toast = document.getElementById("toast");
  var current = { name: "home" };
  var currentSection = null;
  var toastTimer = null;
  var dialHandle = null;
  var exportWorker = null;
  var exportSeq = 0;
  var studioPromise = null;

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function reduced() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function data() {
    return window.UC.data;
  }

  function sections() {
    return (data() && data().sections) || [];
  }

  function findSection(id) {
    for (var i = 0; i < sections().length; i += 1) {
      if (sections()[i].id === id) return sections()[i];
    }
    return null;
  }

  function journeyById(id) {
    var list = (data() && data().journeys) || [];
    for (var i = 0; i < list.length; i += 1) if (list[i].id === id) return list[i];
    return null;
  }

  function accent(n) {
    return "var(--cc-accent-" + (n || 1) + ")";
  }

  function loadProgress() {
    try {
      var raw = JSON.parse(localStorage.getItem(PROGRESS_KEY) || "{}");
      raw.seen = raw.seen || {};
      raw.done = raw.done || {};
      raw.milestones = raw.milestones || {};
      return raw;
    } catch (err) {
      return { seen: {}, done: {}, milestones: {} };
    }
  }

  function saveProgress(state) {
    try { localStorage.setItem(PROGRESS_KEY, JSON.stringify(state)); } catch (err) { /* full or private */ }
  }

  function journeySections(journeyId) {
    return sections().filter(function (item) { return item.journey === journeyId; });
  }

  function seenCount(journeyId) {
    var state = loadProgress();
    return journeySections(journeyId).filter(function (item) { return state.seen[item.id]; }).length;
  }

  function pct(journeyId) {
    var all = journeySections(journeyId);
    if (!all.length) return 0;
    return Math.round((seenCount(journeyId) / all.length) * 100);
  }

  function showToast(message) {
    toast.hidden = false;
    toast.textContent = message;
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.hidden = true; }, 4200);
  }

  function markSeen(meta) {
    var state = loadProgress();
    var fresh = !state.seen[meta.id];
    state.seen[meta.id] = 1;
    saveProgress(state);
    if (!fresh) return;
    var total = journeySections(meta.journey).length;
    var seen = seenCount(meta.journey);
    var ratio = total ? seen / total : 0;
    var gate = ratio >= 1 ? 100 : ratio >= 0.75 ? 75 : ratio >= 0.5 ? 50 : ratio >= 0.25 ? 25 : 0;
    if (!gate) return;
    state = loadProgress();
    state.milestones[meta.journey] = state.milestones[meta.journey] || {};
    if (state.milestones[meta.journey][gate]) return;
    state.milestones[meta.journey][gate] = 1;
    saveProgress(state);
    var journey = journeyById(meta.journey);
    showToast((journey ? journey.name : "Path") + " is " + gate + "% opened.");
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[data-src="' + src + '"]');
      if (existing) {
        if (existing.dataset.ready === "1") resolve();
        else existing.addEventListener("load", function () { resolve(); }, { once: true });
        return;
      }
      var script = document.createElement("script");
      script.src = src;
      script.async = false;
      script.dataset.src = src;
      script.onload = function () {
        script.dataset.ready = "1";
        resolve();
      };
      script.onerror = function () { reject(new Error("Could not load " + src)); };
      document.head.appendChild(script);
    });
  }

  function loadSection(id) {
    if (window.UC._packs[id]) return Promise.resolve(window.UC._packs[id]);
    return new Promise(function (resolve, reject) {
      window.UC._pending[id] = resolve;
      loadScript("assets/curriculum/sections/" + id + ".js").catch(reject);
    });
  }

  function loadWalks() {
    if (window.UC._walkList) return Promise.resolve(window.UC._walkList);
    return loadScript("assets/curriculum/walks.js").then(function () { return window.UC._walkList || []; });
  }

  function ensureCss(href) {
    return new Promise(function (resolve) {
      if (document.querySelector('link[data-href="' + href + '"]')) {
        resolve();
        return;
      }
      var link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.dataset.href = href;
      link.onload = function () { resolve(); };
      link.onerror = function () { resolve(); };
      document.head.appendChild(link);
    });
  }

  function ensureStudio() {
    if (studioPromise) return studioPromise;
    studioPromise = ensureCss("assets/visual-studio.css").then(function () {
      return loadScript("assets/visual-charts.js");
    }).then(function () {
      return loadScript("assets/visual-audio.js");
    }).then(function () {
      return loadScript("assets/visual-illustrations.js");
    }).then(function () {
      return loadScript("assets/visual-progress.js");
    }).then(function () {
      return loadScript("assets/visual-studio.js");
    });
    return studioPromise;
  }

  function setTitle(text) {
    titleEl.textContent = text;
    document.title = text + " · UC Lab";
  }

  function ring(percent, spot) {
    var radius = 16;
    var circ = 2 * Math.PI * radius;
    var dash = (Math.max(0, Math.min(100, percent)) / 100) * circ;
    return '<svg class="ring" viewBox="0 0 44 44" style="--spot:' + spot + '" aria-hidden="true"><circle class="ring-bg" cx="22" cy="22" r="' + radius + '"></circle><circle class="ring-fg" cx="22" cy="22" r="' + radius + '" stroke-dasharray="' + dash.toFixed(2) + " " + circ.toFixed(2) + '"></circle></svg>';
  }

  function heroSvg() {
    var motion = reduced() ? "" : ' class="march"';
    return '<div class="hero-visual"><svg viewBox="0 0 640 280" role="img" aria-label="Phone, CUCM, CUBE, PSTN, and Webex Calling">' +
      '<rect width="640" height="280" rx="28" fill="#0b1120"/>' +
      '<path' + motion + ' d="M70 150 H190" stroke="#2dd4bf" stroke-width="3" fill="none"/>' +
      '<path' + motion + ' d="M270 150 H390" stroke="#818cf8" stroke-width="3" fill="none"/>' +
      '<path' + motion + ' d="M470 150 H560" stroke="#fbbf24" stroke-width="3" fill="none"/>' +
      '<path' + motion + ' d="M230 120 L300 70" stroke="#f472b6" stroke-width="3" fill="none"/>' +
      box(40, 126, "Phone") + box(190, 126, "CUCM") + box(390, 126, "CUBE") + box(530, 126, "PSTN") + box(250, 36, "Webex") +
      "</svg></div>";
  }

  function box(x, y, name) {
    return '<rect x="' + x + '" y="' + y + '" width="80" height="40" rx="12" fill="#131d31" stroke="#818cf8"/>' +
      '<text x="' + (x + 40) + '" y="' + (y + 25) + '" text-anchor="middle" fill="#f8fafc" font-size="12" font-family="ui-sans-serif,system-ui" font-weight="700">' + name + "</text>";
  }

  function renderSide() {
    var journeys = (data() && data().journeys) || [];
    var html = '<p class="side-label kicker">Paths</p>';
    journeys.forEach(function (journey) {
      var href = "#/journey/" + journey.id;
      var currentPage = current.name === "journey" && current.id === journey.id;
      html += '<a href="' + href + '"' + (currentPage ? ' aria-current="page"' : "") + "><span>" + esc(journey.name) + "</span><small>" + pct(journey.id) + "%</small></a>";
    });
    html += '<p class="side-label kicker">Labs</p>';
    [["#/lab/ladder", "SIP ladder"], ["#/lab/dial", "Dialpad"], ["#/lab/topology", "3D fabric"], ["#/lab/erlang", "Erlang"], ["#/lab/sdp", "SDP"], ["#/lab/tones", "Tones"]].forEach(function (item) {
      html += '<a href="' + item[0] + '">' + item[1] + "</a>";
    });
    if (current.name === "lesson" && currentSection) {
      var siblings = sections().filter(function (item) {
        return item.journey === currentSection.journey && item.group === currentSection.group;
      });
      var at = 0;
      siblings.forEach(function (item, index) { if (item.id === currentSection.id) at = index; });
      var start = Math.max(0, at - 4);
      var slice = siblings.slice(start, start + 9);
      html += '<p class="side-label kicker">' + esc(currentSection.group) + "</p>";
      slice.forEach(function (item) {
        html += '<a href="#/lesson/' + esc(item.id) + '"' + (item.id === currentSection.id ? ' aria-current="page"' : "") + "><span>" + esc(item.title) + "</span></a>";
      });
      html += '<a href="#/journey/' + currentSection.journey + "/" + currentSection.track + '">All in this track</a>';
    }
    side.innerHTML = html;
  }

  function markBottom() {
    var tab = "home";
    if (current.name === "journey") tab = "paths";
    if (current.name === "lab") tab = "lab";
    if (current.name === "search") tab = "search";
    if (current.name === "progress") tab = "progress";
    document.querySelectorAll(".bottom-nav a").forEach(function (link) {
      if (link.getAttribute("data-tab") === tab) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
  }

  function closeSide() {
    side.classList.remove("open");
    document.getElementById("backdrop").hidden = true;
    document.getElementById("menuBtn").setAttribute("aria-expanded", "false");
  }

  function cleanupTools() {
    if (dialHandle && dialHandle.destroy) dialHandle.destroy();
    dialHandle = null;
    if (window.UCTopology) window.UCTopology.destroy();
  }

  function renderHome() {
    cleanupTools();
    currentSection = null;
    setTitle("UC Lab Free University");
    var stats = data().stats;
    var cards = data().journeys.map(function (journey) {
      var spot = accent(journey.accent);
      return '<a class="journey-card" style="--spot:' + spot + '" href="#/journey/' + journey.id + '">' +
        '<div class="ring-row">' + ring(pct(journey.id), spot) + "<small>" + pct(journey.id) + "% opened</small></div>" +
        "<strong>" + esc(journey.name) + "</strong><p>" + esc(journey.blurb) + "</p><small class=\"kicker\">" +
        esc(journey.kicker) + " · " + stats.journeys[journey.id] + " sections</small></a>";
    }).join("");
    view.innerHTML =
      '<div class="hero-stage"><div class="hero-copy"><p class="lede">Four certification paths over the same 476 sections. Open one lesson at a time. The SIP ladder, dialpad, Erlang and SDP tools, and the 3D fabric sit inside the work.</p>' +
      '<div class="actions"><a class="primary" style="display:inline-flex;align-items:center;text-decoration:none;border-radius:999px;min-height:40px;padding:0 14px" href="#/lab/topology">Open the 3D fabric</a>' +
      '<a href="#/lesson/home">Campus orientation</a></div></div>' + heroSvg() + "</div>" +
      '<div class="stat-row">' +
      stat(stats.sections, "Sections") + stat(stats.flows, "Flows") + stat(stats.walkthroughs, "Walkthroughs") +
      stat(stats.charts, "Charts") + stat(stats.illustrations, "Illustrations") + stat(stats.audioClips, "Tones") +
      stat(stats.selfChecks, "Self-checks") + stat(stats.drills, "Drills") +
      "</div>" +
      '<h2>Certification paths</h2><div class="journey-grid">' + cards + "</div>" +
      '<h2>Study sequence</h2><ol><li>Read a ladder and separate SIP from RTP.</li><li>Trace CUCM digit analysis and the CUBE B2BUA.</li><li>Choose Webex Calling or Teams Phone and prove the trunk.</li><li>Follow a contact through UCCE, PCCE, or the CCaaS you operate.</li><li>Write leg, identifier, counter, and capture before you change production.</li></ol>' +
      window.UCTools.sourcesHtml("");
    renderSide();
    markBottom();
  }

  function stat(value, label) {
    return '<div class="stat"><b>' + esc(value) + "</b><span>" + esc(label) + "</span></div>";
  }

  function renderJourney(id, track) {
    cleanupTools();
    currentSection = null;
    var journey = journeyById(id);
    if (!journey) return renderMissing();
    setTitle(journey.name);
    var all = journeySections(id);
    var shown = track ? all.filter(function (item) { return item.track === track; }) : all;
    var groups = [];
    var seen = {};
    all.forEach(function (item) {
      if (seen[item.track]) return;
      seen[item.track] = true;
      groups.push(item);
    });
    var tracks = groups.map(function (item) {
      var count = all.filter(function (row) { return row.track === item.track; }).length;
      var href = "#/journey/" + id + "/" + item.track;
      return '<a href="' + href + '"' + (track === item.track ? ' aria-current="page"' : "") + "><span>" + esc(item.group) + "</span><small>" + count + "</small></a>";
    }).join("");
    var list = shown.map(function (item) {
      var state = loadProgress();
      var mark = state.done[item.id] ? "Done" : state.seen[item.id] ? "Opened" : item.num;
      return '<a href="#/lesson/' + esc(item.id) + '"><span>' + esc(item.title) + "</span><small>" + esc(mark) + "</small></a>";
    }).join("");
    var continueId = null;
    for (var i = 0; i < all.length; i += 1) {
      if (!loadProgress().seen[all[i].id]) { continueId = all[i].id; break; }
    }
    if (!continueId && all.length) continueId = all[0].id;
    view.innerHTML =
      '<p class="kicker">' + esc(journey.kicker) + "</p><p class=\"lede\">" + esc(journey.blurb) + "</p>" +
      '<div class="ring-row">' + ring(pct(id), accent(journey.accent)) + "<span>" + seenCount(id) + " of " + all.length + " sections opened</span></div>" +
      (continueId ? '<p><a class="primary" style="display:inline-flex;align-items:center;text-decoration:none;border-radius:999px;min-height:40px;padding:0 14px" href="#/lesson/' + continueId + '">Continue</a></p>' : "") +
      '<h2>Tracks in this path</h2><nav class="track-list" aria-label="Tracks">' + tracks + "</nav>" +
      "<h2>" + (track ? esc(shown[0] ? shown[0].group : "Track") : "Lessons") + "</h2>" +
      '<nav class="path-list" aria-label="Lessons">' + list + "</nav>" +
      window.UCTools.sourcesHtml(id);
    renderSide();
    markBottom();
  }

  function demoteHeadings(html) {
    return html.replace(/<h1(\s|>)/gi, "<h2$1").replace(/<\/h1>/gi, "</h2>");
  }

  function localDetails(root) {
    return Array.prototype.filter.call(root.querySelectorAll("details"), function (node) {
      var pane = node.closest(".tab-pane");
      return !pane || pane === root;
    });
  }

  function wireItems(root) {
    root.querySelectorAll(".item").forEach(function (item) {
      if (item.dataset.wired === "1") return;
      item.dataset.wired = "1";
      item.addEventListener("click", function () { item.classList.toggle("open"); });
    });
    root.querySelectorAll('a[href^="http"]').forEach(function (link) {
      link.rel = "noopener noreferrer";
      if (!link.target) link.target = "_blank";
    });
  }

  function paginate(root) {
    var cards = localDetails(root);
    if (cards.length <= 8) return;
    var stored = cards.map(function (card) { return card.outerHTML; });
    var pager = document.createElement("div");
    pager.className = "q-pager";
    cards[0].before(pager);
    cards.forEach(function (card) { card.remove(); });
    var page = 0;
    var size = 6;
    function draw() {
      var slice = stored.slice(page * size, page * size + size);
      var pages = Math.ceil(stored.length / size);
      pager.innerHTML = '<div class="q-pager-bar"><button type="button" data-dir="-1">Previous</button><span>Cards ' +
        (page * size + 1) + "–" + Math.min(stored.length, (page + 1) * size) + " of " + stored.length +
        '</span><button type="button" data-dir="1">Next</button></div><div class="q-list">' + slice.join("") + "</div>";
      pager.querySelectorAll("button").forEach(function (button) {
        button.addEventListener("click", function () {
          page = Math.max(0, Math.min(pages - 1, page + Number(button.getAttribute("data-dir"))));
          draw();
        });
      });
      wireItems(pager);
    }
    draw();
  }

  function wireTabs(root) {
    root.querySelectorAll(".tab-bar").forEach(function (bar) {
      if (bar.dataset.wired === "1") return;
      bar.dataset.wired = "1";
      var panes = [];
      var el = bar.nextElementSibling;
      while (el && !(el.classList && el.classList.contains("tab-bar"))) {
        if (el.classList && el.classList.contains("tab-pane")) panes.push(el);
        el = el.nextElementSibling;
      }
      if (!panes.length) return;
      var stored = panes.map(function (pane) { return pane.innerHTML; });
      panes.forEach(function (pane) { pane.innerHTML = ""; pane.classList.remove("show"); });
      var buttons = Array.prototype.slice.call(bar.querySelectorAll(".tab-btn"));
      function activate(index) {
        buttons.forEach(function (button, i) {
          var on = i === index;
          button.classList.toggle("active", on);
          button.setAttribute("aria-pressed", on ? "true" : "false");
        });
        panes.forEach(function (pane, i) {
          var on = i === index;
          pane.classList.toggle("show", on);
          if (on && pane.dataset.ready !== "1") {
            pane.innerHTML = stored[i];
            pane.dataset.ready = "1";
            paginate(pane);
            wireItems(pane);
            wireTabs(pane);
          }
        });
      }
      buttons.forEach(function (button, index) {
        button.addEventListener("click", function () { activate(index); });
      });
      if (buttons.length) activate(0);
    });
  }

  function embedsFor(meta) {
    if (/^qb-/.test(meta.id)) return [];
    var blob = (meta.group + " " + meta.title + " " + meta.id).toLowerCase();
    var tools = [];
    if (/sip|sdp|invite|cube|dial/.test(blob)) tools.push("ladder");
    if (/qos|erlang|queue|staff|contact|ucce|trunk|ccaas/.test(blob)) tools.push("erlang");
    if (/dial|cucm|sip|pstn|calling|cube/.test(blob)) tools.push("dial");
    if (/sdp|offer|codec|rtp/.test(blob) && tools.indexOf("sdp") < 0) tools.push("sdp");
    return tools.slice(0, 2);
  }

  function mountEmbeds(meta) {
    embedsFor(meta).forEach(function (name) {
      var host = document.createElement("div");
      view.appendChild(host);
      if (name === "ladder") window.UCTools.ladder(host);
      if (name === "erlang") window.UCTools.erlang(host);
      if (name === "sdp") window.UCTools.sdp(host);
      if (name === "dial") dialHandle = window.UCTelephony.mount(host);
    });
  }

  function neighbor(meta, delta) {
    var list = journeySections(meta.journey);
    var index = -1;
    list.forEach(function (item, i) { if (item.id === meta.id) index = i; });
    return list[index + delta] || null;
  }

  function renderLesson(id) {
    cleanupTools();
    var meta = findSection(id);
    if (!meta) return renderMissing();
    setTitle(meta.title);
    view.innerHTML = '<p class="muted">Opening ' + esc(meta.title) + "…</p>";
    var walksNeeded = meta.walks && meta.walks.length;
    Promise.all([
      loadSection(id),
      ensureStudio(),
      walksNeeded ? loadWalks() : Promise.resolve([])
    ]).then(function (parts) {
      if (current.name !== "lesson" || current.id !== id) return;
      var pack = parts[0];
      var section = pack.section;
      currentSection = meta;
      markSeen(meta);
      window.SECTIONS = sections();
      window.UC_SECTION_FLOW = window.UC_SECTION_FLOW || {};
      window.UC_SECTION_FLOW[section.id] = meta.flow;
      var flows = pack.flows.slice();
      if (walksNeeded) {
        (window.UC._walkList || []).forEach(function (flow) {
          if (meta.walks.indexOf(flow.id) >= 0) flows.push(flow);
        });
      }
      window.UC_FLOW_CATALOG = flows;
      var prev = neighbor(meta, -1);
      var next = neighbor(meta, 1);
      view.innerHTML =
        '<p class="kicker">' + esc(meta.group) + " · " + esc(meta.num) + "</p>" +
        '<p class="lede">' + esc(meta.sub) + "</p>" +
        '<div class="actions"><button type="button" id="markDone">Mark complete</button>' +
        (prev ? '<a href="#/lesson/' + prev.id + '">Previous</a>' : "") +
        (next ? '<a href="#/lesson/' + next.id + '">Next</a>' : "") +
        '<a href="#/journey/' + meta.journey + '">Back to path</a></div>' +
        '<article class="sec-body"></article>';
      var body = view.querySelector(".sec-body");
      body.innerHTML = window.UCTools.linkifyHtml(demoteHeadings(section.body || ""));
      wireTabs(body);
      paginate(body);
      wireItems(body);
      document.getElementById("markDone").addEventListener("click", function () {
        var state = loadProgress();
        state.done[meta.id] = 1;
        state.seen[meta.id] = 1;
        saveProgress(state);
        showToast("Marked complete in this browser.");
      });
      if (window.UCVisual && window.UCVisual.paint) {
        try { window.UCVisual.paint(section); } catch (err) { console.error(err); }
      }
      mountEmbeds(meta);
      view.insertAdjacentHTML("beforeend", window.UCTools.sourcesHtml(meta.journey));
      renderSide();
      markBottom();
    }).catch(function () {
      view.innerHTML = '<p class="warn">This lesson did not load. Check that the assets folder is beside the HTML file.</p>';
    });
    renderSide();
    markBottom();
  }

  function renderLabs() {
    cleanupTools();
    currentSection = null;
    setTitle("Labs");
    view.innerHTML = '<p class="lede">The labs are wired into lessons and also live here on their own.</p><div class="lab-grid">' +
      labCard("#/lab/ladder", "SIP ladder", "Play, pause, step, and inspect a CUCM and CUBE call.") +
      labCard("#/lab/dial", "Dialpad", "Dial tone, ringback, busy, and a lab dial plan.") +
      labCard("#/lab/topology", "3D fabric", "Orbit CUCM, CUBE, PSTN, and Webex. Cut a link.") +
      labCard("#/lab/erlang", "Erlang", "Blocking, wait probability, and a teaching ASA.") +
      labCard("#/lab/sdp", "SDP", "Break an offer into lines.") +
      labCard("#/lab/tones", "Tone bench", "Thirty-five WebAudio clips from the studio.") +
      "</div>";
    renderSide();
    markBottom();
  }

  function labCard(href, name, copy) {
    return '<a class="lab-card" href="' + href + '"><strong>' + name + "</strong><p>" + copy + "</p></a>";
  }

  function renderLab(name) {
    cleanupTools();
    currentSection = null;
    var titles = { ladder: "SIP ladder", dial: "Dialpad", topology: "3D fabric", erlang: "Erlang", sdp: "SDP", tones: "Tone bench" };
    if (!titles[name]) return renderMissing();
    setTitle(titles[name]);
    view.innerHTML = '<p><a href="#/lab">All labs</a></p><div data-lab></div>';
    var host = view.querySelector("[data-lab]");
    if (name === "ladder") window.UCTools.ladder(host);
    if (name === "dial") dialHandle = window.UCTelephony.mount(host);
    if (name === "erlang") window.UCTools.erlang(host);
    if (name === "sdp") window.UCTools.sdp(host);
    if (name === "topology") loadTopology(host);
    if (name === "tones") {
      ensureStudio().then(function () {
        if (current.name === "lab" && current.lab === "tones" && window.UCAudio) host.appendChild(window.UCAudio.bench());
      });
    }
    view.insertAdjacentHTML("beforeend", window.UCTools.sourcesHtml(""));
    renderSide();
    markBottom();
  }

  function loadTopology(host) {
    if (window.UCTopology) {
      window.UCTopology.mount(host);
      return;
    }
    var script = document.createElement("script");
    script.type = "module";
    script.src = "assets/topology.js";
    script.dataset.src = "assets/topology.js";
    script.onload = function () {
      if (current.name === "lab" && current.lab === "topology" && window.UCTopology) window.UCTopology.mount(host);
    };
    script.onerror = function () {
      host.innerHTML = "<p>The 3D fabric did not load.</p>";
    };
    document.head.appendChild(script);
  }

  function renderSearch(query) {
    cleanupTools();
    currentSection = null;
    setTitle("Search");
    var q = (query || "").trim().toLowerCase();
    var hits = [];
    if (q) {
      sections().forEach(function (item) {
        var blob = (item.title + " " + item.sub + " " + item.group + " " + item.id + " " + item.blurb).toLowerCase();
        if (blob.indexOf(q) >= 0) hits.push(item);
      });
    }
    view.innerHTML = '<label>Find a section<input id="searchBox" type="search" value="' + esc(q) + '"></label>' +
      '<p class="muted">' + (q ? hits.length + " matches" : "Titles, tracks, and the opening lines of each section.") + "</p>" +
      '<nav class="path-list">' + hits.slice(0, 40).map(function (item) {
        return '<a href="#/lesson/' + esc(item.id) + '"><span>' + esc(item.title) + "</span><small>" + esc(item.group) + "</small></a>";
      }).join("") + "</nav>";
    var box = document.getElementById("searchBox");
    box.addEventListener("input", function () {
      current.query = box.value;
      renderSearch(box.value);
      box.focus();
    });
    renderSide();
    markBottom();
  }

  function renderProgress() {
    cleanupTools();
    currentSection = null;
    setTitle("Progress");
    var state = loadProgress();
    var opened = Object.keys(state.seen).length;
    var done = Object.keys(state.done).length;
    var rows = data().journeys.map(function (journey) {
      return "<li>" + esc(journey.name) + ": " + seenCount(journey.id) + " of " + journeySections(journey.id).length + " opened</li>";
    }).join("");
    view.innerHTML = '<p class="lede">' + opened + " sections opened. " + done + " marked complete. Progress stays in this browser.</p><ul>" + rows + "</ul>" +
      '<p><button type="button" id="resetProgress">Reset progress</button></p>';
    document.getElementById("resetProgress").addEventListener("click", function () {
      localStorage.removeItem(PROGRESS_KEY);
      showToast("Progress cleared on this browser.");
      renderProgress();
    });
    renderSide();
    markBottom();
  }

  function renderMissing() {
    cleanupTools();
    currentSection = null;
    setTitle("Not found");
    view.innerHTML = '<p>That page is not in the campus. <a href="#/">Go to the start</a>.</p>';
    renderSide();
    markBottom();
  }

  function parseHash() {
    var hash = decodeURIComponent(location.hash || "#/");
    if (hash.indexOf("#/") !== 0) {
      var legacy = hash.replace(/^#/, "");
      return legacy ? { name: "lesson", id: legacy } : { name: "home" };
    }
    var parts = hash.slice(2).split("/").filter(Boolean);
    if (!parts.length) return { name: "home" };
    if (parts[0] === "journey" && parts[1]) return { name: "journey", id: parts[1], track: parts[2] || "" };
    if (parts[0] === "lesson" && parts[1]) return { name: "lesson", id: parts[1] };
    if (parts[0] === "lab") return { name: "lab", lab: parts[1] || "" };
    if (parts[0] === "search") return { name: "search", query: current.query || "" };
    if (parts[0] === "progress") return { name: "progress" };
    if (findSection(parts[0])) return { name: "lesson", id: parts[0] };
    return { name: "missing" };
  }

  function render() {
    if (!data()) return;
    current = parseHash();
    window.UC_PUBLISHED_COUNTS = publishedCounts();
    if (current.name === "home") renderHome();
    else if (current.name === "journey") renderJourney(current.id, current.track);
    else if (current.name === "lesson") renderLesson(current.id);
    else if (current.name === "lab" && !current.lab) renderLabs();
    else if (current.name === "lab") renderLab(current.lab);
    else if (current.name === "search") renderSearch(current.query || "");
    else if (current.name === "progress") renderProgress();
    else renderMissing();
  }

  function publishedCounts() {
    var stats = data().stats;
    return {
      sections: stats.sections,
      flowDefinitions: stats.flows,
      animatedSections: stats.sections,
      walkthroughs: stats.walkthroughs,
      illustrations: stats.illustrations,
      chartTypes: stats.charts,
      audioClips: stats.audioClips,
      trackHubs: stats.trackHubs
    };
  }

  function openPalette() {
    var palette = document.getElementById("palette");
    palette.hidden = false;
    var input = document.getElementById("paletteInput");
    input.value = "";
    paintHits("");
    input.focus();
  }

  function closePalette() {
    document.getElementById("palette").hidden = true;
  }

  function paintHits(query) {
    var q = query.trim().toLowerCase();
    var hits = sections().filter(function (item) {
      if (!q) return false;
      return (item.title + " " + item.group + " " + item.id).toLowerCase().indexOf(q) >= 0;
    }).slice(0, 12);
    document.getElementById("paletteHits").innerHTML = hits.map(function (item) {
      return '<button type="button" class="hit" data-id="' + esc(item.id) + '"><b>' + esc(item.title) + "</b><small>" + esc(item.group) + "</small></button>";
    }).join("");
  }

  function workerJob(payload) {
    if (!exportWorker) exportWorker = new Worker("assets/export-worker.js");
    var id = ++exportSeq;
    return new Promise(function (resolve, reject) {
      function onMessage(event) {
        if (!event.data || event.data.id !== id) return;
        exportWorker.removeEventListener("message", onMessage);
        if (event.data.error) reject(new Error(event.data.error));
        else resolve(event.data);
      }
      exportWorker.addEventListener("message", onMessage);
      payload.id = id;
      exportWorker.postMessage(payload);
    });
  }

  function download(name, type, text) {
    var blob = new Blob([text], { type: type });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
  }

  function ensureMeter() {
    var meter = document.getElementById("exportMeter");
    if (meter) return meter;
    view.insertAdjacentHTML("afterbegin", '<div id="exportMeter"><p data-label>Working…</p><div class="meter"><i data-bar></i></div></div>');
    return document.getElementById("exportMeter");
  }

  function fetchModules(ids, label) {
    var meter = ensureMeter();
    var bar = meter.querySelector("[data-bar]");
    var text = meter.querySelector("[data-label]");
    var done = 0;
    var chunks = [];
    function next(index) {
      if (index >= ids.length) return Promise.resolve(chunks);
      var slice = ids.slice(index, index + 3);
      return Promise.all(slice.map(function (id) {
        return fetch("assets/curriculum/sections/" + id + ".js").then(function (response) {
          if (!response.ok) throw new Error(id);
          return response.text();
        });
      })).then(function (texts) {
        chunks.push(texts);
        done += texts.length;
        var ratio = Math.round((done / ids.length) * 100);
        bar.style.width = ratio + "%";
        text.textContent = label + " " + done + " / " + ids.length;
        return next(index + 3);
      });
    }
    return next(0).then(function () {
      return chunks.reduce(function (all, group) { return all.concat(group); }, []);
    });
  }

  function exportCsv() {
    if (location.protocol === "file:") {
      showToast("Open the campus over http to build the CSV in a worker.");
      return;
    }
    var ids = sections().map(function (item) { return item.id; });
    fetchModules(ids, "Reading").then(function (texts) {
      var groups = [];
      for (var i = 0; i < texts.length; i += 8) groups.push(texts.slice(i, i + 8));
      var rows = ["section,group,title,number,kind,prompt,answer"];
      var chain = Promise.resolve();
      groups.forEach(function (group) {
        chain = chain.then(function () {
          return workerJob({ type: "csv", texts: group }).then(function (result) {
            if (result.csv) rows.push(result.csv);
          });
        });
      });
      return chain.then(function () {
        download("uc-lab-questions.csv", "text/csv", rows.join("\n"));
        showToast("Question CSV is ready.");
      });
    }).catch(function () { showToast("Export stopped before the file was built."); });
  }

  function exportMarkdown(ids, filename) {
    if (!ids.length) {
      showToast("Open a lesson first.");
      return;
    }
    if (location.protocol === "file:") {
      var loaded = ids.map(function (id) { return window.UC._packs[id]; }).filter(Boolean);
      if (loaded.length !== ids.length) {
        showToast("Open the campus over http to export lessons that are not already open.");
        return;
      }
    }
    var source = location.protocol === "file:"
      ? Promise.resolve([])
      : fetchModules(ids, "Reading");
    source.then(function (texts) {
      if (location.protocol === "file:") {
        texts = ids.map(function (id) {
          var pack = window.UC._packs[id];
          return "UC.pack(" + JSON.stringify(pack.section) + ",[]);";
        });
      }
      return workerJob({ type: "md", texts: texts });
    }).then(function (result) {
      download(filename, "text/markdown", result.md || "");
      showToast("Markdown is ready.");
    }).catch(function () { showToast("Markdown export did not finish."); });
  }

  function idsForJourney(journeyId) {
    return journeySections(journeyId).map(function (item) { return item.id; });
  }

  function saveOffline() {
    if (!("serviceWorker" in navigator) || location.protocol === "file:") {
      showToast("Offline save runs when the campus is served over http.");
      return;
    }
    var ids = sections().map(function (item) { return item.id; });
    var meter = ensureMeter();
    var bar = meter.querySelector("[data-bar]");
    var text = meter.querySelector("[data-label]");
    var done = 0;
    function step(index) {
      if (index >= ids.length) {
        text.textContent = "Offline copy stored in this browser.";
        showToast("Lessons are cached for offline use.");
        return;
      }
      var id = ids[index];
      fetch("assets/curriculum/sections/" + id + ".js").then(function () {
        done += 1;
        bar.style.width = Math.round((done / ids.length) * 100) + "%";
        text.textContent = "Saving " + done + " / " + ids.length;
        step(index + 1);
      }).catch(function () {
        text.textContent = "Stopped at " + id + ".";
      });
    }
    step(0);
  }

  function registerWorker() {
    if (!("serviceWorker" in navigator) || location.protocol === "file:") return;
    navigator.serviceWorker.register("sw.js").catch(function () { /* file or blocked */ });
  }

  function bind() {
    document.getElementById("menuBtn").addEventListener("click", function () {
      var open = !side.classList.contains("open");
      side.classList.toggle("open", open);
      document.getElementById("backdrop").hidden = !open;
      document.getElementById("menuBtn").setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.getElementById("backdrop").addEventListener("click", closeSide);
    side.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeSide();
    });
    document.getElementById("theme").value = document.documentElement.getAttribute("data-theme") || "light";
    document.getElementById("theme").addEventListener("change", function (event) {
      var theme = event.target.value;
      document.documentElement.setAttribute("data-theme", theme);
      try { localStorage.setItem("uc_theme", theme); } catch (err) { /* private */ }
    });
    document.getElementById("searchBtn").addEventListener("click", openPalette);
    document.getElementById("palette").addEventListener("click", function (event) {
      if (event.target.id === "palette") closePalette();
      var hit = event.target.closest(".hit");
      if (!hit) return;
      closePalette();
      location.hash = "#/lesson/" + hit.getAttribute("data-id");
    });
    document.getElementById("paletteInput").addEventListener("input", function (event) {
      paintHits(event.target.value);
    });
    document.addEventListener("keydown", function (event) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        openPalette();
      } else if (event.key === "Escape") closePalette();
    });
    document.getElementById("exportCsv").addEventListener("click", exportCsv);
    document.getElementById("exportMd").addEventListener("click", function () {
      if (!currentSection) showToast("Open a lesson first.");
      else exportMarkdown([currentSection.id], currentSection.id + ".md");
    });
    document.getElementById("exportJourney").addEventListener("click", function () {
      var journeyId = currentSection ? currentSection.journey : (current.name === "journey" ? current.id : "cisco-voice");
      exportMarkdown(idsForJourney(journeyId), journeyId + ".md");
    });
    document.getElementById("printLesson").addEventListener("click", function () {
      if (current.name !== "lesson") showToast("Open a lesson, then print that lesson.");
      else window.print();
    });
    document.getElementById("saveOffline").addEventListener("click", saveOffline);
    window.addEventListener("hashchange", render);
  }

  window.openSection = function (id) {
    location.hash = "#/lesson/" + id;
  };
  window.getCurrentSectionId = function () {
    return currentSection ? currentSection.id : "";
  };

  bind();
  registerWorker();
  loadScript("assets/curriculum/manifest.js").then(function () {
    window.UC_CHART_TYPES = data().chartTypes || [];
    window.UC_PUBLISHED_COUNTS = publishedCounts();
    if (!location.hash) history.replaceState(null, "", "#/");
    render();
  }).catch(function () {
    view.innerHTML = "<p>The curriculum manifest did not load. Keep the assets folder beside this HTML file.</p>";
  });
})();
