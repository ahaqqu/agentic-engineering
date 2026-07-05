import { execSync, spawn } from "node:child_process";
import { After, AfterAll, Before, BeforeAll, setDefaultTimeout } from "@cucumber/cucumber";
import type { MyWorld } from "./world";

const BASE_PORT = 8787;
const BASE = `http://localhost:${BASE_PORT}`;

setDefaultTimeout(180_000);

let devProc: ReturnType<typeof spawn> | null = null;
let spawned = false;

function waitForHealth(url: string, maxMs = 60_000): Promise<void> {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    function poll() {
      fetch(url)
        .then((r) => (r.ok ? resolve() : retry()))
        .catch(() => retry());
    }
    function retry() {
      if (Date.now() - start > maxMs) reject(new Error(`health check timeout after ${maxMs}ms`));
      else setTimeout(poll, 500);
    }
    poll();
  });
}

async function ensureServer() {
  // Check if already running
  try {
    const res = await fetch(`${BASE}/health`);
    if (res.ok) return;
  } catch {
    /* not running */
  }

  execSync("pnpm exec wrangler d1 migrations apply DB --local 2>&1", { stdio: "pipe" });

  devProc = spawn("pnpm", ["exec", "wrangler", "dev", "--port", String(BASE_PORT)], {
    stdio: "pipe",
    env: {
      ...process.env,
      LD_LIBRARY_PATH: "/tmp/opencode/libfix/usr/lib/x86_64-linux-gnu",
    },
    shell: true,
  });
  spawned = true;

  await waitForHealth(`${BASE}/health`);
}

async function resetDb() {
  execSync(
    `pnpm exec wrangler d1 execute DB --local --command "DELETE FROM items;" 2>/dev/null || true`,
    { stdio: "pipe" },
  );
}

BeforeAll(async () => {
  await ensureServer();
});

AfterAll(async () => {
  if (spawned && devProc?.pid) {
    try {
      process.kill(-devProc.pid);
    } catch {
      devProc.kill();
    }
    devProc = null;
  }
});

Before(async function (this: MyWorld) {
  this.baseURL = BASE;
  this.currentUser = null;
  this.lastResponse = null;
  await resetDb();
});

After(async function (this: MyWorld) {
  if (this.page) {
    try {
      await this.page.close();
    } catch {
      /* ignore */
    }
    this.page = null;
  }
  if (this.context) {
    try {
      await this.context.close();
    } catch {
      /* ignore */
    }
    this.context = null;
  }
  if (this.browser) {
    try {
      await this.browser.close();
    } catch {
      /* ignore */
    }
    this.browser = null;
  }
});
