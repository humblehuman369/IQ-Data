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
