/* In-browser tones. Labels say when a clip is a teaching approximation. */
(function () {
  var audioCtx = null;
  var master = null;
  var analyser = null;
  var listeners = [];
  function ctx() {
    if (window.UCSettings && window.UCSettings.soundEnabled && !window.UCSettings.soundEnabled()) return null;
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }
  function masterGain(c) {
    if (!master || master.context !== c) {
      master = c.createGain();
      master.gain.value = 1;
      analyser = c.createAnalyser();
      analyser.fftSize = 256;
      master.connect(analyser);
      analyser.connect(c.destination);
    }
    return master;
  }
  function emit(payload) {
    listeners.forEach(function (fn) {
      try { fn(payload); } catch (e) {}
    });
  }
  function envGain(c, start, dur, peak) {
    var g = c.createGain();
    g.gain.setValueAtTime(0.0001, start);
    g.gain.exponentialRampToValueAtTime(peak, start + 0.015);
    g.gain.exponentialRampToValueAtTime(0.0001, start + Math.max(0.02, dur));
    return g;
  }
  function mix(c, freqs, start, dur, peak) {
    var g = envGain(c, start, dur, peak);
    g.connect(masterGain(c));
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
    if (!c) return;
    var t = c.currentTime + 0.05;
    pattern.forEach(function (seg) {
      if (seg.hz) mix(c, seg.hz, t, seg.ms / 1000, peak || 0.06);
      t += seg.ms / 1000;
    });
  }
  function dtmf(digit) {
    var low = { "1": 697, "2": 697, "3": 697, "4": 770, "5": 770, "6": 770, "7": 852, "8": 852, "9": 852, "*": 941, "0": 941, "#": 941 };
    var high = { "1": 1209, "2": 1336, "3": 1477, "4": 1209, "5": 1336, "6": 1477, "7": 1209, "8": 1336, "9": 1477, "*": 1209, "0": 1336, "#": 1477 };
    return [low[digit], high[digit]];
  }
  function burst(mode) {
    var c = ctx();
    if (!c) return;
    var dur = 1.2;
    var n = Math.floor(c.sampleRate * dur);
    var buf = c.createBuffer(1, n, c.sampleRate);
    var data = buf.getChannelData(0);
    for (var i = 0; i < n; i++) {
      var t = i / c.sampleRate;
      var s = 0.5 * Math.sin(2 * Math.PI * 700 * t) + 0.25 * Math.sin(2 * Math.PI * 1200 * t) + 0.12 * Math.sin(2 * Math.PI * 2600 * t);
      s *= 0.35 * (0.6 + 0.4 * Math.sin(2 * Math.PI * 110 * t));
      if (mode === "mu") {
        var MU = 255;
        var sign = s < 0 ? -1 : 1;
        var ax = Math.min(1, Math.abs(s));
        var comp = sign * Math.log(1 + MU * ax) / Math.log(1 + MU);
        var q = Math.round(comp * 127) / 127;
        s = (q < 0 ? -1 : 1) * (Math.pow(1 + MU, Math.abs(q)) - 1) / MU;
      } else if (mode === "narrow") {
        if (i % 6 !== 0) s = data[Math.max(0, i - 1)];
        s = s * 0.8;
      } else if (mode === "loss") {
        if (Math.floor(t * 20) % 5 === 2) s = 0;
      } else if (mode === "jitter") {
        var slot = Math.floor(t * 12);
        if (slot % 4 === 3) s = 0;
      }
      data[i] = Math.max(-1, Math.min(1, s));
    }
    var src = c.createBufferSource();
    src.buffer = buf;
    src.connect(masterGain(c));
    src.start();
  }
  function tone(hz, ms, peak) {
    playCadence([{ hz: hz, ms: ms }], peak || 0.06);
  }
  function onOff(hz, on, off, times) {
    var p = [];
    for (var i = 0; i < times; i++) {
      p.push({ hz: hz, ms: on });
      p.push({ ms: off });
    }
    playCadence(p, 0.06);
  }

  var CLIPS = [
    { name: "DTMF 5", text: "ITU-T Q.23 digit 5: 770 Hz and 1336 Hz.", run: function () { tone(dtmf("5"), 220); } },
    { name: "DTMF 0", text: "Q.23 digit 0: 941 Hz and 1336 Hz.", run: function () { tone(dtmf("0"), 220); } },
    { name: "DTMF star", text: "Q.23 star: 941 Hz and 1209 Hz.", run: function () { tone(dtmf("*"), 220); } },
    { name: "DTMF pound", text: "Q.23 pound: 941 Hz and 1477 Hz.", run: function () { tone(dtmf("#"), 220); } },
    { name: "DTMF run", text: "Digits 1, 5, 9, 0. Each pair is the Q.23 low and high tone.", run: function () { var p = []; "1590".split("").forEach(function (d) { p.push({ hz: dtmf(d), ms: 150 }); p.push({ ms: 70 }); }); playCadence(p, 0.05); } },
    { name: "NANP dial", text: "North American dial tone: 350 Hz plus 440 Hz.", run: function () { tone([350, 440], 1400, 0.05); } },
    { name: "NANP ringback", text: "440 Hz plus 480 Hz for 2 seconds. The real cadence is 2 s on and 4 s off. This is one on-period.", run: function () { tone([440, 480], 2000, 0.05); } },
    { name: "NANP busy", text: "480 Hz plus 620 Hz, 0.5 s on and 0.5 s off.", run: function () { onOff([480, 620], 500, 500, 3); } },
    { name: "NANP reorder", text: "480 Hz plus 620 Hz, 0.25 s on and 0.25 s off. Faster than busy.", run: function () { onOff([480, 620], 250, 250, 4); } },
    { name: "SIT", text: "North American special information tone, about 914 Hz, then 1371 Hz, then 1777 Hz.", run: function () { playCadence([{ hz: [913.8], ms: 330 }, { hz: [1370.6], ms: 330 }, { hz: [1776.7], ms: 330 }], 0.06); } },
    { name: "UK ringback", text: "400 Hz plus 450 Hz. UK double ring is about 0.4 s, 0.2 s, 0.4 s, then 2 s off. This plays one double ring.", run: function () { playCadence([{ hz: [400, 450], ms: 400 }, { ms: 200 }, { hz: [400, 450], ms: 400 }], 0.05); } },
    { name: "UK busy", text: "400 Hz, about 0.375 s on and 0.375 s off.", run: function () { onOff([400], 375, 375, 4); } },
    { name: "Germany dial", text: "425 Hz continuous, the common ETSI dial tone.", run: function () { tone([425], 1400, 0.05); } },
    { name: "Germany ringback", text: "425 Hz, about 1 s on and 4 s off. This is one on-period.", run: function () { tone([425], 1000, 0.05); } },
    { name: "Germany busy", text: "425 Hz, about 0.48 s on and 0.48 s off.", run: function () { onOff([425], 480, 480, 3); } },
    { name: "France ringback", text: "440 Hz, about 1.5 s on and 3.5 s off. This is one on-period.", run: function () { tone([440], 1500, 0.05); } },
    { name: "Japan ringback", text: "Teaching pair at 400 Hz and 416 Hz. A real Japanese ringback is amplitude-modulated 400 Hz. This is not that modulator.", run: function () { tone([400, 416], 1000, 0.05); } },
    { name: "Australia dial", text: "425 Hz plus 450 Hz, the common Australian dial pair.", run: function () { tone([425, 450], 1400, 0.05); } },
    { name: "Australia ringback", text: "400 Hz plus 450 Hz, one double burst of 0.4 s, 0.2 s, 0.4 s.", run: function () { playCadence([{ hz: [400, 450], ms: 400 }, { ms: 200 }, { hz: [400, 450], ms: 400 }], 0.05); } },
    { name: "Call waiting", text: "A short 440 Hz beep used as a call-waiting teaching tone.", run: function () { tone([440], 200, 0.07); } },
    { name: "Recorder beep", text: "1400 Hz beep, the sort of tone a recording announcement uses. Not a legal consent notice.", run: function () { tone([1400], 280, 0.05); } },
    { name: "Confirmation", text: "Two short 480 Hz notes. A lab confirmation, not a carrier tone plan.", run: function () { onOff([480], 120, 80, 2); } },
    { name: "Wideband vowel", text: "Three formants. The reference before quantization.", run: function () { burst("clean"); } },
    { name: "G.711 mu-law", text: "The same vowel through a mu-law compand and 8-bit quantizer. A teaching model, not a bit-exact codec.", run: function () { burst("mu"); } },
    { name: "Narrowband simulation", text: "Sample-and-hold. Not a G.729 decoder. It shows a thinner path.", run: function () { burst("narrow"); } },
    { name: "Codec A/B", text: "Wideband vowel, a short gap, then the mu-law version. Compare them on headphones.", run: function () { burst("clean"); setTimeout(function () { burst("mu"); }, 1400); } },
    { name: "Mild jitter", text: "A vowel with every fourth slot dropped, like a shallow jitter buffer.", run: function () { burst("jitter"); } },
    { name: "Loss about 1 in 5", text: "The vowel with about one slot in five removed.", run: function () { burst("loss"); } },
    { name: "Heavy jitter gaps", text: "A 440 Hz tone with uneven gaps.", run: function () { var c = ctx(); var t = c.currentTime + 0.05; for (var i = 0; i < 8; i++) { mix(c, [440], t, 0.07, 0.06); t += 0.07 + (i % 3) * 0.09; } } },
    { name: "Severe packet loss", text: "Short 523 Hz tones with two of every five removed.", run: function () { var c = ctx(); var t = c.currentTime + 0.05; for (var i = 0; i < 10; i++) { if (i % 5 > 1) mix(c, [523], t, 0.08, 0.06); t += 0.1; } } },
    { name: "One-way left", text: "Tone panned left when the browser allows it. The other ear is the missing direction.", run: function () { var c = ctx(); var o = c.createOscillator(); var g = c.createGain(); o.frequency.value = 440; g.gain.value = 0.05; o.connect(g); if (c.createStereoPanner) { var p = c.createStereoPanner(); g.connect(p); p.pan.value = -1; p.connect(masterGain(c)); } else g.connect(masterGain(c)); o.start(); o.stop(c.currentTime + 1.1); } },
    { name: "Fax CNG", text: "Calling tone, 1100 Hz. T.30 callers send this.", run: function () { onOff([1100], 500, 400, 2); } },
    { name: "Fax CED", text: "Called tone, 2100 Hz.", run: function () { tone([2100], 900, 0.05); } },
    { name: "Comfort noise", text: "Low noise where silence suppression would insert comfort noise. Not a real CN payload.", run: function () { var c = ctx(); var n = Math.floor(c.sampleRate * 1.1); var b = c.createBuffer(1, n, c.sampleRate); var d = b.getChannelData(0); for (var i = 0; i < n; i++) d[i] = (Math.random() - 0.5) * 0.02; var s = c.createBufferSource(); s.buffer = b; s.connect(masterGain(c)); s.start(); } },
    { name: "Stutter dial", text: "350 plus 440 Hz in short bursts. A lab picture of a message-waiting stutter, not a full cadence spec.", run: function () { playCadence([{ hz: [350, 440], ms: 100 }, { ms: 100 }, { hz: [350, 440], ms: 100 }, { ms: 100 }, { hz: [350, 440], ms: 100 }, { ms: 100 }, { hz: [350, 440], ms: 700 }], 0.05); } }
  ];

  function playIndex(i) {
    var clip = CLIPS[i];
    if (!clip) return;
    try {
      var c = ctx();
      masterGain(c);
      if (master) master.gain.setValueAtTime(1, c.currentTime);
      clip.run();
      if (window.UCProgress) window.UCProgress.tone();
      emit({ index: i, name: clip.name, text: clip.text });
    } catch (e) {
      emit(null);
    }
  }
  function stop() {
    if (audioCtx) {
      try { audioCtx.suspend(); } catch (e) {}
    }
    emit(null);
  }
  function bench() {
    var det = document.createElement("details");
    det.className = "vs-audio";
    det.innerHTML = "<summary>Tone and media bench · " + CLIPS.length + " labeled clips, generated in this browser</summary><div class=\"vs-clips\"></div>";
    var grid = det.querySelector(".vs-clips");
    CLIPS.forEach(function (clip, i) {
      var card = document.createElement("div");
      card.className = "vs-clip";
      card.innerHTML = "<b>" + esc(clip.name) + "</b><p>" + esc(clip.text) + "</p>";
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "Play";
      btn.setAttribute("aria-label", "Play " + clip.name);
      btn.addEventListener("click", function () {
        try { playIndex(i); } catch (e) { btn.textContent = "Unavailable"; }
      });
      card.appendChild(btn);
      grid.appendChild(card);
    });
    return det;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  window.UCAudio = {
    clips: CLIPS,
    bench: bench,
    play: playIndex,
    stop: stop,
    subscribe: function (fn) { listeners.push(fn); },
    analyser: function () { return analyser; }
  };
})();
