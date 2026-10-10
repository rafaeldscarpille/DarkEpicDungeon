const CACHE = "ded-web-v4.19.0-pirata-padrao-jogo";

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || !req.url.startsWith(self.location.origin)) return;
  // vídeos (e pedidos parciais/range) vão direto à rede: o cache não guarda respostas 206
  if (new URL(req.url).pathname.match(/\.(mp4|webm)$/) || req.headers.has("range")) return;
  // sinalização de rede e ranking online sempre direto da rede
  if (new URL(req.url).pathname.includes("/api/") || new URL(req.url).pathname.endsWith("online-config.json")) return;
  const isDynamic = req.mode === "navigate" || new URL(req.url).pathname.endsWith("/index.html") || new URL(req.url).pathname.includes("index-") || new URL(req.url).pathname.includes("network-coop") || new URL(req.url).pathname.includes("user-auth");
  if (isDynamic) {
    // Página principal e scripts: sempre da rede (cópia guardada só se estiver offline).
    // Atenção: um pedido de navegação não pode ser repassado com opções extras —
    // fetch(req, {...}) falha e caía na cópia antiga para sempre. Por isso usamos a URL.
    e.respondWith(
      fetch(req.url, { cache: "no-cache", credentials: "same-origin" })
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }
  e.respondWith(
    caches.match(req).then(
      (hit) =>
        hit ||
        fetch(req, { cache: "no-cache" }).then((res) => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
    )
  );
});
