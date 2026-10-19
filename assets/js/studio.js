/* Home-page aurora. Decorative only. Stops when the visitor prefers reduced motion. */
(function () {
  var canvas = document.getElementById("studio-aurora");
  if (!canvas) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (reduce.matches) return;
  var ctx = canvas.getContext("2d");
  if (!ctx) return;
  var frame = 0;
  var running = true;

  function size() {
    var rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width));
    canvas.height = Math.max(1, Math.floor(rect.height));
  }

  function draw() {
    if (!running) return;
    frame += 1;
    var w = canvas.width;
    var h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    var bands = [
      ["rgba(15,155,142,0.35)", 0.2],
      ["rgba(99,102,241,0.28)", 0.45],
      ["rgba(244,114,182,0.22)", 0.7]
    ];
    bands.forEach(function (band, index) {
      ctx.beginPath();
      var y = h * band[1];
      ctx.moveTo(0, y);
      for (var x = 0; x <= w; x += 12) {
        var wave = Math.sin((x / 90) + frame / 40 + index) * 18;
        ctx.lineTo(x, y + wave);
      }
      ctx.lineTo(w, h);
      ctx.lineTo(0, h);
      ctx.closePath();
      ctx.fillStyle = band[0];
      ctx.fill();
    });
    if (running) requestAnimationFrame(draw);
  }

  size();
  draw();
  window.addEventListener("resize", size);
  document.addEventListener("visibilitychange", function () {
    var hidden = document.hidden;
    if (hidden) running = false;
    else if (!running) { running = true; draw(); }
  });
})();
