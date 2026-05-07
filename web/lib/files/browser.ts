import fs from "node:fs";
import path from "node:path";

const MAX_BYTES = 1_048_576; // 1 MB

export type Entry = { name: string; kind: "file" | "dir"; size?: number };
export type Listing = { entries: Entry[] };
export type ReadResult = { content: string; truncated: boolean };

export interface FilesBrowser {
  list(rel: string): Listing;
  read(rel: string): ReadResult;
}

export function createBrowser(projectRoot: string): FilesBrowser {
  const rootReal = fs.realpathSync(projectRoot);
  const outputsRoot = path.join(rootReal, "outputs");
  const watchlistPath = path.join(rootReal, "watchlist.md");

  function assertInsideSandbox(abs: string): void {
    const insideOutputs =
      abs === outputsRoot || abs.startsWith(outputsRoot + path.sep);
    const isWatchlist = abs === watchlistPath;
    if (!insideOutputs && !isWatchlist) {
      throw new Error(`sandbox_violation: ${abs}`);
    }
  }

  function resolveAndCheck(rel: string): string {
    if (path.isAbsolute(rel)) {
      throw new Error("sandbox_violation: absolute paths not permitted");
    }
    const cleaned = rel.replace(/^\/+/, "");
    if (cleaned === "" || cleaned === ".") {
      return rootReal;
    }
    if (cleaned === "watchlist.md") {
      if (!fs.existsSync(watchlistPath)) throw new Error("not_found");
      const real = fs.realpathSync(watchlistPath);
      // The watchlist must resolve to itself or to an outputs/ file — anything else is a sandbox escape.
      if (real !== watchlistPath) {
        assertInsideSandbox(real);
      }
      return real;
    }
    const candidate = path.resolve(rootReal, cleaned);
    let real: string;
    try {
      real = fs.realpathSync(candidate);
    } catch {
      // File doesn't exist — still apply sandbox check on the candidate path so
      // we don't leak structure for paths outside the sandbox.
      const candidateNormalized = path.resolve(candidate);
      assertInsideSandbox(candidateNormalized);
      throw new Error("not_found");
    }
    assertInsideSandbox(real);
    return real;
  }

  return {
    list(rel: string): Listing {
      if (rel === "" || rel === ".") {
        const entries: Entry[] = [];
        if (fs.existsSync(outputsRoot)) entries.push({ name: "outputs", kind: "dir" });
        if (fs.existsSync(watchlistPath)) {
          const stat = fs.statSync(watchlistPath);
          entries.push({ name: "watchlist.md", kind: "file", size: stat.size });
        }
        return { entries };
      }
      const abs = resolveAndCheck(rel);
      const stat = fs.statSync(abs);
      if (!stat.isDirectory()) throw new Error("not_directory");
      const names = fs.readdirSync(abs);
      const entries: Entry[] = names
        .map((name) => {
          const child = path.join(abs, name);
          // Use lstatSync so symlinks are detected and filtered out below
          // (instead of being reported with target metadata, which leaks structure).
          const cs = fs.lstatSync(child);
          if (cs.isSymbolicLink()) return null;
          return cs.isDirectory()
            ? ({ name, kind: "dir" } as Entry)
            : ({ name, kind: "file", size: cs.size } as Entry);
        })
        .filter((e): e is Entry => e !== null)
        .sort((a, b) => {
          if (a.kind !== b.kind) return a.kind === "dir" ? -1 : 1;
          return a.name.localeCompare(b.name);
        });
      return { entries };
    },

    read(rel: string): ReadResult {
      const abs = resolveAndCheck(rel);
      const stat = fs.statSync(abs);
      if (stat.isDirectory()) throw new Error("is_directory");
      if (stat.size <= MAX_BYTES) {
        return { content: fs.readFileSync(abs, "utf8"), truncated: false };
      }
      const fd = fs.openSync(abs, "r");
      try {
        const buf = Buffer.alloc(MAX_BYTES);
        fs.readSync(fd, buf, 0, MAX_BYTES, 0);
        return { content: buf.toString("utf8"), truncated: true };
      } finally {
        fs.closeSync(fd);
      }
    },
  };
}
