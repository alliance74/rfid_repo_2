const CACHE_NAME = 'nexus-pos-v2';

// The essential files to make the UI look right offline
const ASSETS_TO_CACHE = [
  '/',
  '/static/dist/output.css',
  '/static/manifest.json'
];

// Install Phase: Safe Caching
self.addEventListener('install', (event) => {
  console.log('✅ Service Worker: Installing and caching assets...');
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // We loop through the array and catch errors individually
      // This prevents the "All-or-Nothing" crash!
      return Promise.allSettled(
        ASSETS_TO_CACHE.map(url => {
          return cache.add(url).catch(err => console.warn(`⚠️ PWA: Failed to cache ${url}`, err));
        })
      );
    }).then(() => {
      self.skipWaiting(); // Force activation
    })
  );
});

// Activate Phase: Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Activated!');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('🧹 PWA: Clearing old cache');
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Phase: Network First, then Cache
self.addEventListener('fetch', (event) => {
  // We only want to handle GET requests (not POST requests like your checkout API)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});