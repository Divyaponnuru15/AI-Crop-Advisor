const CACHE_NAME = "crop-planner-cache-v1";
const OFFLINE_URL = "/offline.html";

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll([
        "/",
        OFFLINE_URL,
        "/static/style.css",
        "/static/manifest.json",
        "/static/icon-192.png",
        "/static/icon-512.png",
      ]);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  console.log("Service Worker Activated");
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
  const request = event.request;

  // Handle POST requests (like form submission) gracefully
  if (request.method === "POST") {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({ error: "You are offline. Please try again when connected." }),
          { headers: { "Content-Type": "application/json" } }
        );
      })
    );
    return;
  }

  // Handle GET requests (static files / pages)
  event.respondWith(
    fetch(request)
      .then(response => {
        return response;
      })
      .catch(() => {
        return caches.match(request).then(cachedResponse => {
          return cachedResponse || caches.match(OFFLINE_URL);
        });
      })
  );
});