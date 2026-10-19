/* Same-origin cache for the UC university shell.
   Scope is the directory that contains this file. Register with { scope: "./" }. */
var CACHE = "uc-university-r12";
var SHELL = [
  "./",
  "./index.html",
  "./offline.html",
  "./start.html",
  "./play.html",
  "./sim.html",
  "./listen.html",
  "./downloads.html",
  "./diagrams.html",
  "./help.html",
  "./rooms/sip-transactions.html",
  "./manifest.webmanifest",
  "./favicon.svg",
  "./assets/icon-192.png",
  "./assets/icon-512.png",
  "./assets/icon-maskable-512.png",
  "./assets/css/canon.css",
  "./assets/css/shell.css",
  "./assets/css/wow.css",
  "./assets/css/frame.css",
  "./assets/css/polish.css",
  "./assets/css/footer.css",
  "./assets/css/university.css",
  "./assets/css/uc.css",
  "./assets/css/studio.css",
  "./assets/js/frame.js",
  "./assets/js/canon-theme.js",
  "./assets/js/university.js",
  "./assets/js/studio.js",
  "./assets/js/dialsim.js",
  "./assets/fonts/outfit-latin.woff2",
  "./guide/guide.js",
  "./guide/guide.css",
  "./guide/dragbot.js",
  "./guide/ucbot-host.js",
  "./shared/pybot-chat/engine.js",
  "./shared/pybot-chat/ui.js",
  "./shared/pybot-chat/chat.css",
  "./js/content/ucbot-index.json"
];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) {
    return Promise.all(SHELL.map(function (url) {
      return cache.add(url).catch(function () { return null; });
    }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (key) { return key !== CACHE; }).map(function (key) {
      return caches.delete(key);
    }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET") return;
  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  event.respondWith(fetch(request).then(function (response) {
    if (response && response.ok && response.type === "basic") {
      var copy = response.clone();
      caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
    }
    return response;
  }).catch(function () {
    return caches.match(request).then(function (cached) {
      if (cached) return cached;
      if (request.mode === "navigate") return caches.match("./offline.html");
      return caches.match("./offline.html");
    });
  }));
});
