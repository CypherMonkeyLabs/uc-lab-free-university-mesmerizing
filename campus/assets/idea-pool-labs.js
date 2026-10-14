/* Idea-pool labs. Teaching models only. They do not touch a live system.
   Algorithms follow the source labs. Addresses stay in documentation ranges. */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function done(id, btn) {
    if (window.UCApp && window.UCApp.markLab) window.UCApp.markLab(id);
    if (btn) btn.textContent = "Marked finished on this browser";
  }
  function field(label, control) {
    return '<label class="uc-app-field pool-field"><span>' + label + "</span>" + control + "</label>";
  }

  function digits(root) {
    var presets = {
      "national-to-e164": { dialed: "915551234567", pattern: "9.1XXXXXXXXXX", discard: "predot", prefix: "+", mask: "" },
      "strip-access": { dialed: "95551212", pattern: "9.XXXXXXX", discard: "predot", prefix: "", mask: "" },
      "intl-plus": { dialed: "9011442079460958", pattern: "9011.!", discard: "predot", prefix: "+", mask: "" },
      "four-digit": { dialed: "1402", pattern: "1XXX", discard: "0", prefix: "", mask: "" }
    };
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> A translation pattern matches, then discard and prefix change the called party. A calling-party mask does not.</p>' +
      '<div class="pool-lab-row">' +
      field("Preset", '<select id="poolDPreset"><option value="">Choose</option><option value="national-to-e164">National to +E.164</option><option value="strip-access">Strip access</option><option value="intl-plus">International plus</option><option value="four-digit">Four digit</option></select>') +
      field("Dialed", '<input id="poolDDialed" value="915551234567" inputmode="numeric" autocomplete="off">') +
      field("Pattern", '<input id="poolDPattern" value="9.1XXXXXXXXXX" autocomplete="off">') +
      field("Discard", '<select id="poolDDiscard"><option value="predot">Predot</option><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option></select>') +
      field("Prefix", '<input id="poolDPrefix" value="+" autocomplete="off">') +
      field("Calling mask", '<input id="poolDMask" value="" autocomplete="off" placeholder="optional">') +
      "</div>" +
      '<div id="poolDOut" class="uc-app-status" aria-live="polite"></div>' +
      '<button type="button" class="uc-app-btn" id="poolDDone">Mark this lab finished</button></div>';

    function match(pat, digitsOnly) {
      var pre = pat.indexOf(".");
      var body = pre >= 0 ? pat.slice(pre + 1) : pat;
      var access = pre >= 0 ? pat.slice(0, pre) : "";
      if (access && digitsOnly.slice(0, access.length) !== access) return null;
      var rest = digitsOnly.slice(access.length);
      var i = 0;
      var d = 0;
      while (i < body.length) {
        var c = body[i];
        if (c === "X") {
          if (d >= rest.length || !/\d/.test(rest[d])) return null;
          d += 1; i += 1;
        } else if (c === "!") {
          if (d >= rest.length) return null;
          d = rest.length; i += 1;
        } else if (c === "[") {
          var end = body.indexOf("]", i);
          var cls = body.slice(i + 1, end);
          if (d >= rest.length) return null;
          var ch = rest[d];
          var ok = cls.length === 3 && cls[1] === "-" ? (ch >= cls[0] && ch <= cls[2]) : cls.indexOf(ch) >= 0;
          if (!ok) return null;
          d += 1; i = end + 1;
        } else {
          if (d >= rest.length || rest[d] !== c) return null;
          d += 1; i += 1;
        }
      }
      if (d !== rest.length) return null;
      return { access: access, rest: rest };
    }

    function run() {
      var raw = root.querySelector("#poolDDialed").value || "";
      var digitsOnly = raw.replace(/[^\d+]/g, "");
      var pat = root.querySelector("#poolDPattern").value.trim();
      var m = match(pat, digitsOnly.replace(/^\+/, ""));
      var out = root.querySelector("#poolDOut");
      if (!m) {
        out.className = "uc-app-status is-bad";
        out.textContent = "Pattern " + pat + " does not match " + digitsOnly + ".";
        return;
      }
      var steps = ["Matched " + pat + ". Access code \"" + (m.access || "(none)") + "\". Digits after the dot: " + m.rest];
      var current = m.access + m.rest;
      var mode = root.querySelector("#poolDDiscard").value;
      if (mode === "predot") {
        current = m.rest;
        steps.push("Discard predot. Called party is now " + current);
      } else {
        var n = parseInt(mode, 10) || 0;
        current = current.slice(n);
        steps.push("Discard " + n + " leading digits. Called party is now " + (current || "(empty)"));
      }
      var prefix = root.querySelector("#poolDPrefix").value;
      if (prefix) {
        current = prefix + current;
        steps.push("Prefix \"" + prefix + "\". Called party is now " + current);
      }
      var calling = root.querySelector("#poolDMask").value.trim();
      out.className = "uc-app-status is-ok";
      out.innerHTML = "<strong>Called party</strong> " + esc(current || "(empty)") +
        "<ol>" + steps.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ol>" +
        (calling ? "<p>Calling party external mask: <strong>" + esc(calling) + "</strong>. This does not change the called number. DNA can disagree with the transformation a trunk actually selects.</p>" : "");
    }

    root.querySelector("#poolDPreset").addEventListener("change", function () {
      var p = presets[this.value];
      if (!p) return;
      root.querySelector("#poolDDialed").value = p.dialed;
      root.querySelector("#poolDPattern").value = p.pattern;
      root.querySelector("#poolDDiscard").value = p.discard;
      root.querySelector("#poolDPrefix").value = p.prefix;
      root.querySelector("#poolDMask").value = p.mask;
      run();
    });
    ["poolDDialed", "poolDPattern", "poolDDiscard", "poolDPrefix", "poolDMask"].forEach(function (id) {
      root.querySelector("#" + id).addEventListener("input", run);
      root.querySelector("#" + id).addEventListener("change", run);
    });
    root.querySelector("#poolDDone").addEventListener("click", function () { done("pool-digits", this); });
    run();
  }

  function cssSim(root) {
    var PARTITIONS = {
      Emergency: [{ pat: "911", dest: "Emergency route list", kind: "route" }, { pat: "9911", dest: "Emergency route list", kind: "route" }],
      Internal: [{ pat: "1XXX", dest: "On-net directory number", kind: "route" }],
      Local: [{ pat: "9XXXXXXX", dest: "Local route list (SLRG)", kind: "route" }],
      National: [{ pat: "91XXXXXXXXXX", dest: "National route list (SLRG)", kind: "route" }],
      International: [{ pat: "9011!", dest: "International route list", kind: "route" }],
      BlockIntl: [{ pat: "9011!", dest: "Block this pattern", kind: "block" }]
    };
    var line = ["BlockIntl"];
    var device = ["Emergency", "Internal", "Local", "National", "International"];

    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> The line CSS is searched before the device CSS. A more specific pattern still wins. Equal matches break toward the earlier partition, so a block in the line CSS beats the same pattern in the device CSS.</p>' +
      field("Dialed", '<input id="poolCssDial" value="911" inputmode="numeric" autocomplete="off">') +
      '<p class="uc-app-note">Click a name to move it: pool, then line CSS, then device CSS, then back to the pool. Drag works too.</p>' +
      '<p><strong>Pool</strong></p><div class="pool-drop" id="poolCssPool" data-box="pool"></div>' +
      '<p><strong>Line CSS</strong></p><div class="pool-drop" id="poolCssLine" data-box="line"></div>' +
      '<p><strong>Device CSS</strong></p><div class="pool-drop" id="poolCssDev" data-box="device"></div>' +
      '<div class="pool-lab-row"><button type="button" class="uc-app-btn" id="poolCssReset">Reset</button></div>' +
      '<div id="poolCssOut" class="uc-app-status" aria-live="polite"></div>' +
      '<button type="button" class="uc-app-btn" id="poolCssDone">Mark this lab finished</button></div>';

    function boxOf(name) {
      if (line.indexOf(name) >= 0) return "line";
      if (device.indexOf(name) >= 0) return "device";
      return "pool";
    }
    function removeName(name) {
      line = line.filter(function (n) { return n !== name; });
      device = device.filter(function (n) { return n !== name; });
    }
    function place(name, target) {
      if (!PARTITIONS[name]) return;
      removeName(name);
      if (target === "line") line.push(name);
      else if (target === "device") device.push(name);
    }
    function paint() {
      ["pool", "line", "device"].forEach(function (which) {
        var host = root.querySelector('[data-box="' + which + '"]');
        var names = which === "line" ? line : which === "device" ? device : Object.keys(PARTITIONS).filter(function (n) { return boxOf(n) === "pool"; });
        host.innerHTML = names.map(function (name) {
          return '<button type="button" class="pool-token" draggable="true" data-name="' + name + '">' + name + "</button>";
        }).join("") || '<span class="uc-app-note">Empty</span>';
      });
      route();
    }
    function matchPattern(pat, digitsOnly) {
      var i = 0;
      var d = 0;
      var literals = 0;
      var wild = 0;
      while (i < pat.length) {
        var c = pat[i];
        if (c === "X") {
          if (d >= digitsOnly.length || !/\d/.test(digitsOnly[d])) return null;
          d += 1; wild += 1; i += 1;
        } else if (c === "!") {
          if (d >= digitsOnly.length) return null;
          wild += digitsOnly.length - d;
          d = digitsOnly.length;
          i += 1;
        } else if (c === "[") {
          var end = pat.indexOf("]", i);
          if (end < 0) return null;
          var cls = pat.slice(i + 1, end);
          if (d >= digitsOnly.length) return null;
          var ch = digitsOnly[d];
          var ok = cls.indexOf("-") > 0 && cls.length === 3 ? ch >= cls[0] && ch <= cls[2] : cls.indexOf(ch) >= 0;
          if (!ok) return null;
          d += 1; wild += 1; i = end + 1;
        } else {
          if (d >= digitsOnly.length || digitsOnly[d] !== c) return null;
          d += 1; literals += 1; i += 1;
        }
      }
      if (d !== digitsOnly.length) return null;
      return { literals: literals, wild: wild };
    }
    function route() {
      var digitsOnly = (root.querySelector("#poolCssDial").value || "").replace(/\D/g, "");
      var seen = {};
      var css = [];
      line.concat(device).forEach(function (n) {
        if (!seen[n]) { seen[n] = true; css.push(n); }
      });
      var hits = [];
      css.forEach(function (part, idx) {
        (PARTITIONS[part] || []).forEach(function (p) {
          var m = matchPattern(p.pat, digitsOnly);
          if (m) hits.push({ part: part, idx: idx, pat: p.pat, dest: p.dest, kind: p.kind, score: m.literals * 100 - m.wild });
        });
      });
      hits.sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        return a.idx - b.idx;
      });
      var out = root.querySelector("#poolCssOut");
      var html = "<p><strong>Effective CSS</strong> (line, then device): " + esc(css.join(" → ") || "empty") + "</p>";
      if (!digitsOnly) {
        out.className = "uc-app-status";
        out.innerHTML = html + "<p>Dial a number. Try 911, 1402, 95551212, 915551234567, or 901144207946.</p>";
        return;
      }
      if (!hits.length) {
        out.className = "uc-app-status is-bad";
        out.innerHTML = html + "<p>No pattern in the effective CSS matches " + esc(digitsOnly) + ". The caller hears reorder.</p>";
        return;
      }
      var win = hits[0];
      out.className = "uc-app-status " + (win.kind === "block" ? "is-bad" : "is-ok");
      html += "<p><strong>" + (win.kind === "block" ? "Blocked" : "Routed") + "</strong> by " + esc(win.pat) + " in " + esc(win.part) + " → " + esc(win.dest) + "</p><ol>";
      hits.forEach(function (h, i) {
        html += "<li>" + (i === 0 ? "Winner: " : "Also matched: ") + esc(h.part) + " / " + esc(h.pat) + " (" + esc(h.dest) + ")</li>";
      });
      html += "</ol><p>Equal matches break toward the partition that appears first.</p>";
      out.innerHTML = html;
    }
    root.addEventListener("click", function (ev) {
      var token = ev.target.closest(".pool-token");
      if (!token || !root.contains(token)) return;
      var name = token.getAttribute("data-name");
      var where = boxOf(name);
      place(name, where === "pool" ? "line" : where === "line" ? "device" : "pool");
      paint();
    });
    root.addEventListener("dragstart", function (ev) {
      var token = ev.target.closest(".pool-token");
      if (!token) return;
      ev.dataTransfer.setData("text/plain", token.getAttribute("data-name"));
    });
    root.querySelectorAll(".pool-drop").forEach(function (box) {
      box.addEventListener("dragover", function (ev) { ev.preventDefault(); });
      box.addEventListener("drop", function (ev) {
        ev.preventDefault();
        place(ev.dataTransfer.getData("text/plain"), box.getAttribute("data-box"));
        paint();
      });
    });
    root.querySelector("#poolCssDial").addEventListener("input", route);
    root.querySelector("#poolCssReset").addEventListener("click", function () {
      line = ["BlockIntl"];
      device = ["Emergency", "Internal", "Local", "National", "International"];
      paint();
    });
    root.querySelector("#poolCssDone").addEventListener("click", function () { done("pool-css", this); });
    paint();
  }

  function cert(root) {
    var LAB_DAY = "2026-10-14";
    var presets = {
      good: { domain: "collab.example.com", san: "exp-e.example.com, collab.example.com", serverSubject: "exp-e.example.com", serverIssuer: "Public Intermediate", serverNotAfter: "2027-06-01", midSubject: "Public Intermediate", midIssuer: "Public Root", midNotAfter: "2030-01-01", rootSubject: "Public Root", rootIssuer: "Public Root", rootNotAfter: "2035-01-01", facing: "public" },
      expired: { domain: "collab.example.com", san: "exp-e.example.com, collab.example.com", serverSubject: "exp-e.example.com", serverIssuer: "Public Intermediate", serverNotAfter: "2025-01-01", midSubject: "Public Intermediate", midIssuer: "Public Root", midNotAfter: "2030-01-01", rootSubject: "Public Root", rootIssuer: "Public Root", rootNotAfter: "2035-01-01", facing: "public" },
      "missing-san": { domain: "collab.example.com", san: "exp-e.example.com", serverSubject: "exp-e.example.com", serverIssuer: "Public Intermediate", serverNotAfter: "2027-06-01", midSubject: "Public Intermediate", midIssuer: "Public Root", midNotAfter: "2030-01-01", rootSubject: "Public Root", rootIssuer: "Public Root", rootNotAfter: "2035-01-01", facing: "public" },
      "broken-chain": { domain: "collab.example.com", san: "exp-e.example.com, collab.example.com", serverSubject: "exp-e.example.com", serverIssuer: "Some Other CA", serverNotAfter: "2027-06-01", midSubject: "Public Intermediate", midIssuer: "Public Root", midNotAfter: "2030-01-01", rootSubject: "Public Root", rootIssuer: "Public Root", rootNotAfter: "2035-01-01", facing: "public" },
      "private-on-edge": { domain: "collab.example.com", san: "exp-e.example.com, collab.example.com, ucm.local", serverSubject: "exp-e.example.com", serverIssuer: "Lab Private CA", serverNotAfter: "2027-06-01", midSubject: "Lab Private CA", midIssuer: "Lab Private CA", midNotAfter: "2030-01-01", rootSubject: "Lab Private CA", rootIssuer: "Lab Private CA", rootNotAfter: "2035-01-01", facing: "public" }
    };
    var keys = ["domain", "san", "serverSubject", "serverIssuer", "serverNotAfter", "midSubject", "midIssuer", "midNotAfter", "rootSubject", "rootIssuer", "rootNotAfter"];
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> Expressway-E faces the public internet. This checker looks at names, dates against ' + LAB_DAY + ', and issuer links. It does not validate signatures.</p>' +
      field("Preset", '<select id="poolCertPreset"><option value="good">Good chain</option><option value="expired">Expired</option><option value="missing-san">Missing SAN</option><option value="broken-chain">Broken chain</option><option value="private-on-edge">Private CA on the edge</option></select>') +
      '<div class="pool-lab-row">' + keys.map(function (k) {
        return field(k, '<input id="poolCert-' + k + '" autocomplete="off">');
      }).join("") + field("Facing", '<select id="poolCert-facing"><option value="public">public</option><option value="internal">internal</option></select>') + "</div>" +
      '<button type="button" class="uc-app-btn" id="poolCertCheck">Check</button>' +
      '<div id="poolCertOut" class="uc-app-status" aria-live="polite"></div>' +
      '<button type="button" class="uc-app-btn" id="poolCertDone">Mark this lab finished</button></div>';

    function val(id) { return root.querySelector("#poolCert-" + id).value.trim(); }
    function apply(p) {
      Object.keys(p).forEach(function (k) { root.querySelector("#poolCert-" + k).value = p[k]; });
      check();
    }
    function check() {
      var issues = [];
      var notes = [];
      var san = val("san").split(",").map(function (s) { return s.trim().toLowerCase(); }).filter(Boolean);
      var domain = val("domain").toLowerCase();
      if (san.indexOf(domain) < 0) issues.push("SAN list does not contain the collab-edge discovery domain " + domain + ".");
      if (san.some(function (s) { return s.endsWith(".local"); })) issues.push("A .local name is on the public certificate. Expressway-E does not need private names.");
      if (val("serverNotAfter") < LAB_DAY) issues.push("Server certificate notAfter " + val("serverNotAfter") + " is before the lab date " + LAB_DAY + ".");
      if (val("midNotAfter") < LAB_DAY) issues.push("Intermediate notAfter " + val("midNotAfter") + " is before " + LAB_DAY + ".");
      if (val("rootNotAfter") < LAB_DAY) issues.push("Root notAfter " + val("rootNotAfter") + " is before " + LAB_DAY + ".");
      if (val("serverIssuer") !== val("midSubject")) issues.push("Server issuer \"" + val("serverIssuer") + "\" does not match intermediate subject \"" + val("midSubject") + "\".");
      if (val("midIssuer") !== val("rootSubject")) issues.push("Intermediate issuer \"" + val("midIssuer") + "\" does not match root subject \"" + val("rootSubject") + "\".");
      if (val("rootSubject") !== val("rootIssuer")) issues.push("Root is not self-signed (subject and issuer differ).");
      if (val("facing") === "public" && /private|lab /i.test(val("serverIssuer") + val("rootSubject"))) {
        issues.push("A private CA is presented on a public-facing Expressway-E. Outside clients will not trust it.");
      }
      if (!issues.length) notes.push("Chain links, dates against " + LAB_DAY + ", and the discovery domain in the SAN all pass this checker.");
      notes.push("This checker does not validate signatures. It checks the names, dates, and links you typed.");
      var box = root.querySelector("#poolCertOut");
      box.className = "uc-app-status " + (issues.length ? "is-bad" : "is-ok");
      box.innerHTML = (issues.length ? "<strong>Fail</strong><ul>" + issues.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</ul>" : "<strong>Pass</strong>") +
        "<p>" + notes.map(esc).join(" ") + "</p>";
    }
    root.querySelector("#poolCertPreset").addEventListener("change", function () {
      if (presets[this.value]) apply(presets[this.value]);
    });
    root.querySelector("#poolCertCheck").addEventListener("click", check);
    root.querySelector("#poolCertDone").addEventListener("click", function () { done("pool-cert", this); });
    apply(presets.good);
  }

  function codecBw(root) {
    var table = {
      "G.711": { payload: 64, cited: true },
      "G.722": { payload: 64, cited: true },
      "G.729": { payload: 8, cited: false }
    };
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> Collaboration 14 Preferred Architecture sizes G.711 and G.722 as 64 kbps payload plus 16 kbps IP/UDP. This is not Ethernet overhead and it is not a queue percent.</p>' +
      '<div class="pool-lab-row">' +
      field("Codec", '<select id="poolBwCodec"><option>G.711</option><option>G.722</option><option>G.729</option></select>') +
      field("Audio calls", '<input id="poolBwAudio" type="number" min="0" value="2">') +
      field("Video calls", '<input id="poolBwVideo" type="number" min="0" value="1">') +
      field("Video region kbps", '<input id="poolBwRate" type="number" min="0" value="384">') +
      field("Deduct audio from audio pool", '<input id="poolBwDeduct" type="checkbox" checked>') +
      "</div>" +
      '<div id="poolBwOut" class="uc-app-status" aria-live="polite"></div>' +
      '<button type="button" class="uc-app-btn" id="poolBwDone">Mark this lab finished</button></div>';
    function num(id) {
      var n = parseInt(root.querySelector(id).value, 10);
      return isNaN(n) || n < 0 ? 0 : n;
    }
    function run() {
      var row = table[root.querySelector("#poolBwCodec").value];
      var overhead = 16;
      var perAudio = row.payload + overhead;
      var aCalls = num("#poolBwAudio");
      var vCalls = num("#poolBwVideo");
      var rate = num("#poolBwRate");
      var deduct = root.querySelector("#poolBwDeduct").checked;
      var audioPool = aCalls * perAudio;
      var videoPool = 0;
      if (vCalls > 0) {
        if (deduct) {
          audioPool += vCalls * perAudio;
          videoPool = vCalls * Math.max(0, rate - row.payload);
        } else videoPool = vCalls * rate;
      }
      var cite = row.cited
        ? "G.711 and G.722 use the Collaboration 14 Preferred Architecture figure: 64 + 16 = 80 kbps."
        : "G.729 payload is 8 kbps in that PA narrative. Adding the same 16 kbps IP/UDP overhead gives 24 kbps. Re-check the PA row before you size a link from this cell.";
      var html = "<p><strong>Audio pool</strong> " + audioPool + " kbps. <strong>Video pool</strong> " + videoPool + " kbps.</p><ul>";
      html += "<li>Per audio call: " + row.payload + " kbps payload + " + overhead + " kbps IP/UDP = " + perAudio + " kbps.</li>";
      html += "<li>Audio-only calls: " + aCalls + " × " + perAudio + " = " + (aCalls * perAudio) + " kbps.</li>";
      if (vCalls > 0 && deduct) {
        html += "<li>Video calls with deduct-audio on: each call takes " + perAudio + " kbps from audio and " + Math.max(0, rate - row.payload) + " kbps from video (region " + rate + " minus " + row.payload + " payload).</li>";
        html += "<li>The PA worked example is 384 kbps video and 64 kbps audio: 320 video + 80 audio.</li>";
      } else if (vCalls > 0) {
        html += "<li>Deduct-audio is off. The whole " + rate + " kbps stays in the video pool.</li>";
      }
      html += "</ul><p>" + cite + "</p>";
      var out = root.querySelector("#poolBwOut");
      out.className = "uc-app-status is-ok";
      out.innerHTML = html;
    }
    ["#poolBwCodec", "#poolBwAudio", "#poolBwVideo", "#poolBwRate", "#poolBwDeduct"].forEach(function (id) {
      root.querySelector(id).addEventListener("input", run);
      root.querySelector(id).addEventListener("change", run);
    });
    root.querySelector("#poolBwDone").addEventListener("click", function () { done("pool-codec", this); });
    run();
  }

  function hunt(root) {
    var names = ["1001", "1002", "1003", "1004"];
    var members = [
      { state: "idle", idle: 40 },
      { state: "idle", idle: 10 },
      { state: "busy", idle: 0 },
      { state: "out", idle: 90 }
    ];
    var cursor = 0;
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> Release 15 names four algorithms. The default is Longest Idle Time. Broadcast should not contain shared-line directory numbers.</p>' +
      field("Algorithm", '<select id="poolHAlg"><option value="longest">Longest Idle Time</option><option value="top">Top Down</option><option value="circular">Circular</option><option value="broadcast">Broadcast</option></select>') +
      '<div id="poolHMembers" class="pool-lab-row"></div>' +
      '<svg id="poolHSvg" viewBox="0 0 640 150" role="img" aria-label="Line group members"></svg>' +
      '<div class="pool-lab-row"><button type="button" class="uc-app-btn" id="poolHNext">Offer the next call</button></div>' +
      '<div id="poolHOut" class="uc-app-status" aria-live="polite"></div>' +
      '<button type="button" class="uc-app-btn" id="poolHDone">Mark this lab finished</button></div>';
    var host = root.querySelector("#poolHMembers");
    names.forEach(function (name, i) {
      var wrap = document.createElement("label");
      wrap.className = "uc-app-field pool-field";
      var state = document.createElement("select");
      state.setAttribute("aria-label", name + " state");
      ["idle", "busy", "out"].forEach(function (s) {
        var opt = document.createElement("option");
        opt.value = s;
        opt.textContent = name + " · " + (s === "out" ? "logged out" : s);
        if (s === members[i].state) opt.selected = true;
        state.appendChild(opt);
      });
      var idle = document.createElement("input");
      idle.type = "number";
      idle.min = "0";
      idle.value = String(members[i].idle);
      idle.setAttribute("aria-label", name + " idle seconds");
      state.addEventListener("change", function () { members[i].state = state.value; run(); });
      idle.addEventListener("input", function () { members[i].idle = parseInt(idle.value, 10) || 0; run(); });
      wrap.appendChild(state);
      wrap.appendChild(idle);
      host.appendChild(wrap);
    });
    function eligible(m) { return m.state === "idle"; }
    function offer() {
      var mode = root.querySelector("#poolHAlg").value;
      var chosen = [];
      if (mode === "broadcast") {
        members.forEach(function (m, i) { if (eligible(m)) chosen.push(i); });
      } else if (mode === "top") {
        for (var i = 0; i < members.length; i += 1) {
          if (eligible(members[i])) { chosen.push(i); break; }
        }
      } else if (mode === "longest") {
        var best = -1;
        var bestIdle = -1;
        members.forEach(function (m, i) {
          if (eligible(m) && m.idle > bestIdle) { best = i; bestIdle = m.idle; }
        });
        if (best >= 0) chosen.push(best);
      } else {
        for (var step = 1; step <= members.length; step += 1) {
          var idx = (cursor + step) % members.length;
          if (eligible(members[idx])) { chosen.push(idx); cursor = idx; break; }
        }
      }
      return chosen;
    }
    function run() {
      var chosen = offer();
      var svg = "";
      names.forEach(function (name, i) {
        var on = chosen.indexOf(i) >= 0;
        var x = 8 + i * 158;
        svg += '<rect x="' + x + '" y="16" width="148" height="110" rx="8" fill="' + (on ? "#1a2438" : "#121a2b") + '" stroke="' + (on ? "#f0b429" : "#334155") + '"/>';
        svg += '<text x="' + (x + 12) + '" y="48" fill="#f0b429" font-family="ui-monospace,monospace" font-size="16">' + name + "</text>";
        svg += '<text x="' + (x + 12) + '" y="74" fill="#e7ecf5" font-size="14">' + members[i].state + "</text>";
        svg += '<text x="' + (x + 12) + '" y="100" fill="#93a0b8" font-size="13">' + members[i].idle + "s idle</text>";
      });
      root.querySelector("#poolHSvg").innerHTML = svg;
      var mode = root.querySelector("#poolHAlg").value;
      var note = "";
      if (mode === "longest") note = "Longest Idle Time uses idle members only, longest idle first. The chapter default is this algorithm.";
      if (mode === "top") note = "Top Down starts at the first idle member.";
      if (mode === "circular") note = "In the Release 15 hunt chapter, Circular starts at the (n+1)th member of the line group, where n is the next sequential member who is idle or busy but not down. If n is the last member, it starts at the top. This model keeps a cursor and offers the next idle member after that cursor. Busy and logged-out members are skipped.";
      if (mode === "broadcast") note = "Broadcast offers every idle member at once. The settings note says not to put shared-line directory numbers in a Broadcast group.";
      var who = chosen.map(function (i) { return names[i]; });
      var out = root.querySelector("#poolHOut");
      if (!who.length) {
        out.className = "uc-app-status is-bad";
        out.textContent = "No idle member. A logged-out or busy line group looks like a broken hunt. " + note;
        return;
      }
      out.className = "uc-app-status is-ok";
      out.textContent = "Offered to " + who.join(", ") + ". " + note;
    }
    root.querySelector("#poolHAlg").addEventListener("change", function () { cursor = 0; run(); });
    root.querySelector("#poolHNext").addEventListener("click", run);
    root.querySelector("#poolHDone").addEventListener("click", function () { done("pool-hunt", this); });
    run();
  }

  function routePattern(root) {
    var presets = {
      t2: { dialed: "915551234567", list: "911\n9.1XXXXXXXXXX\n9011.!\n@" },
      e911: { dialed: "911", list: "911\n9!\n@" },
      intl: { dialed: "901144207946", list: "911\n9.1XXXXXXXXXX\n9011.!\n@" },
      nanp: { dialed: "15551234567", list: "1XXXXXXXXXX\n@" }
    };
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> X is one digit. ! is the rest. The dot is a zero-width PreDot. @ stands in for exactly 10 digits, or 1 plus 10 digits, and scores below an explicit pattern. This is not Dialed Number Analyzer, and @ does not expand to the full NANP.</p>' +
      field("Preset", '<select id="poolRpPreset"><option value="">Choose</option><option value="t2">National</option><option value="e911">911</option><option value="intl">International</option><option value="nanp">10-digit</option></select>') +
      field("Dialed", '<input id="poolRpDialed" value="915551234567" autocomplete="off">') +
      field("Patterns, one per line", '<textarea id="poolRpList" rows="5">911\n9.1XXXXXXXXXX\n9011.!\n@</textarea>') +
      '<div id="poolRpOut" class="uc-app-status" aria-live="polite"></div>' +
      '<button type="button" class="uc-app-btn" id="poolRpDone">Mark this lab finished</button></div>';
    function matchOne(pat, digitsOnly) {
      var di = 0;
      var score = 0;
      var predot = -1;
      var i = 0;
      while (i < pat.length) {
        var c = pat[i];
        if (c === ".") { predot = di; score += 2; i += 1; continue; }
        if (c === "X") {
          if (di >= digitsOnly.length || !/\d/.test(digitsOnly[di])) return null;
          di += 1; score += 3; i += 1; continue;
        }
        if (c === "!") {
          if (di >= digitsOnly.length || !/^\d+$/.test(digitsOnly.slice(di))) return null;
          score += 1; di = digitsOnly.length; i += 1; continue;
        }
        if (c === "@") {
          var rest = digitsOnly.slice(di);
          var take = null;
          if (/^\d{10}$/.test(rest)) take = 10;
          else if (/^1\d{10}$/.test(rest)) take = 11;
          if (take === null) return null;
          di += take; score += 1; i += 1; continue;
        }
        if (c === "[") {
          var end = pat.indexOf("]", i);
          if (end < 0 || di >= digitsOnly.length) return null;
          var cls = pat.slice(i + 1, end);
          var ch = digitsOnly[di];
          var ok = cls.length === 3 && cls[1] === "-" ? ch >= cls[0] && ch <= cls[2] : cls.indexOf(ch) >= 0;
          if (!ok) return null;
          di += 1; score += 4; i = end + 1; continue;
        }
        if (di >= digitsOnly.length || digitsOnly[di] !== c) return null;
        di += 1; score += 10; i += 1;
      }
      if (di !== digitsOnly.length) return null;
      return { score: score, predot: predot };
    }
    function run() {
      var digitsOnly = (root.querySelector("#poolRpDialed").value || "").replace(/\s+/g, "");
      var pats = (root.querySelector("#poolRpList").value || "").split(/\n/).map(function (s) { return s.trim(); }).filter(Boolean);
      var out = root.querySelector("#poolRpOut");
      if (!digitsOnly) {
        out.className = "uc-app-status";
        out.textContent = "Type a dialed number. Digits only for this model.";
        return;
      }
      if (!/^\d+$/.test(digitsOnly)) {
        out.className = "uc-app-status is-bad";
        out.textContent = "This model takes digits. Strip punctuation before you paste.";
        return;
      }
      var rows = [];
      var winner = null;
      pats.forEach(function (pat, idx) {
        var m = matchOne(pat, digitsOnly);
        if (!m) {
          rows.push("<tr><td>" + esc(pat) + "</td><td>no</td><td></td><td></td></tr>");
          return;
        }
        var split = m.predot < 0 ? "no dot" : digitsOnly.slice(0, m.predot) + " | " + digitsOnly.slice(m.predot);
        rows.push("<tr><td>" + esc(pat) + "</td><td>yes</td><td>" + m.score + "</td><td>" + esc(split) + "</td></tr>");
        if (!winner || m.score > winner.score) winner = { pat: pat, score: m.score, predot: m.predot, idx: idx };
      });
      var html = '<div class="pool-table-wrap"><table><thead><tr><th>Pattern</th><th>Match</th><th>Score</th><th>PreDot split</th></tr></thead><tbody>' + rows.join("") + "</tbody></table></div>";
      if (!winner) {
        out.className = "uc-app-status is-bad";
        html += "<p>No pattern matched. @ only stands in for 10 digits or 1 plus 10 digits, and only when that is the whole remaining number.</p>";
      } else {
        out.className = "uc-app-status is-ok";
        var note = winner.pat.indexOf("@") >= 0
          ? " @ won only because nothing more specific matched. Real @ expansion is route-filter specific. This lab does not expand it into the NANP."
          : "";
        html += "<p><strong>Winner</strong> " + esc(winner.pat) + " (score " + winner.score + ", listed at position " + (winner.idx + 1) + ")." + esc(note) + "</p>";
        if (winner.predot >= 0) {
          html += "<p>PreDot discards <strong>" + esc(digitsOnly.slice(0, winner.predot)) + "</strong> and keeps <strong>" + esc(digitsOnly.slice(winner.predot) || "(nothing)") + "</strong>.</p>";
        }
      }
      html += "<p>Literals score above X, and X scores above @ and !. Equal scores keep the pattern you typed first.</p>";
      out.innerHTML = html;
    }
    root.querySelector("#poolRpPreset").addEventListener("change", function () {
      var p = presets[this.value];
      if (!p) return;
      root.querySelector("#poolRpDialed").value = p.dialed;
      root.querySelector("#poolRpList").value = p.list;
      run();
    });
    root.querySelector("#poolRpDialed").addEventListener("input", run);
    root.querySelector("#poolRpList").addEventListener("input", run);
    root.querySelector("#poolRpDone").addEventListener("click", function () { done("pool-route", this); });
    run();
  }

  function sipLadder(root) {
    var ACTORS = ["Phone", "CUCM", "CUBE", "ITSP"];
    var presets = {
      "early-offer": [
        ["Phone", "CUCM", "INVITE", true], ["CUCM", "CUBE", "INVITE", true], ["CUBE", "ITSP", "INVITE", true],
        ["ITSP", "CUBE", "100 Trying", false], ["ITSP", "CUBE", "183 Session Progress", true], ["CUBE", "CUCM", "183 Session Progress", true], ["CUCM", "Phone", "183 Session Progress", true],
        ["ITSP", "CUBE", "200 OK", true], ["CUBE", "CUCM", "200 OK", true], ["CUCM", "Phone", "200 OK", true],
        ["Phone", "CUCM", "ACK", false], ["CUCM", "CUBE", "ACK", false], ["CUBE", "ITSP", "ACK", false]
      ],
      "delayed-offer": [
        ["Phone", "CUCM", "INVITE", false], ["CUCM", "CUBE", "INVITE", false], ["CUBE", "ITSP", "INVITE", true],
        ["ITSP", "CUBE", "200 OK", true], ["CUBE", "CUCM", "200 OK", true], ["CUCM", "Phone", "200 OK", true],
        ["Phone", "CUCM", "ACK", true], ["CUCM", "CUBE", "ACK", true], ["CUBE", "ITSP", "ACK", true]
      ],
      "codec-488": [
        ["CUCM", "CUBE", "INVITE", true], ["CUBE", "ITSP", "INVITE", true],
        ["ITSP", "CUBE", "488 Not Acceptable", false], ["CUBE", "CUCM", "488 Not Acceptable", false]
      ],
      "one-way": [
        ["CUCM", "CUBE", "INVITE", true], ["CUBE", "ITSP", "INVITE", true],
        ["ITSP", "CUBE", "200 OK", true], ["CUBE", "CUCM", "200 OK", false], ["CUCM", "CUBE", "ACK", false]
      ]
    };
    var messages = [];
    var actorOpts = ACTORS.map(function (a) { return "<option>" + a + "</option>"; }).join("");
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> Green arrows carry SDP. A 200 toward CUCM without SDP, after an outside offer that had SDP, is a one-way audio suspect. 488 is an SDP reject. An INVITE from CUCM with no SDP, then an early offer from CUBE, is delayed-offer to early-offer, and the ACK must carry the answer.</p>' +
      field("Preset", '<select id="poolSipPreset"><option value="early-offer">Early offer</option><option value="delayed-offer">Delayed offer</option><option value="codec-488">488</option><option value="one-way">Missing answer</option></select>') +
      '<div class="pool-lab-row">' +
      field("From", '<select id="poolSipFrom">' + actorOpts + "</select>") +
      field("To", '<select id="poolSipTo">' + actorOpts + "</select>") +
      field("Label", '<input id="poolSipLabel" value="INVITE" autocomplete="off">') +
      field("SDP", '<input id="poolSipSdp" type="checkbox">') +
      "</div>" +
      '<div class="pool-lab-row"><button type="button" class="uc-app-btn" id="poolSipAdd">Add</button><button type="button" class="uc-app-btn" id="poolSipPop">Remove last</button></div>' +
      '<svg id="poolSipSvg" role="img" aria-label="SIP ladder"></svg>' +
      '<ol id="poolSipList"></ol>' +
      '<p id="poolSipNote" class="uc-app-note"></p>' +
      '<button type="button" class="uc-app-btn" id="poolSipDone">Mark this lab finished</button></div>';
    function load(name) {
      messages = presets[name].map(function (row) {
        return { from: row[0], to: row[1], label: row[2], sdp: row[3] };
      });
      draw();
    }
    function draw() {
      var w = 760;
      var col = 180;
      var top = 46;
      var rowH = 34;
      var h = top + 28 + messages.length * rowH + 16;
      var parts = ['<rect width="' + w + '" height="' + h + '" fill="#0a1020"/>'];
      ACTORS.forEach(function (name, i) {
        var x = 70 + i * col;
        parts.push('<text x="' + x + '" y="28" fill="#e7ecf5" font-size="14" text-anchor="middle">' + name + "</text>");
        parts.push('<line x1="' + x + '" y1="40" x2="' + x + '" y2="' + (h - 12) + '" stroke="#2a3548"/>');
      });
      messages.forEach(function (m, i) {
        var y = top + 16 + i * rowH;
        var x1 = 70 + ACTORS.indexOf(m.from) * col;
        var x2 = 70 + ACTORS.indexOf(m.to) * col;
        var color = m.label.indexOf("488") === 0 || m.label.indexOf("503") === 0 ? "#ff6b8a" : (m.sdp ? "#3dd68c" : "#3dbeff");
        var dir = x2 >= x1 ? 1 : -1;
        parts.push('<line x1="' + x1 + '" y1="' + y + '" x2="' + (x2 - dir * 8) + '" y2="' + y + '" stroke="' + color + '" stroke-width="1.6"/>');
        parts.push('<polygon points="' + x2 + "," + y + " " + (x2 - dir * 8) + "," + (y - 4) + " " + (x2 - dir * 8) + "," + (y + 4) + '" fill="' + color + '"/>');
        var label = (i + 1) + " " + m.label + (m.sdp ? " (SDP)" : "");
        parts.push('<text x="' + ((x1 + x2) / 2) + '" y="' + (y - 6) + '" fill="#c5d0e0" font-size="11" text-anchor="middle">' + esc(label) + "</text>");
      });
      var svg = root.querySelector("#poolSipSvg");
      svg.setAttribute("viewBox", "0 0 " + w + " " + h);
      svg.innerHTML = parts.join("");
      root.querySelector("#poolSipList").innerHTML = messages.map(function (m, i) {
        return "<li>" + (i + 1) + ". " + esc(m.from) + " → " + esc(m.to) + " " + esc(m.label) + (m.sdp ? " +SDP" : "") + "</li>";
      }).join("");
      var note = root.querySelector("#poolSipNote");
      var fromCucm = messages.filter(function (m) { return m.label === "INVITE" && m.from === "CUCM" && m.to === "CUBE"; })[0];
      var invite = messages.filter(function (m) { return m.label === "INVITE" && m.from === "CUBE" && m.to === "ITSP"; })[0];
      var ok = messages.filter(function (m) { return m.label.indexOf("200") === 0 && m.from === "CUBE" && m.to === "CUCM"; })[0];
      if (invite && invite.sdp && ok && !ok.sdp) {
        note.textContent = "The outside offer had SDP and the 200 toward Unified CM does not. That answer never reaches the phone. Suspect one-way or no audio, and read the CUBE SIP profile before you blame the carrier.";
      } else if (messages.some(function (m) { return m.label.indexOf("488") === 0; })) {
        note.textContent = "488 means the SDP was rejected. Compare codec lists on the two legs before you change routing.";
      } else if (fromCucm && !fromCucm.sdp && invite && invite.sdp) {
        note.textContent = "Unified CM's INVITE had no SDP and CUBE offered early toward the provider. That is delayed-offer to early-offer. The ACK from the caller must carry the answer.";
      } else if (messages.some(function (m) { return m.label === "INVITE" && m.sdp; })) {
        note.textContent = "SDP on the INVITE is early offer. If the first SDP is on the 200 and the ACK carries the answer, the call was delayed offer.";
      } else if (messages.length) {
        note.textContent = "No SDP on these messages yet. Add an offer or load a preset. Green arrows carry SDP.";
      } else {
        note.textContent = "Add messages or load a preset. Green arrows carry SDP.";
      }
    }
    root.querySelector("#poolSipAdd").addEventListener("click", function () {
      messages.push({
        from: root.querySelector("#poolSipFrom").value,
        to: root.querySelector("#poolSipTo").value,
        label: root.querySelector("#poolSipLabel").value.trim() || "INVITE",
        sdp: root.querySelector("#poolSipSdp").checked
      });
      draw();
    });
    root.querySelector("#poolSipPop").addEventListener("click", function () { messages.pop(); draw(); });
    root.querySelector("#poolSipPreset").addEventListener("change", function () { if (presets[this.value]) load(this.value); });
    root.querySelector("#poolSipDone").addEventListener("click", function () { done("pool-sip", this); });
    load("early-offer");
  }

  function pcap(root) {
    var PRESETS = {
      mismatch: [
        "INVITE sip:+15551234567@198.51.100.20 SIP/2.0",
        "Via: SIP/2.0/UDP 192.0.2.10:5060;branch=z9hG4bKlab1",
        "From: <sip:+14155550199@192.0.2.10>;tag=labfrom",
        "To: <sip:+15551234567@198.51.100.20>",
        "Call-ID: lab-mismatch@192.0.2.10",
        "CSeq: 1 INVITE",
        "Content-Type: application/sdp",
        "",
        "v=0",
        "o=lab 1 1 IN IP4 192.0.2.10",
        "s=offer",
        "c=IN IP4 192.0.2.10",
        "t=0 0",
        "m=audio 20000 RTP/AVP 0 8",
        "a=rtpmap:0 PCMU/8000",
        "a=rtpmap:8 PCMA/8000",
        "a=sendrecv",
        "",
        "SIP/2.0 200 OK",
        "Via: SIP/2.0/UDP 192.0.2.10:5060;branch=z9hG4bKlab1",
        "From: <sip:+14155550199@192.0.2.10>;tag=labfrom",
        "To: <sip:+15551234567@198.51.100.20>;tag=labto",
        "Call-ID: lab-mismatch@192.0.2.10",
        "CSeq: 1 INVITE",
        "Content-Type: application/sdp",
        "",
        "v=0",
        "o=lab 1 2 IN IP4 198.51.100.20",
        "s=answer",
        "c=IN IP4 198.51.100.20",
        "t=0 0",
        "m=audio 30000 RTP/AVP 18",
        "a=rtpmap:18 G729/8000",
        "a=sendrecv"
      ].join("\n"),
      direction: [
        "INVITE sip:+15551234567@198.51.100.20 SIP/2.0",
        "Via: SIP/2.0/UDP 192.0.2.10:5060;branch=z9hG4bKlab2",
        "From: <sip:+14155550199@192.0.2.10>;tag=dfrom",
        "To: <sip:+15551234567@198.51.100.20>",
        "Call-ID: lab-direction@192.0.2.10",
        "CSeq: 2 INVITE",
        "Content-Type: application/sdp",
        "",
        "v=0",
        "o=lab 2 1 IN IP4 192.0.2.10",
        "s=offer",
        "c=IN IP4 192.0.2.10",
        "t=0 0",
        "m=audio 20000 RTP/AVP 0",
        "a=rtpmap:0 PCMU/8000",
        "a=sendrecv",
        "",
        "SIP/2.0 200 OK",
        "Via: SIP/2.0/UDP 192.0.2.10:5060;branch=z9hG4bKlab2",
        "From: <sip:+14155550199@192.0.2.10>;tag=dfrom",
        "To: <sip:+15551234567@198.51.100.20>;tag=dto",
        "Call-ID: lab-direction@192.0.2.10",
        "CSeq: 2 INVITE",
        "Content-Type: application/sdp",
        "",
        "v=0",
        "o=lab 2 2 IN IP4 198.51.100.20",
        "s=answer",
        "c=IN IP4 0.0.0.0",
        "t=0 0",
        "m=audio 30000 RTP/AVP 0",
        "a=rtpmap:0 PCMU/8000",
        "a=sendonly"
      ].join("\n"),
      reject: [
        "INVITE sip:+15551234567@198.51.100.20 SIP/2.0",
        "Via: SIP/2.0/UDP 192.0.2.10:5060;branch=z9hG4bKlab3",
        "From: <sip:+14155550199@192.0.2.10>;tag=rfrom",
        "To: <sip:+15551234567@198.51.100.20>",
        "Call-ID: lab-488@192.0.2.10",
        "CSeq: 3 INVITE",
        "Content-Type: application/sdp",
        "",
        "v=0",
        "o=lab 3 1 IN IP4 192.0.2.10",
        "s=offer",
        "c=IN IP4 192.0.2.10",
        "t=0 0",
        "m=audio 20000 RTP/AVP 0",
        "a=rtpmap:0 PCMU/8000",
        "a=sendrecv",
        "",
        "SIP/2.0 488 Not Acceptable Here",
        "Via: SIP/2.0/UDP 192.0.2.10:5060;branch=z9hG4bKlab3",
        "From: <sip:+14155550199@192.0.2.10>;tag=rfrom",
        "To: <sip:+15551234567@198.51.100.20>;tag=rto",
        "Call-ID: lab-488@192.0.2.10",
        "CSeq: 3 INVITE",
        "Content-Length: 0"
      ].join("\n")
    };
    var START = /^(INVITE|ACK|BYE|CANCEL|REGISTER|OPTIONS|PRACK|UPDATE|INFO|REFER|NOTIFY|SUBSCRIBE|MESSAGE|SIP\/2\.0)\b/;
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> Paste signaling. The notes look for 488, a 200 without SDP, c=0.0.0.0, an answer codec missing from the offer, and a direction change. Addresses in the presets are documentation examples.</p>' +
      field("Preset", '<select id="poolPcapPreset"><option value="mismatch">Codec mismatch</option><option value="direction">Hold or one-way</option><option value="reject">488</option></select>') +
      '<textarea id="poolPcapIn" rows="10" spellcheck="false"></textarea>' +
      '<button type="button" class="uc-app-btn" id="poolPcapGo">Read</button>' +
      '<div id="poolPcapOut"></div><div id="poolPcapNotes"></div>' +
      '<button type="button" class="uc-app-btn" id="poolPcapDone">Mark this lab finished</button></div>';
    function splitMessages(raw) {
      var lines = raw.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
      var blocks = [];
      var cur = [];
      lines.forEach(function (line) {
        if (START.test(line) && cur.length) {
          blocks.push(cur.join("\n"));
          cur = [line];
        } else cur.push(line);
      });
      if (cur.join("").trim()) blocks.push(cur.join("\n"));
      return blocks;
    }
    function parseOne(block) {
      var parts = block.split(/\n\n/);
      var head = parts[0] || "";
      var body = parts.slice(1).join("\n\n").trim();
      var hlines = head.split("\n");
      var start = (hlines.shift() || "").trim();
      var headers = {};
      hlines.forEach(function (line) {
        var i = line.indexOf(":");
        if (i < 1) return;
        var name = line.slice(0, i).trim().toLowerCase();
        if (!headers[name]) headers[name] = line.slice(i + 1).trim();
      });
      var sdp = { media: [], maps: {}, dir: "", conn: "", present: false };
      if (body && (/^v=0/m.test(body) || /^m=/m.test(body))) {
        sdp.present = true;
        body.split("\n").forEach(function (line) {
          if (line.indexOf("m=") === 0) sdp.media.push(line.trim());
          if (line.indexOf("c=") === 0 && !sdp.conn) sdp.conn = line.trim();
          var map = line.match(/^a=rtpmap:(\d+)\s+(\S+)/);
          if (map) sdp.maps[map[1]] = map[2];
          var dir = line.match(/^a=(sendrecv|sendonly|recvonly|inactive)\s*$/);
          if (dir) sdp.dir = dir[1];
        });
      }
      var kind = "other";
      if (/^INVITE\b/.test(start)) kind = "invite";
      else if (/^SIP\/2\.0\s+200\b/.test(start)) kind = "ok";
      else if (/^SIP\/2\.0\s+18[03]\b/.test(start)) kind = "early";
      else if (/^SIP\/2\.0\s+488\b/.test(start)) kind = "reject";
      return { start: start, headers: headers, sdp: sdp, kind: kind };
    }
    function codecs(sdp) {
      return Object.keys(sdp.maps).map(function (pt) { return sdp.maps[pt].split("/")[0].toUpperCase(); });
    }
    function analyze(messages) {
      var notes = [];
      var offer = null;
      var answer = null;
      messages.forEach(function (msg) {
        if (msg.kind === "invite" && msg.sdp.present && !offer) offer = msg;
        if ((msg.kind === "ok" || msg.kind === "early") && msg.sdp.present && !answer) answer = msg;
        if (msg.kind === "reject") notes.push({ level: "bad", text: "488 Not Acceptable Here. The far end refused the SDP. Compare the codecs on the offer with what that hop allows. This is not a CSS miss." });
        if (msg.kind === "ok" && !msg.sdp.present) notes.push({ level: "bad", text: "A 200 OK has no SDP. If the INVITE was early offer, the answer was stripped. If both sides delayed, the offer never arrived." });
        if (msg.sdp.conn.indexOf("0.0.0.0") !== -1) notes.push({ level: "bad", text: "Connection address 0.0.0.0. That is a hold or a black hole, not a reachable RTP target." });
      });
      if (offer && answer) {
        var offered = codecs(offer.sdp);
        var answered = codecs(answer.sdp);
        var missing = answered.filter(function (c) { return offered.indexOf(c) === -1; });
        if (missing.length) notes.push({ level: "bad", text: "Answer codec " + missing.join(", ") + " was not in the offer (" + (offered.join(", ") || "no rtpmap") + "). One hop changed the codec list." });
        else if (answered.length) notes.push({ level: "ok", text: "Answer codec " + answered.join(", ") + " was in the offer (" + offered.join(", ") + ")." });
        if (offer.sdp.dir && answer.sdp.dir && offer.sdp.dir !== answer.sdp.dir) {
          notes.push({ level: "bad", text: "Direction changed from " + offer.sdp.dir + " on the offer to " + answer.sdp.dir + " on the answer. sendonly or inactive is how one-way audio is negotiated on purpose." });
        }
        if (!answered.length && offer.sdp.present) notes.push({ level: "warn", text: "The answer SDP has an m= line but no a=rtpmap. Payload types alone are ambiguous." });
      } else if (!notes.length) {
        notes.push({ level: "warn", text: "No INVITE-with-SDP paired with a 200 or 183 that carries SDP. Paste both the offer and the answer." });
      }
      return notes;
    }
    function render() {
      var messages = splitMessages(root.querySelector("#poolPcapIn").value).map(parseOne).filter(function (m) { return m.start; });
      var out = root.querySelector("#poolPcapOut");
      var notesEl = root.querySelector("#poolPcapNotes");
      if (!messages.length) {
        out.innerHTML = "<p class='uc-app-note'>No SIP start line found. A block should begin with INVITE or SIP/2.0.</p>";
        notesEl.innerHTML = "";
        return;
      }
      out.innerHTML = messages.map(function (msg, i) {
        var bits = ["<article class='pool-card'><p><strong>" + (i + 1) + ".</strong> " + esc(msg.start) + "</p>"];
        if (msg.headers["call-id"]) bits.push("<p>Call-ID " + esc(msg.headers["call-id"]) + "</p>");
        if (msg.sdp.present) {
          var maps = Object.keys(msg.sdp.maps).map(function (pt) { return pt + " " + msg.sdp.maps[pt]; });
          bits.push("<p>SDP " + esc(msg.sdp.conn || "(none)") + " · " + esc(msg.sdp.media.join(" · ") || "(none)") + "</p>");
          bits.push("<p>rtpmap " + esc(maps.join(", ") || "(none)") + " · " + esc(msg.sdp.dir || "default sendrecv") + "</p>");
        } else bits.push("<p>No SDP body.</p>");
        bits.push("</article>");
        return bits.join("");
      }).join("");
      notesEl.innerHTML = analyze(messages).map(function (n) {
        return '<div class="uc-app-status ' + (n.level === "bad" ? "is-bad" : "is-ok") + '">' + esc(n.text) + "</div>";
      }).join("");
    }
    root.querySelector("#poolPcapGo").addEventListener("click", render);
    root.querySelector("#poolPcapPreset").addEventListener("change", function () {
      if (PRESETS[this.value]) root.querySelector("#poolPcapIn").value = PRESETS[this.value];
      render();
    });
    root.querySelector("#poolPcapDone").addEventListener("click", function () { done("pool-pcap", this); });
    root.querySelector("#poolPcapIn").value = PRESETS.mismatch;
    render();
  }

  function cases(root) {
    var scenes = (window.UC_IDEA_POOL && window.UC_IDEA_POOL.scenarios) || [];
    var current = scenes[0] || null;
    var nodeId = current ? current.start : "";
    root.innerHTML =
      '<div class="pool-lab">' +
      '<p class="uc-app-note"><b>Why it matters.</b> Each choice is a next check. A detour explains why that action does not produce evidence.</p>' +
      field("Case", '<select id="poolCasePick"></select>') +
      '<div id="poolCaseStage"></div><ol id="poolCaseLog"></ol>' +
      '<button type="button" class="uc-app-btn" id="poolCaseDone">Mark this lab finished</button></div>';
    var pick = root.querySelector("#poolCasePick");
    scenes.forEach(function (s, i) {
      var opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = s.title;
      pick.appendChild(opt);
    });
    function draw() {
      var stage = root.querySelector("#poolCaseStage");
      if (!current) {
        stage.textContent = "No cases loaded.";
        return;
      }
      var node = current.nodes[nodeId] || { text: "Missing node.", next: current.start };
      var html = "<h3>" + esc(current.title) + "</h3><p>" + esc(current.blurb) + "</p>";
      if (node.solved) {
        html += '<div class="uc-app-status is-ok">' + esc(node.text) + "</div>";
        if (window.UCApp && window.UCApp.markLab) window.UCApp.markLab("pool-cases");
      } else if (node.choices) {
        html += "<p>" + esc(node.text) + "</p>";
        node.choices.forEach(function (c, idx) {
          html += '<button type="button" class="uc-app-choice" data-i="' + idx + '">' + esc(c.label) + "</button>";
        });
      } else {
        html += '<div class="uc-app-status is-bad">' + esc(node.text) + "</div>";
        html += '<button type="button" class="uc-app-btn" id="poolCaseBack">Return to the last real check</button>';
      }
      stage.innerHTML = html;
      stage.querySelectorAll("[data-i]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var c = node.choices[Number(btn.getAttribute("data-i"))];
          var li = document.createElement("li");
          li.textContent = (c.good ? "Useful: " : "Detour: ") + c.note;
          root.querySelector("#poolCaseLog").appendChild(li);
          nodeId = c.next;
          draw();
        });
      });
      var back = stage.querySelector("#poolCaseBack");
      if (back) back.addEventListener("click", function () { nodeId = node.next || current.start; draw(); });
    }
    pick.addEventListener("change", function () {
      current = scenes[Number(pick.value)];
      nodeId = current.start;
      root.querySelector("#poolCaseLog").innerHTML = "";
      draw();
    });
    root.querySelector("#poolCaseDone").addEventListener("click", function () { done("pool-cases", this); });
    draw();
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest && ev.target.closest(".pool-room .choices button[data-correct]");
    if (!btn) return;
    var box = btn.parentNode;
    if (!box || box.getAttribute("data-answered") === "1") return;
    box.setAttribute("data-answered", "1");
    var ok = btn.getAttribute("data-correct") === "1";
    btn.classList.add(ok ? "good" : "bad");
    if (!ok) {
      var right = box.querySelector('button[data-correct="1"]');
      if (right) right.classList.add("good");
    }
  });

  window.UCLabs = window.UCLabs || {};
  window.UCLabs["pool-css"] = cssSim;
  window.UCLabs["pool-digits"] = digits;
  window.UCLabs["pool-sip"] = sipLadder;
  window.UCLabs["pool-cert"] = cert;
  window.UCLabs["pool-route"] = routePattern;
  window.UCLabs["pool-codec"] = codecBw;
  window.UCLabs["pool-pcap"] = pcap;
  window.UCLabs["pool-hunt"] = hunt;
  window.UCLabs["pool-cases"] = cases;
})();
