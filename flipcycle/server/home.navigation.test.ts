import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";

const featureRoutes = [
  "/dashboard/analyzer",
  "/dashboard/pipeline",
  "/dashboard/budgets",
  "/dashboard/documents",
  "/dashboard/team",
];

describe("homepage feature navigation", () => {
  it("defines direct protected dashboard destinations for every homepage feature", async () => {
    const homeSource = await readFile(new URL("../client/src/pages/Home.tsx", import.meta.url), "utf8");

    for (const route of featureRoutes) {
      expect(homeSource).toContain(`path: "${route}"`);
    }
  });

  it("renders feature destinations through links instead of homepage-only anchors", async () => {
    const homeSource = await readFile(new URL("../client/src/pages/Home.tsx", import.meta.url), "utf8");
    const featurePathLinks = homeSource.match(/href=\{feature\.path\}/g) ?? [];

    expect(featurePathLinks.length).toBeGreaterThanOrEqual(3);
    expect(homeSource).toContain("Protected workspace page");
  });

  it("registers dashboard section routes through the protected dashboard shell", async () => {
    const appSource = await readFile(new URL("../client/src/App.tsx", import.meta.url), "utf8");

    expect(appSource).toContain('path="/dashboard/:section"');
    expect(appSource).toContain("component={ProtectedDashboard}");
  });
});
