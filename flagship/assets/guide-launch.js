(function () {
  var btn = document.getElementById("guideLaunch");
  if (!btn) return;
  var root = (document.body && document.body.getAttribute("data-root")) || "";
  btn.addEventListener("click", function () {
    if (window.UC_GUIDE) {
      window.UC_GUIDE.toggle();
      return;
    }
    btn.disabled = true;
    var script = document.createElement("script");
    script.src = root + "assets/guide-bot.js";
    script.onload = function () {
      btn.disabled = false;
      if (window.UC_GUIDE) window.UC_GUIDE.open();
    };
    script.onerror = function () {
      btn.disabled = false;
    };
    document.body.appendChild(script);
  });
})();
