import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { getLoginUrl } from "@/const";
import { ArrowRight, BarChart3, BriefcaseBusiness, Calculator, Check, FileText, KanbanSquare, LockKeyhole, ReceiptText, ShieldCheck, Sparkles, Users } from "lucide-react";

const features = [
  { icon: Calculator, title: "Deal analyzer", path: "/dashboard/analyzer", cta: "Open analyzer", text: "Model purchase price, repairs, ARV, financing, profit, ROI, and cash-on-cash return in one focused workflow." },
  { icon: KanbanSquare, title: "Pipeline tracker", path: "/dashboard/pipeline", cta: "Open pipeline", text: "Move opportunities and active flips through Acquisition, Rehab, Listed, and Sold without losing context." },
  { icon: ReceiptText, title: "Budget controls", path: "/dashboard/budgets", cta: "Open budgets", text: "Track labor, materials, and permits with estimate-versus-actual reporting for every project." },
  { icon: FileText, title: "Documents", path: "/dashboard/documents", cta: "Open documents", text: "Store contracts, photos, and inspection reports with S3-backed references for every active project." },
  { icon: Users, title: "Team collaboration", path: "/dashboard/team", cta: "Open team", text: "Invite collaborators with owner, editor, and viewer access for cleaner accountability." },
];

const pricing = [
  { name: "Solo", price: "$79", note: "For independent investors", items: ["Deal analysis", "Project pipeline", "Budget tracking", "Document storage"] },
  { name: "Team", price: "$199", note: "For active flip teams", items: ["Everything in Solo", "Collaborator roles", "Team dashboards", "Portfolio insights"], featured: true },
  { name: "Business", price: "$499", note: "For scaling operators", items: ["Unlimited projects", "Advanced reporting", "Team permissions", "Priority onboarding"] },
];

const testimonials = [
  { quote: "FlipCycle gives our acquisitions and rehab team a shared operating view before we commit capital.", name: "Maya R.", role: "Principal investor" },
  { quote: "The deal analyzer and budget tracker keep assumptions visible, which makes project meetings far more useful.", name: "Jordan T.", role: "Project manager" },
  { quote: "It feels modern without getting in the way of the numbers we need to make fast decisions.", name: "Elena C.", role: "Operations lead" },
];

const login = () => { window.location.href = getLoginUrl(); };

export default function Home() {
  return (
    <div className="min-h-screen overflow-hidden bg-background text-foreground">
      <header className="sticky top-0 z-50 border-b border-border/70 bg-background/85 backdrop-blur-xl">
        <nav className="container flex h-18 items-center justify-between gap-4 py-4" aria-label="Primary navigation">
          <a href="#top" className="flex items-center gap-3 rounded-2xl outline-none focus-visible:ring-4 focus-visible:ring-sky-100" aria-label="FlipCycle home">
            <span className="brand-gradient flex h-10 w-10 items-center justify-center rounded-2xl text-white shadow-lg shadow-sky-300/30"><BriefcaseBusiness className="h-5 w-5" /></span>
            <span className="text-lg font-semibold tracking-tight">FlipCycle</span>
          </a>
          <div className="hidden items-center gap-7 rounded-full border border-border/80 bg-white/70 px-5 py-3 text-sm font-medium text-muted-foreground shadow-sm md:flex">
            <details className="group relative">
              <summary className="cursor-pointer list-none rounded-xl px-2 py-1 outline-none hover:text-foreground focus-visible:ring-4 focus-visible:ring-sky-100">Features</summary>
              <div className="invisible absolute left-1/2 top-9 z-50 w-72 -translate-x-1/2 rounded-2xl border border-blue-100 bg-white p-2 opacity-0 shadow-2xl shadow-sky-200/40 transition group-open:visible group-open:opacity-100">
                <a href="#features" className="block rounded-xl px-3 py-2 text-sm font-semibold text-slate-950 outline-none hover:bg-sky-50 focus-visible:ring-4 focus-visible:ring-sky-100">Feature overview</a>
                {features.map((feature) => (
                  <a key={feature.path} href={feature.path} className="block rounded-xl px-3 py-2 outline-none hover:bg-sky-50 focus-visible:ring-4 focus-visible:ring-sky-100">
                    <span className="block text-sm font-semibold text-slate-900">{feature.title}</span>
                    <span className="block text-xs text-muted-foreground">Protected workspace page</span>
                  </a>
                ))}
              </div>
            </details>
            <a href="#pricing" className="rounded-xl px-2 py-1 outline-none hover:text-foreground focus-visible:ring-4 focus-visible:ring-sky-100">Pricing</a>
            <a href="#testimonials" className="rounded-xl px-2 py-1 outline-none hover:text-foreground focus-visible:ring-4 focus-visible:ring-sky-100">Customers</a>
            <a href="#security" className="rounded-xl px-2 py-1 outline-none hover:text-foreground focus-visible:ring-4 focus-visible:ring-sky-100">Security</a>
          </div>
          <div className="flex items-center gap-2">
            <details className="relative md:hidden">
              <summary className="list-none rounded-full border border-border bg-white/80 px-4 py-2 text-sm font-medium shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-ring">Menu</summary>
              <div className="absolute right-0 top-12 z-50 w-56 rounded-2xl border bg-white p-3 text-sm shadow-2xl shadow-sky-200/40">
                <a href="#features" className="block rounded-xl px-3 py-2 font-semibold outline-none hover:bg-accent focus-visible:ring-4 focus-visible:ring-sky-100">Feature overview</a>
                {features.map((feature) => (
                  <a key={feature.path} href={feature.path} className="block rounded-xl px-3 py-2 outline-none hover:bg-accent focus-visible:ring-4 focus-visible:ring-sky-100">{feature.title}</a>
                ))}
                <a href="#pricing" className="block rounded-xl px-3 py-2 outline-none hover:bg-accent focus-visible:ring-4 focus-visible:ring-sky-100">Pricing</a>
                <a href="#testimonials" className="block rounded-xl px-3 py-2 outline-none hover:bg-accent focus-visible:ring-4 focus-visible:ring-sky-100">Customers</a>
                <a href="#security" className="block rounded-xl px-3 py-2 outline-none hover:bg-accent focus-visible:ring-4 focus-visible:ring-sky-100">Security</a>
                <button onClick={login} className="mt-2 w-full rounded-xl px-3 py-2 text-left font-medium text-primary outline-none hover:bg-accent focus-visible:ring-4 focus-visible:ring-sky-100">Log in or sign up</button>
              </div>
            </details>
            <Button variant="ghost" className="hidden sm:inline-flex" onClick={login}>Log in</Button>
            <Button className="brand-gradient hidden border-0 text-white shadow-lg shadow-sky-300/30 hover:opacity-95 sm:inline-flex" onClick={login}>Sign up</Button>
          </div>
        </nav>
      </header>

      <main id="top">
        <section className="grid-fade relative py-20 sm:py-28 lg:py-32">
          <div className="container grid items-center gap-14 lg:grid-cols-[1.03fr_.97fr]">
            <div className="max-w-3xl">
              <Badge className="mb-6 border-sky-200 bg-sky-50 text-sky-700 hover:bg-sky-50"><Sparkles className="mr-1 h-3.5 w-3.5" /> Built for modern house-flip teams</Badge>
              <h1 className="text-4xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-6xl lg:text-7xl">Analyze deals, manage flips, and keep every <span className="brand-text-gradient">FlipCycle</span> moving.</h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">FlipCycle is a full-stack operating platform for real estate investors who need clean deal analysis, project pipeline control, budget visibility, S3-backed documents, and role-based team collaboration.</p>
              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Button size="lg" className="brand-gradient border-0 text-white shadow-xl shadow-sky-300/30 hover:opacity-95" onClick={login}>Start with Manus OAuth <ArrowRight className="ml-2 h-4 w-4" /></Button>
                <Button size="lg" variant="outline" asChild><a href="#features">Explore features</a></Button>
              </div>
              <div className="mt-8 grid max-w-xl grid-cols-3 gap-4 text-sm">
                <div><p className="text-2xl font-semibold text-slate-950">4</p><p className="text-muted-foreground">pipeline stages</p></div>
                <div><p className="text-2xl font-semibold text-slate-950">3</p><p className="text-muted-foreground">required returns</p></div>
                <div><p className="text-2xl font-semibold text-slate-950">S3</p><p className="text-muted-foreground">file storage</p></div>
              </div>
            </div>
            <div className="soft-panel relative rounded-[2rem] p-5">
              <div className="rounded-[1.5rem] border bg-white p-5 shadow-sm">
                <div className="mb-5 flex items-center justify-between"><div><p className="text-sm font-medium text-muted-foreground">Portfolio summary</p><h2 className="text-2xl font-semibold">Active flip command center</h2></div><Badge className="brand-gradient border-0 text-white">Live</Badge></div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {["Active deals", "Total invested", "Projected profit", "Completed flips"].map((item, index) => (<div key={item} className="rounded-2xl border bg-slate-50/80 p-4"><p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">{item}</p><p className="mt-2 text-2xl font-semibold">{["12", "$1.84M", "$412K", "28"][index]}</p></div>))}
                </div>
                <div className="mt-5 rounded-2xl border p-4"><div className="mb-4 flex items-center justify-between"><p className="font-medium">Deal pipeline</p><p className="text-sm text-muted-foreground">Acquisition → Sold</p></div><div className="grid grid-cols-4 gap-2">{["Acquisition", "Rehab", "Listed", "Sold"].map((stage, i) => (<div key={stage} className="rounded-xl bg-slate-50 p-3"><div className="h-1.5 rounded-full brand-gradient" style={{ opacity: 1 - i * 0.14 }} /><p className="mt-3 text-xs font-medium">{stage}</p></div>))}</div></div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="container py-20">
          <div className="mx-auto max-w-3xl text-center"><Badge variant="outline" className="mb-4">Core platform</Badge><h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">A minimal workspace for the full house-flip lifecycle.</h2><p className="mt-5 text-muted-foreground">FlipCycle translates fragmented spreadsheets, file folders, and task boards into one branded system for analysis, execution, and collaboration. Each feature card now opens the matching protected workspace after sign-in.</p></div>
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-5">{features.map(feature => (<Card key={feature.title} className="border-blue-100/80 bg-white/80 shadow-sm transition hover:-translate-y-1 hover:shadow-xl hover:shadow-sky-200/30"><CardContent className="flex h-full flex-col p-6"><div className="brand-gradient mb-5 flex h-12 w-12 items-center justify-center rounded-2xl text-white"><feature.icon className="h-5 w-5" /></div><h3 className="text-lg font-semibold">{feature.title}</h3><p className="mt-3 flex-1 text-sm leading-6 text-muted-foreground">{feature.text}</p><Button variant="outline" className="mt-5 justify-between" asChild><a href={feature.path}>{feature.cta}<ArrowRight className="h-4 w-4" /></a></Button></CardContent></Card>))}</div>
        </section>

        <section className="bg-slate-950 py-20 text-white" id="security">
          <div className="container grid gap-10 lg:grid-cols-[.9fr_1.1fr] lg:items-center">
            <div><Badge className="mb-5 border-white/15 bg-white/10 text-sky-100 hover:bg-white/10"><LockKeyhole className="mr-1 h-3.5 w-3.5" /> Secure by design</Badge><h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">Protected access, durable storage, and clear permissions.</h2><p className="mt-5 text-sky-100/75">FlipCycle uses Manus OAuth for authentication and S3-backed storage for project files. Project roles stay simple and auditable with owner, editor, and viewer permissions.</p></div>
            <div className="grid gap-4 sm:grid-cols-3">{[[ShieldCheck, "Manus OAuth"], [FileText, "S3 documents"], [Users, "Role access"]].map(([Icon, label]) => (<div key={String(label)} className="rounded-3xl border border-white/10 bg-white/5 p-6"><Icon className="mb-5 h-8 w-8 text-sky-300" /><p className="font-semibold">{String(label)}</p><p className="mt-2 text-sm text-sky-100/65">Built into the FlipCycle workflow.</p></div>))}</div>
          </div>
        </section>

        <section id="pricing" className="container py-20">
          <div className="mx-auto max-w-3xl text-center"><Badge variant="outline" className="mb-4">Pricing</Badge><h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">Choose a plan for your flip volume.</h2><p className="mt-5 text-muted-foreground">Original FlipCycle plan packaging for solo investors, growing teams, and scaled operators.</p></div>
          <div className="mt-12 grid gap-6 lg:grid-cols-3">{pricing.map(plan => (<Card key={plan.name} className={`relative overflow-hidden ${plan.featured ? "border-primary shadow-2xl shadow-sky-200/40" : "border-blue-100/80"}`}>{plan.featured ? <div className="brand-gradient absolute inset-x-0 top-0 h-1.5" /> : null}<CardContent className="p-7"><p className="text-xl font-semibold">{plan.name}</p><p className="mt-2 text-sm text-muted-foreground">{plan.note}</p><p className="mt-7"><span className="text-4xl font-semibold">{plan.price}</span><span className="text-muted-foreground">/mo</span></p><Button className={`mt-7 w-full ${plan.featured ? "brand-gradient border-0 text-white" : ""}`} variant={plan.featured ? "default" : "outline"} onClick={login}>Start with FlipCycle</Button><div className="mt-7 space-y-3">{plan.items.map(item => (<p key={item} className="flex items-center gap-3 text-sm"><Check className="h-4 w-4 text-sky-500" /> {item}</p>))}</div></CardContent></Card>))}</div>
        </section>

        <section id="testimonials" className="container pb-20">
          <div className="grid gap-6 lg:grid-cols-3">{testimonials.map(item => (<Card key={item.name} className="bg-white/80"><CardContent className="p-7"><p className="text-lg leading-8">“{item.quote}”</p><p className="mt-6 font-semibold">{item.name}</p><p className="text-sm text-muted-foreground">{item.role}</p></CardContent></Card>))}</div>
        </section>

        <section className="container pb-24">
          <div className="brand-gradient rounded-[2rem] p-8 text-white shadow-2xl shadow-sky-300/30 sm:p-12"><div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center"><div><h2 className="text-3xl font-semibold tracking-tight sm:text-5xl">Bring your next flip into FlipCycle.</h2><p className="mt-4 max-w-2xl text-white/82">Create a protected workspace for deal analysis, pipeline tracking, budgets, documents, and team collaboration.</p></div><Button size="lg" variant="secondary" onClick={login}>Open dashboard <ArrowRight className="ml-2 h-4 w-4" /></Button></div></div>
        </section>
      </main>
    </div>
  );
}
