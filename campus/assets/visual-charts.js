/* Distinct chart types for the campus visual studio. Offline. */
(function () {
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function mosFromR(R) {
    if (R < 0) return 1;
    if (R > 100) return 4.5;
    return 1 + 0.035 * R + R * (R - 60) * (100 - R) * 7e-6;
  }
  function rScore(delay, ie, bpl, loss) {
    var ieEff = ie + (95 - ie) * loss / (loss + bpl);
    var id = 0.024 * delay;
    if (delay > 177.3) id += 0.11 * (delay - 177.3);
    return 93.2 - id - ieEff;
  }
  function erlangB(N, A) {
    if (N <= 0) return 1;
    var B = 1;
    for (var k = 1; k <= N; k++) B = (A * B) / (k + A * B);
    return B;
  }
  function erlangC(N, A) {
    if (!(A < N)) return 1;
    var B = erlangB(N, A);
    var denom = N - A * (1 - B);
    if (denom <= 0) return 1;
    return Math.max(0, Math.min(1, (N * B) / denom));
  }
  function bw(bps, ptime, l2) {
    var payload = bps * ptime / 8000;
    return (payload + 40 + l2) * 8 * (1000 / ptime) / 1000;
  }
  var CODECS = {
    "G.711": { bps: 64000, ie: 0, bpl: 25.1 },
    "G.729A": { bps: 8000, ie: 11, bpl: 19 },
    "G.722": { bps: 64000, ie: 0, bpl: 25.1 }
  };

  function box(parent, title, formula, note) {
    var el = document.createElement("div");
    el.className = "vs-chart";
    el.innerHTML = "<h3>" + esc(title) + "</h3><p class=\"vs-formula\">" + esc(formula) + "</p><div class=\"vs-sliders\" data-c></div><svg data-svg viewBox=\"0 0 640 180\" width=\"100%\" height=\"170\" role=\"img\"></svg><div class=\"vs-out\" data-o></div><p class=\"vs-note\">" + esc(note) + "</p>";
    parent.appendChild(el);
    return el;
  }
  function controls(el, specs, onChange) {
    var host = el.querySelector("[data-c]");
    specs.forEach(function (spec) {
      var label = document.createElement("label");
      label.textContent = spec.label + " ";
      var input = document.createElement(spec.options ? "select" : "input");
      if (spec.options) {
        spec.options.forEach(function (opt) {
          var o = document.createElement("option");
          o.value = opt;
          o.textContent = opt;
          if (String(opt) === String(spec.value)) o.selected = true;
          input.appendChild(o);
        });
      } else {
        input.type = "range";
        input.min = spec.min;
        input.max = spec.max;
        input.step = spec.step || 1;
        input.value = spec.value;
      }
      input.dataset.k = spec.key;
      input.addEventListener("input", onChange);
      label.appendChild(input);
      host.appendChild(label);
    });
  }
  function val(el, key) {
    var node = el.querySelector('[data-k="' + key + '"]');
    return node ? (node.tagName === "SELECT" ? node.value : parseFloat(node.value)) : 0;
  }
  function svgText(parts) {
    return parts.join("");
  }
  function axis(yLabel) {
    return '<path d="M40 20 V150 H620" fill="none" stroke="currentColor" stroke-opacity=".35"/>' +
      '<text x="8" y="16" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + esc(yLabel) + "</text>";
  }
  function polyline(pts, color) {
    if (!pts.length) return "";
    var d = pts.map(function (p, i) { return (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" ");
    return '<path d="' + d + '" fill="none" stroke="' + color + '" stroke-width="2.4"/>';
  }
  function legend(items) {
    return items.map(function (item, i) {
      return '<rect x="' + (48 + i * 140) + '" y="156" width="10" height="10" fill="' + item[1] + '"/><text x="' + (62 + i * 140) + '" y="166" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + esc(item[0]) + "</text>";
    }).join("");
  }

  var TEAL = "#0F9B8E", INDIGO = "#6366F1", AMBER = "#E08A00", GREEN = "#22C55E", ROSE = "#E11D48";
  var types = [];
  function add(id, title, formula, note, specs, draw) {
    types.push({ id: id, title: title, formula: formula, note: note, specs: specs, draw: draw });
  }

  add("mos-loss", "MOS versus packet loss",
    "Ie-eff = Ie + (95-Ie) x Ppl / (Ppl+Bpl). R = 93.2 - Ie-eff at 80 ms delay. Teaching G.107, not POLQA.",
    "G.722 uses the G.711 PLC impairment pair here. The curve falls as random loss rises.",
    [{ key: "d", label: "Delay ms", min: 20, max: 300, value: 80 }],
    function (el) {
      var d = val(el, "d");
      var series = [["G.711", TEAL, 0, 25.1], ["G.729A", INDIGO, 11, 19]];
      var lines = series.map(function (s) {
        var pts = [];
        for (var p = 0; p <= 10; p += 0.5) {
          var x = 40 + (p / 10) * 560;
          var y = 150 - (mosFromR(rScore(d, s[2], s[3], p)) / 4.5) * 120;
          pts.push([x, y]);
        }
        return polyline(pts, s[1]);
      });
      var m711 = mosFromR(rScore(d, 0, 25.1, 1));
      el.querySelector("[data-svg]").innerHTML = svgText([axis("MOS"), lines.join(""), legend([["G.711", TEAL], ["G.729A", INDIGO]]), '<text x="560" y="148" fill="currentColor" font-size="10">10% loss</text>']);
      el.querySelector("[data-o]").innerHTML = "<b>G.711 at 1% " + m711.toFixed(2) + "</b><b>Delay " + d + " ms</b>";
    });

  add("mos-delay", "MOS versus one-way delay",
    "Id = 0.024d, plus 0.11 x (d-177.3) when d is above 177.3. Loss held at the slider.",
    "The knee past 177.3 ms is the G.107 delay impairment, a planning model.",
    [{ key: "loss", label: "Loss %", min: 0, max: 5, step: 0.1, value: 0 }],
    function (el) {
      var loss = val(el, "loss");
      var pts = [];
      for (var d = 20; d <= 300; d += 10) {
        pts.push([40 + ((d - 20) / 280) * 560, 150 - (mosFromR(rScore(d, 0, 25.1, loss)) / 4.5) * 120]);
      }
      var limit = 40 + ((150 - 20) / 280) * 560;
      el.querySelector("[data-svg]").innerHTML = svgText([axis("MOS"), polyline(pts, TEAL), '<path d="M' + limit + ' 20 V150" stroke="' + ROSE + '" stroke-dasharray="3 3"/>', '<text x="' + (limit + 4) + '" y="32" fill="' + ROSE + '" font-size="10">150 ms</text>']);
      el.querySelector("[data-o]").innerHTML = "<b>At 150 ms " + mosFromR(rScore(150, 0, 25.1, loss)).toFixed(2) + "</b>";
    });

  add("codec-bw", "Codec bandwidth comparison",
    "kbit/s = (payload + 40 + L2) x 8 x (1000/ptime) / 1000. Payload = codec bit rate x ptime / 8000.",
    "G.711 at 20 ms is 80 kbit/s with a 40-byte header and 87.2 with 18 bytes of Ethernet.",
    [{ key: "p", label: "ptime", options: ["10", "20", "30"], value: "20" }, { key: "l2", label: "L2 bytes", options: ["0", "18"], value: "18" }],
    function (el) {
      var p = parseFloat(val(el, "p")), l2 = parseFloat(val(el, "l2"));
      var names = Object.keys(CODECS);
      var body = names.map(function (name, i) {
        var kb = bw(CODECS[name].bps, p, l2);
        var h = Math.max(8, (kb / 120) * 110);
        var x = 70 + i * 160;
        return '<rect x="' + x + '" y="' + (140 - h) + '" width="70" height="' + h + '" rx="8" fill="' + [TEAL, INDIGO, GREEN][i] + '"/><text x="' + (x + 35) + '" y="158" text-anchor="middle" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + name + " " + kb.toFixed(1) + "</text>";
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>G.711 " + bw(64000, p, l2).toFixed(1) + " kbit/s</b>";
    });

  add("jitter-buffer", "Jitter buffer versus late packets",
    "Teaching model: if peak jitter J is uniform from 0 to J, the late fraction is max(0, (J-buffer) / J).",
    "A deeper buffer hides jitter and adds delay. It is not free MOS.",
    [{ key: "j", label: "Peak jitter ms", min: 5, max: 120, value: 40 }, { key: "b", label: "Buffer ms", min: 0, max: 120, value: 30 }],
    function (el) {
      var j = Math.max(1, val(el, "j")), b = val(el, "b");
      var late = Math.max(0, (j - b) / j);
      var w = Math.max(8, late * 520);
      el.querySelector("[data-svg]").innerHTML = '<text x="40" y="40" fill="currentColor" font-size="13" font-family="ui-sans-serif,system-ui">Late packets</text><rect x="40" y="52" width="520" height="28" rx="8" fill="currentColor" fill-opacity=".08"/><rect x="40" y="52" width="' + w + '" height="28" rx="8" fill="' + (late > 0.05 ? ROSE : TEAL) + '"/><text x="40" y="110" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">Buffer ' + b + " ms against peak jitter " + j + " ms</text>";
      el.querySelector("[data-o]").innerHTML = "<b>Late " + (late * 100).toFixed(1) + "%</b><b>Added delay " + b + " ms</b>";
    });

  add("erlang-b-curve", "Erlang B blocking curve",
    "B starts at 1. Then B = A x B / (k + A x B) for k = 1..N.",
    "Trunks on the x axis. The curve is the probability a call finds every trunk busy.",
    [{ key: "a", label: "Erlangs", min: 1, max: 40, value: 12 }],
    function (el) {
      var A = val(el, "a"), pts = [];
      for (var n = 1; n <= 40; n++) pts.push([40 + ((n - 1) / 39) * 560, 150 - (1 - erlangB(n, A)) * 120]);
      el.querySelector("[data-svg]").innerHTML = svgText([axis("1-B"), polyline(pts, INDIGO)]);
      el.querySelector("[data-o]").innerHTML = "<b>B(20) " + (erlangB(20, A) * 100).toFixed(2) + "%</b><b>A " + A + "</b>";
    });

  add("erlang-c-curve", "Erlang C wait curve",
    "C = N x B / (N - A x (1-B)) when A is below N. Otherwise the queue is unstable.",
    "This is the probability a contact waits, not the probability it is blocked.",
    [{ key: "a", label: "Erlangs", min: 1, max: 30, value: 10 }],
    function (el) {
      var A = val(el, "a"), pts = [];
      for (var n = Math.ceil(A) + 1; n <= Math.ceil(A) + 20; n++) pts.push([40 + ((n - A) / 20) * 560, 150 - erlangC(n, A) * 120]);
      el.querySelector("[data-svg]").innerHTML = svgText([axis("C"), polyline(pts, TEAL)]);
      el.querySelector("[data-o]").innerHTML = "<b>C at A+2 " + (erlangC(Math.ceil(A) + 2, A) * 100).toFixed(1) + "%</b>";
    });

  add("sla-agents", "Service level versus agents",
    "SL = 1 - C x exp(-(N-A) x target / AHT), when A is below N.",
    "The target here is the seconds you are willing to wait, not a vendor score.",
    [{ key: "a", label: "Erlangs", min: 2, max: 30, value: 12 }, { key: "t", label: "Target s", min: 5, max: 60, value: 20 }, { key: "aht", label: "AHT s", min: 60, max: 600, value: 180 }],
    function (el) {
      var A = val(el, "a"), t = val(el, "t"), aht = val(el, "aht");
      var pts = [];
      for (var i = 1; i <= 15; i++) {
        var n = Math.ceil(A) + i;
        var C = erlangC(n, A);
        var sl = 1 - C * Math.exp(-(n - A) * t / aht);
        pts.push([40 + ((i - 1) / 14) * 560, 150 - Math.max(0, sl) * 120]);
      }
      el.querySelector("[data-svg]").innerHTML = svgText([axis("SL"), polyline(pts, GREEN)]);
      el.querySelector("[data-o]").innerHTML = "<b>Target " + t + " s</b><b>AHT " + aht + " s</b>";
    });

  add("asa-agents", "ASA versus agents",
    "ASA = C x AHT / (N-A) when the queue is stable.",
    "Average speed of answer grows without a bound as occupancy approaches 1.",
    [{ key: "a", label: "Erlangs", min: 2, max: 24, value: 10 }, { key: "aht", label: "AHT s", min: 30, max: 400, value: 180 }],
    function (el) {
      var A = val(el, "a"), aht = val(el, "aht"), pts = [];
      for (var i = 1; i <= 12; i++) {
        var n = Math.ceil(A) + i;
        var asa = erlangC(n, A) * aht / (n - A);
        pts.push([40 + ((i - 1) / 11) * 560, 150 - Math.min(1, asa / 120) * 120]);
      }
      el.querySelector("[data-svg]").innerHTML = svgText([axis("ASA"), polyline(pts, AMBER)]);
      el.querySelector("[data-o]").innerHTML = "<b>Stable only while agents exceed " + A + " erlang</b>";
    });

  add("aht-sensitivity", "ASA sensitivity to AHT",
    "Same staff, longer handle time. A = calls/hour x AHT / 3600, then ASA from Erlang C.",
    "A small AHT miss moves occupancy faster than a small staff miss.",
    [{ key: "cph", label: "Calls/hour", min: 20, max: 400, value: 120 }, { key: "n", label: "Agents", min: 2, max: 40, value: 12 }],
    function (el) {
      var cph = val(el, "cph"), n = val(el, "n"), pts = [];
      for (var aht = 60; aht <= 360; aht += 20) {
        var A = cph * aht / 3600;
        var asa = A >= n ? 120 : erlangC(n, A) * aht / (n - A);
        pts.push([40 + ((aht - 60) / 300) * 560, 150 - Math.min(1, asa / 180) * 120]);
      }
      el.querySelector("[data-svg]").innerHTML = svgText([axis("ASA"), polyline(pts, INDIGO)]);
      el.querySelector("[data-o]").innerHTML = "<b>" + n + " agents</b><b>" + cph + " calls/hour</b>";
    });

  add("trunk-util", "Trunk utilization and blocking",
    "Occupancy = A / N. Blocking = Erlang B(N, A).",
    "High occupancy with low blocking needs more trunks than the average call count.",
    [{ key: "a", label: "Erlangs", min: 1, max: 40, value: 18 }, { key: "n", label: "Trunks", min: 1, max: 60, value: 24 }],
    function (el) {
      var A = val(el, "a"), n = Math.max(1, val(el, "n"));
      var occ = Math.min(1, A / n), B = erlangB(Math.round(n), A);
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="40" width="' + (occ * 520) + '" height="36" rx="8" fill="' + TEAL + '"/><text x="40" y="100" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">Occupancy ' + (occ * 100).toFixed(0) + "% · blocking " + (B * 100).toFixed(2) + "%</text>";
      el.querySelector("[data-o]").innerHTML = "<b>" + (occ * 100).toFixed(0) + "% used</b><b>B " + (B * 100).toFixed(2) + "%</b>";
    });

  add("cac-budget", "CAC call budget",
    "Calls that fit = floor(link kbit/s x budget / per-call kbit/s).",
    "The budget slider is the share of the link you will give to bearer, not the whole interface.",
    [{ key: "link", label: "Link kbit/s", min: 256, max: 10000, step: 64, value: 1544 }, { key: "share", label: "Bearer share %", min: 10, max: 80, value: 33 }],
    function (el) {
      var link = val(el, "link"), share = val(el, "share");
      var per = bw(64000, 20, 18);
      var calls = Math.floor(link * (share / 100) / per);
      el.querySelector("[data-svg]").innerHTML = '<text x="40" y="80" fill="currentColor" font-size="28" font-family="Georgia,serif">' + calls + '</text><text x="40" y="110" fill="currentColor" font-size="13" font-family="ui-sans-serif,system-ui">G.711 20 ms calls inside ' + share + "% of " + link + " kbit/s</text>";
      el.querySelector("[data-o]").innerHTML = "<b>" + calls + " calls</b><b>" + per.toFixed(1) + " kbit/s each</b>";
    });

  add("failover-timeline", "Failover detection timeline",
    "Detection waits for missed keepalives. Recovery is the next successful INVITE, not the moment the peer died.",
    "OPTIONS interval times the miss count, then a new INVITE on the backup.",
    [{ key: "iv", label: "OPTIONS s", min: 1, max: 30, value: 5 }, { key: "miss", label: "Misses", min: 1, max: 8, value: 3 }],
    function (el) {
      var iv = val(el, "iv"), miss = val(el, "miss");
      var detect = iv * miss;
      var events = [["Peer silent", 0], ["Declared down", detect], ["INVITE backup", detect + 1], ["200 OK", detect + 2]];
      var max = detect + 2;
      var body = events.map(function (ev, i) {
        var x = 40 + (ev[1] / max) * 540;
        return '<circle cx="' + x + '" cy="70" r="7" fill="' + [ROSE, AMBER, INDIGO, GREEN][i] + '"/><text x="' + x + '" y="' + (100 + (i % 2) * 18) + '" text-anchor="middle" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + esc(ev[0]) + "</text>";
      }).join("");
      el.querySelector("[data-svg]").innerHTML = '<path d="M40 70 H580" stroke="currentColor" stroke-opacity=".3"/>' + body;
      el.querySelector("[data-o]").innerHTML = "<b>Detect " + detect + " s</b>";
    });

  add("latency-waterfall", "Call-setup latency waterfall",
    "Each bar is added delay before the 200 OK: DNS, TCP or TLS, SIP hops, and alerting.",
    "This is setup time, not the G.114 talk-path delay.",
    [{ key: "dns", label: "DNS ms", min: 0, max: 200, value: 20 }, { key: "tls", label: "TLS ms", min: 0, max: 300, value: 40 }, { key: "sip", label: "SIP hops ms", min: 10, max: 400, value: 80 }, { key: "ring", label: "Alerting ms", min: 0, max: 3000, value: 400 }],
    function (el) {
      var parts = [["DNS", val(el, "dns"), TEAL], ["TLS", val(el, "tls"), INDIGO], ["SIP", val(el, "sip"), AMBER], ["Alert", val(el, "ring"), GREEN]];
      var sum = parts.reduce(function (a, p) { return a + p[1]; }, 0);
      var x = 40;
      var body = parts.map(function (p) {
        var w = Math.max(6, (p[1] / Math.max(sum, 1)) * 540);
        var rect = '<rect x="' + x + '" y="50" width="' + w + '" height="32" fill="' + p[2] + '"/><text x="' + (x + 4) + '" y="110" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + p[0] + " " + p[1] + "</text>";
        x += w;
        return rect;
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>Setup " + sum + " ms</b>";
    });

  add("sip-timers", "SIP timer budget on UDP",
    "T1 defaults to 500 ms. T2 is 4 s. Timer B and Timer F are 64 x T1 = 32 s.",
    "TCP and TLS do not retransmit the INVITE the way UDP does. Timer B still means the transaction failed.",
    [{ key: "t1", label: "T1 ms", min: 100, max: 1000, step: 50, value: 500 }],
    function (el) {
      var t1 = val(el, "t1");
      var rows = [["T1", t1, TEAL], ["T2", 4000, INDIGO], ["Timer B", 64 * t1, AMBER], ["Timer F", 64 * t1, GREEN]];
      var body = rows.map(function (r, i) {
        var w = Math.max(8, Math.log10(r[1]) / Math.log10(64000) * 480);
        return '<rect x="120" y="' + (24 + i * 32) + '" width="' + w + '" height="20" rx="6" fill="' + r[2] + '"/><text x="16" y="' + (38 + i * 32) + '" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + r[0] + " " + (r[1] >= 1000 ? (r[1] / 1000) + " s" : r[1] + " ms") + "</text>";
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>Timer B " + (64 * t1 / 1000) + " s</b>";
    });

  add("ptime-bw", "Bandwidth versus packetization",
    "Shorter ptime sends the same header more often, so the wire rate rises.",
    "G.711 payload is 80 bytes at 20 ms and 40 bytes at 10 ms. The header does not shrink with it.",
    [{ key: "l2", label: "L2 bytes", options: ["0", "18"], value: "0" }],
    function (el) {
      var l2 = parseFloat(val(el, "l2"));
      var pts = [];
      [10, 20, 30, 40].forEach(function (p, i) {
        var kb = bw(64000, p, l2);
        pts.push([80 + i * 130, 150 - (kb / 160) * 120, kb, p]);
      });
      el.querySelector("[data-svg]").innerHTML = pts.map(function (p) {
        return '<rect x="' + p[0] + '" y="' + p[1] + '" width="60" height="' + (150 - p[1]) + '" rx="8" fill="' + TEAL + '"/><text x="' + (p[0] + 30) + '" y="166" text-anchor="middle" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + p[3] + " ms " + p[2].toFixed(0) + "</text>";
      }).join("");
      el.querySelector("[data-o]").innerHTML = "<b>10 ms " + bw(64000, 10, l2).toFixed(1) + "</b><b>20 ms " + bw(64000, 20, l2).toFixed(1) + "</b>";
    });

  add("dscp-map", "DSCP marking map",
    "EF is DSCP 46. Cisco collaboration signaling is commonly CS3, DSCP 24. Best effort is 0.",
    "A remark from EF to 0 does not change SIP. It changes who gets the queue.",
    [{ key: "trust", label: "Trust voice mark", options: ["yes", "no"], value: "yes" }],
    function (el) {
      var trust = val(el, "trust") === "yes";
      var rows = [["RTP bearer", trust ? "EF 46" : "BE 0", trust ? GREEN : ROSE], ["SIP signaling", trust ? "CS3 24" : "BE 0", trust ? INDIGO : AMBER]];
      el.querySelector("[data-svg]").innerHTML = rows.map(function (r, i) {
        return '<rect x="40" y="' + (36 + i * 50) + '" width="220" height="36" rx="8" fill="' + r[2] + '"/><text x="52" y="' + (58 + i * 50) + '" fill="#fff" font-size="13" font-family="ui-sans-serif,system-ui">' + r[0] + " · " + r[1] + "</text>";
      }).join("");
      el.querySelector("[data-o]").innerHTML = trust ? "<b>Marks kept</b>" : "<b>EF rewritten to 0</b>";
    });

  add("loss-burst", "Loss concealment window",
    "A burst longer than the jitter buffer cannot be hidden by PLC. Isolated losses often can.",
    "This is a teaching picture of buffer depth against burst length, not a codec score.",
    [{ key: "buf", label: "Buffer packets", min: 1, max: 10, value: 3 }, { key: "burst", label: "Burst packets", min: 1, max: 12, value: 2 }],
    function (el) {
      var buf = val(el, "buf"), burst = val(el, "burst");
      var hid = burst <= buf;
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="40" width="' + (buf * 40) + '" height="30" rx="6" fill="' + TEAL + '"/><rect x="40" y="84" width="' + (burst * 40) + '" height="30" rx="6" fill="' + (hid ? GREEN : ROSE) + '"/><text x="40" y="140" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">' + (hid ? "Buffer covers this burst" : "Burst exceeds the buffer") + "</text>";
      el.querySelector("[data-o]").innerHTML = hid ? "<b>Concealable</b>" : "<b>Gap in audio</b>";
    });

  add("occupancy-sl", "Occupancy versus service level",
    "Move agents with erlangs fixed. Occupancy = A/N. Service level uses Erlang C.",
    "The last few points of occupancy cost the most service level.",
    [{ key: "a", label: "Erlangs", min: 4, max: 30, value: 15 }, { key: "t", label: "Target s", min: 10, max: 40, value: 20 }],
    function (el) {
      var A = val(el, "a"), t = val(el, "t"), pts = [];
      for (var i = 1; i <= 16; i++) {
        var n = Math.ceil(A) + i;
        var C = erlangC(n, A);
        var sl = 1 - C * Math.exp(-(n - A) * t / 180);
        pts.push([40 + (1 - A / n) * 560, 150 - sl * 120]);
      }
      el.querySelector("[data-svg]").innerHTML = svgText([axis("SL"), polyline(pts, TEAL)]);
      el.querySelector("[data-o]").innerHTML = "<b>AHT fixed at 180 s</b>";
    });

  add("queue-depth", "Queue depth from wait probability",
    "Expected waiting contacts is a picture of C x A / (N-A), the Erlang C queue length.",
    "Unstable when agents do not exceed the erlangs.",
    [{ key: "a", label: "Erlangs", min: 2, max: 30, value: 14 }, { key: "n", label: "Agents", min: 2, max: 40, value: 18 }],
    function (el) {
      var A = val(el, "a"), n = val(el, "n");
      var q = A >= n ? Infinity : erlangC(n, A) * A / (n - A);
      var shown = q === Infinity ? 8 : Math.min(8, q);
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="' + (140 - shown * 14) + '" width="80" height="' + (shown * 14) + '" rx="8" fill="' + (q === Infinity ? ROSE : INDIGO) + '"/><text x="140" y="80" fill="currentColor" font-size="14" font-family="ui-sans-serif,system-ui">' + (q === Infinity ? "Unstable queue" : q.toFixed(2) + " contacts waiting") + "</text>";
      el.querySelector("[data-o]").innerHTML = q === Infinity ? "<b>A is not below N</b>" : "<b>" + q.toFixed(2) + " waiting</b>";
    });

  add("rona-rate", "RONA versus ring time",
    "Teaching model: answer probability rises with ring time and falls as agents are already busy. RONA is the miss.",
    "Not a vendor forecast. Longer ring time trades caller wait for fewer misses.",
    [{ key: "ring", label: "Ring s", min: 4, max: 30, value: 12 }, { key: "busy", label: "Agent busy %", min: 0, max: 80, value: 20 }],
    function (el) {
      var ring = val(el, "ring"), busy = val(el, "busy") / 100;
      var hit = (1 - busy) * (1 - Math.exp(-ring / 8));
      var rona = 1 - hit;
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="48" width="' + (rona * 500) + '" height="28" rx="8" fill="' + ROSE + '"/><text x="40" y="110" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">RONA ' + (rona * 100).toFixed(0) + "% at " + ring + " s ring</text>";
      el.querySelector("[data-o]").innerHTML = "<b>RONA " + (rona * 100).toFixed(0) + "%</b>";
    });

  add("register-expires", "Registration refresh timeline",
    "The phone must refresh before Expires. A missed refresh plus the client retry is when the device goes unknown.",
    "Expires is negotiated. 3600 s is only a common lab value, not a rule.",
    [{ key: "exp", label: "Expires s", min: 60, max: 3600, step: 60, value: 3600 }, { key: "retry", label: "Retry s", min: 5, max: 120, value: 30 }],
    function (el) {
      var exp = val(el, "exp"), retry = val(el, "retry");
      el.querySelector("[data-svg]").innerHTML = '<path d="M40 80 H600" stroke="currentColor" stroke-opacity=".3"/><circle cx="40" cy="80" r="6" fill="' + TEAL + '"/><circle cx="' + (40 + 400) + '" cy="80" r="6" fill="' + AMBER + '"/><circle cx="' + (40 + 480) + '" cy="80" r="6" fill="' + ROSE + '"/><text x="40" y="110" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">REGISTER</text><text x="400" y="110" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">Refresh at ' + exp + ' s</text><text x="470" y="130" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">Unknown after +' + retry + " s</text>";
      el.querySelector("[data-o]").innerHTML = "<b>Expires " + exp + " s</b>";
    });

  add("dns-ttl", "DNS TTL and failover wait",
    "A client can keep the old address until the TTL you published expires, then it looks up again.",
    "Failover is TTL plus the new lookup, not the moment the server died.",
    [{ key: "ttl", label: "TTL s", min: 5, max: 3600, step: 5, value: 300 }, { key: "lookup", label: "Lookup ms", min: 5, max: 500, value: 30 }],
    function (el) {
      var ttl = val(el, "ttl"), lookup = val(el, "lookup");
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="50" width="' + Math.min(520, ttl / 6) + '" height="28" rx="6" fill="' + INDIGO + '"/><text x="40" y="110" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">Stale answer for ' + ttl + " s, then " + lookup + " ms</text>";
      el.querySelector("[data-o]").innerHTML = "<b>Wait " + ttl + " s + " + lookup + " ms</b>";
    });

  add("cert-expiry", "Certificate expiry runway",
    "Days left until the not-after date. Warning bands at 60, 30, and 7 days are operational, not part of TLS itself.",
    "A failed handshake has no INVITE. Check the date before the dial plan.",
    [{ key: "days", label: "Days left", min: 0, max: 120, value: 45 }],
    function (el) {
      var days = val(el, "days");
      var color = days < 7 ? ROSE : days < 30 ? AMBER : GREEN;
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="48" width="' + Math.max(8, (days / 120) * 520) + '" height="28" rx="8" fill="' + color + '"/><path d="M' + (40 + (7 / 120) * 520) + ' 40 V90" stroke="' + ROSE + '"/><path d="M' + (40 + (30 / 120) * 520) + ' 40 V90" stroke="' + AMBER + '"/><text x="40" y="120" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">' + days + " days · bands at 7 and 30</text>";
      el.querySelector("[data-o]").innerHTML = "<b>" + days + " days left</b>";
    });

  add("codec-mos-bars", "Codec MOS at zero loss",
    "R = 93.2 - Id - Ie, delay fixed by the slider, loss 0. G.722 shown with the G.711 Ie pair.",
    "A wideband codec is not credited with a separate Bpl in this teaching model.",
    [{ key: "d", label: "Delay ms", min: 20, max: 250, value: 60 }],
    function (el) {
      var d = val(el, "d");
      var body = Object.keys(CODECS).map(function (name, i) {
        var c = CODECS[name];
        var m = mosFromR(rScore(d, c.ie, c.bpl, 0));
        var h = (m / 4.5) * 110;
        return '<rect x="' + (70 + i * 160) + '" y="' + (140 - h) + '" width="70" height="' + h + '" rx="8" fill="' + [TEAL, INDIGO, GREEN][i] + '"/><text x="' + (105 + i * 160) + '" y="158" text-anchor="middle" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + name + " " + m.toFixed(2) + "</text>";
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>Loss held at 0</b>";
    });

  add("g114-stack", "One-way delay against G.114",
    "Sum of packetization, queuing, serialization, propagation, and jitter buffer.",
    "About 150 ms one way is the planning limit. G.711 look-ahead is omitted because it has none.",
    [{ key: "pkt", label: "Packet ms", min: 10, max: 40, value: 20 }, { key: "q", label: "Queue ms", min: 0, max: 40, value: 10 }, { key: "ser", label: "Serial ms", min: 0, max: 20, value: 3 }, { key: "prop", label: "Prop ms", min: 0, max: 80, value: 20 }, { key: "jb", label: "Jitter buf", min: 0, max: 80, value: 40 }],
    function (el) {
      var parts = [["Pkt", val(el, "pkt"), TEAL], ["Queue", val(el, "q"), INDIGO], ["Serial", val(el, "ser"), AMBER], ["Prop", val(el, "prop"), "#7C3AED"], ["JB", val(el, "jb"), GREEN]];
      var sum = parts.reduce(function (a, p) { return a + p[1]; }, 0);
      var x = 20;
      var body = parts.map(function (p) {
        var w = Math.max(8, (p[1] / 180) * 520);
        var rect = '<rect x="' + x + '" y="46" width="' + w + '" height="28" fill="' + p[2] + '"/>';
        x += w;
        return rect;
      }).join("");
      var limit = 20 + (150 / 180) * 520;
      el.querySelector("[data-svg]").innerHTML = body + '<path d="M' + limit + ' 30 V90" stroke="' + ROSE + '" stroke-dasharray="3 3"/><text x="20" y="120" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">Total ' + sum + " ms</text>";
      el.querySelector("[data-o]").innerHTML = "<b>Total " + sum + " ms</b><b>" + (sum <= 150 ? "Inside 150 ms" : "Over the G.114 planning limit") + "</b>";
    });

  add("srtp-overhead", "SRTP overhead on G.711",
    "RTP is 12 bytes inside the 40-byte IP/UDP/RTP header. SRTP adds authentication tag bytes on top of that rate.",
    "A 10-byte tag at 20 ms is 4 kbit/s extra. The codec payload does not change.",
    [{ key: "tag", label: "Tag bytes", min: 0, max: 20, value: 10 }, { key: "p", label: "ptime", options: ["10", "20", "30"], value: "20" }],
    function (el) {
      var tag = val(el, "tag"), p = parseFloat(val(el, "p"));
      var base = bw(64000, p, 0);
      var extra = tag * 8 * (1000 / p) / 1000;
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="50" width="' + Math.min(500, base * 3) + '" height="24" fill="' + TEAL + '"/><rect x="' + (40 + Math.min(500, base * 3)) + '" y="50" width="' + Math.max(2, extra * 3) + '" height="24" fill="' + AMBER + '"/><text x="40" y="110" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">Bearer ' + base.toFixed(1) + " + tag " + extra.toFixed(1) + " kbit/s</text>";
      el.querySelector("[data-o]").innerHTML = "<b>" + (base + extra).toFixed(1) + " kbit/s</b>";
    });

  add("setup-waterfall", "Post-dial delay waterfall",
    "Dial tone to INVITE, then to 180, then to 200. The sum is post-dial delay.",
    "A long gap before INVITE is the dial plan or the client. A long gap after INVITE is the network or the far end.",
    [{ key: "dial", label: "To INVITE ms", min: 20, max: 1500, value: 200 }, { key: "ring", label: "To 180 ms", min: 20, max: 2000, value: 300 }, { key: "ans", label: "180 to 200 ms", min: 20, max: 4000, value: 800 }],
    function (el) {
      var parts = [["INVITE", val(el, "dial"), TEAL], ["180", val(el, "ring"), AMBER], ["200", val(el, "ans"), GREEN]];
      var sum = 0;
      var body = parts.map(function (p, i) {
        sum += p[1];
        return '<rect x="40" y="' + (28 + i * 36) + '" width="' + Math.min(520, p[1] / 4) + '" height="24" rx="6" fill="' + p[2] + '"/><text x="' + (48 + Math.min(520, p[1] / 4)) + '" y="' + (44 + i * 36) + '" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">' + p[0] + " " + p[1] + "</text>";
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>Post-dial " + sum + " ms</b>";
    });

  add("staffing-shrink", "Shrinkage and productive agents",
    "Productive agents = roster x (1 - shrinkage). Erlangs still have to fit under that smaller number.",
    "Shrinkage is breaks, meetings, and absence. It is not occupancy.",
    [{ key: "roster", label: "Roster", min: 5, max: 80, value: 20 }, { key: "shrink", label: "Shrink %", min: 0, max: 50, value: 30 }, { key: "a", label: "Erlangs", min: 1, max: 40, value: 10 }],
    function (el) {
      var roster = val(el, "roster"), shrink = val(el, "shrink") / 100, A = val(el, "a");
      var prod = roster * (1 - shrink);
      var occ = prod <= 0 ? 1 : A / prod;
      el.querySelector("[data-svg]").innerHTML = '<rect x="40" y="40" width="200" height="28" rx="6" fill="' + INDIGO + '"/><rect x="40" y="78" width="' + Math.max(8, (prod / roster) * 200) + '" height="28" rx="6" fill="' + TEAL + '"/><text x="260" y="60" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">Roster ' + roster + "</text><text x=\"260\" y=\"98\" fill=\"currentColor\" font-size=\"12\" font-family=\"ui-sans-serif,system-ui\">Productive " + prod.toFixed(1) + "</text>";
      el.querySelector("[data-o]").innerHTML = "<b>Occupancy on productive staff " + (Math.min(999, occ) * 100).toFixed(0) + "%</b>";
    });

  add("jitter-histogram", "Arrival jitter histogram",
    "Packets should land on the ptime grid. The slider spreads them. Bins past the buffer are late.",
    "A histogram of a lab spread, not a capture file.",
    [{ key: "spread", label: "Spread ms", min: 0, max: 80, value: 20 }, { key: "buf", label: "Buffer ms", min: 5, max: 80, value: 30 }],
    function (el) {
      var spread = val(el, "spread"), buf = val(el, "buf");
      var bins = [0, 5, 10, 20, 30, 40, 60, 80];
      var body = bins.map(function (b, i) {
        var weight = Math.max(0, 1 - Math.abs(b - spread) / 40);
        var h = 20 + weight * 90;
        var late = b > buf;
        return '<rect x="' + (40 + i * 70) + '" y="' + (140 - h) + '" width="40" height="' + h + '" rx="6" fill="' + (late ? ROSE : TEAL) + '"/><text x="' + (60 + i * 70) + '" y="156" text-anchor="middle" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + b + "</text>";
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>Late bins are past " + buf + " ms</b>";
    });

  add("cutover-clock", "Cutover clock",
    "Discover, dual-run, pilot, cut, hypercare. Rollback has to fit before the irreversible mark.",
    "Minutes are the slider. The shape of the plan does not change.",
    [{ key: "pilot", label: "Pilot min", min: 5, max: 120, value: 30 }, { key: "hyper", label: "Hypercare min", min: 15, max: 240, value: 60 }],
    function (el) {
      var pilot = val(el, "pilot"), hyper = val(el, "hyper");
      var rows = [["Discover", 15, TEAL], ["Dual-run", 20, INDIGO], ["Pilot", pilot, AMBER], ["Cut", 10, ROSE], ["Hypercare", hyper, GREEN]];
      var x = 30;
      var body = rows.map(function (r) {
        var w = Math.max(16, r[1] / 2);
        var rect = '<rect x="' + x + '" y="48" width="' + w + '" height="26" fill="' + r[2] + '"/><text x="' + x + '" y="96" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + r[0] + "</text>";
        x += w + 6;
        return rect;
      }).join("");
      el.querySelector("[data-svg]").innerHTML = body;
      el.querySelector("[data-o]").innerHTML = "<b>Pilot " + pilot + " min</b><b>Hypercare " + hyper + " min</b>";
    });

  add("early-media-timing", "Early media versus final answer",
    "183 can carry SDP before the 200. The 200 may replace that answer. Ringback must follow the right one.",
    "PRACK applies only when the provisional was sent reliably.",
    [{ key: "gap", label: "183 to 200 ms", min: 50, max: 4000, value: 800 }, { key: "rel", label: "Reliable", options: ["yes", "no"], value: "yes" }],
    function (el) {
      var gap = val(el, "gap"), rel = val(el, "rel") === "yes";
      el.querySelector("[data-svg]").innerHTML = '<circle cx="80" cy="70" r="8" fill="' + AMBER + '"/><text x="96" y="74" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">183</text><circle cx="' + (160 + Math.min(360, gap / 8)) + '" cy="70" r="8" fill="' + GREEN + '"/><text x="' + (176 + Math.min(360, gap / 8)) + '" y="74" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">200</text><text x="40" y="120" fill="currentColor" font-size="12" font-family="ui-sans-serif,system-ui">' + (rel ? "PRACK required on the reliable 183" : "Unreliable 183: no PRACK") + "</text>";
      el.querySelector("[data-o]").innerHTML = "<b>" + gap + " ms of early media</b>";
    });

  add("retransmission-backoff", "UDP INVITE retransmission backoff",
    "Retransmit at T1, 2 T1, 4 T1, and so on, capped by T2, until Timer B at 64 x T1.",
    "Seeing the same INVITE repeated is UDP reliability, not five new calls.",
    [{ key: "t1", label: "T1 ms", min: 200, max: 1000, step: 50, value: 500 }],
    function (el) {
      var t1 = val(el, "t1");
      var t = 0, pts = [[40, 140]];
      for (var i = 0; i < 6; i++) {
        var wait = Math.min(4000, t1 * Math.pow(2, i));
        t += wait;
        pts.push([40 + Math.min(560, t / 40), 140 - i * 16]);
      }
      el.querySelector("[data-svg]").innerHTML = svgText([axis("retry"), polyline(pts, INDIGO), '<text x="40" y="24" fill="currentColor" font-size="11" font-family="ui-sans-serif,system-ui">Timer B at ' + (64 * t1 / 1000) + " s</text>"]);
      el.querySelector("[data-o]").innerHTML = "<b>T1 " + t1 + " ms</b><b>Timer B " + (64 * t1 / 1000) + " s</b>";
    });

  function mount(parent, kind) {
    if (!kind || kind === "none") return false;
    var found = null;
    for (var i = 0; i < types.length; i++) if (types[i].id === kind) found = types[i];
    if (!found) return false;
    var el = box(parent, found.title, found.formula, found.note);
    controls(el, found.specs, function () { found.draw(el); });
    found.draw(el);
    return true;
  }

  window.UCCharts = {
    types: types.map(function (t) { return t.id; }),
    mount: mount,
    mosFromR: mosFromR,
    erlangB: erlangB,
    erlangC: erlangC,
    bandwidthKbps: bw
  };
})();
