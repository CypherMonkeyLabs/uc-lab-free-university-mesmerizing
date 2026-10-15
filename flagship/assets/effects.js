import { animate } from "./vendor/anime.esm.min.js";
import rough from "./vendor/rough.esm.js";

const reduce = document.documentElement.getAttribute("data-motion") === "reduce"
  || window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function cssColor(name, fallback) {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

function mountHero(THREE, canvas) {
  if (reduce) {
    canvas.hidden = true;
    document.documentElement.setAttribute("data-webgl", "off");
    return;
  }
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: false, antialias: true, powerPreference: "high-performance" });
    if (!renderer.getContext()) throw new Error("no webgl context");
  } catch (err) {
    canvas.hidden = true;
    document.documentElement.setAttribute("data-webgl", "off");
    return;
  }
  document.documentElement.setAttribute("data-webgl", "on");
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(58, 1, 0.1, 80);
  camera.position.set(0.4, 1.5, 7.2);
  const grid = new THREE.GridHelper(48, 28, 0x5eead4, 0x6d28d9);
  grid.position.y = -2.6;
  scene.add(grid);
  const globe = new THREE.Mesh(
    new THREE.SphereGeometry(3.15, 28, 18),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee, wireframe: true, transparent: true, opacity: 0.45 })
  );
  scene.add(globe);
  const rings = [8.4, 6.6, 4.4, 3.3, 2.15].map(function (radius, i) {
    const mesh = new THREE.Mesh(
      new THREE.TorusGeometry(radius, i < 2 ? 0.03 : 0.045, 12, 140),
      new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: i < 2 ? 0.55 : 0.95 })
    );
    mesh.rotation.x = Math.PI / 2.4 + i * 0.38;
    mesh.rotation.y = i * 0.35;
    scene.add(mesh);
    return mesh;
  });
  const fleet = [
    { name: "CUCM", radius: 4.8, tilt: 0.15, speed: 0.00022, phase: 0.2, y: 0.5, color: 0x22d3ee, link: "phone-cucm" },
    { name: "Webex", radius: 6.4, tilt: 0.85, speed: 0.00016, phase: 1.1, y: 1.7, color: 0xe879f9, link: "" },
    { name: "UCCE", radius: 3.7, tilt: 1.35, speed: 0.00028, phase: 2.2, y: -0.8, color: 0xfde047, link: "" },
    { name: "SBC", radius: 5.6, tilt: 0.45, speed: 0.00019, phase: 3.4, y: 0.2, color: 0xfb7185, link: "cucm-cube" },
    { name: "PSTN", radius: 7.1, tilt: 1.7, speed: 0.00014, phase: 4.3, y: -1.5, color: 0x86efac, link: "cube-pstn" },
    { name: "Teams", radius: 5.1, tilt: 2.3, speed: 0.00024, phase: 5.1, y: 2.0, color: 0x67e8f9, link: "" }
  ];
  function glowTexture(hex) {
    const paint = document.createElement("canvas");
    paint.width = 128;
    paint.height = 128;
    const pen = paint.getContext("2d");
    const grad = pen.createRadialGradient(64, 64, 4, 64, 64, 64);
    grad.addColorStop(0, hex);
    grad.addColorStop(0.35, hex);
    grad.addColorStop(1, "rgba(0,0,0,0)");
    pen.fillStyle = grad;
    pen.fillRect(0, 0, 128, 128);
    const tex = new THREE.CanvasTexture(paint);
    return tex;
  }
  function labelSprite(text, hex) {
    const paint = document.createElement("canvas");
    paint.width = 256;
    paint.height = 72;
    const pen = paint.getContext("2d");
    pen.font = "700 36px Segoe UI, sans-serif";
    pen.fillStyle = hex;
    pen.shadowColor = hex;
    pen.shadowBlur = 18;
    pen.fillText(text, 16, 48);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(paint),
      transparent: true,
      depthWrite: false
    }));
    sprite.scale.set(2.6, 0.74, 1);
    return sprite;
  }
  const nodes = fleet.map(function (spec) {
    const hex = "#" + spec.color.toString(16).padStart(6, "0");
    const mesh = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.34, 1),
      new THREE.MeshBasicMaterial({ color: spec.color })
    );
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(hex),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      opacity: 0.95
    }));
    halo.scale.set(2.4, 2.4, 1);
    mesh.add(halo);
    const label = labelSprite(spec.name, "#f8fbff");
    label.position.set(0, 0.72, 0);
    mesh.add(label);
    mesh.userData.spec = spec;
    mesh.userData.halo = halo;
    const trailCount = 48;
    const trailPos = new Float32Array(trailCount * 3);
    const trailGeo = new THREE.BufferGeometry();
    trailGeo.setAttribute("position", new THREE.BufferAttribute(trailPos, 3));
    const trailMat = new THREE.LineBasicMaterial({
      color: spec.color,
      transparent: true,
      opacity: 0.9
    });
    const trail = new THREE.Line(trailGeo, trailMat);
    const trailPts = new THREE.Points(trailGeo, new THREE.PointsMaterial({
      color: spec.color,
      size: 0.2,
      transparent: true,
      opacity: 0.95,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    }));
    scene.add(trail);
    scene.add(trailPts);
    mesh.userData.trail = trail;
    mesh.userData.trailPts = trailPts;
    mesh.userData.trailPos = trailPos;
    scene.add(mesh);
    return mesh;
  });
  function placeNode(mesh, angle) {
    const spec = mesh.userData.spec;
    const x = Math.cos(angle) * spec.radius;
    const z = Math.sin(angle) * spec.radius * 0.72;
    const y = spec.y + Math.sin(angle + spec.tilt) * 0.85;
    mesh.position.set(x, y, z);
  }
  nodes.forEach(function (mesh) {
    const spec = mesh.userData.spec;
    const pos = mesh.userData.trailPos;
    for (let s = 0; s < 48; s += 1) {
      placeNode(mesh, spec.phase - s * 0.08);
      pos[s * 3] = mesh.position.x;
      pos[s * 3 + 1] = mesh.position.y;
      pos[s * 3 + 2] = mesh.position.z;
    }
    mesh.userData.trail.geometry.attributes.position.needsUpdate = true;
    placeNode(mesh, spec.phase);
  });
  const links = nodes.map(function (mesh) {
    const geo = new THREE.BufferGeometry().setFromPoints([mesh.position.clone(), new THREE.Vector3()]);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({
      color: mesh.userData.spec.color,
      transparent: true,
      opacity: 0.45
    }));
    line.userData.link = mesh.userData.spec.link;
    scene.add(line);
    return line;
  });
  const atmo = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture("#22d3ee"),
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    opacity: 0.32
  }));
  atmo.scale.set(10, 10, 1);
  scene.add(atmo);
  const nebulaSpots = [
    { color: 0x7c3aed, x: -6.2, y: 2.2, z: -4, s: 13 },
    { color: 0x0891b2, x: 6.4, y: 1.4, z: -5, s: 12 },
    { color: 0xdb2777, x: 0.2, y: -2.2, z: -6, s: 14 },
    { color: 0x22d3ee, x: -5.4, y: -1.6, z: -3, s: 9 },
    { color: 0xe879f9, x: 5.2, y: -1.8, z: -3.5, s: 10 }
  ];
  const nebula = nebulaSpots.map(function (spot) {
    const hex = "#" + spot.color.toString(16).padStart(6, "0");
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture(hex),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      opacity: 0.42
    }));
    sprite.scale.set(spot.s, spot.s * 0.72, 1);
    sprite.position.set(spot.x, spot.y, spot.z);
    sprite.userData.home = spot;
    scene.add(sprite);
    return sprite;
  });
  const layers = [];
  [900, 500, 220].forEach(function (count, layer) {
    const positions = new Float32Array(count * 3);
    const spread = 16 - layer * 2;
    for (let i = 0; i < count; i += 1) {
      positions[i * 3] = (Math.random() - 0.5) * spread;
      positions[i * 3 + 1] = (Math.random() - 0.5) * (spread * 0.62);
      positions[i * 3 + 2] = (Math.random() - 0.5) * spread - layer;
    }
    const points = new THREE.Points(
      new THREE.BufferGeometry().setAttribute("position", new THREE.BufferAttribute(positions, 3)),
      new THREE.PointsMaterial({
        color: layer === 1 ? 0xe879f9 : 0x67e8f9,
        size: 0.1 + layer * 0.08,
        transparent: true,
        opacity: 0.7,
        depthWrite: false,
        blending: THREE.AdditiveBlending
      })
    );
    scene.add(points);
    layers.push(points);
  });
  scene.add(new THREE.AmbientLight(0xffffff, 0.35));
  const key = new THREE.PointLight(0x22d3ee, 12, 40);
  key.position.set(4, 6, 8);
  scene.add(key);
  const fill = new THREE.PointLight(0xe879f9, 8, 30);
  fill.position.set(-6, 2, -4);
  scene.add(fill);
  let mx = 0;
  let my = 0;
  window.addEventListener("pointermove", function (event) {
    mx = event.clientX / Math.max(window.innerWidth, 1) - 0.5;
    my = event.clientY / Math.max(window.innerHeight, 1) - 0.5;
  }, { passive: true });
  document.querySelectorAll("[data-break]").forEach(function (box) {
    box.addEventListener("change", function () {
      const id = box.getAttribute("data-break");
      links.forEach(function (line) {
        if (line.userData.link === id) line.visible = !box.checked;
      });
    });
  });
  function applyTheme() {
    const colors = ["--node1", "--node2", "--node3", "--node4"].map(function (token, i) {
      return new THREE.Color(cssColor(token, ["#22d3ee", "#e879f9", "#fde047", "#fb7185"][i]));
    });
    scene.background = new THREE.Color(cssColor("--scene", "#05030d"));
    globe.material.color.copy(colors[0]);
    nodes.forEach(function (mesh, i) {
      const color = colors[i % colors.length];
      mesh.material.color.copy(color);
      mesh.userData.trail.material.color.copy(color);
      mesh.userData.trailPts.material.color.copy(color);
    });
    rings.forEach(function (ring, i) { ring.material.color.copy(colors[i % colors.length]); });
    layers.forEach(function (points, i) { points.material.color.copy(colors[i % colors.length]); });
    key.color.copy(colors[0]);
    fill.color.copy(colors[1]);
  }
  applyTheme();
  window.UC_APPLY_THEME = applyTheme;
  function size() {
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || 640;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
  }
  size();
  window.addEventListener("resize", size);
  let running = true;
  document.addEventListener("visibilitychange", function () { running = !document.hidden; });
  function frame(t) {
    if (!running) {
      requestAnimationFrame(frame);
      return;
    }
    const scroll = window.scrollY || 0;
    globe.rotation.y = t * 0.00012;
    nodes.forEach(function (mesh) {
      const spec = mesh.userData.spec;
      const angle = spec.phase + t * spec.speed;
      placeNode(mesh, angle);
      mesh.rotation.y = t * 0.001;
      const pos = mesh.userData.trailPos;
      for (let s = pos.length / 3 - 1; s > 0; s -= 1) {
        pos[s * 3] = pos[(s - 1) * 3];
        pos[s * 3 + 1] = pos[(s - 1) * 3 + 1];
        pos[s * 3 + 2] = pos[(s - 1) * 3 + 2];
      }
      pos[0] = mesh.position.x;
      pos[1] = mesh.position.y;
      pos[2] = mesh.position.z;
      mesh.userData.trail.geometry.attributes.position.needsUpdate = true;
    });
    links.forEach(function (line, i) {
      const from = nodes[i].position;
      const to = nodes[(i + 1) % nodes.length].position;
      line.geometry.setFromPoints([from, to]);
      line.geometry.attributes.position.needsUpdate = true;
    });
    rings.forEach(function (ring, i) { ring.rotation.z = t * 0.00018 * (i + 1); });
    layers.forEach(function (points, i) {
      points.rotation.y = t * 0.00004 * (i + 1);
      points.position.x = -mx * (0.4 + i * 0.35);
      points.position.y = my * (0.25 + i * 0.2) - scroll * 0.0004 * (i + 1);
    });
    nebula.forEach(function (sprite, i) {
      const home = sprite.userData.home;
      sprite.position.x = home.x + mx * (1.1 + i * 0.35);
      sprite.position.y = home.y - my * (0.7 + i * 0.25) - scroll * 0.0003;
    });
    atmo.position.x = mx * 0.4;
    atmo.position.y = -my * 0.3;
    camera.position.x = 0.2 + mx * 2.4;
    camera.position.y = 1.2 - my * 1.3 + scroll * 0.0016;
    camera.position.z = 7.6 - scroll * 0.001;
    camera.lookAt(mx * 0.4, my * -0.2, 0);
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function mountMini(THREE, canvas) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    if (!renderer.getContext()) throw new Error("no webgl");
  } catch (err) {
    canvas.hidden = true;
    return;
  }
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 20);
  camera.position.set(1.8, 1.3, 2.6);
  const core = new THREE.Mesh(
    iconGeometry(THREE, canvas.getAttribute("data-shape") || "sip"),
    new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x0e7490, emissiveIntensity: 0.6, flatShading: true })
  );
  const halo = new THREE.Mesh(
    new THREE.TorusGeometry(0.78, 0.045, 8, 32),
    new THREE.MeshBasicMaterial({ color: 0xe879f9 })
  );
  halo.rotation.x = 1.1;
  scene.add(core);
  scene.add(halo);
  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const sun = new THREE.PointLight(0xffffff, 6, 10);
  sun.position.set(2, 3, 2);
  scene.add(sun);
  renderer.setSize(canvas.clientWidth || 140, canvas.clientHeight || 140, false);
  function frame(t) {
    core.rotation.y = t * 0.001;
    halo.rotation.z = t * 0.0014;
    renderer.render(scene, camera);
    if (!reduce) requestAnimationFrame(frame);
  }
  if (reduce) renderer.render(scene, camera);
  else requestAnimationFrame(frame);
}

function iconGeometry(THREE, shape) {
  const table = {
    start: function () { return new THREE.BoxGeometry(0.7, 1.05, 0.28); },
    sip: function () { return new THREE.TorusGeometry(0.55, 0.14, 10, 28); },
    cucm: function () { return new THREE.BoxGeometry(0.85, 0.85, 0.85); },
    cloud: function () { return new THREE.IcosahedronGeometry(0.62, 1); },
    ucce: function () { return new THREE.ConeGeometry(0.55, 1.05, 6); },
    ccaas: function () { return new THREE.OctahedronGeometry(0.68, 0); },
    e911: function () { return new THREE.TetrahedronGeometry(0.72, 0); },
    qos: function () { return new THREE.CylinderGeometry(0.22, 0.22, 1.1, 8); },
    migrate: function () { return new THREE.TorusKnotGeometry(0.38, 0.12, 48, 8); },
    trouble: function () { return new THREE.TorusGeometry(0.48, 0.16, 8, 20); },
    evidence: function () { return new THREE.BoxGeometry(0.95, 0.2, 0.7); },
    design: function () { return new THREE.DodecahedronGeometry(0.58, 0); },
    practice: function () { return new THREE.SphereGeometry(0.55, 16, 12); },
    reference: function () { return new THREE.CylinderGeometry(0.15, 0.55, 0.9, 5); }
  };
  return (table[shape] || table.sip)();
}

function mountIconDock(THREE, canvas) {
  const host = canvas.parentElement;
  const links = host.querySelectorAll(".icon-links a");
  const n = links.length;
  if (!n) return;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    if (!renderer.getContext()) throw new Error("no webgl");
  } catch (err) {
    canvas.hidden = true;
    return;
  }
  const colors = [0x22d3ee, 0xe879f9, 0xfde047, 0xfb7185, 0x86efac, 0xa78bfa, 0x67e8f9, 0xf97316];
  const slots = Array.prototype.map.call(links, function (link, i) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 20);
    camera.position.set(1.4, 1.1, 2.3);
    const mesh = new THREE.Mesh(
      iconGeometry(THREE, link.getAttribute("data-shape")),
      new THREE.MeshBasicMaterial({ color: colors[i % colors.length] })
    );
    const halo = new THREE.Mesh(
      new THREE.SphereGeometry(0.95, 12, 8),
      new THREE.MeshBasicMaterial({ color: colors[i % colors.length], transparent: true, opacity: 0.18 })
    );
    scene.add(mesh);
    scene.add(halo);
    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    return { scene: scene, camera: camera, mesh: mesh };
  });
  function draw(t) {
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height) {
      if (!reduce) requestAnimationFrame(draw);
      return;
    }
    const bleed = document.querySelector(".bleed");
    if (bleed) bleed.style.setProperty("--dock-h", height + "px");
    renderer.setSize(width, height, false);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    const origin = host.getBoundingClientRect();
    renderer.setScissorTest(false);
    renderer.setClearColor(0x000000, 0);
    renderer.clear();
    renderer.setScissorTest(true);
    slots.forEach(function (slot, i) {
      const box = links[i].getBoundingClientRect();
      const x = box.left - origin.left;
      const y = height - (box.bottom - origin.top);
      const w = Math.max(box.width, 1);
      const h = Math.max(box.height, 1);
      renderer.setViewport(x, y, w, h);
      renderer.setScissor(x, y, w, h);
      slot.mesh.rotation.y = t * 0.001 + i;
      slot.mesh.rotation.x = 0.4;
      slot.camera.aspect = w / h;
      slot.camera.updateProjectionMatrix();
      renderer.render(slot.scene, slot.camera);
    });
    if (!reduce) requestAnimationFrame(draw);
  }
  if (reduce) draw(0);
  else requestAnimationFrame(draw);
}

function mountCounts() {
  document.querySelectorAll("[data-count]").forEach(function (el) {
    const target = Number(el.getAttribute("data-count"));
    if (!Number.isFinite(target) || reduce) return;
    const proxy = { n: 0 };
    try {
      animate(proxy, {
        n: target,
        duration: 900,
        ease: "outCubic",
        onUpdate: function () { el.textContent = String(Math.round(proxy.n)); }
      });
    } catch (err) {
      el.textContent = String(target);
    }
  });
}

function mountMascots() {
  if (reduce || !document.querySelector(".mascot")) return;
  try {
    animate(".mascot", {
      rotate: [-3, 3],
      duration: 2200,
      alternate: true,
      loop: true,
      ease: "inOutSine"
    });
  } catch (err) { /* selector or reduced environment */ }
}

function mountRough() {
  const host = document.querySelector("#roughBoard");
  if (!host) return;
  const rc = rough.svg(host);
  const nodes = [
    [24, 30, "Symptom"],
    [210, 30, "One leg"],
    [400, 30, "One change"],
    [590, 30, "Evidence"]
  ];
  nodes.forEach(function (node, i) {
    host.appendChild(rc.rectangle(node[0], node[1], 150, 54, { roughness: 1.3, stroke: "#e879f9", fill: "#141028", fillStyle: "hachure" }));
    if (i < nodes.length - 1) {
      host.appendChild(rc.line(node[0] + 150, node[1] + 27, nodes[i + 1][0], nodes[i + 1][1] + 27, { stroke: "#22d3ee", roughness: 1.2 }));
    }
  });
  nodes.forEach(function (node) {
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", String(node[0] + 75));
    text.setAttribute("y", String(node[1] + 33));
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", "14");
    text.setAttribute("fill", "#f5f7ff");
    text.textContent = node[2];
    host.appendChild(text);
  });
}

const hero = document.querySelector("#hero3d");
const minis = document.querySelectorAll("[data-mini3d]");
const iconStage = document.querySelector("#iconStage");
if (hero || minis.length || iconStage) {
  import("./vendor/three.module.js").then(function (THREE) {
    if (hero) mountHero(THREE, hero);
    if (iconStage) {
      try { mountIconDock(THREE, iconStage); } catch (err) { iconStage.hidden = true; }
    }
    minis.forEach(function (canvas) { mountMini(THREE, canvas); });
  }).catch(function () {
    if (hero) {
      hero.hidden = true;
      document.documentElement.setAttribute("data-webgl", "off");
    }
  });
} else if (document.querySelector(".neon-fallback")) {
  document.documentElement.setAttribute("data-webgl", "off");
}
mountCounts();
mountMascots();
mountRough();
