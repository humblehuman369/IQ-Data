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
