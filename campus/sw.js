/* Campus service worker. Shell is precached. Lessons fill the cache as they are opened
   and when the page asks for a full offline copy. */
"use strict";

var CACHE = "uc-lab-v23-sources";
var SHELL = [
  "./uc-lab-free-university.html",
  "./manifest.webmanifest",
  "./assets/app.css",
  "./assets/app.js",
  "./assets/telephony.js",
  "./assets/tools.js",
  "./assets/settings.js",
  "./assets/tips.js",
  "./assets/go-deeper.js",
  "./assets/icon.svg"
];
/* Not precached. The fetch handler stores these on first use, and Save lessons
   offline requests them so a later offline visit can open the ladders and quiz. */
var LAZY = [
  "./assets/labs/restored-walks.js",
  "./assets/curriculum/walks.js",
  "./assets/labs.js",
  "./assets/labs.css",
  "./assets/app-labs.js",
  "./assets/app-drills.js"
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

function lazyAsset(url) {
  var path = url.pathname;
  for (var i = 0; i < LAZY.length; i++) {
    if (path.endsWith(LAZY[i].replace(/^\.\//, "/"))) return true;
  }
  return false;
}

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET" || !sameOrigin(request)) return;
  event.respondWith(
    caches.open(CACHE).then(function (cache) {
      return cache.match(request).then(function (cached) {
        if (cached) return cached;
        return fetch(request).then(function (response) {
          if (response && response.ok) {
            cache.put(request, response.clone());
          }
          return response;
        }).catch(function () {
          if (lazyAsset(new URL(request.url))) return cache.match(request);
          if (request.mode === "navigate") return cache.match("./uc-lab-free-university.html");
          throw new Error("offline");
        });
      });
    })
  );
});
