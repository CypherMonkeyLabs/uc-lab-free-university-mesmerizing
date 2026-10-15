
var CACHE = "uc-flagship-v1";
var CORE = ["./index.html", "./assets/site.css", "./assets/site.js", "./assets/play.js", "./assets/bank.js", "./assets/icon.svg", "./manifest.webmanifest"];
self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) { return cache.addAll(CORE); }));
});
self.addEventListener("activate", function (event) {
  event.waitUntil(self.clients.claim());
});
self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;
  event.respondWith(caches.match(event.request).then(function (hit) {
    var fetched = fetch(event.request).then(function (res) {
      if (res && res.status === 200) {
        var copy = res.clone();
        caches.open(CACHE).then(function (cache) { cache.put(event.request, copy); });
      }
      return res;
    }).catch(function () { return hit; });
    return hit || fetched;
  }));
});
