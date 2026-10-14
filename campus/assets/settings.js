/* Settings: theme, sound, narration, motion, and type size. Stored in this browser. */
(function () {
  "use strict";

  var KEY = "uc_lab_settings_v21";
  var THEMES = ["light", "dark", "contrast", "signal"];
  var FONTS = ["sm", "md", "lg", "xl"];
  var pending = "";
  var silent = false;

  function defaults() {
    return { theme: "light", sound: true, narration: false, voiceURI: "", rate: 1, motion: "system", font: "md" };
  }

  function load() {
    var prefs = defaults();
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || "{}");
      if (raw && typeof raw === "object") {
        Object.keys(prefs).forEach(function (key) {
          if (raw[key] !== undefined) prefs[key] = raw[key];
        });
      }
    } catch (err) { /* private mode */ }
    if (THEMES.indexOf(prefs.theme) < 0) prefs.theme = "light";
    if (FONTS.indexOf(prefs.font) < 0) prefs.font = "md";
    if (prefs.motion !== "reduce" && prefs.motion !== "allow") prefs.motion = "system";
    prefs.sound = prefs.sound !== false;
    prefs.narration = prefs.narration === true;
    var rate = Number(prefs.rate);
    prefs.rate = rate >= 0.7 && rate <= 1.4 ? Math.round(rate * 10) / 10 : 1;
    prefs.voiceURI = String(prefs.voiceURI || "");
    return prefs;
  }

  function save(prefs) {
    try {
      localStorage.setItem(KEY, JSON.stringify(prefs));
      localStorage.setItem("uc_theme", prefs.theme);
    } catch (err) { /* full or private */ }
  }

  function apply(prefs) {
    var root = document.documentElement;
    root.setAttribute("data-theme", prefs.theme);
    root.setAttribute("data-font", prefs.font);
    if (prefs.motion === "system") root.removeAttribute("data-motion");
    else root.setAttribute("data-motion", prefs.motion);
  }

  function roboticEdge(voice) {
    var name = ((voice && voice.name) || "") + " " + ((voice && voice.voiceURI) || "");
    return /edge/i.test(name) || /microsoft (david|zira|mark)\b/i.test(name);
  }

  function voiceScore(voice) {
    if (!voice || roboticEdge(voice)) return -1;
    var name = (voice.name || "") + " " + (voice.voiceURI || "");
    var score = 1;
    if (/natural|neural|premium|enhanced/i.test(name)) score += 5;
    if (/siri|google|samantha|daniel|karen|moira|serena|allison|ava/i.test(name)) score += 3;
    if ((voice.lang || "").toLowerCase().indexOf("en") === 0) score += 2;
    return score;
  }

  function voices() {
    if (!window.speechSynthesis) return [];
    return window.speechSynthesis.getVoices() || [];
  }

  function bestVoice(list) {
    var winner = null;
    var best = 0;
    list.forEach(function (voice) {
      var score = voiceScore(voice);
      if (score > best) {
        best = score;
        winner = voice;
      }
    });
    return winner;
  }

  function chosenVoice(prefs) {
    var list = voices();
    if (prefs.voiceURI) {
      for (var i = 0; i < list.length; i += 1) {
        if (list[i].voiceURI === prefs.voiceURI) return list[i];
      }
    }
    return bestVoice(list);
  }

  function fillVoices() {
    var select = document.getElementById("setVoice");
    var note = document.getElementById("setVoiceNote");
    if (!select) return;
    var prefs = load();
    var list = voices();
    var options = '<option value="">Best available voice</option>';
    list.forEach(function (voice) {
      var label = voice.name + (voice.lang ? " (" + voice.lang + ")" : "");
      if (roboticEdge(voice)) label += " — robotic, not the default";
      options += '<option value="' + voice.voiceURI.replace(/"/g, "&quot;") + '">' + label.replace(/</g, "") + "</option>";
    });
    select.innerHTML = options;
    select.value = prefs.voiceURI && list.some(function (voice) { return voice.voiceURI === prefs.voiceURI; }) ? prefs.voiceURI : "";
    if (!note) return;
    if (!window.speechSynthesis) {
      note.textContent = "This browser has no speech synthesis.";
      return;
    }
    if (!list.length) {
      note.textContent = "Waiting for the voice list.";
      return;
    }
    var pick = chosenVoice(prefs);
    note.textContent = pick
      ? "Narration uses " + pick.name + ". Robotic Microsoft Edge voices are listed, and they are not the default."
      : "No natural voice is installed yet. Pick a voice before narration. A robotic Edge voice is not selected for you.";
  }

  function speak(text, force) {
    var prefs = load();
    if (!force && !prefs.narration) return;
    if (!window.speechSynthesis || !text) return;
    var list = voices();
    if (!list.length) {
      pending = text;
      return;
    }
    var voice = chosenVoice(prefs);
    if (!voice) return;
    window.speechSynthesis.cancel();
    var utterance = new SpeechSynthesisUtterance(String(text).replace(/\s+/g, " ").trim().slice(0, 700));
    utterance.rate = prefs.rate;
    utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  }

  function flushPending() {
    if (!pending) return;
    var text = pending;
    pending = "";
    speak(text, false);
  }

  function syncForm() {
    silent = true;
    var prefs = load();
    apply(prefs);
    var theme = document.querySelector('#settingsForm input[name="theme"][value="' + prefs.theme + '"]');
    if (theme) theme.checked = true;
    document.getElementById("setSound").checked = prefs.sound;
    document.getElementById("setNarration").checked = prefs.narration;
    document.getElementById("setRate").value = String(prefs.rate);
    document.getElementById("setRate").setAttribute("aria-valuenow", String(prefs.rate));
    document.getElementById("setRateOut").textContent = prefs.rate.toFixed(1);
    document.getElementById("setMotion").value = prefs.motion;
    document.getElementById("setFont").value = prefs.font;
    fillVoices();
    silent = false;
  }

  function readForm() {
    var selected = document.querySelector('#settingsForm input[name="theme"]:checked');
    return {
      theme: selected ? selected.value : "light",
      sound: document.getElementById("setSound").checked,
      narration: document.getElementById("setNarration").checked,
      voiceURI: document.getElementById("setVoice").value,
      rate: Number(document.getElementById("setRate").value),
      motion: document.getElementById("setMotion").value,
      font: document.getElementById("setFont").value
    };
  }

  function open() {
    syncForm();
    document.getElementById("settings").hidden = false;
    var close = document.getElementById("settingsClose");
    if (close) close.focus();
  }

  function close() {
    document.getElementById("settings").hidden = true;
  }

  function bind() {
    var button = document.getElementById("settingsBtn");
    if (!button || button.dataset.bound === "1") return;
    button.dataset.bound = "1";
    button.addEventListener("click", open);
    document.getElementById("settingsClose").addEventListener("click", close);
    document.getElementById("settings").addEventListener("click", function (event) {
      if (event.target.id === "settings") close();
    });
    document.getElementById("settingsForm").addEventListener("change", function () {
      if (silent) return;
      var prefs = readForm();
      save(prefs);
      apply(prefs);
      if (!prefs.narration && window.speechSynthesis) window.speechSynthesis.cancel();
      fillVoices();
    });
    document.getElementById("setRate").addEventListener("input", function (event) {
      var prefs = readForm();
      prefs.rate = Number(event.target.value);
      document.getElementById("setRateOut").textContent = prefs.rate.toFixed(1);
      event.target.setAttribute("aria-valuenow", String(prefs.rate));
      save(prefs);
    });
    document.getElementById("setRead").addEventListener("click", function () {
      var view = document.getElementById("view");
      var title = document.getElementById("viewTitle");
      var text = ((title && title.textContent) || "") + ". " + ((view && view.innerText) || "");
      speak(text, true);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
    if (window.speechSynthesis) {
      window.speechSynthesis.addEventListener("voiceschanged", function () {
        fillVoices();
        flushPending();
      });
      fillVoices();
    }
    syncForm();
  }

  window.UCSettings = {
    soundEnabled: function () { return load().sound; },
    motionReduce: function () {
      var mode = load().motion;
      if (mode === "reduce") return true;
      if (mode === "allow") return false;
      return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    },
    onRoute: function (title, extra) {
      var text = title || "";
      if (extra) text += ". " + extra;
      speak(text, false);
    },
    stop: function () {
      pending = "";
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    }
  };

  bind();
})();
