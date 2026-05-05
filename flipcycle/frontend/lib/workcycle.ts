import type { Comp, DealInput, PipelineStage, Project } from './types';

export const PIPELINE_STAGES: PipelineStage[] = ['Acquisition', 'Rehab', 'Listed', 'Sold'];

const round = (value: number) => (Number.isFinite(value) ? Math.round(value * 100) / 100 : 0);

export function calculateDeal(input: DealInput) {
  const monthlyInterest = input.loanAmount * (input.interestRate / 100 / 12);
  const financingCost = monthlyInterest * input.holdingMonths;
  const totalInvested =
    input.purchasePrice + input.repairCosts + input.closingCosts + input.sellingCosts + financingCost;
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

export function estimateArvFromComps(comps: Array<Pick<Comp, 'salePrice' | 'sqft'>>, targetSqft?: number) {
  const valid = comps.filter((comp) => comp.salePrice > 0);
  if (valid.length === 0) {
    return { estimatedArv: 0, averageSalePrice: 0, averagePricePerSqft: 0, compCount: 0 };
  }
  const averageSalePrice = valid.reduce((sum, comp) => sum + comp.salePrice, 0) / valid.length;
  const ppsfComps = valid.filter((comp) => comp.sqft > 0);
  const averagePricePerSqft = ppsfComps.length
    ? ppsfComps.reduce((sum, comp) => sum + comp.salePrice / comp.sqft, 0) / ppsfComps.length
    : 0;
  const estimatedArv = targetSqft && targetSqft > 0 && averagePricePerSqft > 0 ? targetSqft * averagePricePerSqft : averageSalePrice;
  return {
    estimatedArv: round(estimatedArv),
    averageSalePrice: round(averageSalePrice),
    averagePricePerSqft: round(averagePricePerSqft),
    compCount: valid.length,
  };
}

export function summarizeProjects(projects: Project[]) {
  return {
    activeDeals: projects.filter((project) => project.stage !== 'Sold').length,
    completedFlips: projects.filter((project) => project.stage === 'Sold').length,
    totalInvested: round(projects.reduce((sum, project) => sum + calculateDeal(project).cashInvested, 0)),
    projectedProfit: round(projects.reduce((sum, project) => sum + calculateDeal(project).profit, 0)),
  };
}
