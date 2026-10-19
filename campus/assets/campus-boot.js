
try {
  var prefs = JSON.parse(localStorage.getItem("uc_lab_settings_v21") || "{}");
  var saved = prefs.theme || localStorage.getItem("uc_theme");
  if (saved === "night" || saved === "aurora" || saved === "cobalt" || saved === "forest" || saved === "sunset") saved = "dark";
  if (saved === "paper" || saved === "warm") saved = "light";
  if (saved === "dark" || saved === "contrast" || saved === "light" || saved === "signal") document.documentElement.setAttribute("data-theme", saved);
  if (prefs.font === "sm" || prefs.font === "md" || prefs.font === "lg" || prefs.font === "xl") document.documentElement.setAttribute("data-font", prefs.font);
  if (prefs.motion === "reduce" || prefs.motion === "allow") document.documentElement.setAttribute("data-motion", prefs.motion);
} catch (err) { /* private mode */ }
window.STATS = {"version":"v21","built":"2026-10-14","sections":580,"note":"Modular v21 campus. CUCM, CUBE, SIP, Webex Calling, Teams Phone, UCCE/PCCE, CCaaS, E911, QoS."};
window.UC_NO_AUTOPLAY = true;
window.UC = window.UC || {};
UC._packs = {};
UC._pending = {};
UC.manifest = function (data) {
  UC.data = data;
  document.dispatchEvent(new Event("uc-manifest"));
};
UC.pack = function (section, flows) {
  UC._packs[section.id] = { section: section, flows: flows };
  var wait = UC._pending[section.id];
  if (wait) {
    delete UC._pending[section.id];
    wait(UC._packs[section.id]);
  }
};
UC.walks = function (list) {
  UC._walkList = list;
  document.dispatchEvent(new Event("uc-walks"));
};
