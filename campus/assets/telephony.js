/* Dialpad, dial-plan normalization, and call-state tones. WebAudio only. */
(function () {
  "use strict";

  var audioCtx = null;
  var LOW = { "1": 697, "2": 697, "3": 697, "4": 770, "5": 770, "6": 770, "7": 852, "8": 852, "9": 852, "*": 941, "0": 941, "#": 941 };
  var HIGH = { "1": 1209, "2": 1336, "3": 1477, "4": 1209, "5": 1336, "6": 1477, "7": 1209, "8": 1336, "9": 1477, "*": 1209, "0": 1336, "#": 1477 };

  function audio() {
    if (window.UCSettings && window.UCSettings.soundEnabled && !window.UCSettings.soundEnabled()) return null;
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    if (!audioCtx) audioCtx = new AC();
    if (audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }

  function bandwidth(codec) {
    var rate = codec === "G.729" ? 8000 : 64000;
    var ptime = 20;
    var payload = rate * ptime / 8000;
    var l3 = (payload + 40) * 8 * (1000 / ptime) / 1000;
    var eth = (payload + 40 + 18) * 8 * (1000 / ptime) / 1000;
    return { l3: l3, eth: eth };
  }

  function normalize(raw) {
    var trimmed = String(raw || "").trim();
    var compact = trimmed.replace(/[\s().-]/g, "");
    if (!compact) return { kind: "invalid", e164: "", reason: "Nothing dialed yet." };
    if (/^[*#]/.test(compact)) {
      return { kind: "feature", e164: compact, reason: "Feature code. It stays a code. It is not rewritten to E.164." };
    }
    if (compact === "911" || compact === "933" || compact === "112") {
      return { kind: "emergency", e164: compact, reason: "Emergency number. Prove location and on-site notification before you treat this like a normal call." };
    }
    if (/2222$/.test(compact)) {
      return { kind: "busy", e164: compact, reason: "Lab rule: a number ending in 2222 is a busy far end." };
    }
    if (/3333$/.test(compact)) {
      return { kind: "reorder", e164: compact, reason: "Lab rule: a number ending in 3333 is reorder, faster than busy." };
    }
    if (/^\d{3,5}$/.test(compact)) {
      return { kind: "extension", e164: compact, reason: "On-net extension. Digit analysis can stay inside the cluster." };
    }
    if (/^011\d{8,15}$/.test(compact)) {
      return { kind: "international", e164: "+" + compact.slice(3), reason: "011 prefix removed. The lab stores the destination in plus form." };
    }
    if (/^\+\d{8,15}$/.test(compact)) {
      return { kind: "international", e164: compact, reason: "Already plus-form. No prefix rewrite." };
    }
    if (/^1?\d{10}$/.test(compact)) {
      var national = compact.length === 11 ? compact.slice(1) : compact;
      return { kind: "national", e164: "+1" + national, reason: "NANP 10-digit number, with an optional leading 1, normalized to +1." };
    }
    return { kind: "invalid", e164: compact, reason: "This lab dial plan accepts an extension, NANP, 011 international, plus-form, 911, or a feature code." };
  }

  function mount(host, opts) {
    opts = opts || {};
    host.classList.add("dialpad");
    host.innerHTML =
      '<div class="dial-top"><p class="eyebrow">Telephony testbed</p><h2>Place a lab call</h2>' +
      '<p class="muted">Off hook, digits, and hangup drive the tones. 2222 is busy. 3333 is reorder. 911 is the emergency path. Numbers are synthetic.</p></div>' +
      '<div class="dial-grid">' +
      '<div class="handset">' +
      '<p class="dial-state" data-state role="status">On hook</p>' +
      '<p class="dial-digits" data-digits aria-live="polite">Ready</p>' +
      '<div class="keys" role="group" aria-label="Dialpad">' +
      ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"].map(function (key) {
        return '<button type="button" data-key="' + key + '">' + key + "</button>";
      }).join("") +
      "</div>" +
      '<div class="dial-actions">' +
      '<button type="button" class="primary" data-act="call">Call</button>' +
      '<button type="button" data-act="hook">Off hook</button>' +
      '<button type="button" data-act="hang">Hang up</button>' +
      '<button type="button" data-act="clear">Clear</button>' +
      "</div>" +
      '<label class="codec">Codec <select data-codec aria-label="Negotiated codec"><option>G.711</option><option>G.722</option><option>G.729</option></select></label>' +
      '<p class="dial-bw" data-bw></p>' +
      "</div>" +
      '<div class="dial-side">' +
      '<h3>Normalization</h3><p data-plan>Dial a number to see the lab dial plan rewrite it.</p>' +
      '<h3>SIP sketch</h3><ol data-log class="sip-log" aria-live="polite"></ol>' +
      "</div></div>";

    var stateEl = host.querySelector("[data-state]");
    var digitEl = host.querySelector("[data-digits]");
    var planEl = host.querySelector("[data-plan]");
    var logEl = host.querySelector("[data-log]");
    var bwEl = host.querySelector("[data-bw]");
    var codecEl = host.querySelector("[data-codec]");
    var digits = "";
    var mode = "idle";
    var timers = [];
    var nodes = [];

    function stopSound() {
      timers.forEach(function (id) { clearTimeout(id); });
      timers = [];
      nodes.forEach(function (node) {
        try { if (node.stop) node.stop(); } catch (err) { /* already stopped */ }
        try { if (node.disconnect) node.disconnect(); } catch (err2) { /* closed */ }
      });
      nodes = [];
    }

    function hold(freqs, peak) {
      var c = audio();
      if (!c) return;
      var g = c.createGain();
      g.gain.value = peak || 0.04;
      g.connect(c.destination);
      nodes.push(g);
      freqs.forEach(function (freq) {
        var osc = c.createOscillator();
        osc.type = "sine";
        osc.frequency.value = freq;
        osc.connect(g);
        osc.start();
        nodes.push(osc);
      });
    }

    function blip(freqs, ms, peak) {
      var c = audio();
      if (!c) return;
      var t0 = c.currentTime + 0.02;
      var dur = ms / 1000;
      var g = c.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(peak || 0.06, t0 + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + Math.max(0.04, dur));
      g.connect(c.destination);
      nodes.push(g);
      freqs.forEach(function (freq) {
        var osc = c.createOscillator();
        osc.type = "sine";
        osc.frequency.value = freq;
        osc.connect(g);
        osc.start(t0);
        osc.stop(t0 + dur + 0.02);
        nodes.push(osc);
      });
    }

    function pulse(freqs, onMs, offMs, peak) {
      if (mode !== "ringing" && mode !== "busy" && mode !== "reorder") return;
      blip(freqs, onMs, peak);
      var id = setTimeout(function () { pulse(freqs, onMs, offMs, peak); }, onMs + offMs);
      timers.push(id);
    }

    function paintDigits() {
      digitEl.textContent = digits || "—";
    }

    function logLine(text) {
      var item = document.createElement("li");
      item.textContent = text;
      logEl.appendChild(item);
      while (logEl.children.length > 12) logEl.removeChild(logEl.firstChild);
    }

    function showPlan(plan) {
      planEl.textContent = (plan.e164 || plan.kind) + " · " + plan.reason;
    }

    function showBandwidth() {
      var codec = codecEl.value;
      var bw = bandwidth(codec);
      bwEl.textContent = codec + " at 20 ms is " + bw.l3.toFixed(1) + " kbit/s at layer 3 and " + bw.eth.toFixed(1) + " kbit/s with an 18-byte Ethernet header.";
    }

    function setMode(next, label) {
      stopSound();
      mode = next;
      host.dataset.mode = next;
      stateEl.textContent = label;
      if (next === "dialtone") hold([350, 440], 0.04);
      if (next === "ringing") pulse([440, 480], 2000, 4000, 0.05);
      if (next === "busy") pulse([480, 620], 500, 500, 0.05);
      if (next === "reorder") pulse([480, 620], 250, 250, 0.05);
      if (next === "connected") blip([440], 140, 0.04);
    }

    function press(key) {
      if (!LOW[key]) return;
      if (mode === "idle" || mode === "ended") setMode("dialtone", "Dial tone");
      if (mode === "dialtone") setMode("collect", "Collecting digits");
      if (mode === "ringing" || mode === "busy" || mode === "reorder" || mode === "connected") return;
      digits += key;
      paintDigits();
      blip([LOW[key], HIGH[key]], 160, 0.07);
      showPlan(normalize(digits));
    }

    function call() {
      var plan = normalize(digits);
      showPlan(plan);
      if (!digits) {
        setMode("reorder", "Reorder");
        logLine("No digits. Reorder.");
        return;
      }
      logLine("INVITE " + (plan.e164 || digits) + "  (" + plan.kind + ")");
      logLine("100 Trying");
      if (plan.kind === "invalid" || plan.kind === "reorder") {
        setMode("reorder", "Reorder");
        logLine("503 Service Unavailable");
        return;
      }
      if (plan.kind === "busy") {
        setMode("busy", "Busy");
        logLine("486 Busy Here");
        return;
      }
      if (plan.kind === "emergency") {
        setMode("connected", "Emergency path");
        logLine("180 skipped. Emergency route.");
        logLine("200 OK");
        logLine("ACK");
        logLine("RTP " + codecEl.value);
        return;
      }
      setMode("ringing", "Ringback");
      logLine("180 Ringing");
      var wait = setTimeout(function () {
        if (mode !== "ringing") return;
        setMode("connected", "Talking");
        logLine("200 OK SDP " + codecEl.value);
        logLine("ACK");
        logLine("RTP " + codecEl.value + " sendrecv");
      }, 2100);
      timers.push(wait);
    }

    function hang() {
      if (mode === "connected" || mode === "ringing") {
        logLine(mode === "ringing" ? "CANCEL" : "BYE");
        logLine("200 OK");
      }
      digits = "";
      paintDigits();
      showPlan({ e164: "", kind: "idle", reason: "On hook. The dialog is gone." });
      setMode("idle", "On hook");
    }

    host.addEventListener("click", function (event) {
      var keyBtn = event.target.closest("[data-key]");
      if (keyBtn) press(keyBtn.getAttribute("data-key"));
      var act = event.target.closest("[data-act]");
      if (!act) return;
      var name = act.getAttribute("data-act");
      if (name === "call") call();
      if (name === "hook") {
        if (mode === "idle") setMode(digits ? "collect" : "dialtone", digits ? "Collecting digits" : "Dial tone");
      }
      if (name === "hang") hang();
      if (name === "clear") {
        digits = "";
        paintDigits();
        showPlan(normalize(""));
        if (mode === "collect" || mode === "dialtone") setMode("dialtone", "Dial tone");
      }
    });

    host.addEventListener("keydown", function (event) {
      var tag = (event.target.tagName || "").toLowerCase();
      if (tag === "select" || tag === "input" || tag === "textarea") return;
      if (LOW[event.key]) {
        event.preventDefault();
        press(event.key);
      }
    });

    codecEl.addEventListener("change", showBandwidth);
    host.tabIndex = 0;
    showBandwidth();
    showPlan(normalize(""));
    paintDigits();
    return { destroy: function () { stopSound(); host.innerHTML = ""; } };
  }

  window.UCTelephony = { mount: mount, normalize: normalize, bandwidth: bandwidth };
})();
