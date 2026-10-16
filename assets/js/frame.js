/* UC lab frame. Banner arrows, header menu, drawer, display controls, search.
   Brand links are not created here. The footer is baked into each page. */
(function () {
  var root = document.documentElement;

  function prefix() {
    var nodes = document.querySelectorAll("script[src]");
    var mark = "assets/js/frame.js";
    for (var i = 0; i < nodes.length; i++) {
      var src = nodes[i].getAttribute("src") || "";
      var at = src.indexOf(mark);
      if (at !== -1) return src.slice(0, at);
    }
    return "";
  }
  var rootPrefix = prefix();
  function fromRoot(href) {
    if (!href) return "";
    if (/^(https?:|#)/.test(href)) return href;
    return rootPrefix + String(href).replace(/^\//, "");
  }

  var drawer = document.querySelector(".site-drawer");
  var backdrop = document.querySelector(".drawer-backdrop");
  var menuButtons = document.querySelectorAll("[data-menu-open]");

  function setDrawer(open) {
    document.body.classList.toggle("drawer-open", open);
    menuButtons.forEach(function (btn) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    if (drawer) drawer.setAttribute("aria-hidden", open ? "false" : "true");
    if (open) {
      var field = drawer && drawer.querySelector("input");
      if (field) field.focus();
    }
  }
  menuButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      setDrawer(!document.body.classList.contains("drawer-open"));
    });
  });
  if (backdrop) backdrop.addEventListener("click", function () { setDrawer(false); });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && document.body.classList.contains("drawer-open")) {
      setDrawer(false);
      if (menuButtons[0]) menuButtons[0].focus();
    }
  });
  if (drawer) {
    drawer.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setDrawer(false); });
    });
    var filter = drawer.querySelector("[data-drawer-filter]");
    if (filter) {
      filter.addEventListener("input", function () {
        var q = filter.value.toLowerCase();
        drawer.querySelectorAll("[data-menu-text]").forEach(function (row) {
          var show = !q || row.getAttribute("data-menu-text").indexOf(q) !== -1;
          row.parentElement.hidden = !show;
        });
      });
    }
  }

  document.querySelectorAll("[data-rail]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var rail = document.querySelector(".section-rail");
      if (!rail) return;
      var delta = btn.getAttribute("data-rail") === "next" ? 220 : -220;
      rail.scrollBy({ left: delta, behavior: root.dataset.motion === "reduce" ? "auto" : "smooth" });
    });
  });

  function applyFont(size) {
    if (size !== "sm" && size !== "md" && size !== "lg") size = "md";
    root.dataset.font = size;
    try { localStorage.setItem("canon-font", size); } catch (err) { /* storage off */ }
    document.querySelectorAll("[data-font-set]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-font-set") === size ? "true" : "false");
    });
  }
  function applyTheme(name) {
    if (name !== "aurora" && name !== "bloom") name = "bloom";
    root.dataset.theme = name;
    try { localStorage.setItem("canon-theme", name); } catch (err) { /* storage off */ }
    document.querySelectorAll("[data-set-theme]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-set-theme") === name ? "true" : "false");
    });
  }
  function applyInk(color) {
    if (!/^#[0-9a-f]{6}$/i.test(color)) return;
    root.style.setProperty("--ink", color);
    try { localStorage.setItem("canon-ink", color); } catch (err) { /* storage off */ }
  }
  document.querySelectorAll("[data-font-set]").forEach(function (btn) {
    btn.addEventListener("click", function () { applyFont(btn.getAttribute("data-font-set")); });
  });
  document.querySelectorAll("[data-set-theme]").forEach(function (btn) {
    btn.addEventListener("click", function () { applyTheme(btn.getAttribute("data-set-theme")); });
  });
  var ink = document.querySelector("[data-ink]");
  if (ink) ink.addEventListener("input", function () { applyInk(ink.value); });
  var displayBtn = document.querySelector(".display-btn");
  var displayPanel = document.querySelector(".display-panel");
  if (displayBtn && displayPanel) {
    displayBtn.addEventListener("click", function (event) {
      event.stopPropagation();
      displayPanel.hidden = !displayPanel.hidden;
      displayBtn.setAttribute("aria-expanded", displayPanel.hidden ? "false" : "true");
    });
    document.addEventListener("pointerdown", function (event) {
      if (displayPanel.hidden) return;
      if (displayPanel.contains(event.target) || displayBtn.contains(event.target)) return;
      displayPanel.hidden = true;
      displayBtn.setAttribute("aria-expanded", "false");
    });
  }

  var search = document.querySelector("[data-nav-search]");
  var pop = document.querySelector(".search-pop");
  var catalog = [];
  fetch(fromRoot("assets/data/catalog.json")).then(function (res) {
    if (!res.ok) return null;
    return res.json();
  }).then(function (data) {
    catalog = (data && data.pages) || [];
  }).catch(function () { catalog = []; });

  function paint(q) {
    if (!pop) return;
    var query = (q || "").trim().toLowerCase();
    if (!query) { pop.hidden = true; pop.innerHTML = ""; return; }
    var hits = catalog.filter(function (row) {
      return (row.title + " " + row.blurb).toLowerCase().indexOf(query) !== -1;
    }).slice(0, 8);
    pop.hidden = hits.length === 0;
    pop.innerHTML = hits.map(function (row) {
      return '<a href="' + fromRoot(row.href) + '">' + row.title + "</a>";
    }).join("");
  }
  if (search) {
    search.addEventListener("input", function () { paint(search.value); });
    if (search.form) search.form.addEventListener("submit", function (event) { event.preventDefault(); });
  }

  document.querySelectorAll("[data-quiz]").forEach(function (box) {
    var answer = box.getAttribute("data-answer");
    box.querySelectorAll(".choice").forEach(function (btn) {
      btn.addEventListener("click", function () {
        box.querySelectorAll(".choice").forEach(function (el) { el.classList.remove("is-good", "is-bad"); });
        var ok = btn.getAttribute("data-choice") === answer;
        btn.classList.add(ok ? "is-good" : "is-bad");
        var note = box.querySelector(".quiz-note");
        if (note) note.hidden = false;
      });
    });
  });

  if ("serviceWorker" in navigator && location.protocol.indexOf("http") === 0) {
    navigator.serviceWorker.register(fromRoot("sw.js")).catch(function () { /* file or private mode */ });
  }

  function motionOff() {
    if (document.documentElement.getAttribute("data-motion") === "reduce") return true;
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }
  function mountEffects() {
    if (motionOff() || document.querySelector(".uc-particles")) return;
    var layer = document.createElement("div");
    layer.className = "uc-particles";
    layer.setAttribute("aria-hidden", "true");
    var i;
    for (i = 0; i < 16; i += 1) {
      var dot = document.createElement("span");
      dot.style.left = (Math.random() * 100) + "%";
      dot.style.animationDelay = (Math.random() * -12) + "s";
      dot.style.animationDuration = (9 + Math.random() * 10) + "s";
      layer.appendChild(dot);
    }
    document.body.appendChild(layer);
    var hero = document.querySelector(".hero-diagram");
    if (hero && window.matchMedia("(pointer: fine)").matches) {
      window.addEventListener("pointermove", function (event) {
        if (motionOff()) {
          hero.style.transform = "";
          return;
        }
        var x = (event.clientX / window.innerWidth - 0.5) * 14;
        var y = (event.clientY / window.innerHeight - 0.5) * 8;
        hero.style.transform = "translate3d(" + x.toFixed(1) + "px," + y.toFixed(1) + "px,0)";
      }, { passive: true });
    }
  }
  mountEffects();

  window.UC_FRAME = { fromRoot: fromRoot, setDrawer: setDrawer, applyFont: applyFont, applyTheme: applyTheme };
})();
