/* Campus service worker. Shell is precached. Lessons fill the cache as they are opened
   and when the page asks for a full offline copy. */
"use strict";

var CACHE = "uc-lab-v21-app";
var SHELL = [
  "./uc-lab-free-university.html",
  "./manifest.webmanifest",
  "./assets/app.css",
  "./assets/app.js",
  "./assets/telephony.js",
  "./assets/tools.js",
  "./assets/icon.svg"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(SHELL);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (key) { return key !== CACHE; }).map(function (key) {
        return caches.delete(key);
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
});

function sameOrigin(request) {
  try {
    return new URL(request.url).origin === self.location.origin;
  } catch (err) {
    return false;
  }
}

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET" || !sameOrigin(request)) return;
  event.respondWith(
    caches.open(CACHE).then(function (cache) {
      return cache.match(request).then(function (cached) {
        if (cached) return cached;
        return fetch(request).then(function (response) {
          if (response && response.ok) cache.put(request, response.clone());
          return response;
        }).catch(function () {
          if (request.mode === "navigate") return cache.match("./uc-lab-free-university.html");
          throw new Error("offline");
        });
      });
    })
  );
});
