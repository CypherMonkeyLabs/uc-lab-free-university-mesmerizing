/* UC Lab visual studio. Offline. Renders inline SVG, step-through flows, charts, and WebAudio tones. */
(function () {
  "use strict";

  var INDIGO = "#6366F1";
  var TEAL = "#0F9B8E";
  var GREEN = "#22C55E";
  var AMBER = "#E08A00";
  var NAVY = "#0B1220";
  var ROSE = "#E11D48";

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function byIdMap(list) {
    var m = {};
    (list || []).forEach(function (f) { if (f && f.id) m[f.id] = f; });
    return m;
  }

  function sectionFlow(section) {
    var map = window.UC_SECTION_FLOW || {};
    var id = map[section.id];
    var cat = byIdMap(window.UC_FLOW_CATALOG || []);
    if (id && cat[id]) return cat[id];
    var fallback = {
      "Start here": "licc-path",
      "SIP and media": "sip-basic",
      "CUCM and CUBE": "cube-b2bua",
      "Webex Calling and Teams Phone": "wx-lgw-out",
      "Contact center — UCCE and PCCE": "ucce-comp",
      "CCaaS and UCaaS platforms": "ccaas-generic",
      "Emergency calling": "e911-cer",
      "Voice network and QoS": "qos-path",
      "Migrations": "mig-dual-run",
      "Troubleshooting": "ts-licc",
      "Evidence habits": "evidence-pack",
      "Design notes": "design-read",
      "Practice": "practice-loop",
      "Reference": "reference-loop"
    };
    id = fallback[section.group] || "licc-path";
    return cat[id] || (window.UC_FLOW_CATALOG || [])[0] || null;
  }

  function kindColor(kind) {
    if (kind === "ok" || kind === "media") return GREEN;
    if (kind === "prov") return AMBER;
    if (kind === "err") return ROSE;
    if (kind === "bye") return "#7C3AED";
    if (kind === "note") return TEAL;
    return TEAL;
  }

  function iconSvg(name) {
    var p = {
      sip: '<path d="M4 8h16M4 12h10M4 16h16" fill="none" stroke="' + INDIGO + '" stroke-width="1.8" stroke-linecap="round"/><path d="m14 10 4 2-4 2" fill="none" stroke="' + TEAL + '" stroke-width="1.8"/>',
      cube: '<rect x="3" y="7" width="8" height="10" rx="2" fill="none" stroke="' + TEAL + '" stroke-width="1.7"/><rect x="13" y="7" width="8" height="10" rx="2" fill="none" stroke="' + INDIGO + '" stroke-width="1.7"/><path d="M11 12h2" stroke="' + AMBER + '" stroke-width="1.7"/>',
      phone: '<path d="M8 4h3l1 3-2 1a8 8 0 0 0 4 4l1-2 3 1v3a2 2 0 0 1-2 2A12 12 0 0 1 6 6a2 2 0 0 1 2-2z" fill="none" stroke="' + TEAL + '" stroke-width="1.6"/>',
      queue: '<circle cx="7" cy="8" r="2" fill="' + INDIGO + '"/><circle cx="17" cy="16" r="2" fill="' + TEAL + '"/><path d="M9 8h5a3 3 0 0 1 3 3v3" fill="none" stroke="' + AMBER + '" stroke-width="1.6"/>',
      emergency: '<path d="M12 3 3 20h18L12 3z" fill="none" stroke="' + ROSE + '" stroke-width="1.6"/><path d="M12 9v5" stroke="' + AMBER + '" stroke-width="1.8" stroke-linecap="round"/>',
      qos: '<path d="M4 16h16M7 16V8M12 16V5M17 16v-6" stroke="' + GREEN + '" stroke-width="1.8" stroke-linecap="round"/>',
      route: '<circle cx="6" cy="12" r="2.2" fill="' + TEAL + '"/><circle cx="18" cy="7" r="2.2" fill="' + INDIGO + '"/><circle cx="18" cy="17" r="2.2" fill="' + AMBER + '"/><path d="M8 12h6M14 12l2-4M14 12l2 4" fill="none" stroke="' + NAVY + '" stroke-width="1.4"/>',
      media: '<path d="M5 15c2-6 4-6 6 0s4 6 6 0 4-6 2 0" fill="none" stroke="' + INDIGO + '" stroke-width="1.6" stroke-linecap="round"/>',
      cloud: '<path d="M7 16h10a3 3 0 0 0 .3-6 4.5 4.5 0 0 0-8.6-1A2.8 2.8 0 0 0 7 16z" fill="none" stroke="' + TEAL + '" stroke-width="1.6"/>',
      proof: '<path d="M5 12.5 9 16.5 19 7" fill="none" stroke="' + GREEN + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
      migration: '<path d="M4 8h12M4 16h12M14 5l3 3-3 3M8 13l-3 3 3 3" fill="none" stroke="' + AMBER + '" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
      tree: '<path d="M12 4v6M12 10H7v4M12 10h5v4" fill="none" stroke="' + INDIGO + '" stroke-width="1.6"/><circle cx="12" cy="4" r="1.6" fill="' + TEAL + '"/>',
      team: '<rect x="4" y="6" width="16" height="11" rx="2" fill="none" stroke="' + INDIGO + '" stroke-width="1.6"/><path d="M8 17v2M16 17v2M7 20h10" stroke="' + TEAL + '" stroke-width="1.6" stroke-linecap="round"/>',
      cert: '<path d="M12 3 19 6v6c0 4-7 7-7 7s-7-3-7-7V6z" fill="none" stroke="' + TEAL + '" stroke-width="1.6"/><path d="m9 11 2 2 4-4" fill="none" stroke="' + GREEN + '" stroke-width="1.6" stroke-linecap="round"/>'
    };
    var inner = p[name] || p.proof;
    return '<svg viewBox="0 0 24 24" aria-hidden="true">' + inner + "</svg>";
  }

  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function clipLabel(text, max) {
    var s = String(text || "");
    if (s.length <= max) return s;
    return s.slice(0, Math.max(0, max - 1)) + "…";
  }

  function heroSvg(section, flow) {
    var actors = (flow && flow.actors) || ["Leg", "Function", "Proof"];
    var n = Math.max(actors.length, 1);
    var w = 880, h = 198;
    var gap = (w - 56) / n;
    var parts = [];
    var chars = n > 4 ? 11 : 16;
    parts.push('<svg class="vs-hero" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="Hero for ' + esc(section.title) + '">');
    parts.push('<rect width="' + w + '" height="' + h + '" rx="16" fill="#0B1220"/>');
    parts.push('<path d="M24 96 H856" fill="none" stroke="#6366F1" stroke-opacity=".28" stroke-width="1"/>');
    parts.push('<text x="24" y="32" fill="#5EEAD4" font-size="12" font-weight="800" font-family="ui-sans-serif,system-ui">' + esc(section.num || "") + "  ·  " + esc(section.group || "") + "</text>");
    var title = String(section.title || "").slice(0, 62);
    parts.push('<text x="24" y="58" fill="#F8FAFC" font-size="20" font-weight="800" font-family="Georgia,serif">' + esc(title) + "</text>");
    parts.push('<text x="24" y="80" fill="#C7D2FE" font-size="12" font-family="ui-sans-serif,system-ui">' + esc(String((flow && flow.why) || "").slice(0, 108)) + "</text>");
    for (var i = 0; i < n; i++) {
      var x = 28 + i * gap;
      var cardW = Math.max(64, gap - 20);
      var col = i % 2 === 0 ? TEAL : INDIGO;
      if (i < n - 1) {
        var nextX = 28 + (i + 1) * gap;
        parts.push('<path class="vs-march" d="M' + (x + cardW + 2) + " 140 H" + (nextX - 2) + '" fill="none" stroke="#F5B942" stroke-width="2"/>');
      }
      parts.push('<rect x="' + x + '" y="112" width="' + cardW + '" height="54" rx="14" fill="#121A2F" stroke="' + col + '" stroke-width="2"/>');
      parts.push('<circle cx="' + (x + 16) + '" cy="139" r="5" fill="' + col + '"/>');
      parts.push('<text x="' + (x + 28) + '" y="143" fill="#F8FAFC" font-size="11" font-weight="700" font-family="ui-sans-serif,system-ui">' + esc(clipLabel(actors[i], chars)) + "</text>");
    }
    parts.push("</svg>");
    return parts.join("");
  }

  function packetMarkup(x1, y, x2, color) {
    if (reducedMotion() || Math.abs(x1 - x2) < 2) {
      var at = Math.abs(x1 - x2) < 2 ? x1 : x2;
      return '<circle cx="' + at + '" cy="' + y + '" r="5" fill="#fff" stroke="' + color + '" stroke-width="2"/>';
    }
    return '<circle cx="' + x1 + '" cy="' + y + '" r="5" fill="#fff" stroke="' + color + '" stroke-width="2"><animate attributeName="cx" from="' + x1 + '" to="' + x2 + '" dur="1.15s" repeatCount="indefinite"/></circle>';
  }

  function ladderSvg(flow, index) {
    var actors = flow.actors || [];
    var steps = flow.steps || [];
    var n = Math.max(actors.length, 1);
    var w = 880;
    var top = 86;
    var row = 54;
    var h = top + steps.length * row + 22;
    var colW = (w - 36) / n;
    function cx(i) { return 18 + colW * i + colW / 2; }
    var current = steps[index] || {};
    var out = ['<svg class="vs-flow" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(flow.title) + '">'];
    out.push('<rect width="' + w + '" height="' + h + '" rx="16" fill="transparent"/>');
    for (var a = 0; a < n; a++) {
      var x = cx(a);
      var hot = a === current.f || a === current.t;
      var pillW = Math.min(colW - 10, 156);
      out.push('<rect x="' + (x - colW / 2 + 6) + '" y="48" width="' + (colW - 12) + '" height="' + (h - 64) + '" rx="14" fill="' + (hot ? "#6366F1" : "currentColor") + '" fill-opacity="' + (hot ? "0.08" : "0.035") + '"/>');
      out.push('<rect x="' + (x - pillW / 2) + '" y="10" width="' + pillW + '" height="30" rx="15" fill="' + (hot ? INDIGO : "var(--card)") + '" stroke="' + (hot ? INDIGO : "currentColor") + '" stroke-opacity="' + (hot ? "1" : ".35") + '"/>');
      out.push('<text x="' + x + '" y="30" text-anchor="middle" fill="' + (hot ? "#fff" : "currentColor") + '" font-size="11" font-weight="800" font-family="ui-sans-serif,system-ui">' + esc(clipLabel(actors[a], 22)) + "</text>");
      out.push('<path d="M' + x + " 42 V" + (h - 14) + '" stroke="' + (hot ? INDIGO : "currentColor") + '" stroke-width="' + (hot ? "2.2" : "1.2") + '" stroke-opacity="' + (hot ? ".9" : ".28") + '"/>');
    }
    for (var i = 0; i < steps.length; i++) {
      var st = steps[i];
      var y = top + i * row;
      var x1 = cx(Math.max(0, Math.min(n - 1, st.f || 0)));
      var x2 = cx(Math.max(0, Math.min(n - 1, st.t || 0)));
      var state = i < index ? "done" : i === index ? "current" : "future";
      var op = state === "future" ? 0.28 : 1;
      var color = state === "current" ? INDIGO : kindColor(st.kind);
      var sw = state === "current" ? 3.4 : 1.8;
      var cls = state === "current" ? ' class="vs-current vs-march"' : "";
      var self = Math.abs(x1 - x2) < 2;
      if (state === "current") {
        out.push('<rect x="10" y="' + (y - 22) + '" width="' + (w - 20) + '" height="40" rx="12" fill="#6366F1" fill-opacity="0.12"/>');
      }
      if (self) {
        out.push('<path' + cls + ' d="M' + x1 + " " + (y - 2) + " q22 -20 0 -32" + '" fill="none" stroke="' + color + '" stroke-width="' + sw + '" stroke-opacity="' + op + '" stroke-linecap="round"/>');
      } else {
        out.push('<path' + cls + ' d="M' + x1 + " " + y + " H" + x2 + '" fill="none" stroke="' + color + '" stroke-width="' + sw + '" stroke-opacity="' + op + '" stroke-linecap="round"/>');
        var dir = x2 > x1 ? 1 : -1;
        out.push('<path d="M' + x2 + " " + y + " l" + (-dir * 9) + " -4.5 v9 z" + '" fill="' + color + '" fill-opacity="' + op + '"/>');
        if (state === "current") out.push(packetMarkup(x1, y, x2, color));
      }
      var mx = (x1 + x2) / 2;
      var shown = (i + 1) + "  " + clipLabel(st.label, self ? 16 : 20);
      var tw = Math.min(210, 16 + shown.length * 6.5);
      out.push('<rect x="' + (mx - tw / 2) + '" y="' + (y - 20) + '" width="' + tw + '" height="18" rx="9" fill="var(--card)" stroke="' + color + '" stroke-width="' + (state === "current" ? 2 : 1) + '" stroke-opacity="' + op + '"/>');
      out.push('<text x="' + mx + '" y="' + (y - 7) + '" text-anchor="middle" fill="currentColor" font-size="11" font-weight="800" opacity="' + op + '" font-family="ui-sans-serif,system-ui">' + esc(shown) + "</text>");
    }
    out.push("</svg>");
    return out.join("");
  }

  function treeSvg(flow, index) {
    var steps = flow.steps || [];
    var w = 880;
    var row = 72;
    var h = 20 + steps.length * row;
    var out = ['<svg class="vs-flow" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(flow.title) + '">'];
    out.push('<rect width="' + w + '" height="' + h + '" fill="transparent"/>');
    if (steps.length > 1) {
      out.push('<path d="M48 36 V' + (h - 36) + '" stroke="currentColor" stroke-opacity=".25" stroke-width="2"/>');
    }
    for (var i = 0; i < steps.length; i++) {
      var y = 16 + i * row;
      var state = i < index ? "done" : i === index ? "current" : "future";
      var fill = state === "current" ? INDIGO : state === "done" ? TEAL : "var(--card)";
      var ink = state === "future" ? "currentColor" : "#fff";
      var op = state === "future" ? 0.72 : 1;
      var stroke = state === "current" ? INDIGO : state === "done" ? TEAL : "currentColor";
      out.push('<circle cx="48" cy="' + (y + 26) + '" r="' + (state === "current" ? 16 : 13) + '" fill="' + (state === "future" ? "var(--card)" : fill) + '" stroke="' + stroke + '" stroke-width="2"/>');
      out.push('<text x="48" y="' + (y + 31) + '" text-anchor="middle" fill="' + (state === "future" ? "currentColor" : "#fff") + '" font-size="12" font-weight="800" font-family="ui-sans-serif,system-ui">' + (i + 1) + "</text>");
      out.push('<rect x="76" y="' + y + '" width="780" height="52" rx="14" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + (state === "current" ? 2.5 : 1.5) + '" opacity="' + op + '"/>');
      out.push('<text x="96" y="' + (y + 32) + '" fill="' + ink + '" font-size="15" font-weight="800" font-family="ui-sans-serif,system-ui">' + esc(steps[i].label || "") + "</text>");
    }
    out.push("</svg>");
    return out.join("");
  }

  function walkSvg(flow, index) {
    var steps = flow.steps || [];
    var actors = flow.actors || [];
    var st = steps[index] || {};
    var w = 880;
    var h = 250;
    var out = ['<svg class="vs-flow vs-walk" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(flow.title || "Walkthrough") + '">'];
    out.push('<rect width="' + w + '" height="' + h + '" rx="18" fill="#102033"/>');
    out.push('<text x="28" y="36" fill="#5EEAD4" font-size="13" font-weight="800" font-family="ui-sans-serif,system-ui">Scene ' + (index + 1) + " of " + steps.length + "</text>");
    out.push('<text x="28" y="86" fill="#F8FAFC" font-size="30" font-weight="800" font-family="Georgia,serif">' + esc(st.label || "") + "</text>");
    var tickW = Math.max(8, (w - 56) / Math.max(steps.length, 1) - 6);
    for (var i = 0; i < steps.length; i++) {
      var x = 28 + i * ((w - 56) / Math.max(steps.length, 1));
      var fill = i < index ? "#0F9B8E" : i === index ? "#E08A00" : "#334155";
      out.push('<rect x="' + x + '" y="128" width="' + tickW + '" height="12" rx="4" fill="' + fill + '"/>');
    }
    actors.forEach(function (name, i) {
      var x = 28 + i * 210;
      var on = i === st.f || i === st.t;
      out.push('<rect x="' + x + '" y="168" width="188" height="52" rx="14" fill="' + (on ? "#6366F1" : "#1c2c3d") + '"/>');
      out.push('<text x="' + (x + 94) + '" y="199" text-anchor="middle" fill="#fff" font-size="14" font-weight="700" font-family="ui-sans-serif,system-ui">' + esc(name) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }

  function headerSvg(which) {
    var lines;
    if (which && typeof which === "object" && which.headerLines) {
      lines = which.headerLines;
    } else if (which === "hold") {
      lines = [
        "re-INVITE sip:bob.example SIP/2.0",
        "Call-ID: lab-dialog-001",
        "CSeq: 2 INVITE",
        "Content-Type: application/sdp",
        "m=audio 16384 RTP/AVP 0",
        "a=sendonly"
      ];
    } else if (which === "sdp") {
      lines = [
        "v=0",
        "o=alice 1 1 IN IP4 192.0.2.10",
        "c=IN IP4 192.0.2.10",
        "m=audio 16384 RTP/AVP 0 8",
        "a=rtpmap:0 PCMU/8000",
        "a=sendrecv"
      ];
    } else {
      lines = [
        "INVITE sip:bob.example SIP/2.0",
        "Via: SIP/2.0/TLS alice.example;branch=z9hG4bK-lab",
        "Max-Forwards: 70",
        "From: Alice;tag=from-a",
        "To: Bob",
        "Call-ID: lab-dialog-001",
        "CSeq: 1 INVITE",
        "Contact: sip:alice.example;transport=tls",
        "Content-Type: application/sdp"
      ];
    }
    var h = 36 + lines.length * 18;
    var out = ['<svg viewBox="0 0 880 ' + h + '" role="img" aria-label="Protocol header diagram">'];
    out.push('<rect width="880" height="' + h + '" rx="16" fill="#0B1220"/>');
    out.push('<text x="20" y="24" fill="#5EEAD4" font-size="12" font-weight="800" font-family="ui-sans-serif,system-ui">Lab header · example names · not a capture</text>');
    lines.forEach(function (line, i) {
      out.push('<text x="20" y="' + (48 + i * 18) + '" fill="#F8FAFC" font-size="13" font-family="ui-monospace,monospace">' + esc(line) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }

  var FAMILIES = {
    sip: ["sip-basic", "sip-proxy", "sip-183", "sip-prack", "sip-hold", "sip-refer", "sip-attended", "sip-cancel", "sip-407", "sip-options", "sip-delayed", "sip-dtmf", "sip-486", "sip-503", "stir-shaken"],
    cube: ["cube-b2bua", "cube-delayed", "cube-failover", "cube-ha", "walk-call-setup", "sbc-topo"],
    cucm: ["cucm-route", "cucm-onnet", "cucm-reg", "cucm-srst", "cucm-hunt", "cucm-em", "cucm-moh", "cucm-conf", "cucm-mtp", "cucm-failover", "unity-mwi"],
    wx: ["wx-lgw-out", "wx-lgw-in", "wx-plan"],
    teams: ["teams-dr-out", "teams-dr-in", "teams-options", "teams-bypass", "teams-plan", "walk-failover"],
    ucce: ["ucce-comp", "ucce-rona", "pcce", "cc-route", "cuic"],
    e911: ["e911-cer", "e911-held", "e911-teams", "e911-kari"],
    qos: ["qos-path", "qos-trust", "qos-wifi", "qos-sdwan", "qos-drop"]
  };

  function familyFlows(flow) {
    var cat = byIdMap(window.UC_FLOW_CATALOG || []);
    if (flow.scenarios && flow.scenarios.length) {
      var listed = flow.scenarios.map(function (id) { return cat[id]; }).filter(Boolean);
      if (listed.length > 1) return listed;
    }
    var ids = null;
    Object.keys(FAMILIES).forEach(function (name) {
      if (FAMILIES[name].indexOf(flow.id) >= 0) ids = FAMILIES[name];
    });
    if (!ids) return [];
    return ids.map(function (id) { return cat[id]; }).filter(Boolean);
  }

  function mountPlayer(host, flow, section) {
    var steps = flow.steps || [];
    var index = 0;
    var timer = null;
    var speed = 1;
    var playing = false;
    var params = new URLSearchParams(location.search || "");
    if (params.get("step")) {
      var forced = parseInt(params.get("step"), 10);
      if (!isNaN(forced)) index = Math.max(0, Math.min(steps.length - 1, forced));
    }
    var choices = familyFlows(flow);
    var scenario = "";
    if (choices.length > 1) {
      scenario = '<label class="vs-scenario">Scenario <select data-act="scenario" aria-label="Call-flow scenario">';
      choices.forEach(function (item, i) {
        scenario += '<option value="' + i + '"' + (item.id === flow.id ? " selected" : "") + ">" + esc(item.title) + "</option>";
      });
      scenario += "</select></label>";
    }
    var legend = flow.layout === "tree" ? "" :
      '<div class="vs-legend" aria-hidden="true"><span><i style="background:#0F9B8E"></i>Request</span><span><i style="background:#E08A00"></i>Provisional</span><span><i style="background:#22C55E"></i>Answer or media</span><span><i style="background:#E11D48"></i>Failure</span><span><i style="background:#6366F1"></i>Current step</span></div>';
    host.tabIndex = 0;
    host.innerHTML =
      '<div class="vs-player-top"><h3>' + esc(flow.title) + '</h3><span class="vs-cite">' + esc(flow.cite || "Campus diagram") + "</span></div>" +
      '<p class="vs-why"><b>Why it matters.</b> ' + esc(flow.why || "") + "</p>" +
      scenario +
      legend +
      '<div class="vs-rail" data-rail role="progressbar" aria-valuemin="1" aria-valuemax="' + steps.length + '" aria-valuenow="1"><i></i></div>' +
      '<div class="vs-svg-scroll" data-svg></div>' +
      '<p class="vs-cap vs-cap-in" aria-live="polite"></p>' +
      '<div class="vs-controls">' +
      '<button type="button" data-act="play" aria-pressed="false">Play</button>' +
      '<button type="button" data-act="prev">Step back</button>' +
      '<button type="button" data-act="next">Step forward</button>' +
      '<label>Speed <select data-act="speed" aria-label="Playback speed"><option>0.5x</option><option selected>1x</option><option>2x</option></select></label>' +
      '<span class="vs-pos" data-pos></span></div>' +
      '<div class="vs-timeline" data-dots role="tablist" aria-label="Steps"></div>' +
      '<p class="vs-keys-hint">Focus this player, then use Left and Right to step and Space to play or pause.</p>';
    var svgHost = host.querySelector("[data-svg]");
    var cap = host.querySelector(".vs-cap");
    var pos = host.querySelector("[data-pos]");
    var dots = host.querySelector("[data-dots]");
    var rail = host.querySelector("[data-rail] i");
    var railBox = host.querySelector("[data-rail]");
    var playBtn = host.querySelector('[data-act=play]');
    var titleEl = host.querySelector("h3");
    var citeEl = host.querySelector(".vs-cite");
    var whyEl = host.querySelector(".vs-why");
    function fillSteps() {
      dots.innerHTML = "";
      steps.forEach(function (st, i) {
        var b = document.createElement("button");
        b.type = "button";
        b.setAttribute("role", "tab");
        b.title = st.label || ("Step " + (i + 1));
        b.innerHTML = "<b>" + (i + 1) + "</b> " + esc(st.label || "Step");
        b.addEventListener("click", function () { stop(); index = i; draw(); });
        dots.appendChild(b);
      });
      if (railBox) railBox.setAttribute("aria-valuemax", String(steps.length));
    }
    fillSteps();
    function draw() {
      var svg = flow.layout === "tree" ? treeSvg(flow, index) : flow.layout === "walk" ? walkSvg(flow, index) : ladderSvg(flow, index);
      svgHost.innerHTML = svg;
      var st = steps[index] || { label: "", cap: "" };
      cap.classList.remove("vs-cap-in");
      cap.innerHTML = '<span class="vs-step-k">Step ' + (index + 1) + " of " + steps.length + " · " + esc(st.label || "") + "</span>" + esc(st.cap || "");
      void cap.offsetWidth;
      cap.classList.add("vs-cap-in");
      pos.textContent = (index + 1) + " / " + steps.length;
      if (rail) rail.style.width = (((index + 1) / Math.max(steps.length, 1)) * 100) + "%";
      if (index === steps.length - 1 && window.UCProgress) window.UCProgress.done(flow);
      if (railBox) railBox.setAttribute("aria-valuenow", String(index + 1));
      var ds = dots.querySelectorAll("button");
      var currentBtn = null;
      for (var i = 0; i < ds.length; i++) {
        var on = i === index;
        ds[i].className = on ? "on" : i < index ? "done" : "";
        if (on) {
          ds[i].setAttribute("aria-selected", "true");
          currentBtn = ds[i];
        } else ds[i].setAttribute("aria-selected", "false");
      }
      if (currentBtn) {
        var left = currentBtn.offsetLeft - dots.clientWidth / 2 + currentBtn.offsetWidth / 2;
        dots.scrollLeft = Math.max(0, left);
      }
    }
    function stop() {
      playing = false;
      if (timer) { clearTimeout(timer); timer = null; }
      playBtn.textContent = "Play";
      playBtn.setAttribute("aria-pressed", "false");
    }
    function tick() {
      if (!playing) return;
      if (index >= steps.length - 1) { stop(); return; }
      timer = setTimeout(function () {
        index += 1;
        draw();
        tick();
      }, Math.round(1500 / speed));
    }
    function play() {
      if (reducedMotion()) {
        stop();
        return;
      }
      if (index >= steps.length - 1) index = 0;
      playing = true;
      playBtn.textContent = "Pause";
      playBtn.setAttribute("aria-pressed", "true");
      draw();
      tick();
    }
    function stepBy(delta) {
      stop();
      index = Math.max(0, Math.min(steps.length - 1, index + delta));
      draw();
    }
    playBtn.addEventListener("click", function () { if (playing) stop(); else play(); });
    host.querySelector('[data-act=prev]').addEventListener("click", function () { stepBy(-1); });
    host.querySelector('[data-act=next]').addEventListener("click", function () { stepBy(1); });
    host.querySelector('[data-act=speed]').addEventListener("change", function (e) {
      var v = parseFloat(e.target.value);
      speed = v === 0.5 || v === 2 ? v : 1;
      if (playing) { if (timer) clearTimeout(timer); tick(); }
    });
    var scenarioSelect = host.querySelector('[data-act=scenario]');
    if (scenarioSelect) {
      scenarioSelect.addEventListener("change", function () {
        var next = choices[parseInt(scenarioSelect.value, 10)];
        if (!next) return;
        stop();
        flow = next;
        steps = flow.steps || [];
        index = 0;
        if (titleEl) titleEl.textContent = flow.title || "";
        if (citeEl) citeEl.textContent = flow.cite || "Campus diagram";
        if (whyEl) whyEl.innerHTML = "<b>Why it matters.</b> " + esc(flow.why || "");
        fillSteps();
        var hd = host.parentElement && host.parentElement.querySelector(".vs-header");
        if (flow.header) {
          if (!hd) {
            hd = document.createElement("div");
            hd.className = "vs-header";
            host.insertAdjacentElement("afterend", hd);
          }
          hd.hidden = false;
          hd.innerHTML = headerSvg(flow.headerLines ? flow : flow.header);
          var artHost = host.parentElement && host.parentElement.querySelector(".vs-art");
          if (artHost && window.UCArt) {
            var nextArt = window.UCArt.mount(flow);
            if (nextArt) artHost.replaceWith(nextArt);
          }
        } else if (hd) hd.hidden = true;
        draw();
      });
    }
    host.addEventListener("keydown", function (e) {
      var tag = (e.target && e.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "select" || tag === "textarea") return;
      if (e.key === "ArrowRight") { e.preventDefault(); stepBy(1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); stepBy(-1); }
      else if ((e.key === " " || e.key === "Spacebar") && (e.target === host || (e.target && e.target.getAttribute && e.target.getAttribute("data-act") === "play"))) {
        e.preventDefault();
        if (playing) stop(); else play();
      }
    });
    host._vsStop = stop;
    draw();
    if (!params.get("noplay") && !(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)) {
      setTimeout(play, 350);
    }
    return host;
  }

  function logFact(n) {
    var s = 0;
    for (var i = 2; i <= n; i++) s += Math.log(i);
    return s;
  }
  function erlangB(N, A) {
    if (N <= 0) return 1;
    var B = 1;
    for (var k = 1; k <= N; k++) B = (A * B) / (k + A * B);
    return B;
  }
  function erlangC(N, A) {
    if (A >= N) return 1;
    var B = erlangB(N, A);
    var denom = N - A * (1 - B);
    if (denom <= 0) return 1;
    return Math.max(0, Math.min(1, (N * B) / denom));
  }
  function mosFromR(R) {
    if (R < 0) return 1;
    if (R > 100) return 4.5;
    return 1 + 0.035 * R + R * (R - 60) * (100 - R) * 7e-6;
  }

  var CODECS = {
    "G.711": { bps: 64000, ie: 0, bpl: 25.1, note: "PCMU/PCMA, Ie 0, Bpl 25.1 with PLC (ITU-T G.113 / G.107 teaching pair)" },
    "G.729A": { bps: 8000, ie: 11, bpl: 19, note: "G.729A, Ie 11, Bpl 19 (ITU-T G.107 teaching pair)" },
    "G.722": { bps: 64000, ie: 0, bpl: 25.1, note: "64 kbit/s wideband payload. Impairment shown with the G.711 PLC pair because a separate G.722 Bpl is not assumed here." }
  };

  function bandwidthKbps(bps, ptimeMs, l2Bytes) {
    var payload = bps * ptimeMs / 8000;
    var header = 40 + l2Bytes;
    var rate = 1000 / ptimeMs;
    return (payload + header) * 8 * rate / 1000;
  }

  function chartHost(parent, title) {
    var box = document.createElement("div");
    box.className = "vs-chart";
    box.innerHTML = "<h3>" + esc(title) + "</h3>";
    parent.appendChild(box);
    return box;
  }

  function mountChart(parent, kind) {
    if (window.UCCharts && window.UCCharts.mount(parent, kind)) return;
    if (!kind || kind === "none") return;
    if (kind === "sip") {
      var box = chartHost(parent, "SIP timer budget on UDP (RFC 3261)");
      box.insertAdjacentHTML("beforeend",
        '<p class="vs-formula">T1 = 500 ms default · T2 = 4 s · Timer B = 64×T1 = 32 s · Timer F = 64×T1 = 32 s. TCP and TLS do not retransmit the INVITE the way UDP does.</p>' +
        '<svg viewBox="0 0 640 160" width="100%" height="160" role="img" aria-label="SIP timers">' +
        '<rect width="640" height="160" fill="transparent"/>' +
        bar(20, "T1 0.5s", 0.5, 32, TEAL) +
        bar(180, "T2 4s", 4, 32, INDIGO) +
        bar(340, "Timer B 32s", 32, 32, AMBER) +
        bar(500, "Timer F 32s", 32, 32, GREEN) +
        "</svg>" +
        '<p class="vs-note">Timer B is how long the UAC waits for a final response to INVITE. When it fires, the INVITE transaction has failed. That is a different fault from a 480 or a 486.</p>');
      return;
    }
    if (kind === "codec" || kind === "mos") {
      mountCodecAndMos(parent, kind);
      return;
    }
    if (kind === "qos") mountQos(parent);
    if (kind === "erlang" || kind === "kpi") mountErlang(parent, kind);
  }

  function bar(x, label, value, max, color) {
    var h = Math.max(8, (value / max) * 90);
    return '<rect x="' + x + '" y="' + (120 - h) + '" width="70" height="' + h + '" rx="8" fill="' + color + '"/>' +
      '<text x="' + (x + 35) + '" y="140" text-anchor="middle" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + label + "</text>";
  }

  function mountCodecAndMos(parent, kind) {
    var box = chartHost(parent, kind === "mos" ? "E-model MOS teaching calculator" : "Codec bandwidth on the wire");
    box.insertAdjacentHTML("beforeend",
      '<div class="vs-sliders">' +
      '<label>Codec <select data-c><option>G.711</option><option>G.729A</option><option>G.722</option></select></label>' +
      '<label>Packetization ms <select data-p><option>10</option><option selected>20</option><option>30</option></select></label>' +
      '<label>Layer-2 header bytes <select data-l><option value="0">IP/UDP/RTP only (40)</option><option value="18" selected>Ethernet 18</option></select></label>' +
      '<label>One-way delay ms <input data-d type="range" min="20" max="300" value="80"/></label>' +
      '<label>Random loss % <input data-loss type="range" min="0" max="10" step="0.1" value="0"/></label>' +
      "</div>" +
      '<p class="vs-formula" data-f></p><svg data-svg viewBox="0 0 640 150" width="100%" height="140"></svg><div class="vs-out" data-o></div>' +
      '<p class="vs-note">Bandwidth = (payload bytes + 40 + L2) × 8 × (1000 / ptime) / 1000. Payload bytes = codec bit rate × ptime / 8000. G.711 at 20 ms with a 40-byte IP/UDP/RTP header is 80 kbit/s. Add 18 bytes of Ethernet and it is 87.2 kbit/s. MOS uses a short form of ITU-T G.107: Ie-eff = Ie + (95 − Ie) × Ppl / (Ppl + Bpl), Id = 0.024d + 0.11×(d − 177.3) when d &gt; 177.3, R = 93.2 − Id − Ie-eff, then the G.107 MOS map. This is a teaching model, not a POLQA score.</p>');
    function render() {
      var codec = CODECS[box.querySelector("[data-c]").value];
      var ptime = parseFloat(box.querySelector("[data-p]").value);
      var l2 = parseFloat(box.querySelector("[data-l]").value);
      var delay = parseFloat(box.querySelector("[data-d]").value);
      var loss = parseFloat(box.querySelector("[data-loss]").value);
      var bw = bandwidthKbps(codec.bps, ptime, l2);
      var ppl = loss;
      var ieEff = codec.ie + (95 - codec.ie) * ppl / (ppl + codec.bpl);
      var id = 0.024 * delay;
      if (delay > 177.3) id += 0.11 * (delay - 177.3);
      var R = 93.2 - id - ieEff;
      var mos = mosFromR(R);
      box.querySelector("[data-f]").textContent =
        "BW " + bw.toFixed(1) + " kbit/s · Ie-eff " + ieEff.toFixed(2) + " · Id " + id.toFixed(2) + " · R " + R.toFixed(1) + " · MOS " + mos.toFixed(2);
      var bars = "";
      var names = Object.keys(CODECS);
      names.forEach(function (name, i) {
        var kb = bandwidthKbps(CODECS[name].bps, ptime, l2);
        bars += bar(30 + i * 140, name + " " + kb.toFixed(0), kb, 120, i === 1 ? INDIGO : TEAL);
      });
      var mosH = Math.max(6, (mos / 4.5) * 90);
      bars += '<rect x="470" y="' + (120 - mosH) + '" width="70" height="' + mosH + '" rx="8" fill="' + GREEN + '"/>' +
        '<text x="505" y="140" text-anchor="middle" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">MOS ' + mos.toFixed(2) + "</text>";
      box.querySelector("[data-svg]").innerHTML = bars;
      box.querySelector("[data-o]").innerHTML =
        "<b>" + bw.toFixed(1) + " kbit/s</b><b>MOS " + mos.toFixed(2) + "</b><b>R " + R.toFixed(1) + "</b>";
    }
    box.querySelectorAll("input,select").forEach(function (el) { el.addEventListener("input", render); });
    render();
  }

  function mountQos(parent) {
    var box = chartHost(parent, "One-way delay budget against ITU-T G.114");
    box.insertAdjacentHTML("beforeend",
      '<div class="vs-sliders">' +
      '<label>Packetization ms <input data-k="pkt" type="range" min="10" max="40" value="20"/></label>' +
      '<label>Queuing ms <input data-k="q" type="range" min="0" max="40" value="10"/></label>' +
      '<label>Serialization ms <input data-k="ser" type="range" min="0" max="20" value="3"/></label>' +
      '<label>Propagation ms <input data-k="prop" type="range" min="0" max="80" value="20"/></label>' +
      '<label>Jitter buffer ms <input data-k="jb" type="range" min="0" max="80" value="40"/></label>' +
      '</div><svg data-svg viewBox="0 0 640 120" width="100%" height="120"></svg><div class="vs-out" data-o></div>' +
      '<p class="vs-note">G.114 treats about 150 ms one-way as the planning limit for conversational voice. The sum here is packetization + queuing + serialization + propagation + jitter buffer. It leaves out codec look-ahead on purpose when the codec has none (G.711). Bearer marking on a Cisco collaboration path is EF, DSCP 46. Signaling is commonly CS3, DSCP 24. Loss under 1% and jitter under about 30 ms are the usual design targets, measured, not hoped for.</p>');
    function render() {
      var keys = ["pkt", "q", "ser", "prop", "jb"];
      var labels = ["Packet", "Queue", "Serial", "Prop", "Jitter buf"];
      var colors = [TEAL, INDIGO, AMBER, "#7C3AED", GREEN];
      var vals = keys.map(function (k) { return parseFloat(box.querySelector('[data-k="' + k + '"]').value); });
      var sum = vals.reduce(function (a, b) { return a + b; }, 0);
      var x = 20;
      var svg = "";
      vals.forEach(function (v, i) {
        var w = Math.max(8, (v / 180) * 560);
        svg += '<rect x="' + x + '" y="30" width="' + w + '" height="36" fill="' + colors[i] + '"/>';
        svg += '<text x="' + (x + 4) + '" y="86" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + labels[i] + " " + v + "</text>";
        x += w;
      });
      var limit = 20 + (150 / 180) * 560;
      svg += '<path d="M' + limit + ' 18 V78" stroke="' + ROSE + '" stroke-width="2" stroke-dasharray="3 3"/>';
      svg += '<text x="' + limit + '" y="14" fill="' + ROSE + '" font-size="10" font-family="ui-sans-serif,system-ui">150 ms</text>';
      box.querySelector("[data-svg]").innerHTML = svg;
      box.querySelector("[data-o]").innerHTML = "<b>Total " + sum + " ms</b><b>" + (sum <= 150 ? "Inside 150 ms" : "Over the G.114 planning limit") + "</b>";
    }
    box.querySelectorAll("input").forEach(function (el) { el.addEventListener("input", render); });
    render();
  }

  function mountErlang(parent, kind) {
    var box = chartHost(parent, kind === "kpi" ? "Contact-center sizing and KPIs" : "Erlang B trunks and Erlang C agents");
    box.insertAdjacentHTML("beforeend",
      '<div class="vs-sliders">' +
      '<label>Calls per hour <input data-k="cph" type="number" min="1" value="200"/></label>' +
      '<label>AHT seconds <input data-k="aht" type="number" min="1" value="180"/></label>' +
      '<label>Agents <input data-k="n" type="number" min="1" value="14"/></label>' +
      '<label>Service seconds <input data-k="t" type="number" min="1" value="20"/></label>' +
      '<label>Trunk blocking target <input data-k="block" type="number" min="0.001" max="0.2" step="0.001" value="0.01"/></label>' +
      '</div><p class="vs-formula" data-f></p><div class="vs-out" data-o></div>' +
      '<p class="vs-note">Erlangs A = calls per hour × AHT / 3600. Erlang B (iterative): B = 1, then B = A×B / (k + A×B) for k = 1…N. Erlang C wait probability C = N×B / (N − A×(1 − B)), valid when A &lt; N. ASA = C × AHT / (N − A). Service level = 1 − C × exp(−(N − A) × target / AHT). Occupancy = A / N. These are the standard traffic formulas, not a vendor forecast.</p>');
    function render() {
      var cph = parseFloat(box.querySelector('[data-k=cph]').value) || 0;
      var aht = parseFloat(box.querySelector('[data-k=aht]').value) || 1;
      var N = Math.max(1, parseInt(box.querySelector('[data-k=n]').value, 10) || 1);
      var t = parseFloat(box.querySelector('[data-k=t]').value) || 20;
      var block = parseFloat(box.querySelector('[data-k=block]').value) || 0.01;
      var A = cph * aht / 3600;
      var trunks = 1;
      while (trunks < 400 && erlangB(trunks, A) > block) trunks += 1;
      var C = erlangC(N, A);
      var asa = A >= N ? Infinity : C * aht / (N - A);
      var sl = A >= N ? 0 : 1 - C * Math.exp(-(N - A) * t / aht);
      var occ = A / N;
      box.querySelector("[data-f]").textContent =
        "A = " + A.toFixed(2) + " erlang · B(" + trunks + ") = " + (erlangB(trunks, A) * 100).toFixed(2) +
        "% · C = " + (C * 100).toFixed(1) + "%";
      var asaTxt = asa === Infinity ? "unstable" : asa.toFixed(1) + " s";
      box.querySelector("[data-o]").innerHTML =
        "<b>" + A.toFixed(2) + " erlang</b><b>Trunks " + trunks + "</b><b>SL " + (sl * 100).toFixed(1) + "%</b><b>ASA " + asaTxt + "</b><b>Occupancy " + (occ * 100).toFixed(0) + "%</b>";
    }
    box.querySelectorAll("input").forEach(function (el) { el.addEventListener("input", render); });
    render();
    void logFact;
  }

  var audioCtx = null;
  function ctx() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }
  function envGain(c, start, dur, peak) {
    var g = c.createGain();
    g.gain.setValueAtTime(0.0001, start);
    g.gain.exponentialRampToValueAtTime(peak, start + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    return g;
  }
  function mix(c, freqs, start, dur, peak) {
    var g = envGain(c, start, dur, peak);
    g.connect(c.destination);
    freqs.forEach(function (f) {
      var o = c.createOscillator();
      o.type = "sine";
      o.frequency.value = f;
      o.connect(g);
      o.start(start);
      o.stop(start + dur + 0.02);
    });
  }
  function playCadence(pattern, peak) {
    var c = ctx();
    var t = c.currentTime + 0.05;
    pattern.forEach(function (seg) {
      if (seg.hz) mix(c, seg.hz, t, seg.ms / 1000, peak || 0.08);
      t += seg.ms / 1000;
    });
  }
  function dtmfPair(digit) {
    var low = { "1": 697, "2": 697, "3": 697, "4": 770, "5": 770, "6": 770, "7": 852, "8": 852, "9": 852, "*": 941, "0": 941, "#": 941 };
    var high = { "1": 1209, "2": 1336, "3": 1477, "4": 1209, "5": 1336, "6": 1477, "7": 1209, "8": 1336, "9": 1477, "*": 1209, "0": 1336, "#": 1477 };
    return [low[digit], high[digit]];
  }
  function formantBurst(c, start, dur, mulawMode) {
    var sr = c.sampleRate;
    var n = Math.floor(sr * dur);
    var buf = c.createBuffer(1, n, sr);
    var data = buf.getChannelData(0);
    var f1 = 700, f2 = 1200, f3 = 2600;
    for (var i = 0; i < n; i++) {
      var t = i / sr;
      var s = 0.5 * Math.sin(2 * Math.PI * f1 * t) + 0.25 * Math.sin(2 * Math.PI * f2 * t) + 0.12 * Math.sin(2 * Math.PI * f3 * t);
      s *= 0.4 * (0.6 + 0.4 * Math.sin(2 * Math.PI * 110 * t));
      if (mulawMode === "mu") {
        var MU = 255, sign = s < 0 ? -1 : 1, ax = Math.min(1, Math.abs(s));
        var comp = sign * Math.log(1 + MU * ax) / Math.log(1 + MU);
        var q = Math.round(comp * 127) / 127;
        s = sign * (Math.pow(1 + MU, Math.abs(q)) - 1) / MU;
        if (s < 0) s = -s * (q < 0 ? 1 : 1);
        s = (q < 0 ? -1 : 1) * (Math.pow(1 + MU, Math.abs(q)) - 1) / MU;
      } else if (mulawMode === "narrow") {
        if (i % 6 !== 0) s = data[i - 1] || s;
        s = s * 0.85 + (Math.random() - 0.5) * 0.02;
      }
      data[i] = Math.max(-1, Math.min(1, s));
    }
    var src = c.createBufferSource();
    src.buffer = buf;
    src.connect(c.destination);
    src.start(start);
  }
  function playBufferMode(mode) {
    var c = ctx();
    formantBurst(c, c.currentTime + 0.05, 1.4, mode);
  }
  function playJitter() {
    var c = ctx();
    var t = c.currentTime + 0.05;
    for (var i = 0; i < 8; i++) {
      mix(c, [440], t, 0.08, 0.07);
      t += 0.08 + (i % 3) * 0.07;
    }
  }
  function playLoss() {
    var c = ctx();
    var t = c.currentTime + 0.05;
    for (var i = 0; i < 12; i++) {
      if (i % 5 !== 2) mix(c, [523], t, 0.09, 0.07);
      t += 0.1;
    }
  }
  function playOneWay() {
    var c = ctx();
    var start = c.currentTime + 0.05;
    var o = c.createOscillator();
    var g = c.createGain();
    var p = c.createStereoPanner ? c.createStereoPanner() : null;
    o.frequency.value = 440;
    g.gain.value = 0.06;
    o.connect(g);
    if (p) { g.connect(p); p.pan.value = -1; p.connect(c.destination); }
    else g.connect(c.destination);
    o.start(start); o.stop(start + 1.2);
  }

  var CLIPS = [
    { name: "DTMF 5", text: "ITU-T Q.23 digit 5: 770 Hz and 1336 Hz.", run: function () { playCadence([{ hz: dtmfPair("5"), ms: 220 }], 0.07); } },
    { name: "DTMF run", text: "Digits 1, 5, 9, 0, star, pound. Each pair is the Q.23 low and high tone.", run: function () { var p = []; "1590*#".split("").forEach(function (d) { p.push({ hz: dtmfPair(d), ms: 160 }); p.push({ ms: 80 }); }); playCadence(p, 0.06); } },
    { name: "Dial tone", text: "North American dial tone: 350 Hz + 440 Hz.", run: function () { playCadence([{ hz: [350, 440], ms: 1600 }], 0.05); } },
    { name: "US ringback", text: "440 Hz + 480 Hz, 2 seconds on. The real cadence is 2 s on and 4 s off. This clip plays one on-period.", run: function () { playCadence([{ hz: [440, 480], ms: 2000 }], 0.05); } },
    { name: "Busy", text: "480 Hz + 620 Hz, 0.5 s on, 0.5 s off.", run: function () { playCadence([{ hz: [480, 620], ms: 500 }, { ms: 500 }, { hz: [480, 620], ms: 500 }, { ms: 500 }], 0.05); } },
    { name: "Reorder", text: "480 Hz + 620 Hz, 0.25 s on, 0.25 s off. Faster than busy.", run: function () { var p = []; for (var i = 0; i < 4; i++) { p.push({ hz: [480, 620], ms: 250 }); p.push({ ms: 250 }); } playCadence(p, 0.05); } },
    { name: "SIT", text: "North American special information tone: about 914 Hz, 1371 Hz, then 1777 Hz.", run: function () { playCadence([{ hz: [913.8], ms: 330 }, { hz: [1370.6], ms: 330 }, { hz: [1776.7], ms: 330 }], 0.06); } },
    { name: "Wideband vowel", text: "Synthetic vowel, three formants. The reference before quantization.", run: function () { playBufferMode("clean"); } },
    { name: "G.711 mu-law", text: "The same vowel through a mu-law compand and 8-bit quantizer. A teaching model of PCM, not a bit-exact codec.", run: function () { playBufferMode("mu"); } },
    { name: "Narrowband simulation", text: "Sample-and-hold plus a little noise. Not a G.729 decoder. It shows why a narrowband path sounds thinner.", run: function () { playBufferMode("narrow"); } },
    { name: "Jitter gaps", text: "A steady tone with uneven gaps, the way a starved jitter buffer sounds.", run: playJitter },
    { name: "Packet loss", text: "Short tones with some bursts removed, about one drop in five.", run: playLoss },
    { name: "One-way audio", text: "Tone panned left. Use headphones. The other side of a one-way call is this silence.", run: playOneWay },
    { name: "Fax CNG", text: "Calling tone, 1100 Hz. T.30 callers send this.", run: function () { playCadence([{ hz: [1100], ms: 500 }, { ms: 400 }, { hz: [1100], ms: 500 }], 0.06); } },
    { name: "Fax CED", text: "Called tone, 2100 Hz. The answer side of a fax handshake.", run: function () { playCadence([{ hz: [2100], ms: 900 }], 0.05); } },
    { name: "Comfort noise", text: "Low noise where silence suppression would insert comfort noise. Not a real CN payload.", run: function () { var c = ctx(); var n = Math.floor(c.sampleRate * 1.2); var b = c.createBuffer(1, n, c.sampleRate); var d = b.getChannelData(0); for (var i = 0; i < n; i++) d[i] = (Math.random() - 0.5) * 0.02; var s = c.createBufferSource(); s.buffer = b; s.connect(c.destination); s.start(); } }
  ];

  function audioBench() {
    if (window.UCAudio && window.UCAudio.bench) return window.UCAudio.bench();
    var det = document.createElement("details");
    det.className = "vs-audio";
    det.innerHTML = "<summary>Tone and media bench · " + CLIPS.length + " labeled clips, generated in this browser</summary><div class=\"vs-clips\"></div>";
    var grid = det.querySelector(".vs-clips");
    CLIPS.forEach(function (clip) {
      var card = document.createElement("div");
      card.className = "vs-clip";
      card.innerHTML = "<b>" + esc(clip.name) + "</b><p>" + esc(clip.text) + "</p>";
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "Play";
      btn.addEventListener("click", function () { try { clip.run(); } catch (e) { btn.textContent = "Unavailable"; } });
      card.appendChild(btn);
      grid.appendChild(card);
    });
    return det;
  }

  var TRACKS = [
    { group: "Start here", short: "Start", id: "home", blurb: "LICC before any product screen.", flow: "licc-path", icon: "proof", color: "#0F9B8E" },
    { group: "SIP and media", short: "SIP", id: "proto-sip-master", blurb: "Dialog, offer/answer, and RTP.", flow: "sip-basic", icon: "sip", color: "#6366F1" },
    { group: "CUCM and CUBE", short: "CUCM", id: "prod-cube", blurb: "Digit analysis, then a B2BUA.", flow: "cube-b2bua", icon: "cube", color: "#22C55E" },
    { group: "Webex Calling and Teams Phone", short: "Cloud calling", id: "vd-webex-calling-call-flow", blurb: "Local Gateway and Direct Routing.", flow: "wx-lgw-out", icon: "cloud", color: "#0891B2" },
    { group: "Contact center — UCCE and PCCE", short: "UCCE", id: "hub-icm-ucce", blurb: "CVP, ICM, VVB, Finesse.", flow: "ucce-comp", icon: "queue", color: "#7C3AED" },
    { group: "CCaaS and UCaaS platforms", short: "CCaaS", id: "prod-wxcc", blurb: "Entry, flow, queue, agent id.", flow: "wxcc-in", icon: "cloud", color: "#4F46E5" },
    { group: "Emergency calling", short: "E911", id: "found-11", blurb: "Location, ELIN, on-site notice.", flow: "e911-cer", icon: "emergency", color: "#E11D48" },
    { group: "Voice network and QoS", short: "QoS", id: "hub-qos", blurb: "EF for bearer, measure the budget.", flow: "qos-path", icon: "qos", color: "#0F766E" },
    { group: "Migrations", short: "Migrations", id: "hub-migrations", blurb: "Dual-run, then a rehearsed rollback.", flow: "mig-dual-run", icon: "migration", color: "#E08A00" },
    { group: "Troubleshooting", short: "Faults", id: "trick-0", blurb: "One hypothesis, one capture.", flow: "ts-one-way", icon: "tree", color: "#B45309" },
    { group: "Evidence habits", short: "Evidence", id: "mm-licc", blurb: "The pack you can hand to someone else.", flow: "evidence-pack", icon: "proof", color: "#047857" },
    { group: "Design notes", short: "Design", id: "arch-capacity", blurb: "Failure domain, capacity, identity.", flow: "design-read", icon: "route", color: "#1D4ED8" },
    { group: "Practice", short: "Practice", id: "drill-sip-dialplan-licc", blurb: "Drill the fault before the bridge.", flow: "practice-loop", icon: "proof", color: "#BE185D" },
    { group: "Reference", short: "Reference", id: "glossary", blurb: "Names, then the current vendor document.", flow: "reference-loop", icon: "cert", color: "#64748B" }
  ];

  function sectionsIn(group) {
    var out = [];
    (window.SECTIONS || []).forEach(function (s) { if (s.group === group) out.push(s); });
    return out;
  }

  function placeLine(section) {
    var all = sectionsIn(section.group);
    var at = 1;
    for (var i = 0; i < all.length; i++) if (all[i].id === section.id) at = i + 1;
    return "Section " + at + " of " + all.length;
  }

  function flowPreview(flowId) {
    var cat = byIdMap(window.UC_FLOW_CATALOG || []);
    var flow = cat[flowId];
    var steps = (flow && flow.steps) || [];
    return steps.slice(0, 3).map(function (s) { return s.label; });
  }

  function hubCardSvg(track) {
    var labels = flowPreview(track.flow);
    var parts = ['<svg viewBox="0 0 280 88" aria-hidden="true">'];
    parts.push('<rect width="280" height="88" rx="12" fill="#0B1220"/>');
    parts.push('<rect x="0" y="0" width="8" height="88" fill="' + track.color + '"/>');
    for (var i = 0; i < 3; i++) {
      var x = 22 + i * 86;
      parts.push('<rect x="' + x + '" y="18" width="72" height="28" rx="8" fill="#121A2F" stroke="' + (i === 0 ? track.color : "#6366F1") + '"/>');
      parts.push('<text x="' + (x + 36) + '" y="36" text-anchor="middle" fill="#F8FAFC" font-size="8" font-weight="700" font-family="ui-sans-serif,system-ui">' + esc(clipLabel(labels[i] || "·", 12)) + "</text>");
      if (i < 2) parts.push('<path class="vs-march" d="M' + (x + 74) + ' 32 H' + (x + 84) + '" stroke="#F5B942" stroke-width="2"/>');
    }
    parts.push('<text x="22" y="70" fill="#5EEAD4" font-size="10" font-weight="700" font-family="ui-sans-serif,system-ui">Open the step-through</text>');
    parts.push("</svg>");
    return parts.join("");
  }

  function trackHub(section) {
    var wrap = document.createElement("div");
    wrap.className = "vs-hub";
    var here = null;
    TRACKS.forEach(function (t) { if (t.group === section.group) here = t; });
    if (section.id === "home") {
      wrap.innerHTML = "<h3>Track atlas</h3><p class=\"vs-note\">Fourteen tracks. Each card opens that track’s flagship flow.</p><div class=\"vs-hub-grid\"></div>";
      var grid = wrap.querySelector(".vs-hub-grid");
      TRACKS.forEach(function (t) {
        var count = sectionsIn(t.group).length;
        var b = document.createElement("button");
        b.type = "button";
        b.className = "vs-hub-card";
        b.style.setProperty("--track", t.color);
        b.innerHTML = hubCardSvg(t) + "<strong>" + esc(t.group) + "</strong><span>" + count + " sections · " + esc(t.blurb) + "</span>";
        b.addEventListener("click", function () { if (window.openSection) window.openSection(t.id); });
        grid.appendChild(b);
      });
      return wrap;
    }
    var all = sectionsIn(section.group);
    var at = 0;
    for (var i = 0; i < all.length; i++) if (all[i].id === section.id) at = i;
    var slice;
    if (all.length <= 12) {
      slice = all;
    } else {
      var width = 8;
      var start = Math.max(0, Math.min(at - 3, all.length - width));
      slice = all.slice(start, start + width);
      if (slice[0].id !== all[0].id) slice = [all[0]].concat(slice);
      if (slice[slice.length - 1].id !== all[all.length - 1].id) slice = slice.concat(all[all.length - 1]);
    }
    var color = here ? here.color : TEAL;
    wrap.innerHTML =
      '<h3>This track</h3>' +
      '<div class="vs-track-banner" style="--track:' + color + '"><div><strong>' + esc(section.group || "") + '</strong><span>' + esc(here ? here.blurb : "") + " · " + all.length + ' sections</span></div></div>' +
      '<div class="vs-film" aria-label="Sections in this track"></div>' +
      '<h3 class="vs-atlas-title">All tracks</h3><div class="vs-atlas" aria-label="All tracks"></div>';
    var film = wrap.querySelector(".vs-film");
    slice.forEach(function (s) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "vs-chip" + (s.id === section.id ? " here" : "");
      b.innerHTML = "<i>" + esc(s.num || "") + "</i><b>" + esc(clipLabel(s.title, 42)) + "</b>";
      b.addEventListener("click", function () { if (window.openSection) window.openSection(s.id); });
      film.appendChild(b);
    });
    var atlas = wrap.querySelector(".vs-atlas");
    TRACKS.forEach(function (t) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = t.group === section.group ? "on" : "";
      b.style.setProperty("--track", t.color);
      b.textContent = t.short;
      b.title = t.group;
      b.addEventListener("click", function () { if (window.openSection) window.openSection(t.id); });
      atlas.appendChild(b);
    });
    return wrap;
  }

  function keysHtml(flow) {
    var keys = (flow && flow.keys) || [];
    return keys.map(function (k) {
      return '<div class="vs-key"><b>' + esc(k[0]) + "</b><span>" + esc(k[1]) + "</span></div>";
    }).join("");
  }

  function stopCurrent() {
    var old = document.querySelector(".vs-player");
    if (old && old._vsStop) old._vsStop();
  }

  function wantsAudio(section, flow) {
    var blob = (section.group + " " + section.title + " " + (section.id || "")).toLowerCase();
    if (flow && flow.audio) return true;
    return /sip|media|codec|qos|rtp|tone|fax|jitter|mos|voice quality/.test(blob);
  }

  function paint(section) {
    if (!section) return;
    stopCurrent();
    var main = document.getElementById("main");
    var body = main && main.querySelector(".sec-body");
    if (!body) return;
    var old = body.querySelector(".vs-studio");
    if (old) old.remove();
    var basic = body.querySelector("#ucSecVisual");
    if (basic) basic.remove();
    var flow = sectionFlow(section);
    if (!flow) return;
    var icon = iconSvg(flow.icon || "proof");
    var root = document.createElement("section");
    root.className = "vs-studio";
    root.setAttribute("aria-label", "Visual studio");
    root.innerHTML =
      '<div class="vs-kicker"><span class="vs-num">' + esc(section.num || "—") + '</span><span class="vs-track-pill">' + esc(section.group || "") + '</span><span class="vs-place">' + esc(placeLine(section)) + "</span></div>" +
      '<div class="vs-head"><div class="vs-icon-wrap">' + icon + "</div><div><h2>" + esc(section.title) + "</h2>" +
      '<p class="vs-why">' + esc(section.sub || flow.why || "") + "</p></div></div>" +
      heroSvg(section, flow) +
      '<div class="vs-keys">' + keysHtml(flow) + "</div>";
    if (window.UCProgress) {
      try { window.UCProgress.seen(section); } catch (e) {}
      root.appendChild(window.UCProgress.map(section));
    }
    var player = document.createElement("div");
    player.className = "vs-player";
    root.appendChild(player);
    mountPlayer(player, flow, section);
    if (window.UCArt) {
      var art = window.UCArt.mount(flow);
      if (art) root.appendChild(art);
    }
    if (flow.header || flow.headerLines) {
      var hd = document.createElement("div");
      hd.className = "vs-header";
      hd.innerHTML = headerSvg(flow.headerLines ? flow : flow.header);
      root.appendChild(hd);
    }
    mountChart(root, flow.chart);
    if (wantsAudio(section, flow) || section.id === "home") root.appendChild(audioBench());
    var hub = trackHub(section);
    if (hub) root.appendChild(hub);
    if (section.id === "home" && window.UC_VISUAL_COUNTS) {
      var c = window.UC_VISUAL_COUNTS;
      var row = document.createElement("div");
      row.className = "vs-counts";
      row.innerHTML =
        "<span>" + c.sections + " sections</span>" +
        "<span>" + c.flowDefinitions + " distinct flows</span>" +
        "<span>" + c.walkthroughs + " walkthroughs</span>" +
        "<span>" + c.chartTypes + " chart types</span>" +
        "<span>" + c.illustrations + " distinct illustrations</span>" +
        "<span>" + c.audioClips + " audio clips</span>" +
        "<span>" + c.trackHubs + " track hubs</span>";
      root.appendChild(row);
    }
    body.insertBefore(root, body.firstChild);
    markJump(section.group);
  }

  function ensureJump() {
    var side = document.getElementById("side");
    if (!side || side.querySelector(".vs-jump")) return;
    var bar = document.createElement("nav");
    bar.className = "vs-jump";
    bar.setAttribute("aria-label", "Track jump");
    TRACKS.forEach(function (t) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("data-group", t.group);
      b.title = t.group;
      b.innerHTML = '<i style="background:' + t.color + '"></i>' + esc(t.short);
      b.addEventListener("click", function () { if (window.openSection) window.openSection(t.id); });
      bar.appendChild(b);
    });
    side.insertBefore(bar, side.firstChild);
  }

  function markJump(group) {
    ensureJump();
    var bar = document.querySelector(".vs-jump");
    if (!bar) return;
    var buttons = bar.querySelectorAll("button");
    for (var i = 0; i < buttons.length; i++) {
      var on = buttons[i].getAttribute("data-group") === group;
      buttons[i].classList.toggle("on", on);
      if (on) buttons[i].setAttribute("aria-current", "true");
      else buttons[i].removeAttribute("aria-current");
    }
  }

  function counts() {
    var sections = window.SECTIONS || [];
    var flows = window.UC_FLOW_CATALOG || [];
    var seenArt = {};
    var walks = 0;
    flows.forEach(function (f) {
      if (f.walkthrough || f.layout === "walk") walks += 1;
      var art = f.art || {};
      ["topology", "mockup", "capture"].forEach(function (key) {
        if (!art[key]) return;
        seenArt[key + ":" + JSON.stringify(art[key])] = 1;
      });
    });
    return {
      sections: sections.length,
      flowDefinitions: flows.length,
      animatedSections: sections.length,
      walkthroughs: walks,
      illustrations: Object.keys(seenArt).length,
      chartTypes: (window.UCCharts && window.UCCharts.types && window.UCCharts.types.length) || (window.UC_CHART_TYPES || []).length,
      audioClips: (window.UCAudio && window.UCAudio.clips && window.UCAudio.clips.length) || CLIPS.length,
      trackHubs: TRACKS.length
    };
  }

  function boot() {
    window.getSectionArt = function () { return ""; };
    window.getSectionVisualSVG = window.getSectionArt;
    window.UC_VISUAL_COUNTS = counts();
    window.UCVisual = {
      paint: paint,
      counts: function () { window.UC_VISUAL_COUNTS = counts(); return window.UC_VISUAL_COUNTS; },
      erlangB: erlangB,
      erlangC: erlangC,
      bandwidthKbps: bandwidthKbps,
      mosFromR: mosFromR
    };
    if (window.ucAfterOpen && !window.__vsWrapped) {
      window.__vsWrapped = true;
      var orig = window.ucAfterOpen;
      window.ucAfterOpen = function (s) {
        try { orig(s); } catch (e) {}
        try { paint(s); } catch (err) { if (window.console) console.error(err); }
      };
    }
    var side = document.getElementById("side");
    if (side && window.MutationObserver) {
      new MutationObserver(function () { ensureJump(); }).observe(side, { childList: true });
    }
    ensureJump();
    setTimeout(function () {
      var id = window.getCurrentSectionId && window.getCurrentSectionId();
      var list = window.SECTIONS || [];
      for (var i = 0; i < list.length; i++) if (list[i].id === id) { paint(list[i]); break; }
    }, 60);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
