import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";

const brandedFiles = [
  "../client/index.html",
  "../client/src/components/DashboardLayout.tsx",
  "../client/src/pages/Dashboard.tsx",
  "../client/src/pages/Home.tsx",
  "./db.ts",
  "./workcycle.test.ts",
  "../package.json",
];

describe("FlipCycle branding", () => {
  it("uses FlipCycle in visible copy and metadata instead of the old brand casing", async () => {
    const sources = await Promise.all(
      brandedFiles.map((path) => readFile(new URL(path, import.meta.url), "utf8")),
    );
    const combined = sources.join("\n");

    expect(combined).toContain("FlipCycle");
    expect(combined).not.toMatch(/WorkCycle|Workcycle/);
  });

  it("sets package metadata to the FlipCycle application name", async () => {
    const packageJson = JSON.parse(
      await readFile(new URL("../package.json", import.meta.url), "utf8"),
    ) as { name: string };

    expect(packageJson.name).toBe("flipcycle");
  });
});
