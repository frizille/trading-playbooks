import { createServer } from "node:http";
import next from "next";
import { WebSocketServer } from "ws";
import { parse } from "node:url";
import path from "node:path";
import { loadEnvConfig } from "@next/env";

// Load .env.local / .env before reading any COCKPIT_* env vars below.
// `tsx server.ts` runs Node directly, so Next's normal env loader never runs.
loadEnvConfig(process.cwd(), process.env.NODE_ENV !== "production");

import { getDb, closeDb } from "@/lib/db";
import { SessionManager } from "@/lib/sessions/manager";
import { attachWsRouter } from "@/lib/ws/router";

const PORT = parseInt(process.env.COCKPIT_PORT ?? "3000", 10);
const HOST = "127.0.0.1"; // hardcoded — never bind 0.0.0.0
const dev = process.env.NODE_ENV !== "production";

function resolveProjectRoot(): string {
  if (process.env.COCKPIT_PROJECT_ROOT) return process.env.COCKPIT_PROJECT_ROOT;
  // Default: parent of web/ — the trading-playbooks repo
  return path.resolve(process.cwd(), "..");
}

async function main() {
  const projectRoot = resolveProjectRoot();
  const app = next({ dev, dir: process.cwd(), hostname: HOST, port: PORT });
  await app.prepare();
  const handle = app.getRequestHandler();
  const nextUpgrade = app.getUpgradeHandler();

  const db = getDb();
  const manager = new SessionManager({
    db,
    bridgeOpts: {
      cwd: projectRoot,
      hangTimeoutMs: parseInt(process.env.COCKPIT_HANG_TIMEOUT_MS ?? "60000", 10),
    },
  });

  const httpServer = createServer((req, res) => {
    const parsedUrl = parse(req.url ?? "/", true);
    handle(req, res, parsedUrl);
  });

  const wss = new WebSocketServer({ noServer: true });
  attachWsRouter(wss, manager, { projectRoot });

  httpServer.on("upgrade", (req, socket, head) => {
    const { pathname } = parse(req.url ?? "/");
    if (pathname === "/ws") {
      wss.handleUpgrade(req, socket, head, (ws) => wss.emit("connection", ws, req));
    } else {
      // Forward all other upgrades (Next.js dev HMR, etc.) to Next's handler.
      // Without this, Turbopack's HMR client fails to connect and breaks
      // hydration in dev mode — nothing clickable.
      void nextUpgrade(req, socket, head);
    }
  });

  httpServer.listen(PORT, HOST, () => {
    // eslint-disable-next-line no-console
    console.log(`[cockpit] http://${HOST}:${PORT}  (project: ${projectRoot})`);
  });

  const shutdown = async (sig: string) => {
    // eslint-disable-next-line no-console
    console.log(`[cockpit] ${sig}: shutting down…`);
    wss.close();
    httpServer.close();
    await manager.shutdown();
    closeDb();
    process.exit(0);
  };
  process.on("SIGTERM", () => void shutdown("SIGTERM"));
  process.on("SIGINT", () => void shutdown("SIGINT"));
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error("[cockpit] fatal:", err);
  process.exit(1);
});
