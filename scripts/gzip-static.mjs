/* Tiny static server with gzip for text. Used to measure mobile Lighthouse
   the way a normal host serves these files. */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const port = Number(process.env.PORT || 8742);
const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".pdf": "application/pdf",
  ".woff2": "font/woff2"
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://127.0.0.1");
  let file = path.normalize(path.join(root, decodeURIComponent(url.pathname)));
  if (!file.startsWith(root)) {
    res.writeHead(403);
    res.end("no");
    return;
  }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    res.writeHead(404);
    res.end("missing");
    return;
  }
  const ext = path.extname(file);
  const body = fs.readFileSync(file);
  const type = types[ext] || "application/octet-stream";
  const compressible = /text|javascript|json|svg|xml/.test(type);
  const accept = req.headers["accept-encoding"] || "";
  if (compressible && accept.includes("gzip") && body.length > 800) {
    res.writeHead(200, {
      "Content-Type": type,
      "Content-Encoding": "gzip",
      Vary: "Accept-Encoding",
      "Cache-Control": "no-cache"
    });
    res.end(zlib.gzipSync(body, { level: 6 }));
    return;
  }
  res.writeHead(200, { "Content-Type": type, "Cache-Control": "no-cache" });
  res.end(body);
});

server.listen(port, "127.0.0.1", () => {
  console.log("gzip static on " + port);
});
