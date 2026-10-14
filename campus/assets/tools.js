/* Erlang, SDP, the SIP ladder, and the source list. */
(function () {
  "use strict";

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function reduced() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function erlangB(agents, offered) {
    if (agents <= 0) return 1;
    var blocking = 1;
    for (var k = 1; k <= agents; k += 1) blocking = (offered * blocking) / (k + offered * blocking);
    return blocking;
  }

  function erlangC(agents, offered) {
    if (!(offered < agents)) return 1;
    var blocking = erlangB(agents, offered);
    var denom = agents - offered * (1 - blocking);
    if (denom <= 0) return 1;
    return Math.max(0, Math.min(1, (agents * blocking) / denom));
  }

  function mountErlang(host) {
    host.classList.add("tool-card");
    host.innerHTML =
      '<p class="eyebrow">Traffic</p><h2>Erlang B and Erlang C</h2>' +
      '<p class="muted">Iterative Erlang B, then Erlang C for the chance a call waits. Average speed of answer uses P(wait) × AHT / (N − A). This is a teaching model, not a sizing warranty.</p>' +
      '<div class="sliders">' +
      '<label>Agents <input data-k="agents" type="range" min="1" max="80" value="20"></label>' +
      '<label>Offered load (erlangs) <input data-k="erlangs" type="range" min="1" max="60" step="0.5" value="14"></label>' +
      '<label>Average handle time (seconds) <input data-k="aht" type="range" min="30" max="600" value="180"></label>' +
      "</div>" +
      '<p class="tool-out" data-out role="status"></p>' +
      '<p class="cite-line">Formulas follow the standard recursive Erlang B and the Erlang C wait probability used in contact-center staffing. See the sources list for ITU-T G.107, which is a different model (MOS), and for Cisco collaboration design guidance.</p>';
    var out = host.querySelector("[data-out]");
    function read(key) {
      return parseFloat(host.querySelector('[data-k="' + key + '"]').value);
    }
    function paint() {
      var agents = Math.round(read("agents"));
      var offered = read("erlangs");
      var aht = read("aht");
      var b = erlangB(agents, offered);
      var c = erlangC(agents, offered);
      var asa = offered >= agents ? null : (c * aht) / (agents - offered);
      out.textContent =
        agents + " agents, " + offered.toFixed(1) + " erlangs. Erlang B blocking " +
        (b * 100).toFixed(2) + "%. Erlang C P(wait) " + (c * 100).toFixed(2) + "%. " +
        (asa == null ? "Offered load meets the agent count, so this Erlang C form is saturated." : "ASA about " + asa.toFixed(1) + " seconds at AHT " + aht + " s.");
    }
    host.addEventListener("input", paint);
    paint();
  }

  var SAMPLE_SDP = [
    "v=0",
    "o=alice 2890844526 2890844526 IN IP4 192.0.2.10",
    "s=UC Lab",
    "c=IN IP4 192.0.2.10",
    "t=0 0",
    "m=audio 16384 RTP/AVP 0 8 9",
    "a=rtpmap:0 PCMU/8000",
    "a=rtpmap:8 PCMA/8000",
    "a=rtpmap:9 G722/8000",
    "a=ptime:20",
    "a=sendrecv"
  ].join("\n");

  function explainSdpLine(line) {
    var text = line.trim();
    if (!text) return "";
    var kind = text.charAt(0);
    if (kind === "v") return "Protocol version. SDP uses 0.";
    if (kind === "o") return "Origin. Username, session id, version, network type, and the address that owns the session.";
    if (kind === "s") return "Session name. Often ignored by SIP intermediaries.";
    if (kind === "c" && /0\.0\.0\.0/.test(text)) return "Connection address 0.0.0.0 is the old hold signal. Prefer a=sendonly or a=inactive on a real address.";
    if (kind === "c") return "Connection data. This is where RTP will be sent unless a media-level c= overrides it.";
    if (kind === "t") return "Timing. 0 0 means the session is permanent.";
    if (kind === "m") {
      if (/m=audio\s+0\b/.test(text)) return "Media line with port 0. That media is rejected.";
      return "Media line. Port, transport, and payload types the offerer can receive.";
    }
    if (/^a=rtpmap:/i.test(text)) return "Payload map. The number in m= gets a codec name and clock rate.";
    if (/^a=sendrecv/i.test(text)) return "Direction is both ways.";
    if (/^a=sendonly/i.test(text)) return "Sender only. The other direction should not be expected.";
    if (/^a=recvonly/i.test(text)) return "Receiver only.";
    if (/^a=inactive/i.test(text)) return "Inactive. Hold is cleaner this way than a zero connection address.";
    if (/^a=ptime:/i.test(text)) return "Packet time in milliseconds. Bandwidth math uses this ptime.";
    if (kind === "a") return "Attribute.";
    return "Line.";
  }

  function mountSdp(host) {
    host.classList.add("tool-card");
    host.innerHTML =
      '<p class="eyebrow">Offer / answer</p><h2>SDP breakdown</h2>' +
      '<p class="muted">Paste an offer. The lab explains each line. The sample uses TEST-NET 192.0.2.10 and is not a capture.</p>' +
      '<label class="sdp-label">Session description<textarea data-sdp rows="12" spellcheck="false"></textarea></label>' +
      '<div data-table></div>' +
      '<p class="cite-line"><a href="https://www.rfc-editor.org/rfc/rfc4566" rel="noopener noreferrer">RFC 4566</a> defines SDP. <a href="https://www.rfc-editor.org/rfc/rfc3264" rel="noopener noreferrer">RFC 3264</a> defines the offer/answer model used with SIP.</p>';
    var box = host.querySelector("[data-sdp]");
    var table = host.querySelector("[data-table]");
    box.value = SAMPLE_SDP;
    function paint() {
      var rows = box.value.split(/\r?\n/).filter(function (line) { return line.trim(); });
      table.innerHTML = '<table class="nice"><thead><tr><th>Line</th><th>Meaning</th></tr></thead><tbody>' +
        rows.map(function (line) {
          return "<tr><td class=\"mono\">" + esc(line) + "</td><td>" + esc(explainSdpLine(line)) + "</td></tr>";
        }).join("") +
        "</tbody></table>";
    }
    box.addEventListener("input", paint);
    paint();
  }

  var LADDER = {
    title: "Basic call across CUCM and CUBE",
    actors: ["Phone", "CUCM", "CUBE", "PSTN"],
    steps: [
      { f: 0, t: 1, label: "INVITE", kind: "req", cap: "The phone offers SDP on the CUCM leg. 100 Trying is hop by hop and is not end to end.", packet: "INVITE sip:+14155550100@cucm.example SIP/2.0\nVia: SIP/2.0/TLS phone.example;branch=z9hG4bK-lab\nFrom: <sip:+14155550199@example>;tag=from-a\nTo: <sip:+14155550100@example>\nCall-ID: lab-phone-001\nCSeq: 1 INVITE\nContact: <sip:phone.example;transport=tls>\nContent-Type: application/sdp" },
      { f: 1, t: 0, label: "100 Trying", kind: "prov", cap: "CUCM accepted the INVITE into a transaction. This is not ringing.", packet: "SIP/2.0 100 Trying\nVia: SIP/2.0/TLS phone.example;branch=z9hG4bK-lab\nCall-ID: lab-phone-001\nCSeq: 1 INVITE" },
      { f: 1, t: 2, label: "INVITE", kind: "req", cap: "CUCM is a back-to-back user agent here. The CUBE leg has its own Call-ID.", packet: "INVITE sip:+14155550100@cube.example SIP/2.0\nCall-ID: lab-cube-002\nCSeq: 1 INVITE\nContent-Type: application/sdp\n\nDifferent Call-ID from the phone leg." },
      { f: 2, t: 3, label: "INVITE", kind: "req", cap: "CUBE starts the PSTN leg. Digit manipulation, if any, already happened.", packet: "INVITE sip:+14155550100@pstn.example SIP/2.0\nCall-ID: lab-pstn-003\nCSeq: 1 INVITE" },
      { f: 3, t: 2, label: "180 Ringing", kind: "prov", cap: "The far end is alerting. Early media would be a different step, with SDP and a 183.", packet: "SIP/2.0 180 Ringing\nCall-ID: lab-pstn-003\nCSeq: 1 INVITE" },
      { f: 1, t: 0, label: "180 Ringing", kind: "prov", cap: "Ringing mapped back to the phone. The phone should play local ringback unless early media arrives.", packet: "SIP/2.0 180 Ringing\nCall-ID: lab-phone-001\nCSeq: 1 INVITE" },
      { f: 3, t: 2, label: "200 OK", kind: "ok", cap: "Answer SDP. The media address and payload are chosen here, not by the INVITE alone.", packet: "SIP/2.0 200 OK\nCall-ID: lab-pstn-003\nCSeq: 1 INVITE\nContent-Type: application/sdp\n\nm=audio 16384 RTP/AVP 0\na=rtpmap:0 PCMU/8000" },
      { f: 1, t: 0, label: "200 OK", kind: "ok", cap: "The phone leg is answered. ACK completes the INVITE transaction for this 2xx.", packet: "SIP/2.0 200 OK\nCall-ID: lab-phone-001\nCSeq: 1 INVITE\nContent-Type: application/sdp" },
      { f: 0, t: 1, label: "ACK", kind: "req", cap: "ACK for a 2xx is end to end. It is not the same transaction as the INVITE.", packet: "ACK sip:cucm.example SIP/2.0\nCall-ID: lab-phone-001\nCSeq: 1 ACK" },
      { f: 0, t: 3, label: "RTP", kind: "media", cap: "Media is a different path from the SIP signaling. One-way audio is an RTP problem with a fine SIP ladder.", packet: "RTP payload 0 PCMU/8000\n20 ms ptime\nSignaling Call-IDs do not appear inside the RTP packets." },
      { f: 0, t: 1, label: "BYE", kind: "bye", cap: "Either side can end the dialog. BYE is a new transaction.", packet: "BYE sip:cucm.example SIP/2.0\nCall-ID: lab-phone-001\nCSeq: 2 BYE" },
      { f: 1, t: 0, label: "200 OK", kind: "ok", cap: "The dialog is over after the BYE succeeds on each B2BUA leg.", packet: "SIP/2.0 200 OK\nCall-ID: lab-phone-001\nCSeq: 2 BYE" }
    ]
  };

  function ladderSvg(flow, index) {
    var actors = flow.actors;
    var steps = flow.steps;
    var n = actors.length;
    var w = 880;
    var top = 78;
    var row = 46;
    var h = top + steps.length * row + 16;
    var col = (w - 40) / n;
    function cx(i) { return 20 + col * i + col / 2; }
    var current = steps[index] || {};
    var out = ['<svg class="ladder" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(flow.title) + '">'];
    actors.forEach(function (name, a) {
      var x = cx(a);
      var hot = a === current.f || a === current.t;
      out.push('<rect x="' + (x - 62) + '" y="12" width="124" height="32" rx="16" fill="' + (hot ? "#4338ca" : "#131d31") + '"></rect>');
      out.push('<text x="' + x + '" y="33" text-anchor="middle" fill="#f8fafc" font-size="13" font-family="ui-sans-serif,system-ui" font-weight="700">' + esc(name) + "</text>");
      out.push('<path d="M' + x + " 48 V" + (h - 10) + '" stroke="' + (hot ? "#818cf8" : "#94a3b8") + '" stroke-width="' + (hot ? 2.4 : 1.2) + '"></path>');
    });
    steps.forEach(function (step, i) {
      var y = top + i * row;
      var x1 = cx(step.f);
      var x2 = cx(step.t);
      var on = i === index;
      var color = on ? "#818cf8" : i < index ? "#0f766e" : "#94a3b8";
      if (on) out.push('<rect x="12" y="' + (y - 16) + '" width="' + (w - 24) + '" height="32" rx="10" fill="#818cf8" fill-opacity="0.12"></rect>');
      if (Math.abs(x1 - x2) < 2) {
        out.push('<path d="M' + x1 + " " + y + " q18 -16 0 -28" + '" fill="none" stroke="' + color + '" stroke-width="' + (on ? 3 : 1.6) + '"></path>');
      } else {
        out.push('<path d="M' + x1 + " " + y + " H" + x2 + '" fill="none" stroke="' + color + '" stroke-width="' + (on ? 3 : 1.6) + '"></path>');
        var dir = x2 > x1 ? 1 : -1;
        out.push('<path d="M' + x2 + " " + y + " l" + (-dir * 8) + " -4 v8 z\" fill=\"" + color + "\"></path>");
        if (on && !reduced()) {
          out.push('<circle cx="' + x1 + '" cy="' + y + '" r="5" fill="#fff" stroke="' + color + '" stroke-width="2"><animate attributeName="cx" from="' + x1 + '" to="' + x2 + '" dur="1.1s" repeatCount="indefinite"/></circle>');
        }
      }
      out.push('<text x="' + ((x1 + x2) / 2) + '" y="' + (y - 6) + '" text-anchor="middle" fill="#0f172a" font-size="12" font-weight="700" font-family="ui-sans-serif,system-ui">' + (i + 1) + " " + esc(step.label) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }

  function mountLadder(host) {
    host.classList.add("tool-card");
    var index = 0;
    var playing = false;
    var timer = null;
    var inspect = false;
    host.innerHTML =
      '<p class="eyebrow">Sequence</p><h2>' + esc(LADDER.title) + "</h2>" +
      '<p class="muted">Play, pause, step, and inspect. Each B2BUA leg has its own Call-ID. The example numbers are fictional.</p>' +
      '<div class="ladder-scroll" data-svg></div>' +
      '<p class="ladder-cap" data-cap role="status"></p>' +
      '<div class="tool-actions">' +
      '<button type="button" data-act="play" aria-pressed="false">Play</button>' +
      '<button type="button" data-act="back">Step back</button>' +
      '<button type="button" data-act="next">Step forward</button>' +
      '<button type="button" data-act="inspect" aria-pressed="false">Inspect</button>' +
      "</div>" +
      '<pre class="packet" data-packet hidden></pre>' +
      '<p class="cite-line">Signaling follows <a href="https://www.rfc-editor.org/rfc/rfc3261" rel="noopener noreferrer">RFC 3261</a>. DTMF digits in RTP are <a href="https://www.rfc-editor.org/rfc/rfc4733" rel="noopener noreferrer">RFC 4733</a>. Media transport is <a href="https://www.rfc-editor.org/rfc/rfc3550" rel="noopener noreferrer">RFC 3550</a>.</p>';
    var svgHost = host.querySelector("[data-svg]");
    var cap = host.querySelector("[data-cap]");
    var packet = host.querySelector("[data-packet]");
    var playBtn = host.querySelector('[data-act="play"]');
    var inspectBtn = host.querySelector('[data-act="inspect"]');

    function stop() {
      playing = false;
      if (timer) clearTimeout(timer);
      timer = null;
      playBtn.textContent = "Play";
      playBtn.setAttribute("aria-pressed", "false");
    }

    function draw() {
      svgHost.innerHTML = ladderSvg(LADDER, index);
      var step = LADDER.steps[index];
      cap.textContent = "Step " + (index + 1) + " of " + LADDER.steps.length + ". " + step.label + ". " + step.cap;
      packet.hidden = !inspect;
      packet.textContent = step.packet;
    }

    function tick() {
      if (!playing) return;
      if (index >= LADDER.steps.length - 1) {
        stop();
        return;
      }
      timer = setTimeout(function () {
        index += 1;
        draw();
        tick();
      }, 1100);
    }

    host.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-act]");
      if (!btn) return;
      var act = btn.getAttribute("data-act");
      if (act === "play") {
        if (playing) stop();
        else if (!reduced()) {
          if (index >= LADDER.steps.length - 1) index = 0;
          playing = true;
          playBtn.textContent = "Pause";
          playBtn.setAttribute("aria-pressed", "true");
          draw();
          tick();
        }
      }
      if (act === "back" || act === "next") {
        stop();
        index = Math.max(0, Math.min(LADDER.steps.length - 1, index + (act === "next" ? 1 : -1)));
        draw();
      }
      if (act === "inspect") {
        inspect = !inspect;
        inspectBtn.setAttribute("aria-pressed", inspect ? "true" : "false");
        draw();
      }
    });
    host.tabIndex = 0;
    host.addEventListener("keydown", function (event) {
      if (event.key === "ArrowRight") { event.preventDefault(); index = Math.min(LADDER.steps.length - 1, index + 1); stop(); draw(); }
      if (event.key === "ArrowLeft") { event.preventDefault(); index = Math.max(0, index - 1); stop(); draw(); }
    });
    draw();
    return { destroy: stop };
  }

  var SOURCES = [
    { href: "https://www.rfc-editor.org/rfc/rfc3261", title: "RFC 3261", note: "SIP: Session Initiation Protocol", journeys: ["cisco-voice", "webex", "teams", "contact-center"] },
    { href: "https://www.rfc-editor.org/rfc/rfc3264", title: "RFC 3264", note: "Offer/answer model for SDP", journeys: ["cisco-voice", "webex", "teams", "contact-center"] },
    { href: "https://www.rfc-editor.org/rfc/rfc3550", title: "RFC 3550", note: "RTP", journeys: ["cisco-voice", "webex", "teams", "contact-center"] },
    { href: "https://www.rfc-editor.org/rfc/rfc4566", title: "RFC 4566", note: "Session Description Protocol", journeys: ["cisco-voice", "webex", "teams", "contact-center"] },
    { href: "https://www.rfc-editor.org/rfc/rfc4733", title: "RFC 4733", note: "RTP payload for DTMF digits", journeys: ["cisco-voice", "webex", "teams", "contact-center"] },
    { href: "https://www.rfc-editor.org/rfc/rfc3711", title: "RFC 3711", note: "SRTP", journeys: ["cisco-voice", "webex", "teams"] },
    { href: "https://www.itu.int/rec/T-REC-G.114", title: "ITU-T G.114", note: "One-way delay planning", journeys: ["cisco-voice"] },
    { href: "https://www.itu.int/rec/T-REC-G.107", title: "ITU-T G.107", note: "E-model, the teaching basis for the MOS chart", journeys: ["cisco-voice", "contact-center"] },
    { href: "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html", title: "Cisco Unified CM", note: "Product documentation index", journeys: ["cisco-voice", "webex"] },
    { href: "https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html", title: "Cisco CUBE", note: "Unified Border Element documentation", journeys: ["cisco-voice", "webex", "teams"] },
    { href: "https://www.cisco.com/c/en/us/solutions/enterprise/design-zone-collaboration/index.html", title: "Cisco design zone", note: "Collaboration design guides and CVDs", journeys: ["cisco-voice", "webex", "teams", "contact-center"] },
    { href: "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/srnd/collab12/collab12.html", title: "Collaboration SRND", note: "Preferred architecture reference for CUCM-era designs", journeys: ["cisco-voice"] },
    { href: "https://help.webex.com/en-us/article/b2exve/Port-Reference-Information-for-Cisco-Webex-Calling", title: "Webex Calling ports", note: "Local gateway signaling and media port reference", journeys: ["webex"] },
    { href: "https://help.webex.com/en-us/article/8jda92/Webex-Calling", title: "Webex Calling", note: "Get started, including the local gateway workflow", journeys: ["webex"] },
    { href: "https://learn.microsoft.com/en-us/microsoftteams/setting-up-your-phone-system", title: "Teams Phone", note: "Microsoft phone system setup", journeys: ["teams"] },
    { href: "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan", title: "Direct Routing", note: "Plan Direct Routing between Teams and an SBC", journeys: ["teams"] },
    { href: "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html", title: "Unified CCE", note: "UCCE documentation index", journeys: ["contact-center"] },
    { href: "https://www.cisco.com/c/en/us/support/customer-collaboration/packaged-contact-center-enterprise/series.html", title: "Packaged CCE", note: "PCCE documentation index", journeys: ["contact-center"] }
  ];

  function sourcesHtml(journeyId) {
    var list = SOURCES.filter(function (item) {
      return !journeyId || item.journeys.indexOf(journeyId) >= 0;
    });
    return '<section class="sources"><h2>Sources</h2><ul>' + list.map(function (item) {
      return '<li><a href="' + esc(item.href) + '" rel="noopener noreferrer">' + esc(item.title) + "</a> <span>" + esc(item.note) + "</span></li>";
    }).join("") + "</ul></section>";
  }

  function linkifyHtml(html) {
    return String(html || "").replace(/>([^<]*)</g, function (full, text) {
      var linked = text.replace(/\bRFC\s*(\d{3,5})\b/gi, function (_m, num) {
        return '<a href="https://www.rfc-editor.org/rfc/rfc' + num + '" rel="noopener noreferrer">RFC ' + num + "</a>";
      });
      return ">" + linked + "<";
    });
  }

  window.UCTools = {
    erlang: mountErlang,
    sdp: mountSdp,
    ladder: mountLadder,
    sourcesHtml: sourcesHtml,
    linkifyHtml: linkifyHtml,
    erlangB: erlangB,
    erlangC: erlangC
  };
})();
