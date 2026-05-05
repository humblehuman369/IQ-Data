'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { BarChart3, Building2, FileText, LayoutDashboard, Menu, Users, WalletCards } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { toast } from 'sonner';
import { DealAnalyzer } from '@/components/deal-analyzer';
import { MetricCard } from '@/components/metric-card';
import { flipcycleApi } from '@/lib/api';
import type { Collaborator, DocumentRecord, Expense, PipelineStage, Project } from '@/lib/types';
import { calculateDeal, estimateArvFromComps, PIPELINE_STAGES } from '@/lib/workcycle';
import { useWorkspaceStore } from '@/store/use-workspace-store';

const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

const sections = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'analyzer', label: 'Deal Analyzer', icon: BarChart3 },
  { id: 'pipeline', label: 'Pipeline', icon: Building2 },
  { id: 'budgets', label: 'Budgets', icon: WalletCards },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'team', label: 'Team', icon: Users },
] as const;

type SectionId = (typeof sections)[number]['id'];

function DashboardContent() {
  const searchParams = useSearchParams();
  const requestedSection = searchParams.get('section') as SectionId | null;
  const activeSection = sections.some((section) => section.id === requestedSection) ? requestedSection! : 'overview';
  const [mobileOpen, setMobileOpen] = useState(false);
  const { activeProjectId, setActiveProjectId } = useWorkspaceStore();
  const queryClient = useQueryClient();

  const projectsQuery = useQuery({ queryKey: ['projects'], queryFn: flipcycleApi.projects });
  const summaryQuery = useQuery({ queryKey: ['summary'], queryFn: flipcycleApi.summary });
  const projects = useMemo(() => projectsQuery.data ?? [], [projectsQuery.data]);
  const activeProject = projects.find((project) => project.id === activeProjectId) ?? projects[0];
  const projectId = activeProject?.id ?? 1;
  const expensesQuery = useQuery({ queryKey: ['expenses', projectId], queryFn: () => flipcycleApi.expenses(projectId), enabled: Boolean(activeProject) });
  const compsQuery = useQuery({ queryKey: ['comps', projectId], queryFn: () => flipcycleApi.comps(projectId), enabled: Boolean(activeProject) });
  const docsQuery = useQuery({ queryKey: ['documents', projectId], queryFn: () => flipcycleApi.documents(projectId), enabled: Boolean(activeProject) });
  const collaboratorsQuery = useQuery({ queryKey: ['collaborators', projectId], queryFn: () => flipcycleApi.collaborators(projectId), enabled: Boolean(activeProject) });

  const stageMutation = useMutation({
    mutationFn: ({ id, stage }: { id: number; stage: PipelineStage }) => flipcycleApi.updateProjectStage(id, stage),
    onSuccess: (updated) => {
      queryClient.setQueryData<Project[]>(['projects'], (current = []) => current.map((project) => (project.id === updated.id ? { ...project, stage: updated.stage } : project)));
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      toast.success('Pipeline stage updated');
    },
    onError: () => toast.error('Pipeline stage update failed'),
  });

  const expenseMutation = useMutation({
    mutationFn: ({ id, input }: { id: number; input: Omit<Expense, 'id' | 'projectId'> }) => flipcycleApi.createExpense(id, input),
    onSuccess: (expense) => {
      queryClient.setQueryData<Expense[]>(['expenses', expense.projectId], (current = []) => [...current, expense]);
      toast.success('Budget line added');
    },
    onError: () => toast.error('Budget line could not be added'),
  });

  const documentMutation = useMutation({
    mutationFn: ({ id, input }: { id: number; input: Omit<DocumentRecord, 'id' | 'projectId' | 'url' | 'size'> & { url?: string; size?: number } }) => flipcycleApi.createDocument(id, input),
    onSuccess: (document) => {
      queryClient.setQueryData<DocumentRecord[]>(['documents', document.projectId], (current = []) => [...current, document]);
      toast.success('Document metadata saved');
    },
    onError: () => toast.error('Document metadata could not be saved'),
  });

  const collaboratorMutation = useMutation({
    mutationFn: ({ id, input }: { id: number; input: Pick<Collaborator, 'email' | 'role'> & { name?: string } }) => flipcycleApi.inviteCollaborator(id, input),
    onSuccess: (collaborator) => {
      queryClient.setQueryData<Collaborator[]>(['collaborators', collaborator.projectId], (current = []) => [...current, collaborator]);
      toast.success('Collaborator invited');
    },
    onError: () => toast.error('Collaborator invite failed'),
  });

  const seedMutation = useMutation({
    mutationFn: flipcycleApi.seedSampleData,
    onSuccess: async (result) => {
      await Promise.all([queryClient.invalidateQueries({ queryKey: ['projects'] }), queryClient.invalidateQueries({ queryKey: ['summary'] })]);
      toast.success(result.seeded ? 'Sample workspace seeded' : 'Sample workspace already exists');
    },
    onError: () => toast.error('Sample workspace seeding failed'),
  });

  const chartData = useMemo(
    () => projects.map((project) => ({ name: project.name.replace(' ', '\n'), profit: calculateDeal(project).profit, roi: calculateDeal(project).roi })),
    [projects],
  );
  const compEstimate = estimateArvFromComps(compsQuery.data ?? [], activeProject?.sqft);

  const handleExpenseSubmit = (formData: FormData) => {
    if (!activeProject) return;
    expenseMutation.mutate({
      id: activeProject.id,
      input: {
        category: String(formData.get('category')) as Expense['category'],
        description: String(formData.get('description') ?? ''),
        estimate: Number(formData.get('estimate') ?? 0),
        actual: Number(formData.get('actual') ?? 0),
        vendor: String(formData.get('vendor') ?? ''),
      },
    });
  };

  const handleDocumentSubmit = (formData: FormData) => {
    if (!activeProject) return;
    documentMutation.mutate({
      id: activeProject.id,
      input: {
        name: String(formData.get('name') ?? ''),
        docType: String(formData.get('docType')) as DocumentRecord['docType'],
        url: String(formData.get('url') ?? '#'),
        mimeType: String(formData.get('mimeType') ?? ''),
        size: Number(formData.get('size') ?? 0),
      },
    });
  };

  const handleCollaboratorSubmit = (formData: FormData) => {
    if (!activeProject) return;
    collaboratorMutation.mutate({
      id: activeProject.id,
      input: {
        email: String(formData.get('email') ?? ''),
        name: String(formData.get('name') ?? ''),
        role: String(formData.get('role')) as Collaborator['role'],
      },
    });
  };

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className={`${mobileOpen ? 'block' : 'hidden'} border-r border-black/5 bg-white/75 p-5 backdrop-blur lg:block`}>
        <Link href="/" className="mb-8 flex items-center gap-3 font-semibold text-slate-950">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-slate-950 text-white">FC</span>FlipCycle
        </Link>
        <nav className="space-y-2">
          {sections.map((section) => {
            const Icon = section.icon;
            const active = section.id === activeSection;
            return (
              <Link key={section.id} href={section.id === 'overview' ? '/dashboard' : `/dashboard?section=${section.id}`} className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition ${active ? 'bg-slate-950 text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-slate-950'}`}>
                <Icon className="h-4 w-4" />{section.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <section className="p-5 md:p-8">
        <header className="mb-8 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-emerald-800">FlipCycle workspace</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-950 md:text-4xl">{sections.find((section) => section.id === activeSection)?.label}</h1>
          </div>
          <button onClick={() => setMobileOpen((open) => !open)} className="focus-ring rounded-2xl bg-white p-3 shadow-sm ring-1 ring-black/5 lg:hidden"><Menu className="h-5 w-5" /></button>
        </header>

        {activeSection === 'overview' && (
          <div className="space-y-6">
            <section className="flex flex-col gap-3 rounded-3xl bg-slate-950 p-5 text-white shadow-sm md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-semibold text-emerald-200">First-time onboarding</p>
                <h2 className="mt-1 text-2xl font-semibold">Seed realistic sample projects, budgets, comps, documents, and team access.</h2>
              </div>
              <button onClick={() => seedMutation.mutate()} disabled={seedMutation.isPending} className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-50 disabled:opacity-60">
                {seedMutation.isPending ? 'Seeding…' : 'Seed sample data'}
              </button>
            </section>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricCard label="Active deals" value={String(summaryQuery.data?.activeDeals ?? 0)} icon={Building2} tone="green" />
              <MetricCard label="Total cash invested" value={currency.format(summaryQuery.data?.totalInvested ?? 0)} icon={WalletCards} tone="blue" />
              <MetricCard label="Projected profit" value={currency.format(summaryQuery.data?.projectedProfit ?? 0)} icon={BarChart3} tone="amber" />
              <MetricCard label="Completed flips" value={String(summaryQuery.data?.completedFlips ?? 0)} icon={FileText} tone="slate" />
            </div>
            <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5">
              <h2 className="text-xl font-semibold text-slate-950">Profit by project</h2>
              <div className="mt-6 h-80"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tickLine={false} axisLine={false} /><YAxis tickFormatter={(value) => `$${Number(value) / 1000}k`} tickLine={false} axisLine={false} /><Tooltip formatter={(value) => currency.format(Number(value))} /><Bar dataKey="profit" fill="#1f8a70" radius={[10, 10, 0, 0]} /></BarChart></ResponsiveContainer></div>
            </section>
          </div>
        )}

        {activeSection === 'analyzer' && <DealAnalyzer />}

        {activeSection === 'pipeline' && (
          <div className="grid gap-4 xl:grid-cols-4">
            {PIPELINE_STAGES.map((stage) => (
              <section key={stage} className="rounded-3xl bg-white/86 p-4 shadow-sm ring-1 ring-black/5">
                <h2 className="font-semibold text-slate-950">{stage}</h2>
                <div className="mt-4 space-y-3">
                  {projects.filter((project) => project.stage === stage).map((project) => (
                    <article key={project.id} className="rounded-2xl bg-slate-50 p-4">
                      <button onClick={() => setActiveProjectId(project.id)} className="w-full text-left">
                        <p className="font-semibold text-slate-900">{project.name}</p>
                        <p className="mt-1 text-sm text-slate-500">{currency.format(calculateDeal(project).profit)} projected profit</p>
                      </button>
                      <label className="mt-3 block text-xs font-semibold uppercase tracking-wide text-slate-500" htmlFor={`stage-${project.id}`}>Move stage</label>
                      <select id={`stage-${project.id}`} value={project.stage} onChange={(event) => stageMutation.mutate({ id: project.id, stage: event.target.value as PipelineStage })} className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800">
                        {PIPELINE_STAGES.map((option) => <option key={option} value={option}>{option}</option>)}
                      </select>
                    </article>
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}

        {activeSection === 'budgets' && (
          <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5">
            <h2 className="text-xl font-semibold text-slate-950">Budget lines for {activeProject?.name}</h2>
            <form action={handleExpenseSubmit} className="mt-5 grid gap-3 rounded-2xl bg-slate-50 p-4 md:grid-cols-6">
              <select name="category" className="rounded-xl border border-slate-200 px-3 py-2 text-sm"><option value="labor">Labor</option><option value="materials">Materials</option><option value="permits">Permits</option></select>
              <input required name="description" placeholder="Description" className="rounded-xl border border-slate-200 px-3 py-2 text-sm md:col-span-2" />
              <input required name="estimate" type="number" min="0" placeholder="Estimate" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <input required name="actual" type="number" min="0" placeholder="Actual" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <input name="vendor" placeholder="Vendor" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <button disabled={expenseMutation.isPending} className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white md:col-span-6">Add budget line</button>
            </form>
            <div className="mt-5 overflow-hidden rounded-2xl border border-slate-100"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500"><tr><th className="p-3">Category</th><th>Description</th><th>Estimate</th><th>Actual</th><th>Vendor</th></tr></thead><tbody>{(expensesQuery.data ?? []).map((expense) => <tr key={expense.id} className="border-t border-slate-100"><td className="p-3 font-medium capitalize">{expense.category}</td><td>{expense.description}</td><td>{currency.format(expense.estimate)}</td><td>{currency.format(expense.actual)}</td><td>{expense.vendor}</td></tr>)}</tbody></table></div>
          </section>
        )}

        {activeSection === 'documents' && (
          <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5">
            <h2 className="text-xl font-semibold text-slate-950">Documents for {activeProject?.name}</h2>
            <p className="mt-2 text-sm text-slate-500">FastAPI stores document metadata in PostgreSQL and file bytes in S3. Use the metadata form after uploading bytes to S3.</p>
            <form action={handleDocumentSubmit} className="mt-5 grid gap-3 rounded-2xl bg-slate-50 p-4 md:grid-cols-5">
              <input required name="name" placeholder="File name" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <select name="docType" className="rounded-xl border border-slate-200 px-3 py-2 text-sm"><option value="contracts">Contract</option><option value="photos">Photo log</option><option value="inspection_reports">Inspection report</option><option value="other">Other</option></select>
              <input name="mimeType" placeholder="MIME type" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <input name="url" placeholder="S3 URL or storage path" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <input name="size" type="number" min="0" placeholder="Bytes" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <button disabled={documentMutation.isPending} className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white md:col-span-5">Save document metadata</button>
            </form>
            <div className="mt-5 grid gap-3 md:grid-cols-3">{(docsQuery.data ?? []).map((document) => <article key={document.id} className="rounded-2xl bg-slate-50 p-4"><FileText className="h-5 w-5 text-emerald-700" /><p className="mt-3 font-semibold">{document.name}</p><p className="mt-1 text-sm text-slate-500">{document.docType.replace('_', ' ')}</p></article>)}</div>
          </section>
        )}

        {activeSection === 'team' && (
          <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5">
            <h2 className="text-xl font-semibold text-slate-950">Team access</h2>
            <form action={handleCollaboratorSubmit} className="mt-5 grid gap-3 rounded-2xl bg-slate-50 p-4 md:grid-cols-4">
              <input required name="email" type="email" placeholder="Email" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <input name="name" placeholder="Name" className="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
              <select name="role" className="rounded-xl border border-slate-200 px-3 py-2 text-sm"><option value="viewer">Viewer</option><option value="editor">Editor</option><option value="owner">Owner</option></select>
              <button disabled={collaboratorMutation.isPending} className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white">Invite collaborator</button>
            </form>
            <div className="mt-5 grid gap-3 md:grid-cols-3">{(collaboratorsQuery.data ?? []).map((collaborator) => <article key={collaborator.id} className="rounded-2xl bg-slate-50 p-4"><Users className="h-5 w-5 text-emerald-700" /><p className="mt-3 font-semibold">{collaborator.name ?? collaborator.email}</p><p className="mt-1 text-sm text-slate-500">{collaborator.role} · {collaborator.status}</p></article>)}</div>
          </section>
        )}

        {activeSection === 'analyzer' && activeProject && <p className="mt-4 text-sm text-slate-500">Current comp-derived ARV signal: {currency.format(compEstimate.estimatedArv)} from {compEstimate.compCount} comps.</p>}
      </section>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<main className="min-h-screen p-8 text-slate-600">Loading workspace…</main>}>
      <DashboardContent />
    </Suspense>
  );
}
