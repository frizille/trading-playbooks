import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createBrowser } from "@/lib/files/browser";

describe("files browser sandbox", () => {
  let projectRoot: string;
  beforeEach(() => {
    projectRoot = fs.mkdtempSync(path.join(os.tmpdir(), "cockpit-test-"));
    fs.mkdirSync(path.join(projectRoot, "outputs", "F"), { recursive: true });
    fs.writeFileSync(path.join(projectRoot, "outputs", "F", "report.md"), "# Hello\n", "utf8");
    fs.writeFileSync(path.join(projectRoot, "outputs", "summary.md"), "summary\n", "utf8");
    fs.writeFileSync(path.join(projectRoot, "watchlist.md"), "# Watchlist\n", "utf8");
    fs.writeFileSync(path.join(projectRoot, "secret.csv"), "ssn,1234", "utf8");
  });
  afterEach(() => fs.rmSync(projectRoot, { recursive: true, force: true }));

  it("lists sandbox roots when path is empty", () => {
    const b = createBrowser(projectRoot);
    const out = b.list("");
    const names = out.entries.map((e) => e.name).sort();
    expect(names).toEqual(["outputs", "watchlist.md"]);
  });

  it("lists outputs subdir contents (dirs first then files alphabetical)", () => {
    const b = createBrowser(projectRoot);
    const out = b.list("outputs");
    expect(out.entries[0].name).toBe("F");
    expect(out.entries[0].kind).toBe("dir");
    expect(out.entries[1].name).toBe("summary.md");
    expect(out.entries[1].kind).toBe("file");
  });

  it("lists nested directory contents", () => {
    const b = createBrowser(projectRoot);
    const out = b.list("outputs/F");
    expect(out.entries.find((e) => e.name === "report.md")).toBeTruthy();
  });

  it("reads watchlist.md", () => {
    const b = createBrowser(projectRoot);
    const r = b.read("watchlist.md");
    expect(r.content).toMatch(/Watchlist/);
    expect(r.truncated).toBe(false);
  });

  it("reads files inside outputs", () => {
    const b = createBrowser(projectRoot);
    const r = b.read("outputs/F/report.md");
    expect(r.content).toMatch(/Hello/);
  });

  it("rejects listing outside the sandbox", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.list("..")).toThrowError(/sandbox/);
    expect(() => b.list("../etc")).toThrowError(/sandbox/);
  });

  it("rejects reading outside the sandbox", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.read("secret.csv")).toThrowError(/sandbox/);
  });

  it("rejects traversal via ../ segments inside paths", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.read("outputs/../secret.csv")).toThrowError(/sandbox/);
    expect(() => b.read("outputs/F/../../../secret.csv")).toThrowError(/sandbox/);
  });

  it("rejects absolute paths", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.read("/etc/passwd")).toThrowError(/sandbox/);
  });

  it("resolves symlinks before sandbox check (rejects symlink to outside)", () => {
    const target = path.join(projectRoot, "secret.csv");
    const link = path.join(projectRoot, "outputs", "leak.md");
    fs.symlinkSync(target, link);
    const b = createBrowser(projectRoot);
    expect(() => b.read("outputs/leak.md")).toThrowError(/sandbox/);
  });

  it("truncates files larger than 1 MB and sets truncated flag", () => {
    const b = createBrowser(projectRoot);
    const big = path.join(projectRoot, "outputs", "big.md");
    fs.writeFileSync(big, "x".repeat(1_500_000), "utf8");
    const r = b.read("outputs/big.md");
    expect(r.truncated).toBe(true);
    expect(r.content.length).toBeLessThanOrEqual(1_048_576);
  });

  it("throws not_directory when listing a file path", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.list("watchlist.md")).toThrowError(/not_directory/);
  });

  it("throws is_directory when reading a directory path", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.read("outputs")).toThrowError(/is_directory/);
  });

  it("throws not_found when reading a missing file inside the sandbox", () => {
    const b = createBrowser(projectRoot);
    expect(() => b.read("outputs/missing.md")).toThrowError();
  });

  it("rejects watchlist.md when it is a symlink pointing outside the sandbox", () => {
    // Replace the regular watchlist.md with a symlink to secret.csv (outside sandbox).
    const watchlist = path.join(projectRoot, "watchlist.md");
    fs.unlinkSync(watchlist);
    fs.symlinkSync(path.join(projectRoot, "secret.csv"), watchlist);
    const b = createBrowser(projectRoot);
    expect(() => b.read("watchlist.md")).toThrowError(/sandbox/);
  });

  it("filters symlinks out of directory listings", () => {
    const target = path.join(projectRoot, "secret.csv");
    const link = path.join(projectRoot, "outputs", "leak.md");
    fs.symlinkSync(target, link);
    const b = createBrowser(projectRoot);
    const out = b.list("outputs");
    const names = out.entries.map((e) => e.name);
    expect(names).not.toContain("leak.md");
  });
});
