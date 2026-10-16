import * as THREE from "./vendor/three.module.min.js";

const NODES = [
  { id: "phone", name: "Phone", pos: [-3.3, 0.55, 1.5], color: 0x818cf8 },
  { id: "cucm", name: "CUCM", pos: [-0.7, 1.35, 0.1], color: 0x2dd4bf },
  { id: "cube", name: "CUBE", pos: [2.1, 0.75, 0.45], color: 0xfbbf24 },
  { id: "pstn", name: "PSTN", pos: [4.15, 0.4, 1.85], color: 0xf472b6 },
  { id: "webex", name: "Webex", pos: [0.35, 2.35, -2.15], color: 0x38bdf8 }
];

const LINKS = [
  { id: "reg", a: "phone", b: "cucm", name: "Registration" },
  { id: "trunk", a: "cucm", b: "cube", name: "SIP trunk" },
  { id: "pstn", a: "cube", b: "pstn", name: "PSTN peer" },
  { id: "webex", a: "cucm", b: "webex", name: "Webex Calling" }
];

function reducedMotion() {
  if (window.UCSettings && window.UCSettings.motionReduce) return window.UCSettings.motionReduce();
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function nodeById(id) {
  return NODES.find(function (node) { return node.id === id; });
}

function makeLabel(text) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 64;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "rgba(11,17,32,0.88)";
  ctx.beginPath();
  ctx.roundRect(8, 8, 240, 48, 16);
  ctx.fill();
  ctx.fillStyle = "#f8fafc";
  ctx.font = "700 28px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 128, 32);
  const texture = new THREE.CanvasTexture(canvas);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false }));
  sprite.scale.set(1.7, 0.42, 1);
  return sprite;
}

function makeLink(from, to) {
  const start = new THREE.Vector3(from.pos[0], from.pos[1], from.pos[2]);
  const end = new THREE.Vector3(to.pos[0], to.pos[1], to.pos[2]);
  const dir = new THREE.Vector3().subVectors(end, start);
  const length = dir.length();
  const group = new THREE.Group();
  const core = new THREE.Mesh(
    new THREE.CylinderGeometry(0.035, 0.035, length, 10),
    new THREE.MeshBasicMaterial({ color: 0x2dd4bf })
  );
  const glow = new THREE.Mesh(
    new THREE.CylinderGeometry(0.09, 0.09, length, 10),
    new THREE.MeshBasicMaterial({
      color: 0x818cf8,
      transparent: true,
      opacity: 0.28,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    })
  );
  group.add(core);
  group.add(glow);
  group.position.copy(start).add(end).multiplyScalar(0.5);
  group.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  group.userData.core = core;
  group.userData.glow = glow;
  return group;
}

function fallbackSvg() {
  return (
    '<svg class="topo-flat" viewBox="0 0 760 420" role="img" aria-label="CUCM, CUBE, PSTN, and Webex Calling">' +
    '<rect width="760" height="420" rx="24" fill="#0b1120"/>' +
    '<text x="28" y="42" fill="#2dd4bf" font-size="14" font-family="ui-sans-serif,system-ui" font-weight="700">Reduced motion fabric</text>' +
    nodeBox(70, 170, "Phone") +
    nodeBox(230, 110, "CUCM") +
    nodeBox(420, 180, "CUBE") +
    nodeBox(600, 250, "PSTN") +
    nodeBox(300, 40, "Webex") +
    '<path data-link="reg" d="M150 200 H230" stroke="#2dd4bf" stroke-width="4" fill="none"/>' +
    '<path data-link="trunk" d="M330 160 H420" stroke="#818cf8" stroke-width="4" fill="none"/>' +
    '<path data-link="pstn" d="M520 220 H600" stroke="#fbbf24" stroke-width="4" fill="none"/>' +
    '<path data-link="webex" d="M280 130 L330 90" stroke="#38bdf8" stroke-width="4" fill="none"/>' +
    "</svg>"
  );
}

function nodeBox(x, y, name) {
  return (
    '<g><rect x="' + x + '" y="' + y + '" width="100" height="48" rx="14" fill="#131d31" stroke="#818cf8"/>' +
    '<text x="' + (x + 50) + '" y="' + (y + 30) + '" text-anchor="middle" fill="#f8fafc" font-size="14" font-family="ui-sans-serif,system-ui" font-weight="700">' +
    name + "</text></g>"
  );
}

function paintFallback(root, down) {
  root.querySelectorAll("[data-link]").forEach(function (path) {
    const failed = down[path.getAttribute("data-link")];
    path.setAttribute("stroke", failed ? "#f472b6" : path.getAttribute("data-base") || path.getAttribute("stroke"));
    if (!path.getAttribute("data-base")) path.setAttribute("data-base", path.getAttribute("stroke"));
    path.setAttribute("stroke-dasharray", failed ? "7 6" : "");
  });
}

let active = null;

function destroy() {
  if (!active) return;
  active.stop = true;
  if (active.frame) cancelAnimationFrame(active.frame);
  active.listeners.forEach(function (item) {
    item.target.removeEventListener(item.type, item.fn);
  });
  if (active.observer) active.observer.disconnect();
  active.scene.traverse(function (obj) {
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (obj.material.map) obj.material.map.dispose();
      obj.material.dispose();
    }
  });
  active.renderer.dispose();
  const canvas = active.renderer.domElement;
  if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
  active = null;
}

function mount(host) {
  destroy();
  const down = { reg: false, trunk: false, pstn: false, webex: false };
  host.innerHTML =
    '<div class="topo">' +
    '<div class="topo-stage" data-stage>' + fallbackSvg() + "</div>" +
    '<fieldset class="failures"><legend>Link failures</legend>' +
    LINKS.map(function (link) {
      return '<label><input type="checkbox" data-fail="' + link.id + '"> ' + link.name + " down</label>";
    }).join("") +
    "</fieldset>" +
    '<p class="topo-status" data-status role="status">All links are up. Orbit the fabric, or cut a hop and read which call dies.</p>' +
    "</div>";
  const stage = host.querySelector("[data-stage]");
  const status = host.querySelector("[data-status]");

  function describe() {
    const failed = LINKS.filter(function (link) { return down[link.id]; }).map(function (link) { return link.name; });
    if (!failed.length) {
      status.textContent = "All links are up. A phone registers to CUCM, CUCM trunks to CUBE, CUBE faces the PSTN, and CUCM reaches Webex Calling.";
      return;
    }
    const notes = [];
    if (down.trunk) notes.push("The CUCM to CUBE trunk is down, so PSTN calls from the cluster stop at CUCM.");
    if (down.pstn) notes.push("The PSTN peer is down. CUBE can still signal to CUCM, and the carrier leg fails.");
    if (down.webex) notes.push("The Webex Calling path is down. On-prem CUCM calls can still use CUBE.");
    if (down.reg) notes.push("Registration is down. The phone cannot place a new call.");
    status.textContent = failed.join(", ") + " failed. " + notes.join(" ");
  }

  function syncMaterials() {
    if (!active) return;
    active.links.forEach(function (entry) {
      const failed = down[entry.id];
      entry.group.userData.core.material.color.set(failed ? 0xf472b6 : 0x2dd4bf);
      entry.group.userData.glow.material.color.set(failed ? 0xf472b6 : 0x818cf8);
      entry.group.userData.glow.material.opacity = failed ? 0.55 : 0.28;
    });
  }

  host.addEventListener("change", function (event) {
    const input = event.target.closest("[data-fail]");
    if (!input) return;
    down[input.getAttribute("data-fail")] = input.checked;
    paintFallback(host, down);
    syncMaterials();
    describe();
  });

  if (reducedMotion()) {
    describe();
    return { destroy: function () { host.innerHTML = ""; } };
  }

  const gl = document.createElement("canvas").getContext("webgl");
  if (!gl) {
    describe();
    return { destroy: function () { host.innerHTML = ""; } };
  }

  const canvas = document.createElement("canvas");
  canvas.className = "topo-canvas";
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Orbitable 3D topology of the phone, CUCM, CUBE, PSTN, and Webex Calling");
  canvas.tabIndex = 0;
  stage.appendChild(canvas);
  const flat = stage.querySelector(".topo-flat");
  if (flat) flat.hidden = true;

  const coarseGpu = window.matchMedia("(max-width: 800px), (pointer: coarse)").matches;
  const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: !coarseGpu, alpha: true, powerPreference: coarseGpu ? "low-power" : "default" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, coarseGpu ? 1 : 1.5));
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0b1120, 12, 26);
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 50);
  scene.add(new THREE.HemisphereLight(0xf8fafc, 0x1e293b, 1.1));
  const key = new THREE.DirectionalLight(0xffffff, 1.4);
  key.position.set(4, 8, 6);
  scene.add(key);
  const grid = new THREE.GridHelper(12, 12, 0x243049, 0x1a2740);
  grid.position.y = -0.35;
  scene.fog = new THREE.Fog(0x0b1120, 14, 28);
  scene.add(grid);

  const meshes = [];
  NODES.forEach(function (node) {
    const geo = node.id === "phone" ? new THREE.SphereGeometry(0.38, 24, 18) : new THREE.BoxGeometry(0.85, 0.55, 0.7);
    const mat = new THREE.MeshStandardMaterial({
      color: node.color,
      emissive: node.color,
      emissiveIntensity: 0.35,
      roughness: 0.35,
      metalness: 0.15
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(node.pos[0], node.pos[1], node.pos[2]);
    scene.add(mesh);
    const label = makeLabel(node.name);
    label.position.set(node.pos[0], node.pos[1] + 0.7, node.pos[2]);
    scene.add(label);
    meshes.push(mesh);
  });

  const linkMeshes = LINKS.map(function (link) {
    const group = makeLink(nodeById(link.a), nodeById(link.b));
    scene.add(group);
    return { id: link.id, group: group };
  });

  const orbit = { theta: 0.55, phi: 1.08, radius: 9.2, dragging: false, x: 0, y: 0 };
  function placeCamera() {
    const phi = Math.max(0.25, Math.min(1.45, orbit.phi));
    orbit.phi = phi;
    camera.position.set(
      orbit.radius * Math.sin(phi) * Math.sin(orbit.theta),
      orbit.radius * Math.cos(phi),
      orbit.radius * Math.sin(phi) * Math.cos(orbit.theta)
    );
    camera.lookAt(0.4, 0.9, 0);
  }

  const listeners = [];
  function listen(target, type, fn, options) {
    target.addEventListener(type, fn, options);
    listeners.push({ target: target, type: type, fn: fn });
  }
  listen(canvas, "pointerdown", function (event) {
    orbit.dragging = true;
    orbit.x = event.clientX;
    orbit.y = event.clientY;
    canvas.setPointerCapture(event.pointerId);
  });
  listen(canvas, "pointerup", function () { orbit.dragging = false; });
  listen(canvas, "pointermove", function (event) {
    if (!orbit.dragging) return;
    const dx = event.clientX - orbit.x;
    const dy = event.clientY - orbit.y;
    orbit.x = event.clientX;
    orbit.y = event.clientY;
    orbit.theta -= dx * 0.008;
    orbit.phi -= dy * 0.006;
    placeCamera();
  });
  listen(canvas, "wheel", function (event) {
    event.preventDefault();
    orbit.radius = Math.max(5, Math.min(16, orbit.radius + event.deltaY * 0.01));
    placeCamera();
  }, { passive: false });

  function resize() {
    const width = stage.clientWidth || 640;
    const height = Math.max(280, Math.min(520, Math.round(width * 0.62)));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(stage);
  resize();
  placeCamera();

  active = {
    stop: false,
    frame: 0,
    renderer: renderer,
    scene: scene,
    links: linkMeshes,
    listeners: listeners,
    observer: observer
  };

  const clock = new THREE.Clock();
  function frame() {
    if (!active || active.stop) return;
    const t = clock.getElapsedTime();
    meshes.forEach(function (mesh, i) {
      mesh.material.emissiveIntensity = 0.25 + 0.2 * Math.sin(t * 1.6 + i);
    });
    linkMeshes.forEach(function (entry, i) {
      if (down[entry.id]) return;
      entry.group.userData.glow.material.opacity = 0.18 + 0.16 * Math.sin(t * 2.2 + i);
    });
    renderer.render(scene, camera);
    active.frame = requestAnimationFrame(frame);
  }
  frame();
  describe();
  return { destroy: destroy };
}

window.UCTopology = { mount: mount, destroy: destroy };
