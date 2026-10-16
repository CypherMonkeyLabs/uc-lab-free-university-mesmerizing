/* University helpers. Footer markup is already in the page.
   This file does not add brand links. */
(function () {
  var CONTACT = "https://cyphermonkeylabs.com/#contact";
  var REPO = "https://github.com/CypherMonkeyLabs";
  window.CANON_UNIVERSITY = {
    contact: CONTACT,
    repo: REPO,
    award: function (id) {
      try {
        var bag = JSON.parse(localStorage.getItem("uc-badges") || "{}");
        if (bag[id]) return false;
        bag[id] = new Date().toISOString();
        localStorage.setItem("uc-badges", JSON.stringify(bag));
      } catch (err) { return false; }
      return true;
    }
  };
  document.querySelectorAll("[data-count]").forEach(function (node) {
    var target = Number(node.getAttribute("data-count"));
    if (!target) return;
    node.textContent = String(target);
  });
})();
