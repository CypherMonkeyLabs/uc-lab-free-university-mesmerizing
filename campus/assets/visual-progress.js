/* Local progress, achievements, and the track map. No personal data is stored. */
(function () {
  var KEY = "uc_vs_progress";
  var TRACKS = [
    ["home", "Start"],
    ["proto-sip-master", "SIP"],
    ["prod-cube", "CUCM"],
    ["vd-webex-calling-call-flow", "Cloud"],
    ["hub-icm-ucce", "UCCE"],
    ["prod-wxcc", "CCaaS"],
    ["found-11", "E911"],
    ["hub-qos", "QoS"],
    ["hub-migrations", "Move"],
    ["trick-0", "Faults"],
    ["mm-licc", "Proof"],
    ["arch-capacity", "Design"],
    ["drill-sip-dialplan-licc", "Drills"],
    ["glossary", "Index"]
  ];

  function load() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || "{}");
      raw.seen = raw.seen || {};
      raw.done = raw.done || {};
      raw.tones = raw.tones || 0;
      raw.walks = raw.walks || 0;
      return raw;
    } catch (e) {
      return { seen: {}, done: {}, tones: 0, walks: 0 };
    }
  }
  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }
  function seen(section) {
    if (!section || !section.id) return;
    var state = load();
    state.seen[section.id] = 1;
    save(state);
  }
  function done(flow) {
    if (!flow || !flow.id) return;
    var state = load();
    var first = !state.done[flow.id];
    state.done[flow.id] = 1;
    if (first && (flow.walkthrough || flow.layout === "walk")) state.walks += 1;
    save(state);
  }
  function tone() {
    var state = load();
    state.tones += 1;
    save(state);
  }
  function achievements(state) {
    var seenN = Object.keys(state.seen).length;
    var doneN = Object.keys(state.done).length;
    return [
      ["First section", seenN >= 1],
      ["Five sections", seenN >= 5],
      ["Finished a ladder", doneN >= 1],
      ["Played a tone", state.tones >= 1],
      ["Opened a walkthrough", state.walks >= 1],
      ["Twenty sections", seenN >= 20]
    ];
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function map(section) {
    var state = load();
    var wrap = document.createElement("div");
    wrap.className = "vs-map";
    var parts = ['<svg viewBox="0 0 760 132" role="img" aria-label="Track map">'];
    TRACKS.forEach(function (t, i) {
      var x = 28 + (i % 7) * 104;
      var y = i < 7 ? 18 : 72;
      if (i > 0) {
        var prev = i - 1;
        var x1 = 28 + (prev % 7) * 104 + 36;
        var y1 = prev < 7 ? 36 : 90;
        var x2 = x + 8;
        var y2 = y + 18;
        if (prev !== 6) parts.push('<path d="M' + x1 + " " + y1 + " H" + x2 + '" fill="none" stroke="currentColor" stroke-opacity=".25"/>');
      }
      var on = section && section.id === t[0];
      var visited = state.seen[t[0]];
      parts.push('<rect class="vs-map-node" x="' + x + '" y="' + y + '" width="92" height="36" rx="12" data-id="' + esc(t[0]) + '" fill="' + (on ? "#6366F1" : "var(--card,#fff)") + '" stroke="' + (on ? "#6366F1" : visited ? "#0F9B8E" : "currentColor") + '" stroke-opacity="' + (on ? 1 : 0.35) + '"/>');
      parts.push('<text x="' + (x + 46) + '" y="' + (y + 23) + '" text-anchor="middle" fill="' + (on ? "#fff" : "currentColor") + '" font-size="12" font-weight="700" font-family="ui-sans-serif,system-ui">' + esc(t[1]) + "</text>");
    });
    parts.push("</svg>");
    wrap.innerHTML = parts.join("");
    wrap.querySelectorAll(".vs-map-node").forEach(function (node) {
      node.addEventListener("click", function () {
        if (window.openSection) window.openSection(node.getAttribute("data-id"));
      });
    });
    var row = document.createElement("div");
    row.className = "vs-badges";
    achievements(state).forEach(function (item) {
      var b = document.createElement("span");
      b.className = "vs-badge" + (item[1] ? " got" : "");
      b.textContent = item[0];
      row.appendChild(b);
    });
    wrap.appendChild(row);
    return wrap;
  }
  window.UCProgress = { seen: seen, done: done, tone: tone, map: map, load: load };
})();
