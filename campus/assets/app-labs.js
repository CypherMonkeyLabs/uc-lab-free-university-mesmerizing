/* Offline teaching labs. Models only. They do not touch a live system. */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function reduced() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }
  function succeed(id) {
    if (window.UCApp && window.UCApp.markLab) window.UCApp.markLab(id);
  }
  function kbps(bps, ptimeMs, l2Bytes) {
    var payload = bps * ptimeMs / 8000;
    var header = 40 + l2Bytes;
    var rate = 1000 / ptimeMs;
    return (payload + header) * 8 * rate / 1000;
  }
  function erlangB(n, a) {
    if (n <= 0) return 1;
    var b = 1;
    var k;
    for (k = 1; k <= n; k++) b = (a * b) / (k + a * b);
    return b;
  }
  function erlangC(n, a) {
    if (a >= n) return 1;
    var b = erlangB(n, a);
    var denom = n - a * (1 - b);
    if (denom <= 0) return 1;
    return Math.max(0, Math.min(1, (n * b) / denom));
  }

  var SIP_HEADERS = {
    via: "Via names the hop and the branch. The branch identifies this transaction. A B2BUA adds its own Via on the next leg.",
    from: "From holds the caller's dialog identity and the from-tag. It is not proof of who the carrier will bill.",
    to: "To holds the logical destination. The to-tag appears once a dialog exists. Before that, To often has no tag.",
    "call-id": "Call-ID identifies the dialog on this leg. CUBE and other B2BUAs mint a new one. Match each leg on its own.",
    cseq: "CSeq is a method plus a sequence. A re-INVITE or BYE advances it. ACK for a 200 uses the INVITE's CSeq number.",
    contact: "Contact is where this UA wants the next request sent. It is the target-refresh address, not the To URI.",
    "record-route": "Record-Route asks to stay on the path for later requests. Route then carries that path in reverse.",
    route: "Route is the path this request must follow. It is how a proxy stays in the dialog after Record-Route.",
    "max-forwards": "Max-Forwards counts hops. Zero becomes 483. It is the SIP loop brake.",
    allow: "Allow lists methods this UA claims to support. It is a hint, not a guarantee the next request will succeed.",
    supported: "Supported names extensions the UA can do, such as 100rel or timer. Require is the demand, Supported is the offer.",
    require: "Require demands an extension. If the other side cannot do it, expect 420 Bad Extension.",
    "content-type": "Content-Type says what the body is. An INVITE that offers media uses application/sdp.",
    "content-length": "Content-Length is the body size. A mismatch means you are not looking at a complete message.",
    "session-expires": "Session-Expires is the session timer. A 422 says the interval was too small.",
    "min-se": "Min-SE is the shortest session interval this UA will accept.",
    reason: "Reason explains a BYE or a failure in a short token. Read it before you accept a human's story of who hung up.",
    "retry-after": "Retry-After tells you when to try again. A 503 without a plan becomes a retry storm.",
    rseq: "RSeq numbers a reliable provisional response. PRACK acknowledges it.",
    rack: "RAck acknowledges a specific RSeq. That is the 100rel handshake.",
    "refer-to": "Refer-To is the target of a REFER. Blind and consult transfers both use it, at different moments.",
    "referred-by": "Referred-By names who asked for the transfer. It is identity context, not the media path.",
    replaces: "Replaces names the dialog a new INVITE should take over. Consult transfer and pickup use this idea.",
    "p-asserted-identity": "P-Asserted-Identity is a trusted caller's identity inside a trusted network. It is not a substitute for your own authentication.",
    privacy: "Privacy says which identity fields to withhold. Asserting an identity and then leaking it in From is a policy miss.",
    diversion: "Diversion records a forward. It helps you see that the number you dialed is not the device that answered.",
    expires: "Expires limits a registration or an INVITE. A phone that vanishes may simply have failed to refresh.",
    event: "Event names a subscription, such as message-summary for MWI. It is not the phone call itself.",
    authorization: "Authorization carries the digest response after a 401. A repeated 401 means the challenge is still failing.",
    "www-authenticate": "WWW-Authenticate is the 401 challenge from a UAS. 407 uses Proxy-Authenticate instead.",
    "proxy-authorization": "Proxy-Authorization answers a 407. The proxy, not the phone, issued that challenge.",
    "user-agent": "User-Agent is a product hint. Do not treat it as the dial plan or the codec.",
    server: "Server is the responding product's hint, the same kind of clue as User-Agent.",
    "geolocation": "Geolocation points at a location document. The header's presence is not proof the civic address is right."
  };

  var SIP_CODES = {
    "100": "Trying. The next hop has the request. The phone is not necessarily ringing.",
    "180": "Ringing. Alerting has started. This is still signaling.",
    "183": "Session Progress. Early media may be present. Silence here is often RTP, not a missing 180.",
    "200": "OK. A final success. The ACK still has to complete an INVITE transaction.",
    "202": "Accepted. Often the REFER was accepted for later processing, not that the transfer target answered.",
    "401": "Unauthorized. The UAS wants digest credentials.",
    "403": "Forbidden. Authenticated or not, policy said no.",
    "404": "Not found. This hop has no destination for that URI. Check the pattern or dial-peer on this hop.",
    "407": "Proxy Authentication Required. A proxy, not the final device, wants credentials.",
    "408": "Request Timeout. The transaction timed out. Find which hop stopped answering.",
    "480": "Temporarily Unavailable. The target exists but cannot take the call right now.",
    "486": "Busy Here. Busy at this endpoint. A hunt may still try another member.",
    "487": "Request Terminated. The INVITE ended because of a CANCEL or a similar abort. The CANCEL worked.",
    "488": "Not Acceptable Here. Often the SDP: codec, encryption, or media direction.",
    "491": "Request Pending. Glare. Both sides sent a request at once. Back off and retry.",
    "500": "Server Internal Error. This hop failed while processing. It is not the same as a 404.",
    "503": "Service Unavailable. Capacity, maintenance, or policy. OPTIONS can still be green.",
    "603": "Decline. The target refused the call."
  };

  var PRESETS = {
    invite: "INVITE sip:2008@cu.example SIP/2.0\nVia: SIP/2.0/TLS phone-a.example;branch=z9hG4bKlab1\nFrom: \"Phone A\" <sip:2001@cu.example>;tag=froma\nTo: <sip:2008@cu.example>\nCall-ID: lab-invite-1@phone-a.example\nCSeq: 1 INVITE\nContact: <sip:2001@phone-a.example>\nMax-Forwards: 70\nContent-Type: application/sdp\nContent-Length: 128\n\nv=0\no=- 1 1 IN IP4 10.1.1.21\ns=-\nc=IN IP4 10.1.1.21\nt=0 0\nm=audio 4000 RTP/AVP 0\na=rtpmap:0 PCMU/8000\na=ptime:20\na=sendrecv\n",
    ringing: "SIP/2.0 180 Ringing\nVia: SIP/2.0/TLS phone-a.example;branch=z9hG4bKlab1\nFrom: \"Phone A\" <sip:2001@cu.example>;tag=froma\nTo: <sip:2008@cu.example>;tag=tob\nCall-ID: lab-invite-1@phone-a.example\nCSeq: 1 INVITE\nContact: <sip:2008@phone-b.example>\nContent-Length: 0\n",
    ok: "SIP/2.0 200 OK\nVia: SIP/2.0/TLS phone-a.example;branch=z9hG4bKlab1\nFrom: \"Phone A\" <sip:2001@cu.example>;tag=froma\nTo: <sip:2008@cu.example>;tag=tob\nCall-ID: lab-invite-1@phone-a.example\nCSeq: 1 INVITE\nContact: <sip:2008@phone-b.example>\nContent-Type: application/sdp\nContent-Length: 96\n\nv=0\no=- 2 1 IN IP4 10.1.8.22\ns=-\nc=IN IP4 10.1.8.22\nt=0 0\nm=audio 4002 RTP/AVP 0\na=rtpmap:0 PCMU/8000\na=sendrecv\n",
    ack: "ACK sip:2008@phone-b.example SIP/2.0\nVia: SIP/2.0/TLS phone-a.example;branch=z9hG4bKack1\nFrom: \"Phone A\" <sip:2001@cu.example>;tag=froma\nTo: <sip:2008@cu.example>;tag=tob\nCall-ID: lab-invite-1@phone-a.example\nCSeq: 1 ACK\nMax-Forwards: 70\nContent-Length: 0\n",
    bye: "BYE sip:2001@phone-a.example SIP/2.0\nVia: SIP/2.0/TLS phone-b.example;branch=z9hG4bKbye1\nFrom: <sip:2008@cu.example>;tag=tob\nTo: \"Phone A\" <sip:2001@cu.example>;tag=froma\nCall-ID: lab-invite-1@phone-a.example\nCSeq: 2 BYE\nReason: SIP;cause=200;text=\"User hangup\"\nMax-Forwards: 70\nContent-Length: 0\n"
  };

  function explainSdp(line) {
    var trimmed = line.trim();
    if (trimmed.indexOf("c=") === 0) return "Connection. This is the address where this side wants media. A private address here is a classic one-way-audio clue.";
    if (trimmed.indexOf("m=") === 0) return "Media line. It names the type, port, transport, and payload types. RTP/AVP is ordinary RTP. RTP/SAVP expects SRTP.";
    if (trimmed.indexOf("a=rtpmap:") === 0) return "rtpmap binds a payload type to a codec and clock rate. Payload 0 is PCMU only because the map says so.";
    if (trimmed.indexOf("a=ptime:") === 0) return "ptime is the packetization interval in milliseconds. It changes bandwidth and serialization, not the codec family by itself.";
    if (trimmed.indexOf("a=sendrecv") === 0) return "sendrecv means this side will send and receive media.";
    if (trimmed.indexOf("a=sendonly") === 0) return "sendonly is a one-way offer. Hold often looks like this, or like inactive.";
    if (trimmed.indexOf("a=recvonly") === 0) return "recvonly means this side will only receive.";
    if (trimmed.indexOf("a=inactive") === 0) return "inactive pauses media in both directions. Hold and some resumes use it.";
    if (trimmed.indexOf("a=crypto:") === 0 || trimmed.indexOf("a=fingerprint:") === 0) return "This line carries keying material for SRTP. It does not encrypt the SIP headers.";
    if (trimmed.indexOf("v=") === 0 || trimmed.indexOf("o=") === 0 || trimmed.indexOf("s=") === 0 || trimmed.indexOf("t=") === 0) return "Session-level SDP. The address that matters for audio is still the c= line and the m= port.";
    return "";
  }

  function explainMessage(raw) {
    var text = String(raw || "").replace(/\r/g, "");
    var chunks = text.split(/\n\s*\n/);
    var head = chunks[0] || "";
    var body = chunks.slice(1).join("\n");
    var lines = head.split("\n").filter(function (line) { return line.trim() !== ""; });
    var rows = [];
    if (!lines.length) {
      return [{ name: "Empty", text: "Paste a SIP start line and headers, or choose a sample." }];
    }
    var start = lines[0].trim();
    var status = start.match(/^SIP\/2\.0\s+(\d{3})/i);
    var request = start.match(/^([A-Z]+)\s+\S+\s+SIP\/2\.0/i);
    if (status) {
      rows.push({ name: status[1], text: SIP_CODES[status[1]] || "A SIP response. This teaching set does not have a sentence for that code yet. Class still matters: 1xx provisional, 2xx success, 3xx redirect, 4xx this request, 5xx this server, 6xx global." });
    } else if (request) {
      rows.push({ name: request[1].toUpperCase(), text: "Request line. The method is what this message asks. The URI is the request target for this hop, which may differ from the To header." });
    } else {
      rows.push({ name: "Start line", text: "This does not look like a SIP request or status line. The teaching decoder expects INVITE sip:... SIP/2.0 or SIP/2.0 180 Ringing." });
    }
    lines.slice(1).forEach(function (line) {
      var cut = line.indexOf(":");
      if (cut < 1) {
        rows.push({ name: line.slice(0, 24), text: "Not a header in this teaching set. Headers look like Name: value." });
        return;
      }
      var name = line.slice(0, cut).trim();
      var key = name.toLowerCase();
      rows.push({ name: name, text: SIP_HEADERS[key] || "Not in the teaching set. Do not invent a meaning for a header this lab does not define." });
    });
    body.split("\n").forEach(function (line) {
      if (!line.trim()) return;
      var note = explainSdp(line);
      if (note) rows.push({ name: line.trim().slice(0, 28), text: note });
    });
    return rows;
  }

  function sipdec(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> A header is a job, not decoration. Paste a message or press a header. This lab explains the teaching set only.</p>' +
      '<div class="uc-app-toolbar" id="ucSipPresets"></div>' +
      '<div class="uc-app-field"><label for="ucSipIn">SIP message</label><textarea id="ucSipIn" rows="8" spellcheck="false"></textarea></div>' +
      '<div class="uc-app-toolbar"><button type="button" class="uc-app-btn primary" id="ucSipGo">Explain message</button></div>' +
      '<p class="uc-app-kicker">Or click one header</p>' +
      '<div class="uc-app-toolbar" id="ucSipHeads"></div>' +
      '<div id="ucSipOut" class="uc-app-stack" aria-live="polite"></div>';
    var presets = root.querySelector("#ucSipPresets");
    Object.keys(PRESETS).forEach(function (key) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "uc-app-tab";
      btn.textContent = key.toUpperCase();
      btn.addEventListener("click", function () {
        root.querySelector("#ucSipIn").value = PRESETS[key];
        paint(explainMessage(PRESETS[key]));
        succeed("sipdec");
      });
      presets.appendChild(btn);
    });
    var heads = root.querySelector("#ucSipHeads");
    Object.keys(SIP_HEADERS).forEach(function (key) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "uc-app-tab";
      btn.textContent = key;
      btn.addEventListener("click", function () {
        paint([{ name: key, text: SIP_HEADERS[key] }]);
        succeed("sipdec");
      });
      heads.appendChild(btn);
    });
    root.querySelector("#ucSipIn").value = PRESETS.invite;
    root.querySelector("#ucSipGo").addEventListener("click", function () {
      paint(explainMessage(root.querySelector("#ucSipIn").value));
      succeed("sipdec");
    });
    function paint(rows) {
      root.querySelector("#ucSipOut").innerHTML = rows.map(function (row) {
        return '<article class="uc-app-cardlet"><b>' + esc(row.name) + "</b><p>" + esc(row.text) + "</p></article>";
      }).join("");
    }
  }

  function codec(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> G.711 is 64 kbit/s of payload. On the wire it is more, because of RTP, UDP, IP, and the layer-2 header. This is the same teaching formula as the campus bandwidth chart.</p>' +
      '<div class="uc-app-split">' +
        '<div class="uc-app-field"><label for="ucCodec">Codec</label><select id="ucCodec"><option value="64000">G.711 (64 kbit/s payload)</option><option value="8000">G.729A (8 kbit/s payload)</option><option value="64000">G.722 (64 kbit/s payload)</option></select></div>' +
        '<div class="uc-app-field"><label for="ucPtime">Packetization</label><select id="ucPtime"><option>10</option><option selected>20</option><option>30</option><option>40</option></select></div>' +
        '<div class="uc-app-field"><label for="ucL2">Layer-2 header, bytes</label><select id="ucL2"><option value="0">0, layer 3 only</option><option value="18" selected>18, Ethernet teaching overhead</option></select></div>' +
        '<div class="uc-app-field"><label for="ucCalls">Simultaneous calls</label><input id="ucCalls" type="number" min="1" max="500" value="12"/></div>' +
        '<div class="uc-app-field"><label for="ucBudget">Link budget, kbit/s</label><input id="ucBudget" type="number" min="64" max="1000000" value="1000"/></div>' +
      '</div>' +
      '<button type="button" class="uc-app-btn primary" id="ucCodecGo">Calculate</button>' +
      '<p class="uc-app-status" id="ucCodecOut" aria-live="polite">G.711 at 20 ms with an 18-byte layer-2 header is about 87.2 kbit/s per call.</p>';
    function run() {
      var bps = Number(root.querySelector("#ucCodec").value);
      var ptime = Number(root.querySelector("#ucPtime").value);
      var l2 = Number(root.querySelector("#ucL2").value);
      var calls = Math.max(1, Number(root.querySelector("#ucCalls").value) || 1);
      var budget = Math.max(1, Number(root.querySelector("#ucBudget").value) || 1);
      var one = kbps(bps, ptime, l2);
      var total = one * calls;
      var fit = total <= budget;
      var out = root.querySelector("#ucCodecOut");
      out.className = "uc-app-status " + (fit ? "is-ok" : "is-bad");
      out.textContent = "One call is " + one.toFixed(1) + " kbit/s. " + calls + " calls are " + total.toFixed(1) +
        " kbit/s against a " + budget + " kbit/s budget. " +
        (fit ? "The teaching budget can hold this many calls." : "The teaching budget is short. Fewer calls, a narrower codec, or a larger link.") +
        " Bandwidth is not the one-way delay budget. This campus still plans delay against 150 ms.";
      succeed("codec");
    }
    root.querySelector("#ucCodecGo").addEventListener("click", run);
  }

  function jitter(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> Jitter is variation in arrival. Loss is a missing sequence number. A jitter buffer hides variation by adding delay. This canvas is a teaching model, not a MOS score.</p>' +
      '<div class="uc-app-split">' +
        '<div class="uc-app-field"><label for="ucLoss">Loss, percent <output id="ucLossVal">1</output></label><input id="ucLoss" type="range" min="0" max="15" value="1"/></div>' +
        '<div class="uc-app-field"><label for="ucJitter">Jitter, ms <output id="ucJitterVal">8</output></label><input id="ucJitter" type="range" min="0" max="80" value="8"/></div>' +
      '</div>' +
      '<canvas id="ucJitterCanvas" class="uc-app-labcanvas" width="900" height="220" role="img" aria-label="Packet arrival teaching chart"></canvas>' +
      '<p class="uc-app-status" id="ucJitterOut" aria-live="polite"></p>';
    var loss = root.querySelector("#ucLoss");
    var jit = root.querySelector("#ucJitter");
    function paint() {
      var lossPct = Number(loss.value);
      var jitterMs = Number(jit.value);
      root.querySelector("#ucLossVal").textContent = String(lossPct);
      root.querySelector("#ucJitterVal").textContent = String(jitterMs);
      var canvas = root.querySelector("#ucJitterCanvas");
      var ctx = canvas.getContext("2d");
      var w = canvas.width;
      var h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#0B1220";
      ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = "rgba(248,250,252,.25)";
      ctx.beginPath();
      ctx.moveTo(36, 40);
      ctx.lineTo(36, h - 28);
      ctx.lineTo(w - 16, h - 28);
      ctx.stroke();
      ctx.fillStyle = "#99F6E4";
      ctx.font = "12px ui-sans-serif, system-ui, sans-serif";
      ctx.fillText("expected", 8, 36);
      ctx.fillText("arrival", 8, h - 36);
      var n = 24;
      var seed = lossPct * 17 + jitterMs * 13;
      function rand(i) {
        var x = Math.sin(seed * 12.9898 + i * 78.233) * 43758.5453;
        return x - Math.floor(x);
      }
      for (var i = 0; i < n; i++) {
        var x = 48 + i * ((w - 70) / n);
        var dropped = rand(i) * 100 < lossPct;
        ctx.fillStyle = "rgba(45,212,191,.35)";
        ctx.fillRect(x, 48, 8, 18);
        if (dropped) {
          ctx.strokeStyle = "#FB7185";
          ctx.strokeRect(x, h - 78, 8, 18);
          continue;
        }
        var slip = (rand(i + 40) - 0.5) * 2 * jitterMs;
        var y = h - 78 - Math.max(-30, Math.min(30, slip));
        ctx.fillStyle = slip > 20 || slip < -20 ? "#F5B942" : "#2DD4BF";
        ctx.fillRect(x, y, 8, 18);
      }
      var verdict = "Arrivals are close enough that a small jitter buffer can hide them.";
      if (lossPct >= 5 || jitterMs >= 40) verdict = "Loss or jitter is high enough that listeners will notice. Find the queue or the link before you blame the codec.";
      else if (lossPct > 0 || jitterMs >= 20) verdict = "Some variation is visible. The buffer can absorb a little of it by adding delay.";
      var out = root.querySelector("#ucJitterOut");
      out.className = "uc-app-status " + (lossPct >= 5 || jitterMs >= 40 ? "is-bad" : "is-ok");
      out.textContent = verdict + " Gaps are lost packets. Tall or short arrival marks are jitter around a 20 ms send clock.";
    }
    function onInput() {
      paint();
      succeed("jitter");
    }
    loss.addEventListener("input", onInput);
    jit.addEventListener("input", onInput);
    paint();
  }

  var ROUTE_PATTERNS = [
    { partition: "PT_Internal", pattern: "2008", urgent: false, target: "Phone 2008", kind: "station" },
    { partition: "PT_Internal", pattern: "2XXX", urgent: false, target: "Internal directory numbers", kind: "station" },
    { partition: "PT_Emergency", pattern: "911", urgent: true, target: "Emergency route list", kind: "emergency" },
    { partition: "PT_Emergency", pattern: "9911", urgent: true, target: "Emergency route list", kind: "emergency" },
    { partition: "PT_PSTN", pattern: "9.@", urgent: false, target: "RL_PSTN toward CUBE", kind: "pstn" }
  ];
  var ROUTE_CALLERS = {
    "2001": ["PT_Internal", "PT_Emergency"],
    "2002": ["PT_Internal", "PT_Emergency", "PT_PSTN"],
    "2003": ["PT_PSTN", "PT_Internal", "PT_Emergency"]
  };

  function routeMatches(pattern, digits) {
    if (pattern === "9.@") return /^9\d+$/.test(digits);
    if (pattern.indexOf("X") >= 0) {
      if (pattern.length !== digits.length) return false;
      for (var i = 0; i < pattern.length; i++) {
        if (pattern[i] !== "X" && pattern[i] !== digits[i]) return false;
      }
      return true;
    }
    return pattern === digits;
  }
  function routeScore(pattern) {
    if (pattern === "9.@") return 1;
    if (pattern.indexOf("X") >= 0) return 10 + pattern.replace(/X/g, "").length;
    return 100 + pattern.length;
  }

  function route(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> CUCM searches partitions in calling-search-space order. The first partition that contains a match wins. If 9.@ sits in an earlier partition than 911, emergency digits take the ordinary PSTN route.</p>' +
      '<div class="uc-app-split">' +
        '<div class="uc-app-field"><label for="ucCaller">Calling line</label><select id="ucCaller"><option value="2001">2001, internal and emergency</option><option value="2002">2002, emergency before PSTN</option><option value="2003" selected>2003, PSTN partition first</option></select></div>' +
        '<div class="uc-app-field"><label for="ucDigits">Digits</label><input id="ucDigits" value="911" inputmode="numeric" autocomplete="off"/></div>' +
      '</div>' +
      '<button type="button" class="uc-app-btn primary" id="ucRouteGo">Trace</button>' +
      '<ol id="ucRouteOut" class="uc-app-steps" aria-live="polite"></ol>';
    root.querySelector("#ucRouteGo").addEventListener("click", function () {
      var caller = root.querySelector("#ucCaller").value;
      var digits = String(root.querySelector("#ucDigits").value || "").replace(/\D/g, "");
      var css = ROUTE_CALLERS[caller];
      var lines = [];
      var winner = null;
      if (!digits) {
        lines.push("No digits. Digit analysis has nothing to match.");
      } else if (digits === "9") {
        lines.push("The digit 9 can start 9.@, but that pattern is not urgent. CUCM would wait for more digits or the interdigit timer.");
      } else {
        css.forEach(function (partition) {
          if (winner) {
            lines.push("Did not search " + partition + ". An earlier partition already matched.");
            return;
          }
          var found = ROUTE_PATTERNS.filter(function (item) {
            return item.partition === partition && routeMatches(item.pattern, digits);
          });
          if (!found.length) {
            lines.push("Searched " + partition + ". No pattern matched " + digits + ".");
            return;
          }
          found.sort(function (a, b) { return routeScore(b.pattern) - routeScore(a.pattern); });
          winner = found[0];
          lines.push("Searched " + partition + ". Best match is " + winner.pattern + " to " + winner.target + (winner.urgent ? " (urgent, no interdigit wait)." : "."));
        });
      }
      var verdict;
      if (!winner) verdict = "No route. The line's CSS never saw a matching pattern.";
      else if (digits === "911" && winner.kind !== "emergency") verdict = "911 took " + winner.target + ". The emergency partition was later in the CSS, so it never got a vote. This is the mis-ordered search the lab is here to show.";
      else if (winner.kind === "emergency") verdict = "Emergency pattern won. Callback and location are still separate proof. A route is not a dispatchable address.";
      else verdict = "The call uses " + winner.target + ".";
      root.querySelector("#ucRouteOut").innerHTML = lines.map(function (line) {
        return "<li>" + esc(line) + "</li>";
      }).join("") + '<li><b>' + esc(verdict) + "</b></li>";
      succeed("route");
    });
  }

  function webex(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> Webex Calling still needs a location and an emergency address. Cisco Calling Plan has no local gateway. Premises PSTN does.</p>' +
      '<div class="uc-app-split">' +
        '<div class="uc-app-field"><label for="ucWxLoc">Location name</label><input id="ucWxLoc" value="Site A"/></div>' +
        '<div class="uc-app-field"><label for="ucWxPstn">PSTN</label><select id="ucWxPstn"><option value="plan">Cisco Calling Plan</option><option value="ccp">Cloud Connected PSTN</option><option value="lgw" selected>Premises local gateway</option><option value="di">Dedicated Instance</option></select></div>' +
        '<div class="uc-app-field"><label><input id="ucWxAddr" type="checkbox"/> Validated emergency address on the location</label></div>' +
        '<div class="uc-app-field"><label><input id="ucWxGw" type="checkbox" checked/> Premises gateway is registered</label></div>' +
      '</div>' +
      '<button type="button" class="uc-app-btn primary" id="ucWxGo">Check the design</button>' +
      '<p class="uc-app-status" id="ucWxOut" aria-live="polite"></p>';
    root.querySelector("#ucWxGo").addEventListener("click", function () {
      var mode = root.querySelector("#ucWxPstn").value;
      var addr = root.querySelector("#ucWxAddr").checked;
      var gw = root.querySelector("#ucWxGw").checked;
      var name = root.querySelector("#ucWxLoc").value.trim() || "This location";
      var needsGw = mode === "lgw" || mode === "di";
      var messages = [];
      var ok = true;
      if (!addr) {
        ok = false;
        messages.push(name + " has no validated emergency address. Do not put users there yet.");
      } else {
        messages.push(name + " has an emergency address. Keep testing it on the provider's test procedure, not against a live PSAP.");
      }
      if (mode === "plan") {
        messages.push("Cisco Calling Plan means Cisco is the PSTN. There is no local gateway and there are no customer dial-peers.");
        if (gw) messages.push("A registered gateway does not change Calling Plan. Do not troubleshoot dial-peers you do not have.");
      } else if (mode === "ccp") {
        messages.push("Cloud Connected PSTN means a partner supplies the trunk. You still own the location, the number, and the emergency address.");
      } else if (mode === "lgw") {
        messages.push("A local gateway is your SBC between Webex Calling and the carrier. Signaling to the cloud is not the carrier media path.");
      } else {
        messages.push("Dedicated Instance is call control you still design. PSTN still lands on a gateway. The cloud name does not remove the dial plan.");
      }
      if (needsGw && !gw) {
        ok = false;
        messages.push("This PSTN choice needs a premises border that is up.");
      }
      var out = root.querySelector("#ucWxOut");
      out.className = "uc-app-status " + (ok ? "is-ok" : "is-bad");
      out.textContent = messages.join(" ");
      if (ok) succeed("webex");
    });
  }

  var UCCE_DNS = {
    "8000": { callType: "CT_Sales", script: "Sales_Script", target: "SG_Sales", ready: 4 },
    "8001": { callType: "CT_Support", script: "Support_Script", target: "SG_Support", ready: 0 },
    "8002": null,
    "8003": { callType: "CT_Billing", script: "Billing_Script", target: "PQ_Billing", ready: 2 }
  };

  function ucce(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> Dialed number, call type, script, and skill group or precision queue are different objects. The call type is the report bucket. An empty skill group can still be a queue.</p>' +
      '<div class="uc-app-field"><label for="ucDn">Dialed number</label><select id="ucDn"><option>8000</option><option>8001</option><option>8002</option><option>8003</option></select></div>' +
      '<button type="button" class="uc-app-btn primary" id="ucDnGo">Route</button>' +
      '<ol id="ucDnOut" class="uc-app-steps" aria-live="polite"></ol>';
    root.querySelector("#ucDnGo").addEventListener("click", function () {
      var dn = root.querySelector("#ucDn").value;
      var row = UCCE_DNS[dn];
      var lines;
      if (!row) {
        lines = [
          "Dialed number " + dn + " has no call-type map.",
          "The script you expected does not run.",
          "Fix the dialed-number mapping before you resize the skill group."
        ];
      } else if (row.ready === 0) {
        lines = [
          "Dialed number " + dn + " maps to call type " + row.callType + ".",
          "Script " + row.script + " selects " + row.target + ".",
          "No agent is ready. The contact queues. That is not the same failure as an unmapped number.",
          "CUIC will count this against the call type, which is not the audio path."
        ];
      } else {
        lines = [
          "Dialed number " + dn + " maps to call type " + row.callType + ".",
          "Script " + row.script + " selects " + row.target + ".",
          row.ready + " agents are ready, so the router can reserve one.",
          "The call type remains the report bucket after the agent answers."
        ];
      }
      root.querySelector("#ucDnOut").innerHTML = lines.map(function (line) { return "<li>" + esc(line) + "</li>"; }).join("");
      succeed("ucce");
    });
  }

  var FINESSE = {
    out: { label: "Logged out", next: { login: "notready" } },
    notready: { label: "Not ready", next: { ready: "ready", logout: "out" } },
    ready: { label: "Ready", next: { notready: "notready", logout: "out", reserve: "reserved" } },
    reserved: { label: "Reserved", next: { answer: "talking" } },
    talking: { label: "Talking", next: { hangup: "wrap" } },
    wrap: { label: "Wrap-up", next: { ready: "ready", notready: "notready" } }
  };
  var FINESSE_BUTTONS = [
    ["login", "Log in"],
    ["logout", "Log out"],
    ["ready", "Ready"],
    ["notready", "Not ready"],
    ["reserve", "Incoming reserve"],
    ["answer", "Answer"],
    ["hangup", "Hang up"]
  ];
  var FINESSE_WHY = {
    login: "Login lands in Not ready. The router must not be offered a phone that has not finished sign-in.",
    logout: "Logout is refused while the agent is reserved, talking, or in wrap-up. The contact still exists.",
    ready: "Ready tells the router this agent can be reserved. It does not itself deliver a call.",
    notready: "Not ready keeps the agent out of selection. Use it for a real pause, not as a way to hide a stuck dialog.",
    reserve: "Reserve comes from the router, not from a button the agent should mash. Talking starts only after reserve.",
    answer: "Answer moves Reserved to Talking. A phone that rings with no desktop event is a CTI problem.",
    hangup: "Hang-up from Talking goes to wrap-up. The after-call state is still part of the contact."
  };

  function finesse(root) {
    var state = "out";
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> The router selects on the desktop state it can see. A lamp on the phone is not that state.</p>' +
      '<p class="uc-app-state" id="ucFnState" aria-live="polite"></p>' +
      '<div class="uc-app-toolbar" id="ucFnBtns"></div>' +
      '<p class="uc-app-status" id="ucFnWhy"></p>';
    var bar = root.querySelector("#ucFnBtns");
    FINESSE_BUTTONS.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "uc-app-btn";
      btn.textContent = item[1];
      btn.addEventListener("click", function () { move(item[0]); });
      bar.appendChild(btn);
    });
    function paint(ok, text) {
      root.querySelector("#ucFnState").textContent = "State: " + FINESSE[state].label;
      var why = root.querySelector("#ucFnWhy");
      why.className = "uc-app-status " + (ok ? "is-ok" : "is-bad");
      why.textContent = text;
    }
    function move(action) {
      var from = FINESSE[state];
      if (from.next[action]) {
        state = from.next[action];
        paint(true, FINESSE_WHY[action]);
        if (state === "talking" || state === "wrap") succeed("finesse");
        return;
      }
      paint(false, "That move is not legal from " + from.label + ". " + FINESSE_WHY[action]);
    }
    paint(true, "Start logged out. Log in, go ready, then let the router reserve the agent.");
  }

  var E911_STEPS = [
    ["Discover", "Learn the network location from the jack, access point, subnet, or client. A VPN concentrator is not a civic address."],
    ["Map", "Map that discovery to a dispatchable location: street address plus the floor, room, or suite the jurisdiction expects."],
    ["Callback", "Choose the callback identity, often an ELIN, that reaches the device or a person who can find the caller."],
    ["Route", "Send the call on the emergency route. This is signaling and media, still not proof of the address."],
    ["Notify", "Tell the on-site team. Notification is parallel. It does not replace the public-safety path."],
    ["Prove", "Prove callback and location with the provider's test procedure. A 200 OK proves only that a dialog completed."]
  ];

  function e911(root) {
    var order = [0, 1, 2, 3, 4, 5];
    var cursor = 0;
    var vpn = false;
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> A connected emergency call with the wrong location is a failed emergency call. Put the steps in order.</p>' +
      '<label class="uc-app-check"><input id="ucE911Vpn" type="checkbox"/> Laptop is at home on VPN, while the switch port still says headquarters</label>' +
      '<p id="ucE911Prog" class="uc-app-score" aria-live="polite"></p>' +
      '<div class="uc-app-toolbar" id="ucE911Btns"></div>' +
      '<p class="uc-app-status" id="ucE911Out"></p>';
    var box = root.querySelector("#ucE911Btns");
    order.forEach(function (idx) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "uc-app-btn";
      btn.textContent = E911_STEPS[idx][0];
      btn.addEventListener("click", function () { pick(idx, btn); });
      box.appendChild(btn);
    });
    root.querySelector("#ucE911Vpn").addEventListener("change", function (e) {
      vpn = e.target.checked;
    });
    function progress() {
      root.querySelector("#ucE911Prog").textContent = cursor + " of " + E911_STEPS.length + " steps in order";
    }
    function pick(idx, btn) {
      var out = root.querySelector("#ucE911Out");
      if (idx !== cursor) {
        out.className = "uc-app-status is-bad";
        out.textContent = "Not yet. " + E911_STEPS[cursor][0] + " comes first. " + E911_STEPS[cursor][1];
        return;
      }
      var extra = "";
      if (vpn && idx === 0) extra = " In this fault the discovery says headquarters. Every later step will carry the wrong place unless discovery is fixed.";
      if (vpn && idx === 5) extra = " The 200 OK still does not move the person out of their house.";
      out.className = "uc-app-status is-ok";
      out.textContent = E911_STEPS[idx][1] + extra;
      btn.disabled = true;
      cursor += 1;
      progress();
      if (cursor === E911_STEPS.length) succeed("e911");
    }
    progress();
  }

  function qos(root) {
    var marks = { rtp: "", sip: "", bulk: "" };
    var round = 1;
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> Marking is a label. A priority queue is what the congested link actually does. EF on a FIFO link is cosmetic.</p>' +
      '<div id="ucQosRound"></div>' +
      '<p class="uc-app-status" id="ucQosOut" aria-live="polite"></p>';
    function paint() {
      var host = root.querySelector("#ucQosRound");
      if (round === 1) {
        host.innerHTML =
          '<p>Assign a mark. CS3 is a common enterprise choice for signaling, not the only legal one.</p>' +
          markRow("rtp", "Voice RTP") + markRow("sip", "SIP signaling") + markRow("bulk", "Backup transfer");
        host.querySelectorAll("select").forEach(function (sel) {
          sel.addEventListener("change", function () { marks[sel.getAttribute("data-k")] = sel.value; });
        });
        var go = document.createElement("button");
        go.type = "button";
        go.className = "uc-app-btn primary";
        go.textContent = "Check marks";
        go.addEventListener("click", checkMarks);
        host.appendChild(go);
      } else {
        host.innerHTML =
          '<p>Voice is marked EF. The link is congested. Which treatment makes the mark matter?</p>' +
          '<div class="uc-app-toolbar">' +
            '<button type="button" class="uc-app-btn" data-q="llq">Priority queue, policed</button>' +
            '<button type="button" class="uc-app-btn" data-q="fifo">Single FIFO queue</button>' +
            '<button type="button" class="uc-app-btn" data-q="bulk">Give the backup class more bandwidth</button>' +
          '</div>';
        host.addEventListener("click", function (e) {
          var btn = e.target.closest("[data-q]");
          if (!btn) return;
          var out = root.querySelector("#ucQosOut");
          if (btn.getAttribute("data-q") === "llq") {
            out.className = "uc-app-status is-ok";
            out.textContent = "The priority queue is what forwards voice during congestion. Police it so voice cannot starve everything else. Then prove the mark on the wire, not only in the policy.";
            succeed("qos");
          } else {
            out.className = "uc-app-status is-bad";
            out.textContent = "The packets may say EF and still wait behind a large transfer. Marking without queue placement does not create low latency.";
          }
        });
      }
    }
    function markRow(key, label) {
      return '<div class="uc-app-field"><label>' + label + '</label><select data-k="' + key + '"><option value="">Choose</option><option value="ef">EF / 46</option><option value="cs3">CS3 / 24</option><option value="be">BE / 0</option><option value="af41">AF41 / 34</option></select></div>';
    }
    function checkMarks() {
      var out = root.querySelector("#ucQosOut");
      var good = marks.rtp === "ef" && marks.sip === "cs3" && marks.bulk === "be";
      if (!good) {
        out.className = "uc-app-status is-bad";
        out.textContent = "Voice bearer is the EF candidate. Signaling is often CS3 in enterprise designs. Bulk stays best effort. AF41 is a common video choice, not the backup mark.";
        return;
      }
      out.className = "uc-app-status is-ok";
      out.textContent = "Those marks match the teaching policy. The link still has to honor them.";
      round = 2;
      paint();
    }
    paint();
  }

  var TLS_STEPS = [
    ["ClientHello", "The client starts the TLS flight and offers versions and ciphers."],
    ["ServerHello", "The server chooses the parameters for this teaching flight."],
    ["Certificate", "The server presents a certificate. Trust is a chain and a name, not a padlock icon."],
    ["Key exchange", "The peers establish keys. This lab does not draw a bit-exact TLS 1.3 transcript."],
    ["Finished", "Both sides confirm the handshake. SIP can now ride inside TLS."],
    ["SIP inside TLS", "TLS protects the signaling on this connection. It does not encrypt RTP."],
    ["SRTP", "SRTP protects the audio. Keys come from SDP security descriptions or DTLS-SRTP, which is a separate step from the SIP TLS session."]
  ];

  function srtp(root) {
    var step = 0;
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> TLS on the SIP port and SRTP on the media are different locks. This is a teaching flight, not a packet-exact handshake.</p>' +
      '<ol class="uc-app-steps" id="ucTls"></ol>' +
      '<div class="uc-app-toolbar"><button type="button" class="uc-app-btn primary" id="ucTlsNext">Next flight</button></div>' +
      '<p class="uc-app-status" id="ucTlsOut" aria-live="polite"></p>';
    function paint() {
      root.querySelector("#ucTls").innerHTML = TLS_STEPS.map(function (item, idx) {
        var cls = idx < step ? "is-done" : idx === step ? "is-on" : "";
        return '<li class="' + cls + '"><b>' + esc(item[0]) + "</b> " + esc(item[1]) + "</li>";
      }).join("");
      var out = root.querySelector("#ucTlsOut");
      out.className = "uc-app-status" + (step >= TLS_STEPS.length ? " is-ok" : "");
      out.textContent = step >= TLS_STEPS.length
        ? "Signaling can be encrypted while the audio is still clear, and the reverse is also a misconfiguration. Prove each one."
        : "Step " + (step + 1) + " of " + TLS_STEPS.length + ".";
      if (step >= TLS_STEPS.length) succeed("srtp");
    }
    root.querySelector("#ucTlsNext").addEventListener("click", function () {
      if (reduced()) step = TLS_STEPS.length;
      else if (step < TLS_STEPS.length) step += 1;
      paint();
    });
    if (reduced()) {
      step = TLS_STEPS.length;
    }
    paint();
  }

  function erlang(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> A queueing picture starts from load. A = calls per hour times handle time, divided by 3600. The delay tail below is a teaching formula, not a vendor staffing product.</p>' +
      '<div class="uc-app-split">' +
        '<div class="uc-app-field"><label for="ucErCalls">Calls per hour</label><input id="ucErCalls" type="number" min="1" value="120"/></div>' +
        '<div class="uc-app-field"><label for="ucErAht">Average handle time, seconds</label><input id="ucErAht" type="number" min="10" value="180"/></div>' +
        '<div class="uc-app-field"><label for="ucErTarget">Answer target, seconds</label><input id="ucErTarget" type="number" min="5" value="20"/></div>' +
        '<div class="uc-app-field"><label for="ucErSvc">Service goal, percent</label><input id="ucErSvc" type="number" min="50" max="99" value="80"/></div>' +
      '</div>' +
      '<button type="button" class="uc-app-btn primary" id="ucErGo">Calculate</button>' +
      '<p class="uc-app-status" id="ucErOut" aria-live="polite"></p>';
    root.querySelector("#ucErGo").addEventListener("click", function () {
      var calls = Math.max(1, Number(root.querySelector("#ucErCalls").value) || 1);
      var aht = Math.max(1, Number(root.querySelector("#ucErAht").value) || 1);
      var target = Math.max(1, Number(root.querySelector("#ucErTarget").value) || 1);
      var goal = Math.min(99, Math.max(50, Number(root.querySelector("#ucErSvc").value) || 80)) / 100;
      var offered = calls * aht / 3600;
      var need = Math.ceil(offered) + 1;
      var guard = 0;
      var tail = 1;
      while (guard < 80 && tail > (1 - goal)) {
        tail = erlangC(need, offered) * Math.exp(-(need - offered) * target / aht);
        if (tail <= (1 - goal)) break;
        need += 1;
        guard += 1;
      }
      var out = root.querySelector("#ucErOut");
      out.className = "uc-app-status is-ok";
      out.textContent = "Offered load A is " + offered.toFixed(2) + " erlangs. About " + need +
        " agents meet a teaching goal of " + Math.round(goal * 100) + "% answered within " + target +
        " seconds. Shrinkage, skills, and concurrency are not in this formula. Add them before you publish a schedule.";
      succeed("erlang");
    });
  }

  var FAULTS = [
    {
      title: "Both sides show a 200 OK. The caller hears silence.",
      choices: [
        ["RTP or the address in SDP. Capture both media directions.", true],
        ["Digit analysis failed, so rebuild the CSS.", false],
        ["CUIC stopped, so the audio stopped.", false],
        ["The phone button template is wrong.", false]
      ],
      why: "Signaling already succeeded. The next proof is the media address, port, codec, and whether packets arrive both ways."
    },
    {
      title: "The carrier ladder shows 404. The phone itself is registered.",
      choices: [
        ["The pattern or dial-peer on the hop that sent 404.", true],
        ["A factory reset of every phone.", false],
        ["Finesse wrap-up codes.", false],
        ["The phone's wallpaper.", false]
      ],
      why: "404 is that hop saying it has no destination. Read the request URI on the leg that rejected it."
    },
    {
      title: "The agent phone rings. Finesse stays blank.",
      choices: [
        ["PG, CTI, and the desktop, not the PSTN leg you already proved.", true],
        ["The carrier codec list.", false],
        ["NTP on the public web site.", false],
        ["The queue's greeting WAV.", false]
      ],
      why: "The desktop event is a different path from the INVITE that made the phone ring."
    },
    {
      title: "Users dial 9 and get reorder. Internal extensions work.",
      choices: [
        ["The line CSS cannot see the PSTN partition, or no route pattern matches.", true],
        ["SRTP must be disabled globally.", false],
        ["CUIC needs a new report.", false],
        ["The handset volume.", false]
      ],
      why: "Internal success means registration and the phone are alive. The outside pattern is a different partition and route."
    },
    {
      title: "An emergency call connects, and the dispatch address is the headquarters.",
      choices: [
        ["Location discovery. The 200 OK did not check the civic address.", true],
        ["A new MOH file.", false],
        ["A longer SIP session timer.", false],
        ["More DSCP classes.", false]
      ],
      why: "The dialog completed. The location object that was sent is a separate fact, often a stale port, subnet, or VPN view."
    },
    {
      title: "Voice calls work. Fax calls negotiate then fail.",
      choices: [
        ["The T.38 or fax pass-through switchover, not the user's CSS.", true],
        ["The hunt logout button.", false],
        ["A CSS with only the emergency partition.", false],
        ["Finesse reason codes.", false]
      ],
      why: "Fax often starts as audio and then re-invites into an image codec. That second negotiation can fail while voice never tries it."
    },
    {
      title: "Voice is marked EF and still chops when backups run.",
      choices: [
        ["The queue. EF is not a priority queue by itself.", true],
        ["A new directory number length.", false],
        ["More route filters.", false],
        ["A second Call-ID format.", false]
      ],
      why: "Prove the mark on the wire and prove which queue the congested interface actually served."
    },
    {
      title: "Webex Calling local-gateway calls fail the morning after a certificate expires.",
      choices: [
        ["The TLS certificate on the gateway trunk, before you redraw the dial plan.", true],
        ["A new calling search space for every user.", false],
        ["Disable emergency notification.", false],
        ["Turn off all QoS.", false]
      ],
      why: "An expired certificate stops the handshake. The dial plan did not change overnight. Look at the security failure first."
    }
  ];

  function fault(root) {
    var index = 0;
    function paint() {
      var item = FAULTS[index];
      root.innerHTML =
        '<p class="uc-app-note"><b>Why it matters.</b> Pick the fault you can prove next. A second guess that does not name evidence is not a finding.</p>' +
        '<p class="uc-app-score">Case ' + (index + 1) + " of " + FAULTS.length + "</p>" +
        '<h3 class="uc-app-q">' + esc(item.title) + "</h3>" +
        item.choices.map(function (choice, i) {
          return '<button type="button" class="uc-app-choice" data-i="' + i + '">' + esc(choice[0]) + "</button>";
        }).join("") +
        '<p class="uc-app-status" id="ucFaultOut" aria-live="polite">Choose the first proof.</p>' +
        '<button type="button" class="uc-app-btn" id="ucFaultNext" disabled>Next case</button>';
      root.querySelector("#ucFaultNext").addEventListener("click", function () {
        index = (index + 1) % FAULTS.length;
        paint();
      });
    }
    root.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-i]");
      if (!btn || btn.disabled) return;
      var item = FAULTS[index];
      var pick = Number(btn.getAttribute("data-i"));
      root.querySelectorAll("[data-i]").forEach(function (choice) { choice.disabled = true; });
      var good = !!item.choices[pick][1];
      var out = root.querySelector("#ucFaultOut");
      out.className = "uc-app-status " + (good ? "is-ok" : "is-bad");
      out.textContent = (good ? "That is the fault to prove. " : "That check does not explain this symptom. ") + item.why;
      var next = root.querySelector("#ucFaultNext");
      if (next) next.disabled = false;
      if (good) succeed("fault");
    });
    paint();
  }

  var DIAL_PEERS = [
    { id: "10", dest: "911", pref: 2, target: "Emergency" },
    { id: "20", dest: "9T", pref: 1, target: "Primary PSTN" },
    { id: "30", dest: "9T", pref: 5, target: "Backup PSTN" },
    { id: "40", dest: "9011T", pref: 1, target: "International" }
  ];

  function peerMatch(dest, digits) {
    if (dest.charAt(dest.length - 1) === "T") {
      var prefix = dest.slice(0, -1);
      return digits.indexOf(prefix) === 0 && digits.length > prefix.length;
    }
    return dest === digits;
  }
  function peerLength(dest) {
    return dest.charAt(dest.length - 1) === "T" ? dest.length - 1 : dest.length + 10;
  }

  function dialpeer(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> On a destination pattern, the longest match wins, then the lowest preference. A worse preference on 911 still beats 9T. This is a teaching model of that order, not every IOS incoming-match rule.</p>' +
      '<ul class="uc-app-steps">' + DIAL_PEERS.map(function (peer) {
        return "<li>dial-peer " + peer.id + " destination-pattern " + peer.dest + " preference " + peer.pref + " → " + peer.target + "</li>";
      }).join("") + "</ul>" +
      '<div class="uc-app-field"><label for="ucPeerDigits">Called number</label><input id="ucPeerDigits" value="911"/></div>' +
      '<button type="button" class="uc-app-btn primary" id="ucPeerGo">Match</button>' +
      '<p class="uc-app-status" id="ucPeerOut" aria-live="polite"></p>';
    root.querySelector("#ucPeerGo").addEventListener("click", function () {
      var digits = String(root.querySelector("#ucPeerDigits").value || "").replace(/\D/g, "");
      var hits = DIAL_PEERS.filter(function (peer) { return peerMatch(peer.dest, digits); });
      var out = root.querySelector("#ucPeerOut");
      if (!hits.length) {
        out.className = "uc-app-status is-bad";
        out.textContent = "No destination pattern matched. The call fails at CUBE even if CUCM had a route.";
        succeed("dialpeer");
        return;
      }
      hits.sort(function (a, b) {
        var len = peerLength(b.dest) - peerLength(a.dest);
        if (len) return len;
        return a.pref - b.pref;
      });
      var best = hits[0];
      out.className = "uc-app-status is-ok";
      out.textContent = "Longest match, then preference: dial-peer " + best.id + " (" + best.dest + ", preference " + best.pref + ") sends the call to " + best.target + ".";
      succeed("dialpeer");
    });
  }

  function nat(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> The ladder is a 200 OK. SDP says the audio address is a private address the far side cannot route. Silence follows.</p>' +
      '<h3 class="uc-app-q">What do you change first?</h3>' +
      '<button type="button" class="uc-app-choice" data-ok="1">Anchor media on the SBC and advertise an address the other side can reach.</button>' +
      '<button type="button" class="uc-app-choice" data-ok="0">Add the PSTN partition to the line CSS.</button>' +
      '<button type="button" class="uc-app-choice" data-ok="0">Restart call control. The dialog already completed.</button>' +
      '<button type="button" class="uc-app-choice" data-ok="0">Mark the RTP EF and leave the private address in SDP.</button>' +
      '<p class="uc-app-status" id="ucNatOut" aria-live="polite">The c= line is the clue.</p>';
    root.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-ok]");
      if (!btn) return;
      var out = root.querySelector("#ucNatOut");
      var ok = btn.getAttribute("data-ok") === "1";
      out.className = "uc-app-status " + (ok ? "is-ok" : "is-bad");
      out.textContent = ok
        ? "The far side sends RTP to whatever address SDP named. Make that address reachable. An MTP only helps if the device that terminates media then advertises its own reachable address."
        : "The dialog is already up, so CSS, a restart, and DSCP do not change the address in SDP.";
      if (ok) succeed("nat");
    });
  }

  function record(root) {
    root.innerHTML =
      '<p class="uc-app-note"><b>Why it matters.</b> A recording is a fork of the media, or a desktop capture. It is not the call, and it is not the CUIC row.</p>' +
      '<h3 class="uc-app-q">You must keep the PSTN audio even when the agent phone built-in bridge is off. Where does the fork belong?</h3>' +
      '<button type="button" class="uc-app-choice" data-ok="0">Only on the phone built-in bridge.</button>' +
      '<button type="button" class="uc-app-choice" data-ok="1">On the SBC, where the PSTN media is already anchored.</button>' +
      '<button type="button" class="uc-app-choice" data-ok="0">Inside the historical report.</button>' +
      '<button type="button" class="uc-app-choice" data-ok="0">In the wrap-up code the agent selects.</button>' +
      '<p class="uc-app-status" id="ucRecOut" aria-live="polite"></p>';
    root.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-ok]");
      if (!btn) return;
      var ok = btn.getAttribute("data-ok") === "1";
      var out = root.querySelector("#ucRecOut");
      out.className = "uc-app-status " + (ok ? "is-ok" : "is-bad");
      out.textContent = ok
        ? "A network fork at the border still sees the carrier leg when the phone bridge is disabled. CUCM can invoke recording, but the report is not the audio."
        : "The built-in bridge is off in this requirement. A report and a wrap-up code never carried the RTP.";
      if (ok) succeed("record");
    });
  }

  window.UCLabs = {
    sipdec: sipdec,
    codec: codec,
    jitter: jitter,
    route: route,
    webex: webex,
    ucce: ucce,
    finesse: finesse,
    e911: e911,
    qos: qos,
    srtp: srtp,
    erlang: erlang,
    fault: fault,
    dialpeer: dialpeer,
    nat: nat,
    record: record
  };
})();
