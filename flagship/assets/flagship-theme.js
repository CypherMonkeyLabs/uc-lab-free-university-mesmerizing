
try {
  var params = new URLSearchParams(location.search);
  var t = params.get("theme") || localStorage.getItem("uc_flagship_theme");
  var ok = {neon:1, holographic:1, cyberpunk:1, sunset:1, light:1};
  if (ok[t]) document.documentElement.setAttribute("data-theme", t);
  var motion = localStorage.getItem("uc_flagship_motion");
  if (motion === "reduce" || motion === "allow") document.documentElement.setAttribute("data-motion", motion);
  var lang = localStorage.getItem("uc_flagship_lang");
  if (lang) document.documentElement.lang = lang;
  if (lang === "ar") document.documentElement.dir = "rtl";
} catch (e) {}
