import type { Collaborator, DealInput, DocumentRecord, Expense, PipelineStage, Project } from './types';
import { calculateDeal, summarizeProjects } from './workcycle';
import { sampleCollaborators, sampleComps, sampleDocuments, sampleExpenses, sampleProjects } from './sample-data';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error('NEXT_PUBLIC_API_BASE_URL is not configured');
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error(`FlipCycle API request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const flipcycleApi = {
  async health() {
    if (!API_BASE_URL) return { status: 'ok', service: 'flipcycle-api', mode: 'local-sample' };
    return request<{ status: string; service: string }>('/healthz');
  },
  async summary() {
    if (!API_BASE_URL) return summarizeProjects(sampleProjects);
    return request<ReturnType<typeof summarizeProjects>>('/api/workspace/summary');
  },
  async projects() {
    if (!API_BASE_URL) return sampleProjects;
    return request<typeof sampleProjects>('/api/projects');
  },
  async expenses(projectId: number) {
    if (!API_BASE_URL) return sampleExpenses.filter((expense) => expense.projectId === projectId);
    return request<typeof sampleExpenses>(`/api/projects/${projectId}/expenses`);
  },
  async comps(projectId: number) {
    if (!API_BASE_URL) return sampleComps.filter((comp) => comp.projectId === projectId);
    const response = await request<{ comps: typeof sampleComps; estimate?: unknown }>(`/api/projects/${projectId}/comps`);
    return response.comps;
  },
  async documents(projectId: number) {
    if (!API_BASE_URL) return sampleDocuments.filter((document) => document.projectId === projectId);
    return request<typeof sampleDocuments>(`/api/projects/${projectId}/documents`);
  },
  async collaborators(projectId: number) {
    if (!API_BASE_URL) return sampleCollaborators.filter((collaborator) => collaborator.projectId === projectId);
    return request<typeof sampleCollaborators>(`/api/projects/${projectId}/collaborators`);
  },
  async calculateDeal(input: DealInput) {
    if (!API_BASE_URL) return calculateDeal(input);
    return request<ReturnType<typeof calculateDeal>>('/api/deals/calculate', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },
  async updateProjectStage(projectId: number, stage: PipelineStage) {
    if (!API_BASE_URL) {
      const project = sampleProjects.find((candidate) => candidate.id === projectId) ?? sampleProjects[0];
      return { ...project, stage } satisfies Project;
    }
    return request<Project>(`/api/projects/${projectId}/stage`, {
      method: 'PATCH',
      body: JSON.stringify({ stage }),
    });
  },
  async createExpense(projectId: number, input: Omit<Expense, 'id' | 'projectId'>) {
    if (!API_BASE_URL) return { id: Date.now(), projectId, ...input } satisfies Expense;
    return request<Expense>(`/api/projects/${projectId}/expenses`, {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },
  async createDocument(projectId: number, input: Omit<DocumentRecord, 'id' | 'projectId' | 'url' | 'size'> & { url?: string; size?: number }) {
    const payload = { url: input.url ?? '#', size: input.size ?? 0, ...input };
    if (!API_BASE_URL) return { id: Date.now(), projectId, ...payload } satisfies DocumentRecord;
    return request<DocumentRecord>(`/api/projects/${projectId}/documents`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async inviteCollaborator(projectId: number, input: Pick<Collaborator, 'email' | 'role'> & { name?: string }) {
    if (!API_BASE_URL) return { id: Date.now(), projectId, status: 'invited' as const, ...input } satisfies Collaborator;
    return request<Collaborator>(`/api/projects/${projectId}/collaborators`, {
      method: 'POST',
      body: JSON.stringify(input),
    });
  },
  async seedSampleData() {
    if (!API_BASE_URL) return { seeded: true, projects: sampleProjects.length };
    return request<{ seeded: boolean; projects: number }>('/api/workspace/seed-sample-data', { method: 'POST' });
  },
};
