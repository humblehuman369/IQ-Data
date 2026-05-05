'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Calculator, Percent, WalletCards } from 'lucide-react';
import { useForm, useWatch } from 'react-hook-form';
import { toast } from 'sonner';
import { flipcycleApi } from '@/lib/api';
import { dealFormSchema, type DealFormValues } from '@/lib/forms';
import { calculateDeal } from '@/lib/workcycle';

const defaultValues: DealFormValues = {
  purchasePrice: 218000,
  repairCosts: 62000,
  arv: 372000,
  downPayment: 43600,
  loanAmount: 174400,
  interestRate: 9.5,
  holdingMonths: 7,
  closingCosts: 8400,
  sellingCosts: 21500,
};

const fields: Array<{ name: keyof DealFormValues; label: string; prefix?: string; suffix?: string }> = [
  { name: 'purchasePrice', label: 'Purchase price', prefix: '$' },
  { name: 'repairCosts', label: 'Repair costs', prefix: '$' },
  { name: 'arv', label: 'After-repair value', prefix: '$' },
  { name: 'downPayment', label: 'Down payment', prefix: '$' },
  { name: 'loanAmount', label: 'Loan amount', prefix: '$' },
  { name: 'interestRate', label: 'Interest rate', suffix: '%' },
  { name: 'holdingMonths', label: 'Holding months' },
  { name: 'closingCosts', label: 'Closing costs', prefix: '$' },
  { name: 'sellingCosts', label: 'Selling costs', prefix: '$' },
];

const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

export function DealAnalyzer() {
  const form = useForm<DealFormValues>({ resolver: zodResolver(dealFormSchema), defaultValues });
  const values = useWatch({ control: form.control });
  const liveMetrics = calculateDeal({ ...defaultValues, ...values });
  const mutation = useMutation({
    mutationFn: flipcycleApi.calculateDeal,
    onSuccess: () => toast.success('Deal analysis validated by the API contract.'),
    onError: (error) => toast.error(error.message),
  });

  const onSubmit = form.handleSubmit((payload) => mutation.mutate(payload));

  return (
    <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
      <form onSubmit={onSubmit} className="rounded-3xl bg-white/90 p-6 shadow-sm ring-1 ring-black/5">
        <div className="mb-5 flex items-center gap-3">
          <div className="rounded-2xl bg-emerald-100 p-3 text-emerald-800"><Calculator className="h-5 w-5" /></div>
          <div>
            <h2 className="text-2xl font-semibold text-slate-950">Deal analyzer</h2>
            <p className="text-sm text-slate-500">React Hook Form and Zod validate the same inputs sent to FastAPI.</p>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {fields.map((field) => (
            <label key={field.name} className="space-y-2 text-sm font-medium text-slate-700">
              <span>{field.label}</span>
              <div className="flex items-center rounded-2xl border border-slate-200 bg-slate-50 px-3 focus-within:border-emerald-500 focus-within:ring-2 focus-within:ring-emerald-100">
                {field.prefix && <span className="text-slate-400">{field.prefix}</span>}
                <input className="w-full bg-transparent px-2 py-3 outline-none" type="number" step="0.01" {...form.register(field.name, { valueAsNumber: true })} />
                {field.suffix && <span className="text-slate-400">{field.suffix}</span>}
              </div>
            </label>
          ))}
        </div>
        <button type="submit" className="focus-ring mt-6 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-800">
          Validate scenario
        </button>
      </form>

      <aside className="grid gap-4">
        <div className="rounded-3xl bg-slate-950 p-6 text-white shadow-lg">
          <p className="text-sm font-medium text-emerald-200">Projected profit</p>
          <p className="mt-3 text-5xl font-semibold tracking-tight">{currency.format(liveMetrics.profit)}</p>
          <p className="mt-3 text-sm text-slate-300">Total invested: {currency.format(liveMetrics.totalInvested)}</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-3xl bg-white/90 p-5 shadow-sm ring-1 ring-black/5">
            <Percent className="h-5 w-5 text-emerald-700" />
            <p className="mt-4 text-sm text-slate-500">ROI</p>
            <p className="text-3xl font-semibold">{liveMetrics.roi}%</p>
          </div>
          <div className="rounded-3xl bg-white/90 p-5 shadow-sm ring-1 ring-black/5">
            <WalletCards className="h-5 w-5 text-sky-700" />
            <p className="mt-4 text-sm text-slate-500">Cash-on-cash</p>
            <p className="text-3xl font-semibold">{liveMetrics.cashOnCashReturn}%</p>
          </div>
        </div>
      </aside>
    </section>
  );
}
