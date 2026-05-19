import { createServer } from 'http';
import { readFileSync, existsSync } from 'fs';
import { extname, join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = 3000;

const MIME = {
  '.html': 'text/html',
  '.css':  'text/css',
  '.js':   'text/javascript',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
};

createServer((req, res) => {
  let path = req.url === '/' ? '/index.html' : req.url;
  let filePath = join(__dirname, path);

  if (!existsSync(filePath)) {
    filePath = join(__dirname, 'index.html');
  }

  const ext = extname(filePath);
  const mime = MIME[ext] || 'text/plain';
  res.writeHead(200, { 'Content-Type': mime });
  res.end(readFileSync(filePath));
}).listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});