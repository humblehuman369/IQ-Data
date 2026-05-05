import type { LucideIcon } from 'lucide-react';

export function MetricCard({ label, value, icon: Icon, tone = 'green' }: { label: string; value: string; icon: LucideIcon; tone?: 'green' | 'blue' | 'amber' | 'slate' }) {
  const tones = {
    green: 'bg-emerald-50 text-emerald-800 ring-emerald-100',
    blue: 'bg-sky-50 text-sky-800 ring-sky-100',
    amber: 'bg-amber-50 text-amber-900 ring-amber-100',
    slate: 'bg-slate-50 text-slate-800 ring-slate-100',
  };
  return (
    <section className="rounded-3xl bg-white/86 p-5 shadow-sm ring-1 ring-black/5 backdrop-blur">
      <div className={`mb-4 inline-flex rounded-2xl p-3 ring-1 ${tones[tone]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
    </section>
  );
}
