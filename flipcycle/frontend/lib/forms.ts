import { z } from 'zod';

const money = z.number().finite().min(0).max(100_000_000);

export const dealFormSchema = z.object({
  purchasePrice: money,
  repairCosts: money,
  arv: money,
  downPayment: money,
  loanAmount: money,
  interestRate: z.number().finite().min(0).max(50),
  holdingMonths: z.number().int().min(0).max(120),
  closingCosts: money,
  sellingCosts: money,
});

export type DealFormValues = z.infer<typeof dealFormSchema>;
