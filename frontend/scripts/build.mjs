import { spawn } from "node:child_process";
import { gzipSync } from "node:zlib";
import { readdir, readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join, relative } from "node:path";
import { loadEnv } from "vite";

const ROOT_DIR = fileURLToPath(new URL("..", import.meta.url));
const DIST_DIR = fileURLToPath(new URL("../dist", import.meta.url));
const MAX_GZIP_BYTES = 250 * 1024;
const PRODUCTION_API_PLACEHOLDER = "https://api.dachuang.com";

function validateProductionEnv() {
  const env = loadEnv("production", ROOT_DIR, "");
  const apiBaseUrl = (env.VITE_API_BASE_URL || "").trim().replace(/\/+$/, "");
  if (!apiBaseUrl) return;

  if (/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(apiBaseUrl)) {
    throw new Error(
      "VITE_API_BASE_URL must not point to a local backend in production builds.",
    );
  }

  if (apiBaseUrl === PRODUCTION_API_PLACEHOLDER) {
    throw new Error(
      "VITE_API_BASE_URL must be changed from the placeholder production host.",
    );
  }
}

const run = (command, args) =>
  new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: ROOT_DIR,
      stdio: "inherit",
    });

    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(
        new Error(
          signal
            ? `${command} terminated with signal ${signal}`
            : `${command} exited with code ${code}`,
        ),
      );
    });
  });

async function collectFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map(async (entry) => {
      const path = join(directory, entry.name);
      return entry.isDirectory() ? collectFiles(path) : path;
    }),
  );
  return files.flat();
}

async function enforceBundleBudget() {
  const files = await collectFiles(DIST_DIR);
  const oversized = [];

  for (const file of files) {
    const metadata = await stat(file);
    if (!metadata.isFile()) continue;

    const gzipSize = gzipSync(await readFile(file)).byteLength;
    if (gzipSize > MAX_GZIP_BYTES) {
      oversized.push({
        file: relative(DIST_DIR, file).replace(/\\/g, "/"),
        gzipSize,
      });
    }
  }

  if (oversized.length === 0) return;

  const formattedLimit = `${Math.round(MAX_GZIP_BYTES / 1024)} KiB`;
  const formattedFiles = oversized
    .sort((a, b) => b.gzipSize - a.gzipSize)
    .map(({ file, gzipSize }) => `- ${file}: ${Math.round(gzipSize / 1024)} KiB gzip`)
    .join("\n");

  throw new Error(
    `Bundle budget exceeded. Limit: ${formattedLimit} gzip per asset.\n${formattedFiles}`,
  );
}

validateProductionEnv();
await run("node", ["./node_modules/vue-tsc/bin/vue-tsc.js", "--noEmit"]);
await run("node", ["./node_modules/vite/bin/vite.js", "build"]);
await enforceBundleBudget();
