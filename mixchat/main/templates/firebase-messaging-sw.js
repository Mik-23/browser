const CACHE_VERSION = 'v1.0.1';
console.log(`[SW] Service Worker версии ${CACHE_VERSION} загружен`);

self.addEventListener('install', (event) => {
  console.log('install event');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('activate event');
  event.waitUntil(clients.claim());
});

self.addEventListener('message', event => {
    if (event.data.action === 'getVersion') {
        event.source.postMessage({ version: CACHE_VERSION });
    }
});

self.addEventListener('push', function(event) {
  console.log('push event получен!');

  let data = {};
  if (event.data) {
    data = event.data.json();
  }
  const notification = data.notification
  const options = {
    body: notification.body,
    icon: notification.image,
    vibrate: [200, 100, 200, 100, 200, 100, 200],
    tag: "notification-" + Date.now(),

  }

  let promise = self.registration.showNotification(notification.title, options);

  event.waitUntil(promise);
});
