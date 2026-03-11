import { existsSync } from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

function resolveOutDir(args) {
  let outDir = "dist";
  for (let index = 0; index < args.length; index += 1) {
    const token = args[index];
    if (token === "--outDir" && args[index + 1]) {
      outDir = args[index + 1];
      index += 1;
      continue;
    }
    if (token.startsWith("--outDir=")) {
      outDir = token.slice("--outDir=".length);
    }
  }
  return outDir;
}

const forwardedArgs = process.argv.slice(2);
const outDir = resolveOutDir(forwardedArgs);
const astroCli = path.resolve("node_modules", "astro", "astro.js");

const child = spawn(process.execPath, [astroCli, "build", ...forwardedArgs], {
  stdio: ["ignore", "pipe", "pipe"],
  cwd: process.cwd(),
});

let collected = "";
child.stdout.on("data", (chunk) => {
  const text = String(chunk);
  collected += text;
  process.stdout.write(text);
});
child.stderr.on("data", (chunk) => {
  const text = String(chunk);
  collected += text;
  process.stderr.write(text);
});

child.on("close", (code) => {
  if (code === 0) {
    process.exit(0);
  }

  const hasWindowsBusyCleanupError = collected.includes("EBUSY: resource busy or locked, rmdir");
  const hasOutput = existsSync(path.resolve(outDir, "index.html")) || existsSync(path.resolve(outDir, "feed.xml"));

  if (hasWindowsBusyCleanupError && hasOutput) {
    process.stderr.write(
      "\nwarning: astro build hit a Windows filesystem lock during cleanup, but output artifacts were generated.\n",
    );
    process.exit(0);
  }

  process.exit(code ?? 1);
});
