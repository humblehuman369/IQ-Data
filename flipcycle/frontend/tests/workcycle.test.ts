import { describe, expect, it } from 'vitest';
import { calculateDeal, estimateArvFromComps } from '@/lib/workcycle';

describe('FlipCycle calculation contracts', () => {
  it('calculates deal economics using the migrated formula', () => {
    expect(calculateDeal({
      purchasePrice: 218000,
      repairCosts: 62000,
      arv: 372000,
      downPayment: 43600,
      loanAmount: 174400,
      interestRate: 9.5,
      holdingMonths: 7,
      closingCosts: 8400,
      sellingCosts: 21500,
    })).toEqual({
      profit: 52435.33,
      roi: 16.41,
      cashOnCashReturn: 42.4,
      totalInvested: 319564.67,
      cashInvested: 123664.67,
      financingCost: 9664.67,
    });
  });

  it('estimates ARV from comps and target square footage', () => {
    expect(estimateArvFromComps([{ salePrice: 366000, sqft: 1840 }, { salePrice: 381500, sqft: 1925 }], 1880)).toMatchObject({
      estimatedArv: 373269.17,
      compCount: 2,
    });
  });
});
