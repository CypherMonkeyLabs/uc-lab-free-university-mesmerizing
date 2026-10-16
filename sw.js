/* Same-origin cache for the UC university shell. */
var CACHE = "uc-university-r6";
var SHELL = [
  "./",
  "./index.html",
  "./start.html",
  "./diagrams.html",
  "./flows.html",
  "./downloads.html",
  "./play.html",
  "./listen.html",
  "./help.html",
  "./legal.html",
  "./ecosystem.html",
  "./assets/css/canon.css",
  "./assets/css/frame.css",
  "./assets/css/footer.css",
  "./assets/css/uc.css",
  "./assets/js/frame.js",
  "./assets/js/university.js",
  "./guide/guide.js",
  "./guide/guide.css",
  "./assets/data/catalog.json",
  "./favicon.svg"
];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) {
    return cache.addAll(SHELL);
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
    return caches.match(request);
  }));
});
