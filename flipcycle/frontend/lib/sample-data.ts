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
