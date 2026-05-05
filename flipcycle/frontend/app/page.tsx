import Link from 'next/link';
import { ArrowRight, BarChart3, Building2, FileText, Users, WalletCards } from 'lucide-react';

const features = [
  { title: 'Deal analyzer', href: '/dashboard?section=analyzer', icon: BarChart3, copy: 'Model purchase price, rehab, financing, ARV, ROI, and cash-on-cash returns.' },
  { title: 'Pipeline board', href: '/dashboard?section=pipeline', icon: Building2, copy: 'Track every flip from acquisition through sold with investor-focused stage context.' },
  { title: 'Budget control', href: '/dashboard?section=budgets', icon: WalletCards, copy: 'Compare estimates and actuals across labor, materials, and permit lines.' },
  { title: 'Documents', href: '/dashboard?section=documents', icon: FileText, copy: 'Organize contracts, inspection reports, photo logs, and closing files.' },
  { title: 'Team workspace', href: '/dashboard?section=team', icon: Users, copy: 'Invite contractors, lenders, and partners with owner/editor/viewer roles.' },
];

export default function HomePage() {
  return (
    <main>
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <Link href="/" className="flex items-center gap-3 font-semibold tracking-tight text-slate-950">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-slate-950 text-white">FC</span>
          <span>FlipCycle</span>
        </Link>
        <div className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
          {features.slice(0, 4).map((feature) => <Link key={feature.title} href={feature.href} className="hover:text-slate-950">{feature.title}</Link>)}
        </div>
        <Link href="/dashboard" className="focus-ring rounded-2xl bg-emerald-700 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-800">Open workspace</Link>
      </nav>

      <section className="mx-auto grid max-w-7xl gap-10 px-6 py-16 lg:grid-cols-[1.08fr_0.92fr] lg:py-24">
        <div>
          <p className="mb-5 inline-flex rounded-full bg-white/80 px-4 py-2 text-sm font-semibold text-emerald-800 ring-1 ring-emerald-100">Next.js + FastAPI conversion ready</p>
          <h1 className="max-w-4xl text-5xl font-semibold tracking-[-0.04em] text-slate-950 md:text-7xl">Run your next profitable flip through FlipCycle.</h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">FlipCycle gives real estate investors one place to analyze deal economics, manage rehab execution, protect documents, and coordinate teams across every property stage.</p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/dashboard" className="focus-ring inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-950 px-6 py-4 font-semibold text-white shadow-md hover:-translate-y-0.5 hover:bg-slate-800">Launch dashboard <ArrowRight className="h-4 w-4" /></Link>
            <Link href="#features" className="focus-ring inline-flex items-center justify-center rounded-2xl bg-white/85 px-6 py-4 font-semibold text-slate-800 ring-1 ring-black/5 hover:bg-white">View workflows</Link>
          </div>
        </div>
        <div className="rounded-[2rem] bg-white/75 p-4 shadow-xl ring-1 ring-black/5 backdrop-blur">
          <div className="rounded-[1.5rem] bg-slate-950 p-6 text-white">
            <div className="mb-8 flex items-center justify-between text-sm text-slate-300"><span>Projected portfolio</span><span>Q2 2026</span></div>
            <p className="text-sm text-emerald-200">Projected profit</p>
            <p className="mt-2 text-6xl font-semibold tracking-tight">$244k</p>
            <div className="mt-8 grid grid-cols-2 gap-3">
              {['14 active deals', '27.4% avg ROI', '$1.2M invested', '4 sold flips'].map((item) => <div key={item} className="rounded-2xl bg-white/10 p-4 text-sm font-medium text-slate-100">{item}</div>)}
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-6 pb-20">
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-5">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link key={feature.title} href={feature.href} className="group rounded-3xl bg-white/82 p-5 shadow-sm ring-1 ring-black/5 transition hover:-translate-y-1 hover:shadow-md">
                <Icon className="h-6 w-6 text-emerald-700" />
                <h2 className="mt-5 text-lg font-semibold text-slate-950">{feature.title}</h2>
                <p className="mt-3 text-sm leading-6 text-slate-600">{feature.copy}</p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-emerald-800">Open section <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" /></span>
              </Link>
            );
          })}
        </div>
      </section>
    </main>
  );
}
