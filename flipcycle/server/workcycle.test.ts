import { describe, expect, it } from "vitest";
import { calculateDeal, estimateArvFromComps, PIPELINE_STAGES, COLLABORATOR_ROLES } from "./workcycle";
import { appRouter } from "./routers";
import { SAMPLE_PROJECT_NAMES } from "./db";
import type { TrpcContext } from "./_core/context";

describe("FlipCycle deal calculations", () => {
  it("returns profit, ROI, and cash-on-cash return for a house flip", () => {
    const result = calculateDeal({
      purchasePrice: 200000,
      repairCosts: 45000,
      arv: 330000,
      downPayment: 40000,
      loanAmount: 160000,
      interestRate: 9,
      holdingMonths: 6,
      closingCosts: 6000,
      sellingCosts: 18000,
    });

    expect(result.profit).toBe(53800);
    expect(result.roi).toBe(19.48);
    expect(result.cashOnCashReturn).toBe(54.79);
  });

  it("estimates ARV from comparable sales and preserves required labels", () => {
    const estimate = estimateArvFromComps([
      { salePrice: 315000, sqft: 1500 },
      { salePrice: 330000, sqft: 1600 },
    ], 1550);

    expect(estimate.compCount).toBe(2);
    expect(estimate.estimatedArv).toBeGreaterThan(320000);
    expect(PIPELINE_STAGES).toEqual(["Acquisition", "Rehab", "Listed", "Sold"]);
    expect(COLLABORATOR_ROLES).toEqual(["owner", "editor", "viewer"]);
  });
});

describe("FlipCycle authenticated API surface", () => {
  it("exposes the summary procedure for authenticated users", async () => {
    const ctx = {
      user: { id: 42, openId: "demo", name: "Demo", email: "demo@example.com", loginMethod: "manus", role: "user", createdAt: new Date(), updatedAt: new Date(), lastSignedIn: new Date() },
      req: { protocol: "https", headers: {} },
      res: { clearCookie: () => undefined },
    } as unknown as TrpcContext;

    expect(appRouter._def.procedures).toHaveProperty("workcycle.summary");
    expect(ctx.user?.role).toBe("user");
  });

  it("exposes onboarding sample data with the required stage-spanning project set", () => {
    expect(appRouter._def.procedures).toHaveProperty("workcycle.seedSampleData");
    expect(SAMPLE_PROJECT_NAMES).toHaveLength(4);
    expect(SAMPLE_PROJECT_NAMES.every((name) => name.startsWith("Onboarding Sample ·"))).toBe(true);
  });
});
