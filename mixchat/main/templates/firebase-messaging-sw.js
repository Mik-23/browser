const CACHE_VERSION = 'v1.0.1';
console.log(`[SW] Service Worker версии ${CACHE_VERSION} загружен`);

self.addEventListener('install', (event) => {
  console.log('📦 install event');
  self.skipWaiting(); // Это заставит новый сервис-воркер немедленно активироваться
});

self.addEventListener('activate', (event) => {
  console.log('📦 activate event');
  event.waitUntil(clients.claim()); // Это позволяет новому сервис-воркеру взять под контроль уже открытые вкладки
});

self.addEventListener('message', event => {
    if (event.data.action === 'getVersion') {
        event.source.postMessage({ version: CACHE_VERSION });
    }
});

self.addEventListener('push', function(event) {
  console.log('🎯 push event получен!');

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