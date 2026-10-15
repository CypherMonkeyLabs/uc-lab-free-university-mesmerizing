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
  scene.fog = new THREE.FogExp2(0x05030d, 0.045);
  const camera = new THREE.PerspectiveCamera(48, 1, 0.1, 80);
  camera.position.set(0, 2.4, 11);
  const grid = new THREE.GridHelper(36, 36, 0x22d3ee, 0x24143f);
  grid.position.y = -2.4;
  scene.add(grid);
  const rings = [3.6, 2.5, 1.5].map(function (radius, i) {
    const mesh = new THREE.Mesh(
      new THREE.TorusGeometry(radius, 0.03, 12, 96),
      new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.9 })
    );
    mesh.rotation.x = Math.PI / 2.35 + i * 0.28;
    scene.add(mesh);
    return mesh;
  });
  const names = ["Phone", "CUCM", "CUBE", "Cloud"];
  const nodes = names.map(function (name, i) {
    const mesh = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.38, 1),
      new THREE.MeshStandardMaterial({ color: 0x22d3ee, emissive: 0x22d3ee, emissiveIntensity: 0.85, roughness: 0.25, metalness: 0.35 })
    );
    mesh.userData.name = name;
    mesh.userData.i = i;
    scene.add(mesh);
    return mesh;
  });
  const links = [];
  for (let i = 0; i < nodes.length; i += 1) {
    const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0xe879f9 }));
    line.userData.link = ["phone-cucm", "cucm-cube", "cube-pstn", "cube-cloud"][i];
    scene.add(line);
    links.push(line);
  }
  const count = 420;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i += 1) {
    positions[i * 3] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 14;
  }
  const points = new THREE.Points(
    new THREE.BufferGeometry().setAttribute("position", new THREE.BufferAttribute(positions, 3)),
    new THREE.PointsMaterial({ color: 0xe879f9, size: 0.05, transparent: true, opacity: 0.85 })
  );
  scene.add(points);
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
    const fog = new THREE.Color(cssColor("--scene", "#05030d"));
    scene.fog.color.copy(fog);
    scene.background = fog;
    nodes.forEach(function (mesh, i) {
      mesh.material.color.copy(colors[i]);
      mesh.material.emissive.copy(colors[i]);
    });
    rings.forEach(function (ring, i) { ring.material.color.copy(colors[i % colors.length]); });
    points.material.color.copy(colors[1]);
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
    nodes.forEach(function (mesh, i) {
      const angle = t * 0.00032 + i * (Math.PI / 2);
      const radius = 3.15;
      mesh.position.set(Math.cos(angle) * radius, Math.sin(t * 0.0009 + i) * 0.45, Math.sin(angle) * radius * 0.62);
      mesh.rotation.y = t * 0.001 + i;
    });
    links.forEach(function (line, i) {
      const from = nodes[i].position;
      const to = nodes[(i + 1) % nodes.length].position;
      line.geometry.setFromPoints([from, to]);
    });
    rings.forEach(function (ring, i) { ring.rotation.z = t * 0.00018 * (i + 1); });
    points.rotation.y = t * 0.00006;
    camera.position.x = mx * 2.2;
    camera.position.y = 2.4 - my * 1.1 + scroll * 0.0015;
    camera.lookAt(0, 0, 0);
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
    new THREE.IcosahedronGeometry(0.46, 0),
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
if (hero || minis.length) {
  import("./vendor/three.module.js").then(function (THREE) {
    if (hero) mountHero(THREE, hero);
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
