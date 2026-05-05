export const PIPELINE_STAGES = ["Acquisition", "Rehab", "Listed", "Sold"] as const;
export const COLLABORATOR_ROLES = ["owner", "editor", "viewer"] as const;
export const EXPENSE_CATEGORIES = ["labor", "materials", "permits"] as const;
export const DOCUMENT_TYPES = ["contracts", "photos", "inspection_reports", "other"] as const;

export type PipelineStage = (typeof PIPELINE_STAGES)[number];
export type CollaboratorRole = (typeof COLLABORATOR_ROLES)[number];
export type ExpenseCategory = (typeof EXPENSE_CATEGORIES)[number];
export type DocumentType = (typeof DOCUMENT_TYPES)[number];

export type DealInput = {
  purchasePrice: number;
  repairCosts: number;
  arv: number;
  downPayment: number;
  loanAmount: number;
  interestRate: number;
  holdingMonths: number;
  closingCosts: number;
  sellingCosts: number;
};

const round = (value: number) => Number.isFinite(value) ? Math.round(value * 100) / 100 : 0;

export function calculateDeal(input: DealInput) {
  const monthlyInterest = input.loanAmount * (input.interestRate / 100 / 12);
  const financingCost = monthlyInterest * input.holdingMonths;
  const totalInvested = input.purchasePrice + input.repairCosts + input.closingCosts + input.sellingCosts + financingCost;
  const cashInvested = input.downPayment + input.repairCosts + input.closingCosts + financingCost;
  const profit = input.arv - totalInvested;
  const roi = totalInvested > 0 ? (profit / totalInvested) * 100 : 0;
  const cashOnCashReturn = cashInvested > 0 ? (profit / cashInvested) * 100 : 0;

  return {
    profit: round(profit),
    roi: round(roi),
    cashOnCashReturn: round(cashOnCashReturn),
    totalInvested: round(totalInvested),
    cashInvested: round(cashInvested),
    financingCost: round(financingCost),
  };
}

export function estimateArvFromComps(comps: Array<{ salePrice: number; sqft: number }>, targetSqft?: number) {
  const valid = comps.filter((comp) => comp.salePrice > 0);
  if (valid.length === 0) {
    return { estimatedArv: 0, averageSalePrice: 0, averagePricePerSqft: 0, compCount: 0 };
  }
  const averageSalePrice = valid.reduce((sum, comp) => sum + comp.salePrice, 0) / valid.length;
  const ppsfComps = valid.filter((comp) => comp.sqft > 0);
  const averagePricePerSqft = ppsfComps.length > 0 ? ppsfComps.reduce((sum, comp) => sum + comp.salePrice / comp.sqft, 0) / ppsfComps.length : 0;
  const estimatedArv = targetSqft && targetSqft > 0 && averagePricePerSqft > 0 ? targetSqft * averagePricePerSqft : averageSalePrice;

  return {
    estimatedArv: round(estimatedArv),
    averageSalePrice: round(averageSalePrice),
    averagePricePerSqft: round(averagePricePerSqft),
    compCount: valid.length,
  };
}
