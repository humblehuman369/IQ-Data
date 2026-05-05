import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { trpc } from "@/lib/trpc";
import { BarChart3, Calculator, FileText, KanbanSquare, Plus, ReceiptText, Upload, Users } from "lucide-react";
import { useLocation } from "wouter";

const stages = ["Acquisition", "Rehab", "Listed", "Sold"] as const;
const roles = ["owner", "editor", "viewer"] as const;
const categories = ["labor", "materials", "permits"] as const;
const docTypes = ["contracts", "photos", "inspection_reports", "other"] as const;

type Stage = (typeof stages)[number];
type Role = (typeof roles)[number];
type Category = (typeof categories)[number];
type DocType = (typeof docTypes)[number];

type DealState = {
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

const sections = {
  "/dashboard": { title: "Portfolio overview", icon: BarChart3, description: "Active deals, total invested, projected profit, and completed flips." },
  "/dashboard/analyzer": { title: "Deal analyzer", icon: Calculator, description: "Calculate profit, ROI, cash-on-cash return, and estimated ARV." },
  "/dashboard/pipeline": { title: "Deal pipeline", icon: KanbanSquare, description: "Manage projects through Acquisition, Rehab, Listed, and Sold." },
  "/dashboard/budgets": { title: "Budget tracker", icon: ReceiptText, description: "Compare labor, materials, and permit estimates against actuals." },
  "/dashboard/documents": { title: "Documents", icon: FileText, description: "Store contracts, photos, and inspection reports with S3-backed references." },
  "/dashboard/team": { title: "Team", icon: Users, description: "Invite collaborators as owner, editor, or viewer." },
};

const money = (value?: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value ?? 0);
const percent = (value?: number) => `${Number(value ?? 0).toFixed(2)}%`;

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return <label className="grid gap-2 text-sm font-medium text-slate-700"><span>{label}</span><input className="rounded-2xl border border-blue-100 bg-white px-4 py-3 text-sm outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-100" type="number" value={value} onChange={(event) => onChange(Number(event.target.value))} /></label>;
}

function TextField({ label, value, onChange, placeholder, type = "text" }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string }) {
  return <label className="grid gap-2 text-sm font-medium text-slate-700"><span>{label}</span><input className="rounded-2xl border border-blue-100 bg-white px-4 py-3 text-sm outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-100" type={type} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} /></label>;
}

function SelectField<T extends string>({ label, value, options, onChange }: { label: string; value: T; options: readonly T[]; onChange: (value: T) => void }) {
  return <label className="grid gap-2 text-sm font-medium text-slate-700"><span>{label}</span><select className="rounded-2xl border border-blue-100 bg-white px-4 py-3 text-sm outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-100" value={value} onChange={(event) => onChange(event.target.value as T)}>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select></label>;
}

export default function Dashboard() {
  const [location] = useLocation();
  const utils = trpc.useUtils();
  const section = sections[location as keyof typeof sections] ?? sections["/dashboard"];
  const Icon = section.icon;

  const [selectedProjectId, setSelectedProjectId] = useState<number>(0);
  const [projectForm, setProjectForm] = useState({ name: "Maple Street Flip", address: "128 Maple Street", stage: "Acquisition" as Stage, sqft: 1550 });
  const [deal, setDeal] = useState<DealState>({ purchasePrice: 200000, repairCosts: 45000, arv: 330000, downPayment: 40000, loanAmount: 160000, interestRate: 9, holdingMonths: 6, closingCosts: 6000, sellingCosts: 18000 });
  const [expense, setExpense] = useState({ category: "labor" as Category, description: "Framing and finish labor", estimate: 12000, actual: 9800, vendor: "Preferred contractor" });
  const [comp, setComp] = useState({ address: "214 Oak Avenue", salePrice: 325000, sqft: 1525, beds: 3, baths: 2, soldAt: "2026-03-12" });
  const [invite, setInvite] = useState({ email: "teammate@example.com", name: "Project teammate", role: "viewer" as Role });
  const [uploadType, setUploadType] = useState<DocType>("contracts");
  const [compSearch, setCompSearch] = useState("Oak");

  const summary = trpc.workcycle.summary.useQuery();
  const projects = trpc.workcycle.projects.useQuery();
  const analyzerInput = useMemo(() => deal, [deal]);
  const analysis = trpc.workcycle.calculateDeal.useQuery(analyzerInput);
  const selectedInput = useMemo(() => ({ projectId: selectedProjectId || 1 }), [selectedProjectId]);
  const lookupInput = useMemo(() => ({ projectId: selectedProjectId || 1, query: compSearch }), [selectedProjectId, compSearch]);
  const hasProject = selectedProjectId > 0;
  const expenses = trpc.workcycle.expenses.useQuery(selectedInput, { enabled: hasProject });
  const comps = trpc.workcycle.comps.useQuery(selectedInput, { enabled: hasProject });
  const compLookup = trpc.workcycle.searchComps.useQuery(lookupInput, { enabled: hasProject && compSearch.trim().length > 0 });
  const documents = trpc.workcycle.documents.useQuery(selectedInput, { enabled: hasProject });
  const collaborators = trpc.workcycle.collaborators.useQuery(selectedInput, { enabled: hasProject });

  useEffect(() => {
    if (!selectedProjectId && projects.data?.[0]?.id) setSelectedProjectId(projects.data[0].id);
  }, [projects.data, selectedProjectId]);

  const selectedProject = projects.data?.find((project) => project.id === selectedProjectId);

  const invalidateWorkspace = async () => {
    await Promise.all([utils.workcycle.projects.invalidate(), utils.workcycle.summary.invalidate(), utils.workcycle.expenses.invalidate(), utils.workcycle.comps.invalidate(), utils.workcycle.documents.invalidate(), utils.workcycle.collaborators.invalidate()]);
  };

  const createProject = trpc.workcycle.createProject.useMutation({
    onSuccess: async (project) => { toast.success("FlipCycle project created"); if (project?.id) setSelectedProjectId(project.id); await invalidateWorkspace(); },
    onError: (error) => toast.error(error.message),
  });
  const updateStage = trpc.workcycle.updateStage.useMutation({ onSuccess: invalidateWorkspace, onError: (error) => toast.error(error.message) });
  const addExpense = trpc.workcycle.addExpense.useMutation({ onSuccess: async () => { toast.success("Expense added"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const addComp = trpc.workcycle.addComp.useMutation({ onSuccess: async () => { toast.success("Comparable sale added"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const uploadDocument = trpc.workcycle.uploadDocument.useMutation({ onSuccess: async () => { toast.success("Document uploaded to S3 storage"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const inviteCollaborator = trpc.workcycle.inviteCollaborator.useMutation({ onSuccess: async () => { toast.success("Collaborator invited"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const updateCollaboratorRole = trpc.workcycle.updateCollaboratorRole.useMutation({ onSuccess: async () => { toast.success("Collaborator role updated"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const removeCollaborator = trpc.workcycle.removeCollaborator.useMutation({ onSuccess: async () => { toast.success("Collaborator removed"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const acceptInvitation = trpc.workcycle.acceptInvitation.useMutation({ onSuccess: async () => { toast.success("Invitation accepted"); await invalidateWorkspace(); }, onError: (error) => toast.error(error.message) });
  const seedSampleData = trpc.workcycle.seedSampleData.useMutation({
    onSuccess: async (result) => {
      toast.success(result.message);
      await invalidateWorkspace();
      if (result.projectIds[0]) setSelectedProjectId(result.projectIds[0]);
    },
    onError: (error) => toast.error(error.message),
  });

  const createCurrentProject = () => createProject.mutate({ ...projectForm, ...deal });
  const addCurrentExpense = () => hasProject && addExpense.mutate({ projectId: selectedProjectId, ...expense });
  const addCurrentComp = () => hasProject && addComp.mutate({ projectId: selectedProjectId, ...comp });
  const inviteCurrent = () => hasProject && inviteCollaborator.mutate({ projectId: selectedProjectId, ...invite });

  const handleUpload = (file: File | undefined) => {
    if (!file || !hasProject) return;
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result ?? "");
      const base64Content = result.includes(",") ? result.split(",")[1] : result;
      uploadDocument.mutate({ projectId: selectedProjectId, name: file.name, docType: uploadType, mimeType: file.type || "application/octet-stream", base64Content });
    };
    reader.readAsDataURL(file);
  };

  const workspaceLoading = summary.isLoading || projects.isLoading;
  const workspaceError = summary.error?.message || projects.error?.message || expenses.error?.message || comps.error?.message || documents.error?.message || collaborators.error?.message || analysis.error?.message;

  const dashboardCards = [
    ["Active deals", summary.data?.activeDeals ?? 0],
    ["Total invested", money(summary.data?.totalInvested)],
    ["Projected profit", money(summary.data?.projectedProfit)],
    ["Completed flips", summary.data?.completedFlips ?? 0],
  ];
  const budgetTotals = (expenses.data ?? []).reduce((totals, item) => ({ estimate: totals.estimate + item.estimate, actual: totals.actual + item.actual }), { estimate: 0, actual: 0 });

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6" aria-labelledby="flipcycle-dashboard-title">
      <div className="flex flex-col justify-between gap-4 rounded-[2rem] border bg-white/85 p-6 shadow-xl shadow-sky-200/20 backdrop-blur md:flex-row md:items-center">
        <div className="flex items-start gap-4"><span className="brand-gradient flex h-13 w-13 shrink-0 items-center justify-center rounded-2xl text-white"><Icon className="h-6 w-6" /></span><div><Badge variant="outline" className="mb-2">FlipCycle workspace</Badge><h1 id="flipcycle-dashboard-title" className="text-3xl font-semibold tracking-tight">{section.title}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{section.description}</p></div></div>
        <div className="flex flex-wrap gap-3"><Button variant="outline" onClick={() => seedSampleData.mutate()} disabled={seedSampleData.isPending}>{seedSampleData.isPending ? "Adding samples..." : "Load sample data"}</Button><Button onClick={createCurrentProject} disabled={createProject.isPending} className="brand-gradient border-0 text-white"><Plus className="mr-2 h-4 w-4" />Create project</Button></div>
      </div>

      {workspaceError && <div className="rounded-3xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">{workspaceError}</div>}
      {workspaceLoading && <div className="rounded-3xl border border-sky-100 bg-sky-50 p-4 text-sm text-sky-700">Loading your FlipCycle portfolio data...</div>}
      <div className="grid gap-4 md:grid-cols-4">{dashboardCards.map(([label, value]) => <Card key={label} className="border-blue-100/80 bg-white/85"><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">{label}</CardTitle></CardHeader><CardContent><p className="text-2xl font-semibold tracking-tight">{summary.isLoading ? "Loading..." : value}</p></CardContent></Card>)}</div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Project setup</CardTitle></CardHeader><CardContent className="grid gap-4 md:grid-cols-2"><TextField label="Project name" value={projectForm.name} onChange={(name) => setProjectForm({ ...projectForm, name })} /><TextField label="Address" value={projectForm.address} onChange={(address) => setProjectForm({ ...projectForm, address })} /><SelectField label="Pipeline stage" value={projectForm.stage} options={stages} onChange={(stage) => setProjectForm({ ...projectForm, stage })} /><NumberField label="Square footage" value={projectForm.sqft} onChange={(sqft) => setProjectForm({ ...projectForm, sqft })} /></CardContent></Card>
        <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Selected project</CardTitle></CardHeader><CardContent className="space-y-3"><select aria-label="Select FlipCycle project" className="w-full rounded-2xl border border-blue-100 bg-white px-4 py-3 text-sm outline-none focus:border-sky-400 focus:ring-4 focus:ring-sky-100" value={selectedProjectId} onChange={(event) => setSelectedProjectId(Number(event.target.value))}><option value={0}>Choose a FlipCycle project</option>{(projects.data ?? []).map((project) => <option value={project.id} key={project.id}>{project.name} · {project.stage}</option>)}</select>{!hasProject ? <div className="rounded-3xl border border-dashed border-sky-200 bg-sky-50/70 p-6 text-center"><p className="font-semibold">No FlipCycle projects yet</p><p className="mt-2 text-sm leading-6 text-muted-foreground">Create a project or load realistic onboarding samples to explore budgets, comps, S3 documents, and team access.</p><Button variant="outline" className="mt-4 bg-white" onClick={() => seedSampleData.mutate()} disabled={seedSampleData.isPending}>{seedSampleData.isPending ? "Adding samples..." : "Populate dashboard with sample data"}</Button></div> : <div className="rounded-3xl bg-slate-50 p-5"><p className="font-semibold">{selectedProject?.name}</p><p className="mt-1 text-sm text-muted-foreground">{selectedProject?.address}</p><Badge className="mt-3 bg-sky-100 text-sky-700 hover:bg-sky-100">{selectedProject?.stage}</Badge></div>}</CardContent></Card>
      </div>

      <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Property deal analyzer</CardTitle></CardHeader><CardContent className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"><div className="grid gap-4 md:grid-cols-3"><NumberField label="Purchase price" value={deal.purchasePrice} onChange={(purchasePrice) => setDeal({ ...deal, purchasePrice })} /><NumberField label="Repair costs" value={deal.repairCosts} onChange={(repairCosts) => setDeal({ ...deal, repairCosts })} /><NumberField label="ARV" value={deal.arv} onChange={(arv) => setDeal({ ...deal, arv })} /><NumberField label="Down payment" value={deal.downPayment} onChange={(downPayment) => setDeal({ ...deal, downPayment })} /><NumberField label="Loan amount" value={deal.loanAmount} onChange={(loanAmount) => setDeal({ ...deal, loanAmount })} /><NumberField label="Interest rate" value={deal.interestRate} onChange={(interestRate) => setDeal({ ...deal, interestRate })} /><NumberField label="Holding months" value={deal.holdingMonths} onChange={(holdingMonths) => setDeal({ ...deal, holdingMonths })} /><NumberField label="Closing costs" value={deal.closingCosts} onChange={(closingCosts) => setDeal({ ...deal, closingCosts })} /><NumberField label="Selling costs" value={deal.sellingCosts} onChange={(sellingCosts) => setDeal({ ...deal, sellingCosts })} /></div><div className="rounded-[2rem] bg-gradient-to-br from-[#0465F2] to-[#0FA4E9] p-6 text-white"><p className="text-sm font-medium uppercase tracking-[0.22em] text-sky-100">Calculated outputs</p><div className="mt-6 grid gap-4"><div><p className="text-sm text-sky-100">Profit</p><p className="text-3xl font-semibold">{money(analysis.data?.profit)}</p></div><div><p className="text-sm text-sky-100">ROI</p><p className="text-3xl font-semibold">{percent(analysis.data?.roi)}</p></div><div><p className="text-sm text-sky-100">Cash-on-cash return</p><p className="text-3xl font-semibold">{percent(analysis.data?.cashOnCashReturn)}</p></div></div></div></CardContent></Card>

      <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Deal pipeline</CardTitle></CardHeader><CardContent><div className="grid gap-4 md:grid-cols-4">{stages.map((stage) => <div key={stage} className="rounded-3xl border border-blue-100 bg-slate-50/80 p-4"><div className="flex items-center justify-between"><p className="font-semibold">{stage}</p><Badge variant="outline">{(projects.data ?? []).filter((project) => project.stage === stage).length}</Badge></div><div className="mt-4 space-y-3">{(projects.data ?? []).filter((project) => project.stage === stage).map((project) => <div key={project.id} className="rounded-2xl bg-white p-4 shadow-sm"><p className="font-medium">{project.name}</p><p className="mt-1 text-xs text-muted-foreground">{project.address}</p><select aria-label={`Move ${project.name} to another pipeline stage`} className="mt-3 w-full rounded-xl border border-blue-100 px-3 py-2 text-xs outline-none focus:border-sky-400 focus:ring-4 focus:ring-sky-100" value={project.stage} onChange={(event) => updateStage.mutate({ projectId: project.id, stage: event.target.value as Stage })}>{stages.map((option) => <option value={option} key={option}>{option}</option>)}</select></div>)}{(projects.data ?? []).filter((project) => project.stage === stage).length === 0 && <p className="rounded-2xl border border-dashed border-blue-100 p-4 text-sm text-muted-foreground">No projects in {stage}.</p>}</div></div>)}</div></CardContent></Card>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Budget and expense tracker</CardTitle></CardHeader><CardContent className="space-y-4"><div className="grid gap-4 md:grid-cols-2"><SelectField label="Category" value={expense.category} options={categories} onChange={(category) => setExpense({ ...expense, category })} /><TextField label="Description" value={expense.description} onChange={(description) => setExpense({ ...expense, description })} /><NumberField label="Estimate" value={expense.estimate} onChange={(estimate) => setExpense({ ...expense, estimate })} /><NumberField label="Actual" value={expense.actual} onChange={(actual) => setExpense({ ...expense, actual })} /><TextField label="Vendor" value={expense.vendor} onChange={(vendor) => setExpense({ ...expense, vendor })} /></div><Button onClick={addCurrentExpense} disabled={!hasProject || addExpense.isPending} className="brand-gradient border-0 text-white">Add budget line</Button><div className="rounded-3xl bg-slate-50 p-4"><div className="flex justify-between text-sm"><span>Estimated</span><b>{money(budgetTotals.estimate)}</b></div><div className="mt-2 flex justify-between text-sm"><span>Actual</span><b>{money(budgetTotals.actual)}</b></div><div className="mt-4 space-y-2">{(expenses.data ?? []).map((item) => <div key={item.id} className="rounded-2xl bg-white p-3 text-sm"><b>{item.category}</b> · {item.description}<span className="float-right">{money(item.actual)} / {money(item.estimate)}</span></div>)}</div></div></CardContent></Card>
        <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Comparable sales and ARV estimator</CardTitle></CardHeader><CardContent className="space-y-4"><div className="grid gap-4 md:grid-cols-2"><TextField label="Comparable address" value={comp.address} onChange={(address) => setComp({ ...comp, address })} /><NumberField label="Sale price" value={comp.salePrice} onChange={(salePrice) => setComp({ ...comp, salePrice })} /><NumberField label="Square feet" value={comp.sqft} onChange={(sqft) => setComp({ ...comp, sqft })} /><TextField label="Sold date" value={comp.soldAt} onChange={(soldAt) => setComp({ ...comp, soldAt })} /><NumberField label="Beds" value={comp.beds} onChange={(beds) => setComp({ ...comp, beds })} /><NumberField label="Baths" value={comp.baths} onChange={(baths) => setComp({ ...comp, baths })} /></div><div className="flex flex-wrap gap-3"><Button onClick={addCurrentComp} disabled={!hasProject || addComp.isPending} className="brand-gradient border-0 text-white">Add comp</Button><Button variant="outline" disabled={!comps.data?.estimate.estimatedArv} onClick={() => setDeal({ ...deal, arv: comps.data?.estimate.estimatedArv ?? deal.arv })}>Apply comp ARV to analyzer</Button></div><div className="rounded-3xl bg-sky-50 p-4"><p className="text-sm text-muted-foreground">Estimated ARV from comps</p><p className="text-2xl font-semibold">{comps.isLoading ? "Loading..." : money(comps.data?.estimate.estimatedArv)}</p><p className="mt-1 text-xs text-muted-foreground">{comps.data?.estimate.compCount ?? 0} comps · {money(comps.data?.estimate.averagePricePerSqft)}/sqft</p></div><TextField label="Lookup saved comps by address or sale price" value={compSearch} onChange={setCompSearch} /><div className="rounded-3xl bg-white p-4 shadow-sm"><p className="text-sm font-semibold">Lookup results</p>{compLookup.isLoading && <p className="mt-2 text-sm text-muted-foreground">Searching saved comparable sales...</p>}{!compLookup.isLoading && (compLookup.data?.comps.length ?? 0) === 0 && <p className="mt-2 text-sm text-muted-foreground">No matching comps yet. Add a comp above to build your lookup set.</p>}<div className="mt-3 space-y-2">{(compLookup.data?.comps ?? []).map((row) => <button key={row.id} aria-label={`Apply ARV estimate from ${row.address}`} className="block w-full rounded-2xl bg-slate-50 p-3 text-left text-sm outline-none transition hover:bg-sky-50 focus-visible:ring-4 focus-visible:ring-sky-100" onClick={() => setDeal({ ...deal, arv: compLookup.data?.estimate.estimatedArv ?? deal.arv })}><b>{row.address}</b><span className="float-right">{money(row.salePrice)}</span></button>)}</div></div></CardContent></Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Documents and file upload</CardTitle></CardHeader><CardContent className="space-y-4"><SelectField label="Document type" value={uploadType} options={docTypes} onChange={setUploadType} /><label className="flex cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-sky-200 bg-sky-50/70 p-8 text-center text-sm text-muted-foreground focus-within:ring-4 focus-within:ring-sky-100"><Upload className="mb-3 h-6 w-6 text-sky-500" />Upload contracts, photos, or inspection reports to S3-backed storage<input aria-label="Upload FlipCycle project document" type="file" className="sr-only" onChange={(event) => handleUpload(event.target.files?.[0])} disabled={!hasProject || uploadDocument.isPending} /></label><div className="space-y-2">{documents.isLoading && <p className="rounded-2xl bg-sky-50 p-3 text-sm text-sky-700">Loading project documents...</p>}{!documents.isLoading && (documents.data ?? []).length === 0 && <p className="rounded-2xl bg-slate-50 p-3 text-sm text-muted-foreground">No documents uploaded yet.</p>}{(documents.data ?? []).map((doc) => <a key={doc.id} href={doc.url} target="_blank" className="block rounded-2xl bg-slate-50 p-3 text-sm outline-none hover:bg-sky-50 focus-visible:ring-4 focus-visible:ring-sky-100" rel="noreferrer"><b>{doc.name}</b><span className="ml-2 text-muted-foreground">{doc.docType}</span></a>)}</div></CardContent></Card>
        <Card className="border-blue-100/80 bg-white/85 shadow-sm"><CardHeader><CardTitle>Team and collaborators</CardTitle></CardHeader><CardContent className="space-y-4"><div className="grid gap-4 md:grid-cols-2"><TextField label="Email" type="email" value={invite.email} onChange={(email) => setInvite({ ...invite, email })} /><TextField label="Name" value={invite.name} onChange={(name) => setInvite({ ...invite, name })} /><SelectField label="Role" value={invite.role} options={roles} onChange={(role) => setInvite({ ...invite, role })} /></div><Button onClick={inviteCurrent} disabled={!hasProject || inviteCollaborator.isPending} className="brand-gradient border-0 text-white">Invite collaborator</Button><div className="space-y-2">{collaborators.isLoading && <p className="rounded-2xl bg-sky-50 p-3 text-sm text-sky-700">Loading collaborators...</p>}{!collaborators.isLoading && (collaborators.data ?? []).length === 0 && <p className="rounded-2xl bg-slate-50 p-3 text-sm text-muted-foreground">No collaborators invited yet.</p>}{(collaborators.data ?? []).map((person) => <div key={person.id} className="grid gap-3 rounded-2xl bg-slate-50 p-3 text-sm md:grid-cols-[1fr_auto_auto_auto] md:items-center"><span><b>{person.name || person.email}</b><span className="ml-2 text-muted-foreground">{person.email}</span></span><Badge className="bg-sky-100 text-sky-700 hover:bg-sky-100">{person.status}</Badge><select aria-label={`Change role for ${person.email}`} className="rounded-xl border border-blue-100 bg-white px-3 py-2 text-xs outline-none focus:border-sky-400 focus:ring-4 focus:ring-sky-100" value={person.role} disabled={person.role === "owner"} onChange={(event) => updateCollaboratorRole.mutate({ collaboratorId: person.id, role: event.target.value as Role })}>{roles.map((role) => <option value={role} key={role}>{role}</option>)}</select><div className="flex gap-2"><Button size="sm" variant="outline" disabled={!hasProject || person.status === "active"} onClick={() => acceptInvitation.mutate({ projectId: selectedProjectId })}>Accept</Button><Button size="sm" variant="outline" disabled={person.role === "owner"} onClick={() => removeCollaborator.mutate({ collaboratorId: person.id })}>Remove</Button></div></div>)}</div></CardContent></Card>
      </div>
    </main>
  );
}
