import * as THREE from "./vendor/three.module.js";
import { animate } from "./vendor/anime.esm.min.js";
import rough from "./vendor/rough.esm.js";

const reduce = document.documentElement.getAttribute("data-motion") === "reduce"
  || window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function mountHero(canvas) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    if (!renderer.getContext()) throw new Error("no webgl context");
  } catch (err) {
    canvas.hidden = true;
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 40);
  camera.position.set(0, 1.4, 7.2);
  const colors = [0xf0b429, 0x0f6e62, 0xa34b24, 0x4c3d8f];
  const names = ["Phone", "CUCM", "CUBE", "Cloud"];
  const meshes = names.map(function (name, i) {
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.78, 0.78, 0.78),
      new THREE.MeshStandardMaterial({ color: colors[i], roughness: 0.45, metalness: 0.05 })
    );
    mesh.position.set((i - 1.5) * 1.45, 0.2, 0);
    mesh.userData.name = name;
    scene.add(mesh);
    return mesh;
  });
  const lines = [];
  for (let i = 0; i < meshes.length - 1; i += 1) {
    const geo = new THREE.BufferGeometry().setFromPoints([meshes[i].position, meshes[i + 1].position]);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0x7dcec4 }));
    line.userData.link = ["phone-cucm", "cucm-cube", "cube-pstn"][i] || "cucm-webex";
    scene.add(line);
    lines.push(line);
  }
  scene.add(new THREE.AmbientLight(0xffffff, 0.75));
  const sun = new THREE.DirectionalLight(0xffffff, 1.2);
  sun.position.set(3, 5, 4);
  scene.add(sun);
  document.querySelectorAll("[data-break]").forEach(function (box) {
    box.addEventListener("change", function () {
      const id = box.getAttribute("data-break");
      lines.forEach(function (line) {
        if (line.userData.link === id) line.visible = !box.checked;
      });
    });
  });
  function size() {
    const w = canvas.clientWidth || 480;
    const h = canvas.clientHeight || 220;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
  }
  size();
  window.addEventListener("resize", size);
  function frame(t) {
    meshes.forEach(function (mesh, i) {
      mesh.rotation.y = t * 0.00045 + i * 0.4;
      mesh.position.y = 0.2 + Math.sin(t * 0.001 + i) * 0.08;
    });
    renderer.render(scene, camera);
    if (!reduce) requestAnimationFrame(frame);
  }
  if (reduce) renderer.render(scene, camera);
  else requestAnimationFrame(frame);
}

function mountMini(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 20);
  camera.position.set(1.6, 1.1, 2.4);
  const mesh = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.7, 0),
    new THREE.MeshStandardMaterial({ color: 0x0f6e62, flatShading: true })
  );
  scene.add(mesh);
  scene.add(new THREE.AmbientLight(0xffffff, 0.8));
  const sun = new THREE.DirectionalLight(0xffffff, 1);
  sun.position.set(2, 3, 2);
  scene.add(sun);
  const w = canvas.clientWidth || 120;
  const h = canvas.clientHeight || 120;
  renderer.setSize(w, h, false);
  function frame(t) {
    mesh.rotation.y = t * 0.001;
    mesh.rotation.x = 0.4;
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
      rotate: [-4, 4],
      duration: 1600,
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
    host.appendChild(rc.rectangle(node[0], node[1], 150, 54, { roughness: 1.3, stroke: "#0f6e62", fill: "#e7f6f2", fillStyle: "hachure" }));
    if (i < nodes.length - 1) {
      host.appendChild(rc.line(node[0] + 150, node[1] + 27, nodes[i + 1][0], nodes[i + 1][1] + 27, { stroke: "#a34b24", roughness: 1.2 }));
    }
  });
  nodes.forEach(function (node) {
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", String(node[0] + 75));
    text.setAttribute("y", String(node[1] + 33));
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", "14");
    text.textContent = node[2];
    host.appendChild(text);
  });
}

const hero = document.querySelector("#hero3d");
if (hero) mountHero(hero);
document.querySelectorAll("[data-mini3d]").forEach(mountMini);
mountCounts();
mountMascots();
mountRough();
