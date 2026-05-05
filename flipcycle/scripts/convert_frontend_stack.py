from pathlib import Path
import json

ROOT = Path('/home/ubuntu/workcycle')

def write(path: str, content: str):
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip() + '\n', encoding='utf-8')

root_package = {
    "name": "flipcycle-monorepo",
    "private": True,
    "packageManager": "pnpm@10.0.0",
    "scripts": {
        "dev": "pnpm --dir frontend dev",
        "build": "pnpm --dir frontend build",
        "start": "pnpm --dir frontend start",
        "check": "pnpm --dir frontend typecheck",
        "lint": "pnpm --dir frontend lint",
        "format": "pnpm --dir frontend format",
        "test": "pnpm --dir frontend test --run"
    },
    "devDependencies": {
        "typescript": "^5.9.0"
    }
}
write('package.json', json.dumps(root_package, indent=2))
write('pnpm-workspace.yaml', """
packages:
  - frontend
""")
write('vercel.json', json.dumps({
    "version": 2,
    "framework": "nextjs",
    "regions": ["iad1"],
    "buildCommand": "pnpm --dir frontend build",
    "installCommand": "pnpm install --filter flipcycle-frontend...",
    "outputDirectory": "frontend/.next",
    "rewrites": [
        {"source": "/api/:path*", "destination": "$NEXT_PUBLIC_API_BASE_URL/api/:path*"}
    ],
    "headers": [
        {"source": "/(.*)", "headers": [
            {"key": "X-Frame-Options", "value": "DENY"},
            {"key": "X-Content-Type-Options", "value": "nosniff"},
            {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}
        ]}
    ]
}, indent=2))

frontend_package = {
  "name": "flipcycle-frontend",
  "version": "1.0.0",
  "private": True,
  "type": "module",
  "scripts": {
    "dev": "next dev -H 0.0.0.0 -p ${PORT:-3000}",
    "build": "next build",
    "start": "next start -H 0.0.0.0 -p ${PORT:-3000}",
    "lint": "eslint . --max-warnings=0",
    "format": "prettier --check .",
    "format:write": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest"
  },
  "dependencies": {
    "@capacitor/android": "^8.0.0",
    "@capacitor/core": "^8.0.0",
    "@capacitor/ios": "^8.0.0",
    "@revenuecat/purchases-capacitor": "^11.0.0",
    "@sentry/nextjs": "^10.0.0",
    "@stripe/stripe-js": "^7.0.0",
    "@tanstack/react-query": "^5.90.0",
    "@vercel/analytics": "^1.5.0",
    "@vis.gl/react-google-maps": "^1.5.0",
    "lucide-react": "^0.555.0",
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-hook-form": "^7.65.0",
    "recharts": "^3.3.0",
    "sonner": "^2.0.0",
    "zod": "^4.1.0",
    "zustand": "^5.0.0"
  },
  "devDependencies": {
    "@eslint/eslintrc": "^3.3.0",
    "@testing-library/jest-dom": "^6.9.0",
    "@testing-library/react": "^16.3.0",
    "@testing-library/user-event": "^14.6.0",
    "@types/node": "^22.19.0",
    "@types/react": "^19.2.0",
    "@types/react-dom": "^19.2.0",
    "@vitejs/plugin-react": "^5.0.0",
    "eslint": "^9.38.0",
    "eslint-config-next": "^16.0.0",
    "jsdom": "^27.0.0",
    "prettier": "^3.6.0",
    "tailwindcss": "^4.1.0",
    "typescript": "^5.9.0",
    "vitest": "^3.2.0"
  }
}
write('frontend/package.json', json.dumps(frontend_package, indent=2))
write('frontend/tsconfig.json', json.dumps({
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es2022"],
    "allowJs": False,
    "skipLibCheck": True,
    "strict": True,
    "noEmit": True,
    "esModuleInterop": True,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": True,
    "isolatedModules": True,
    "jsx": "preserve",
    "incremental": True,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}, indent=2))
write('frontend/next-env.d.ts', """
/// <reference types="next" />
/// <reference types="next/image-types/global" />
""")
write('frontend/next.config.ts', """
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
  async redirects() {
    return [
      { source: '/dashboard/analyzer', destination: '/dashboard?section=analyzer', permanent: false },
      { source: '/dashboard/pipeline', destination: '/dashboard?section=pipeline', permanent: false },
      { source: '/dashboard/budgets', destination: '/dashboard?section=budgets', permanent: false },
      { source: '/dashboard/documents', destination: '/dashboard?section=documents', permanent: false },
      { source: '/dashboard/team', destination: '/dashboard?section=team', permanent: false },
    ];
  },
};

export default nextConfig;
""")
write('frontend/postcss.config.mjs', """
export default {
  plugins: {
    tailwindcss: {},
  },
};
""")
write('frontend/eslint.config.mjs', """
import { FlatCompat } from '@eslint/eslintrc';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({ baseDirectory: __dirname });

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    ignores: ['.next/**', 'node_modules/**', 'coverage/**'],
  },
];
""")
write('frontend/.prettierrc.json', json.dumps({"singleQuote": True, "semi": True, "printWidth": 100}, indent=2))
write('frontend/capacitor.config.ts', """
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.flipcycle.app',
  appName: 'FlipCycle',
  webDir: '.next',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    Purchases: {
      apiKey: process.env.NEXT_PUBLIC_REVENUECAT_PUBLIC_KEY,
    },
  },
};

export default config;
""")
write('frontend/vitest.config.ts', """
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}', 'lib/**/*.test.ts'],
  },
});
""")
write('frontend/vitest.setup.ts', """
import '@testing-library/jest-dom/vitest';
""")
write('frontend/sentry.client.config.ts', """
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.15 : 0,
  enabled: Boolean(process.env.NEXT_PUBLIC_SENTRY_DSN),
});
""")
write('frontend/sentry.server.config.ts', """
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 0,
  enabled: Boolean(process.env.SENTRY_DSN),
});
""")
write('frontend/app/globals.css', """
@import 'tailwindcss';

:root {
  color-scheme: light;
  --background: #f7f4ee;
  --foreground: #18201c;
  --muted: #6f756d;
  --panel: #ffffff;
  --accent: #1f8a70;
  --accent-strong: #146c59;
  --blueprint: #e8f3ef;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(31, 138, 112, 0.16), transparent 34rem),
    linear-gradient(135deg, #f7f4ee 0%, #ecf5f1 100%);
  color: var(--foreground);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
select,
textarea {
  font: inherit;
}

.focus-ring:focus-visible {
  outline: 3px solid rgba(31, 138, 112, 0.45);
  outline-offset: 3px;
}
""")
write('frontend/app/layout.tsx', """
import type { Metadata } from 'next';
import { Analytics } from '@vercel/analytics/react';
import { Toaster } from 'sonner';
import './globals.css';
import { Providers } from '@/components/providers';

export const metadata: Metadata = {
  title: 'FlipCycle | Real estate flip workspace',
  description:
    'FlipCycle helps real estate investors analyze deals, manage rehab budgets, track pipeline stages, and coordinate documents with teams.',
  applicationName: 'FlipCycle',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://flipcycle.vercel.app'),
  openGraph: {
    title: 'FlipCycle',
    description: 'A modern workspace for real estate flip teams.',
    type: 'website',
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
        <Toaster position="top-right" richColors />
        <Analytics />
      </body>
    </html>
  );
}
""")
write('frontend/lib/types.ts', """
export type PipelineStage = 'Acquisition' | 'Rehab' | 'Listed' | 'Sold';
export type CollaboratorRole = 'owner' | 'editor' | 'viewer';
export type ExpenseCategory = 'labor' | 'materials' | 'permits';
export type DocumentType = 'contracts' | 'photos' | 'inspection_reports' | 'other';

export type DealInput = {
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

export type DealMetrics = {
  profit: number;
  roi: number;
  cashOnCashReturn: number;
  totalInvested: number;
  cashInvested: number;
  financingCost: number;
};

export type Project = DealInput & {
  id: number;
  name: string;
  address: string;
  stage: PipelineStage;
  sqft: number;
};

export type Expense = {
  id: number;
  projectId: number;
  category: ExpenseCategory;
  description: string;
  estimate: number;
  actual: number;
  vendor?: string;
};

export type Comp = {
  id: number;
  projectId: number;
  address: string;
  salePrice: number;
  sqft: number;
  beds: number;
  baths: number;
  soldAt?: string;
};

export type DocumentRecord = {
  id: number;
  projectId: number;
  name: string;
  docType: DocumentType;
  url: string;
  mimeType?: string;
  size: number;
};

export type Collaborator = {
  id: number;
  projectId: number;
  email: string;
  name?: string;
  role: CollaboratorRole;
  status: 'invited' | 'active';
};
""")
write('frontend/lib/workcycle.ts', """
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
""")
write('frontend/lib/sample-data.ts', """
import type { Collaborator, Comp, DocumentRecord, Expense, Project } from './types';

export const sampleProjects: Project[] = [
  {
    id: 1,
    name: 'Maple Street Flip',
    address: '428 Maple Street, Richmond, VA',
    stage: 'Acquisition',
    purchasePrice: 218000,
    repairCosts: 62000,
    arv: 372000,
    downPayment: 43600,
    loanAmount: 174400,
    interestRate: 9.5,
    holdingMonths: 7,
    closingCosts: 8400,
    sellingCosts: 21500,
    sqft: 1880,
  },
  {
    id: 2,
    name: 'Riverbend Rehab',
    address: '1197 Riverbend Drive, Norfolk, VA',
    stage: 'Rehab',
    purchasePrice: 264000,
    repairCosts: 78000,
    arv: 445000,
    downPayment: 52800,
    loanAmount: 211200,
    interestRate: 10.25,
    holdingMonths: 8,
    closingCosts: 9200,
    sellingCosts: 25800,
    sqft: 2160,
  },
  {
    id: 3,
    name: 'Cedar Court Listing',
    address: '74 Cedar Court, Raleigh, NC',
    stage: 'Listed',
    purchasePrice: 302000,
    repairCosts: 89000,
    arv: 515000,
    downPayment: 60400,
    loanAmount: 241600,
    interestRate: 8.75,
    holdingMonths: 6,
    closingCosts: 11200,
    sellingCosts: 29800,
    sqft: 2440,
  },
  {
    id: 4,
    name: 'Pine Ridge Sold',
    address: '903 Pine Ridge Way, Charlotte, NC',
    stage: 'Sold',
    purchasePrice: 176000,
    repairCosts: 54000,
    arv: 319000,
    downPayment: 35200,
    loanAmount: 140800,
    interestRate: 9.0,
    holdingMonths: 5,
    closingCosts: 7200,
    sellingCosts: 18500,
    sqft: 1650,
  },
];

export const sampleExpenses: Expense[] = [
  { id: 1, projectId: 1, category: 'labor', description: 'Framing and trim crew', estimate: 18000, actual: 17250, vendor: 'Precision Build Co.' },
  { id: 2, projectId: 1, category: 'materials', description: 'Cabinets and fixtures', estimate: 22000, actual: 24100, vendor: 'ProSource Supply' },
  { id: 3, projectId: 2, category: 'permits', description: 'Electrical and plumbing permits', estimate: 3200, actual: 2950, vendor: 'City permits office' },
  { id: 4, projectId: 3, category: 'materials', description: 'Exterior paint package', estimate: 7400, actual: 7100, vendor: 'Sherwin Supply' },
];

export const sampleComps: Comp[] = [
  { id: 1, projectId: 1, address: '413 Maple Street', salePrice: 366000, sqft: 1840, beds: 3, baths: 2, soldAt: '2026-03-12' },
  { id: 2, projectId: 1, address: '440 Maple Street', salePrice: 381500, sqft: 1925, beds: 4, baths: 2, soldAt: '2026-02-18' },
  { id: 3, projectId: 2, address: '1211 Riverbend Drive', salePrice: 452000, sqft: 2210, beds: 4, baths: 3, soldAt: '2026-04-02' },
];

export const sampleDocuments: DocumentRecord[] = [
  { id: 1, projectId: 1, name: 'Purchase agreement.pdf', docType: 'contracts', url: '#', mimeType: 'application/pdf', size: 482000 },
  { id: 2, projectId: 2, name: 'Rehab photo log.zip', docType: 'photos', url: '#', mimeType: 'application/zip', size: 1430000 },
  { id: 3, projectId: 3, name: 'Inspection findings.pdf', docType: 'inspection_reports', url: '#', mimeType: 'application/pdf', size: 620000 },
];

export const sampleCollaborators: Collaborator[] = [
  { id: 1, projectId: 1, email: 'owner@flipcycle.local', name: 'Project Owner', role: 'owner', status: 'active' },
  { id: 2, projectId: 1, email: 'gc@example.com', name: 'General Contractor', role: 'editor', status: 'active' },
  { id: 3, projectId: 2, email: 'lender@example.com', name: 'Capital Partner', role: 'viewer', status: 'invited' },
];
""")
write('frontend/lib/api.ts', """
import type { DealInput } from './types';
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
    return request<typeof sampleComps>(`/api/projects/${projectId}/comps`);
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
};
""")
write('frontend/lib/forms.ts', """
import { z } from 'zod';

const money = z.coerce.number().finite().min(0).max(100_000_000);

export const dealFormSchema = z.object({
  purchasePrice: money,
  repairCosts: money,
  arv: money,
  downPayment: money,
  loanAmount: money,
  interestRate: z.coerce.number().finite().min(0).max(50),
  holdingMonths: z.coerce.number().int().min(0).max(120),
  closingCosts: money,
  sellingCosts: money,
});

export type DealFormValues = z.infer<typeof dealFormSchema>;
""")
write('frontend/store/use-workspace-store.ts', """
import { create } from 'zustand';
import type { PipelineStage } from '@/lib/types';

type DashboardSection = 'overview' | 'analyzer' | 'pipeline' | 'budgets' | 'documents' | 'team';

type WorkspaceState = {
  activeProjectId: number;
  selectedStage: PipelineStage | 'All';
  dashboardSection: DashboardSection;
  setActiveProjectId: (projectId: number) => void;
  setSelectedStage: (stage: PipelineStage | 'All') => void;
  setDashboardSection: (section: DashboardSection) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeProjectId: 1,
  selectedStage: 'All',
  dashboardSection: 'overview',
  setActiveProjectId: (activeProjectId) => set({ activeProjectId }),
  setSelectedStage: (selectedStage) => set({ selectedStage }),
  setDashboardSection: (dashboardSection) => set({ dashboardSection }),
}));
""")
write('frontend/components/providers.tsx', """
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { APIProvider } from '@vis.gl/react-google-maps';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <APIProvider apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? ''}>{children}</APIProvider>
    </QueryClientProvider>
  );
}
""")
write('frontend/components/metric-card.tsx', """
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
""")
write('frontend/components/deal-analyzer.tsx', """
'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Calculator, Percent, WalletCards } from 'lucide-react';
import { useForm } from 'react-hook-form';
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
  const values = form.watch();
  const liveMetrics = calculateDeal(values);
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
                <input className="w-full bg-transparent px-2 py-3 outline-none" type="number" step="0.01" {...form.register(field.name)} />
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
""")
write('frontend/app/page.tsx', """
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
""")
write('frontend/app/dashboard/page.tsx', """
'use client';

import { useQuery } from '@tanstack/react-query';
import { BarChart3, Building2, FileText, LayoutDashboard, Menu, Users, WalletCards } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { DealAnalyzer } from '@/components/deal-analyzer';
import { MetricCard } from '@/components/metric-card';
import { flipcycleApi } from '@/lib/api';
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

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const requestedSection = searchParams.get('section') as SectionId | null;
  const activeSection = sections.some((section) => section.id === requestedSection) ? requestedSection! : 'overview';
  const [mobileOpen, setMobileOpen] = useState(false);
  const { activeProjectId, setActiveProjectId } = useWorkspaceStore();

  const projectsQuery = useQuery({ queryKey: ['projects'], queryFn: flipcycleApi.projects });
  const summaryQuery = useQuery({ queryKey: ['summary'], queryFn: flipcycleApi.summary });
  const projects = projectsQuery.data ?? [];
  const activeProject = projects.find((project) => project.id === activeProjectId) ?? projects[0];
  const projectId = activeProject?.id ?? 1;
  const expensesQuery = useQuery({ queryKey: ['expenses', projectId], queryFn: () => flipcycleApi.expenses(projectId), enabled: Boolean(activeProject) });
  const compsQuery = useQuery({ queryKey: ['comps', projectId], queryFn: () => flipcycleApi.comps(projectId), enabled: Boolean(activeProject) });
  const docsQuery = useQuery({ queryKey: ['documents', projectId], queryFn: () => flipcycleApi.documents(projectId), enabled: Boolean(activeProject) });
  const collaboratorsQuery = useQuery({ queryKey: ['collaborators', projectId], queryFn: () => flipcycleApi.collaborators(projectId), enabled: Boolean(activeProject) });

  const chartData = useMemo(() => projects.map((project) => ({ name: project.name.replace(' ', '\n'), profit: calculateDeal(project).profit, roi: calculateDeal(project).roi })), [projects]);
  const compEstimate = estimateArvFromComps(compsQuery.data ?? [], activeProject?.sqft);

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className={`${mobileOpen ? 'block' : 'hidden'} border-r border-black/5 bg-white/75 p-5 backdrop-blur lg:block`}>
        <Link href="/" className="mb-8 flex items-center gap-3 font-semibold text-slate-950"><span className="grid h-10 w-10 place-items-center rounded-2xl bg-slate-950 text-white">FC</span>FlipCycle</Link>
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
            {PIPELINE_STAGES.map((stage) => <section key={stage} className="rounded-3xl bg-white/86 p-4 shadow-sm ring-1 ring-black/5"><h2 className="font-semibold text-slate-950">{stage}</h2><div className="mt-4 space-y-3">{projects.filter((project) => project.stage === stage).map((project) => <button key={project.id} onClick={() => setActiveProjectId(project.id)} className="w-full rounded-2xl bg-slate-50 p-4 text-left hover:bg-emerald-50"><p className="font-semibold text-slate-900">{project.name}</p><p className="mt-1 text-sm text-slate-500">{currency.format(calculateDeal(project).profit)} projected profit</p></button>)}</div></section>)}
          </div>
        )}

        {activeSection === 'budgets' && (
          <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5"><h2 className="text-xl font-semibold text-slate-950">Budget lines for {activeProject?.name}</h2><div className="mt-5 overflow-hidden rounded-2xl border border-slate-100"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-500"><tr><th className="p-3">Category</th><th>Description</th><th>Estimate</th><th>Actual</th><th>Vendor</th></tr></thead><tbody>{(expensesQuery.data ?? []).map((expense) => <tr key={expense.id} className="border-t border-slate-100"><td className="p-3 font-medium capitalize">{expense.category}</td><td>{expense.description}</td><td>{currency.format(expense.estimate)}</td><td>{currency.format(expense.actual)}</td><td>{expense.vendor}</td></tr>)}</tbody></table></div></section>
        )}

        {activeSection === 'documents' && (
          <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5"><h2 className="text-xl font-semibold text-slate-950">Documents for {activeProject?.name}</h2><p className="mt-2 text-sm text-slate-500">FastAPI stores file metadata in PostgreSQL and file bytes in S3.</p><div className="mt-5 grid gap-3 md:grid-cols-3">{(docsQuery.data ?? []).map((document) => <article key={document.id} className="rounded-2xl bg-slate-50 p-4"><FileText className="h-5 w-5 text-emerald-700" /><p className="mt-3 font-semibold">{document.name}</p><p className="mt-1 text-sm text-slate-500">{document.docType.replace('_', ' ')}</p></article>)}</div></section>
        )}

        {activeSection === 'team' && (
          <section className="rounded-3xl bg-white/88 p-6 shadow-sm ring-1 ring-black/5"><h2 className="text-xl font-semibold text-slate-950">Team access</h2><div className="mt-5 grid gap-3 md:grid-cols-3">{(collaboratorsQuery.data ?? []).map((collaborator) => <article key={collaborator.id} className="rounded-2xl bg-slate-50 p-4"><Users className="h-5 w-5 text-emerald-700" /><p className="mt-3 font-semibold">{collaborator.name ?? collaborator.email}</p><p className="mt-1 text-sm text-slate-500">{collaborator.role} · {collaborator.status}</p></article>)}</div></section>
        )}

        {activeSection === 'analyzer' && activeProject && <p className="mt-4 text-sm text-slate-500">Current comp-derived ARV signal: {currency.format(compEstimate.estimatedArv)} from {compEstimate.compCount} comps.</p>}
      </section>
    </main>
  );
}
""")
write('frontend/tests/workcycle.test.ts', """
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
      profit: 58934.67,
      roi: 18.82,
      cashOnCashReturn: 41.96,
      totalInvested: 313065.33,
      cashInvested: 140465.33,
      financingCost: 9665.33,
    });
  });

  it('estimates ARV from comps and target square footage', () => {
    expect(estimateArvFromComps([{ salePrice: 366000, sqft: 1840 }, { salePrice: 381500, sqft: 1925 }], 1880)).toMatchObject({
      estimatedArv: 374390.24,
      compCount: 2,
    });
  });
});
""")
write('frontend/tests/branding.test.ts', """
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import HomePage from '@/app/page';

describe('FlipCycle branding', () => {
  it('renders the migrated FlipCycle homepage brand', () => {
    render(<HomePage />);
    expect(screen.getAllByText('FlipCycle').length).toBeGreaterThan(0);
    expect(screen.getByText(/Run your next profitable flip through FlipCycle/i)).toBeInTheDocument();
  });
});
""")
print('frontend stack files written')
