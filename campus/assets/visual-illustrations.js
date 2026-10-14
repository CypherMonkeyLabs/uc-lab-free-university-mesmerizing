/* Topology, console, and capture drawings. Specs come from the flow catalog. */
(function () {
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function topology(spec) {
    var nodes = spec.nodes || [];
    var w = 760, h = 210;
    var out = ['<svg class="vs-art-svg" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + esc(spec.title || "Topology") + '">'];
    out.push('<rect width="' + w + '" height="' + h + '" rx="16" fill="currentColor" fill-opacity=".03"/>');
    var pos = nodes.map(function (_, i) {
      return [70 + (i * (w - 120)) / Math.max(1, nodes.length - 1), 78];
    });
    (spec.links || []).forEach(function (link, i) {
      var a = pos[link.a], b = pos[link.b];
      if (!a || !b) return;
      var y = 118 + (i % 3) * 18;
      out.push('<path d="M' + a[0] + " " + a[1] + " C" + a[0] + " " + y + "," + b[0] + " " + y + "," + b[0] + " " + b[1] + '" fill="none" stroke="#6366F1" stroke-opacity=".7" stroke-width="1.5"/>');
      out.push('<text x="' + ((a[0] + b[0]) / 2) + '" y="' + (y + 12) + '" text-anchor="middle" fill="currentColor" font-size="10" font-family="ui-sans-serif,system-ui">' + esc(link.label) + "</text>");
    });
    nodes.forEach(function (name, i) {
      var x = pos[i][0];
      out.push('<rect x="' + (x - 54) + '" y="48" width="108" height="40" rx="12" fill="var(--card, #fff)" stroke="#0F9B8E" stroke-width="2"/>');
      out.push('<text x="' + x + '" y="73" text-anchor="middle" fill="currentColor" font-size="12" font-weight="700" font-family="ui-sans-serif,system-ui">' + esc(name) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }
  function mockup(spec) {
    var lines = spec.lines || [];
    var h = 46 + lines.length * 22;
    var out = ['<svg class="vs-art-svg" viewBox="0 0 760 ' + h + '" role="img" aria-label="' + esc(spec.title || "Console") + '">'];
    out.push('<rect width="760" height="' + h + '" rx="16" fill="#102033"/>');
    out.push('<rect width="760" height="32" rx="16" fill="#0b1724"/>');
    out.push('<circle cx="18" cy="16" r="4" fill="#E11D48"/><circle cx="32" cy="16" r="4" fill="#E08A00"/><circle cx="46" cy="16" r="4" fill="#22C55E"/>');
    out.push('<text x="64" y="20" fill="#d7e2ea" font-size="11" font-family="ui-sans-serif,system-ui">' + esc(spec.kind || "lab") + " · " + esc(spec.title || "") + "</text>");
    lines.forEach(function (line, i) {
      var color = i === 0 ? "#E08A00" : "#d7e2ea";
      out.push('<text x="18" y="' + (54 + i * 22) + '" fill="' + color + '" font-size="13" font-family="ui-monospace,monospace">' + esc(line) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }
  function capture(spec) {
    var rows = spec.packets || [];
    var h = 36 + rows.length * 28;
    var out = ['<svg class="vs-art-svg" viewBox="0 0 760 ' + h + '" role="img" aria-label="' + esc(spec.title || "Capture") + '">'];
    out.push('<rect width="760" height="' + h + '" rx="16" fill="var(--card, #fff)" stroke="currentColor" stroke-opacity=".15"/>');
    out.push('<text x="16" y="22" fill="currentColor" font-size="12" font-weight="700" font-family="ui-sans-serif,system-ui">Annotated messages · ' + esc(spec.title || "") + "</text>");
    rows.forEach(function (row, i) {
      var y = 36 + i * 28;
      out.push('<rect x="8" y="' + y + '" width="744" height="24" rx="6" fill="' + (i % 2 ? "currentColor" : "#6366F1") + '" fill-opacity="' + (i % 2 ? ".04" : ".1") + '"/>');
      out.push('<text x="16" y="' + (y + 16) + '" fill="currentColor" font-size="11" font-family="ui-monospace,monospace">' + row.n + "  " + esc(row.src) + " → " + esc(row.dst) + "  " + esc(row.msg) + "</text>");
    });
    out.push("</svg>");
    return out.join("");
  }
  function mount(flow) {
    var art = flow && flow.art;
    if (!art) return null;
    var wrap = document.createElement("div");
    wrap.className = "vs-art";
    var tabs = document.createElement("div");
    tabs.className = "vs-art-tabs";
    tabs.setAttribute("role", "tablist");
    var panel = document.createElement("div");
    panel.className = "vs-art-panel";
    var views = [
      ["Topology", art.topology ? topology(art.topology) : ""],
      ["Console", art.mockup ? mockup(art.mockup) : ""],
      ["Capture", art.capture ? capture(art.capture) : ""]
    ];
    views.forEach(function (view, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = view[0];
      b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
      b.addEventListener("click", function () {
        var buttons = tabs.querySelectorAll("button");
        for (var n = 0; n < buttons.length; n++) buttons[n].setAttribute("aria-pressed", buttons[n] === b ? "true" : "false");
        panel.innerHTML = view[1];
      });
      tabs.appendChild(b);
    });
    panel.innerHTML = views[0][1];
    wrap.appendChild(tabs);
    wrap.appendChild(panel);
    return wrap;
  }
  window.UCArt = { mount: mount };
})();
