/* Draggable 3D-feeling guide monkey. Self-contained, no dependencies.
   Pointer Events drag, edge snap with bounce, tilt from velocity, lift shadow,
   position saved as fractions of the free viewport range. Loaded by guide.js. */
(function () {
  var dock = document.querySelector(".bot-dock");
  var bot = dock && dock.querySelector(".monkey-btn");
  if (!bot) return;
  var KEY = "uc-bot-pos-v1", M = 8;
  var calm = matchMedia("(prefers-reduced-motion: reduce)");
  var phone = matchMedia("(max-width: 800px)");
  var shadow = document.createElement("div");
  shadow.className = "bot-shadow";
  shadow.setAttribute("aria-hidden", "true");
  var reset = document.createElement("button");
  reset.type = "button";
  reset.className = "bot-reset";
  reset.hidden = true;
  reset.setAttribute("aria-label", "Move the guide back to its home spot");
  reset.textContent = "\u21BA";
  dock.appendChild(shadow);
  dock.appendChild(reset);

  var pos = null, drag = null, tap = 0, pass = false;
  try { pos = JSON.parse(localStorage.getItem(KEY)); } catch (e) { pos = null; }
  if (!pos || typeof pos.fx !== "number" || typeof pos.fy !== "number") pos = null;

  function inset() { return { l: M, t: M, r: M, b: phone.matches ? 84 : M }; }
  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), Math.max(lo, hi)); }
  function sheet() { return phone.matches && dock.classList.contains("is-open"); }
  function place(x, y) {
    var s = dock.style;
    s.left = Math.round(x) + "px"; s.top = Math.round(y) + "px"; s.right = "auto"; s.bottom = "auto";
  }
  function home() {
    var s = dock.style;
    s.left = s.top = s.right = s.bottom = "";
  }
  function bounds() {
    var i = inset(), w = dock.offsetWidth, h = dock.offsetHeight;
    return { x0: i.l, y0: i.t, x1: innerWidth - w - i.r, y1: innerHeight - h - i.b };
  }
  function apply() {
    if (drag && drag.moved) return;
    dock.classList.toggle("is-moved", !!pos);
    reset.hidden = !pos || sheet();
    if (!pos || sheet()) { home(); return; }
    var b = bounds();
    place(clamp(b.x0 + pos.fx * (b.x1 - b.x0), b.x0, b.x1), clamp(b.y0 + pos.fy * (b.y1 - b.y0), b.y0, b.y1));
  }
  function store(x, y) {
    var b = bounds();
    pos = { fx: b.x1 > b.x0 ? (x - b.x0) / (b.x1 - b.x0) : 0, fy: b.y1 > b.y0 ? (y - b.y0) / (b.y1 - b.y0) : 0 };
    try { localStorage.setItem(KEY, JSON.stringify(pos)); } catch (e) { /* storage off */ }
  }
  function tilt(rx, ry, lift) {
    bot.style.transform = rx || ry || lift ? "perspective(600px) rotateX(" + rx + "deg) rotateY(" + ry + "deg) scale(" + (lift ? 1.1 : 1) + ")" : "";
    dock.classList.toggle("is-lifted", !!lift);
  }
  function goHome() {
    pos = null;
    try { localStorage.removeItem(KEY); } catch (e) { /* storage off */ }
    dock.classList.add("is-snapping"); home(); apply(); tilt(0, 0, 0);
  }

  bot.addEventListener("pointerdown", function (e) {
    if (e.button !== 0 || sheet()) return;
    var r = dock.getBoundingClientRect();
    drag = { id: e.pointerId, sx: e.clientX, sy: e.clientY, ox: r.left, oy: r.top, x: r.left, y: r.top, px: e.clientX, py: e.clientY, t: e.timeStamp, vx: 0, vy: 0, moved: false };
    try { bot.setPointerCapture(e.pointerId); } catch (err) { /* no capture */ }
  });
  bot.addEventListener("pointermove", function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    if (!drag.moved && Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) < 6) return;
    if (!drag.moved) { drag.moved = true; dock.classList.remove("is-snapping"); }
    var b = bounds(), dt = Math.max(1, e.timeStamp - drag.t);
    drag.vx = drag.vx * 0.6 + ((e.clientX - drag.px) / dt) * 0.4;
    drag.vy = drag.vy * 0.6 + ((e.clientY - drag.py) / dt) * 0.4;
    drag.px = e.clientX; drag.py = e.clientY; drag.t = e.timeStamp;
    drag.x = clamp(drag.ox + e.clientX - drag.sx, b.x0, b.x1);
    drag.y = clamp(drag.oy + e.clientY - drag.sy, b.y0, b.y1);
    place(drag.x, drag.y);
    if (!calm.matches) tilt(clamp(-drag.vy * 22, -25, 25).toFixed(1), clamp(drag.vx * 22, -25, 25).toFixed(1), true);
    else tilt(0, 0, true);
  });
  function end(e) {
    if (!drag || e.pointerId !== drag.id) return;
    var d = drag; drag = null;
    try { bot.releasePointerCapture(e.pointerId); } catch (err) { /* released */ }
    if (!d.moved) return;
    window.UC_BOT_SUPPRESS = true;
    setTimeout(function () { window.UC_BOT_SUPPRESS = false; }, 0);
    var b = bounds(), dist = [d.x - b.x0, b.x1 - d.x, d.y - b.y0, b.y1 - d.y], k = dist.indexOf(Math.min.apply(null, dist));
    var x = k === 0 ? b.x0 : k === 1 ? b.x1 : d.x, y = k === 2 ? b.y0 : k === 3 ? b.y1 : d.y;
    dock.classList.add("is-snapping");
    place(x, y); tilt(0, 0, 0); store(x, y); dock.classList.add("is-moved"); reset.hidden = false;
  }
  bot.addEventListener("pointerup", end);
  bot.addEventListener("pointercancel", end);
  // A click after a drag is ignored. When moved, a lone tap waits 280ms so a double tap can reset home.
  bot.addEventListener("click", function (e) {
    if (pass) return;
    if (window.UC_BOT_SUPPRESS) { e.stopImmediatePropagation(); e.preventDefault(); return; }
    if (!pos || sheet() || dock.classList.contains("is-open")) return;
    e.stopImmediatePropagation();
    if (tap) { clearTimeout(tap); tap = 0; goHome(); return; }
    tap = setTimeout(function () { tap = 0; pass = true; bot.click(); pass = false; }, 280);
  }, true);
  bot.addEventListener("transitionend", function () { dock.classList.remove("is-snapping"); });
  dock.addEventListener("transitionend", function (e) { if (e.target === dock) dock.classList.remove("is-snapping"); });
  reset.addEventListener("click", goHome);
  addEventListener("resize", apply);
  new MutationObserver(apply).observe(dock, { attributes: true, attributeFilter: ["class"] });
  apply();
})();
