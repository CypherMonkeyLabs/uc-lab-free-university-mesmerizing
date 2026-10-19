/* Dial-plan desk. A simulation. It does not call CUCM, CUBE, or any provider. */
(function () {
  var root = document.querySelector("[data-dial-sim]");
  if (!root) return;
  var digits = root.querySelector("[data-digits]");
  var css = root.querySelector("[data-css]");
  var out = root.querySelector("[data-sim-out]");
  var spaces = {
    internal: ["2xxx", "3xxx"],
    local: ["2xxx", "3xxx", "9.xxxxxxx"],
    pstn: ["2xxx", "3xxx", "9.xxxxxxx", "9.011!"],
    emergency: ["911", "9.911", "2xxx"]
  };
  var patterns = [
    { id: "911", label: "911 in the emergency partition", test: function (d) { return d === "911" || d === "9911"; } },
    { id: "internal", label: "4-digit internal partition", test: function (d) { return /^[23]\d{3}$/.test(d); } },
    { id: "local", label: "local 7-digit pattern", test: function (d) { return /^9\d{7}$/.test(d); } },
    { id: "intl", label: "international pattern", test: function (d) { return /^9011\d{6,}$/.test(d); } }
  ];

  function run() {
    var raw = (digits.value || "").replace(/\D/g, "");
    var space = spaces[css.value] || [];
    var hit = patterns.find(function (row) { return row.test(raw); });
    var allowed = false;
    if (hit && hit.id === "911") allowed = space.indexOf("911") !== -1 || space.indexOf("9.911") !== -1;
    if (hit && hit.id === "internal") allowed = space.indexOf("2xxx") !== -1;
    if (hit && hit.id === "local") allowed = space.indexOf("9.xxxxxxx") !== -1;
    if (hit && hit.id === "intl") allowed = space.indexOf("9.011!") !== -1;
    var lines = ["Simulation only. No phone system was called."];
    lines.push("Digits: " + (raw || "(none)"));
    lines.push("Calling search space sees: " + space.join(", "));
    if (!raw) lines.push("Type digits, then run the desk.");
    else if (!hit) lines.push("No teaching pattern matched. This desk only knows 911, 4-digit, 9 plus 7, and 9011.");
    else if (!allowed) lines.push("Pattern " + hit.label + " exists, but this search space cannot see it. The call stops here.");
    else lines.push("Pattern " + hit.label + " is visible. A real system would still need a route list, a trunk, and a transformation. This desk stops at the match.");
    out.textContent = lines.join("\n");
  }

  root.querySelector("[data-sim-run]").addEventListener("click", run);
  digits.addEventListener("keydown", function (event) {
    if (event.key === "Enter") { event.preventDefault(); run(); }
  });
})();
