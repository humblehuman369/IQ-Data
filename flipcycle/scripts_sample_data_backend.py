from pathlib import Path

root = Path('/home/ubuntu/workcycle')
db_path = root / 'server/db.ts'
router_path = root / 'server/routers.ts'
test_path = root / 'server/workcycle.test.ts'

# Update db.ts imports and append sample-data workflow.
db = db_path.read_text()
if 'import { storagePut } from "./storage";' not in db:
    db = db.replace('import { calculateDeal, CollaboratorRole, estimateArvFromComps } from "./workcycle";\n', 'import { calculateDeal, CollaboratorRole, estimateArvFromComps } from "./workcycle";\nimport { storagePut } from "./storage";\n')

sample_block = r'''

type SampleProjectTemplate = {
  project: Omit<InsertProject, "ownerId">;
  expenses: Array<Omit<InsertExpense, "projectId" | "createdById">>;
  comps: Array<Omit<InsertComp, "projectId" | "createdById">>;
  collaborators: Array<Omit<InsertCollaborator, "projectId" | "createdById">>;
  documents: Array<{
    name: string;
    docType: InsertDocument["docType"];
    mimeType: string;
    content: string;
  }>;
};

export const SAMPLE_PROJECT_NAMES = [
  "Onboarding Sample · Maple Street Flip",
  "Onboarding Sample · Riverbend Rehab",
  "Onboarding Sample · Cedar Court Listing",
  "Onboarding Sample · Pine Ridge Sold",
] as const;

const sampleProjects: SampleProjectTemplate[] = [
  {
    project: { name: SAMPLE_PROJECT_NAMES[0], address: "128 Maple Street, Columbus, OH", stage: "Acquisition", purchasePrice: 214000, repairCosts: 52000, arv: 342000, downPayment: 42800, loanAmount: 171200, interestRate: 9, holdingMonths: 6, closingCosts: 7200, sellingCosts: 19000, sqft: 1580 },
    expenses: [
      { category: "labor", description: "Demo crew and framing deposit", estimate: 16500, actual: 14200, vendor: "Northstar Renovations" },
      { category: "materials", description: "Kitchen cabinet and flooring package", estimate: 18900, actual: 17350, vendor: "Builder Supply Co." },
      { category: "permits", description: "Building and electrical permits", estimate: 2400, actual: 2250, vendor: "City permits office" },
    ],
    comps: [
      { address: "116 Maple Street", salePrice: 336500, sqft: 1540, beds: 3, baths: 2, soldAt: "2026-02-14" },
      { address: "203 Walnut Avenue", salePrice: 348000, sqft: 1625, beds: 3, baths: 2, soldAt: "2026-03-02" },
      { address: "77 Birch Lane", salePrice: 329000, sqft: 1490, beds: 3, baths: 2, soldAt: "2026-03-28" },
    ],
    collaborators: [
      { email: "casey.editor@example.com", name: "Casey Renovation Lead", role: "editor", status: "active" },
      { email: "morgan.viewer@example.com", name: "Morgan Capital Partner", role: "viewer", status: "invited" },
    ],
    documents: [
      { name: "Maple purchase contract.txt", docType: "contracts", mimeType: "text/plain", content: "Sample purchase contract summary for the Maple Street acquisition. This onboarding file demonstrates S3-backed Workcycle contract storage." },
      { name: "Maple inspection report.txt", docType: "inspection_reports", mimeType: "text/plain", content: "Sample inspection notes: roof remaining life 8 years, HVAC service recommended, electrical panel replacement budgeted." },
      { name: "Maple before photo.svg", docType: "photos", mimeType: "image/svg+xml", content: `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520"><rect width="900" height="520" fill="#e0f2fe"/><rect x="210" y="210" width="480" height="220" rx="12" fill="#ffffff" stroke="#0465F2" stroke-width="8"/><path d="M180 230 L450 70 L720 230 Z" fill="#0FA4E9"/><rect x="280" y="275" width="90" height="155" fill="#bae6fd"/><rect x="505" y="280" width="120" height="90" fill="#38bdf8"/><text x="450" y="485" text-anchor="middle" font-family="Inter,Arial" font-size="28" fill="#0f172a">Maple Street sample photo</text></svg>` },
    ],
  },
  {
    project: { name: SAMPLE_PROJECT_NAMES[1], address: "44 Riverbend Drive, Cincinnati, OH", stage: "Rehab", purchasePrice: 188000, repairCosts: 68000, arv: 318000, downPayment: 37600, loanAmount: 150400, interestRate: 10, holdingMonths: 7, closingCosts: 6400, sellingCosts: 17200, sqft: 1425 },
    expenses: [
      { category: "labor", description: "Rough plumbing and bath remodel labor", estimate: 21200, actual: 22400, vendor: "River City Trades" },
      { category: "materials", description: "Roofing materials and exterior paint", estimate: 15500, actual: 15100, vendor: "Summit Materials" },
      { category: "permits", description: "Plumbing and roofing permits", estimate: 1900, actual: 2050, vendor: "County building department" },
    ],
    comps: [
      { address: "51 Riverbend Drive", salePrice: 314000, sqft: 1400, beds: 3, baths: 2, soldAt: "2026-01-22" },
      { address: "9 Harbor Court", salePrice: 322500, sqft: 1460, beds: 3, baths: 2, soldAt: "2026-02-18" },
    ],
    collaborators: [
      { email: "jamie.pm@example.com", name: "Jamie Project Manager", role: "editor", status: "active" },
      { email: "taylor.lender@example.com", name: "Taylor Lending Partner", role: "viewer", status: "invited" },
    ],
    documents: [
      { name: "Riverbend scope of work.txt", docType: "contracts", mimeType: "text/plain", content: "Sample scope of work covering baths, roof, exterior paint, and punch-list milestones for Riverbend Rehab." },
      { name: "Riverbend inspection notes.txt", docType: "inspection_reports", mimeType: "text/plain", content: "Sample inspection report: moisture remediation complete, plumbing rough-in scheduled, final electrical pending." },
    ],
  },
  {
    project: { name: SAMPLE_PROJECT_NAMES[2], address: "812 Cedar Court, Dayton, OH", stage: "Listed", purchasePrice: 246000, repairCosts: 41000, arv: 374000, downPayment: 49200, loanAmount: 196800, interestRate: 8, holdingMonths: 5, closingCosts: 8100, sellingCosts: 22400, sqft: 1810 },
    expenses: [
      { category: "labor", description: "Final punch-list and staging support", estimate: 7200, actual: 6900, vendor: "Polished Home Services" },
      { category: "materials", description: "Lighting fixtures and hardware", estimate: 4800, actual: 5150, vendor: "Brightline Supply" },
      { category: "permits", description: "Final occupancy inspection", estimate: 850, actual: 850, vendor: "City inspection office" },
    ],
    comps: [
      { address: "804 Cedar Court", salePrice: 369000, sqft: 1780, beds: 4, baths: 3, soldAt: "2026-03-08" },
      { address: "21 Garden Way", salePrice: 381500, sqft: 1855, beds: 4, baths: 3, soldAt: "2026-03-20" },
    ],
    collaborators: [
      { email: "alex.agent@example.com", name: "Alex Listing Agent", role: "editor", status: "active" },
      { email: "riley.viewer@example.com", name: "Riley Investor", role: "viewer", status: "active" },
    ],
    documents: [
      { name: "Cedar listing photo.svg", docType: "photos", mimeType: "image/svg+xml", content: `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#0465F2"/><stop offset="1" stop-color="#0FA4E9"/></linearGradient></defs><rect width="900" height="520" fill="#f8fafc"/><rect x="160" y="110" width="580" height="320" rx="26" fill="url(#g)" opacity=".18"/><rect x="235" y="230" width="430" height="180" rx="16" fill="#fff" stroke="#0FA4E9" stroke-width="8"/><path d="M210 245 L450 100 L690 245 Z" fill="#0465F2"/><text x="450" y="480" text-anchor="middle" font-family="Inter,Arial" font-size="28" fill="#0f172a">Cedar Court listing sample</text></svg>` },
      { name: "Cedar seller disclosure.txt", docType: "contracts", mimeType: "text/plain", content: "Sample seller disclosure packet for onboarding. Replace with actual transaction files when using Workcycle live." },
    ],
  },
  {
    project: { name: SAMPLE_PROJECT_NAMES[3], address: "305 Pine Ridge Road, Lexington, KY", stage: "Sold", purchasePrice: 172000, repairCosts: 39000, arv: 286000, downPayment: 34400, loanAmount: 137600, interestRate: 9, holdingMonths: 4, closingCosts: 5900, sellingCosts: 15800, sqft: 1320 },
    expenses: [
      { category: "labor", description: "Completed interior refresh labor", estimate: 12800, actual: 12100, vendor: "Bluegrass Build Team" },
      { category: "materials", description: "Paint, flooring, and appliance package", estimate: 17600, actual: 16950, vendor: "HomePro Supply" },
      { category: "permits", description: "Mechanical permit closeout", estimate: 700, actual: 700, vendor: "County permits" },
    ],
    comps: [
      { address: "299 Pine Ridge Road", salePrice: 279500, sqft: 1280, beds: 3, baths: 2, soldAt: "2026-01-05" },
      { address: "313 Pine Ridge Road", salePrice: 288000, sqft: 1355, beds: 3, baths: 2, soldAt: "2026-01-30" },
    ],
    collaborators: [
      { email: "sam.viewer@example.com", name: "Sam Portfolio Reviewer", role: "viewer", status: "active" },
    ],
    documents: [
      { name: "Pine closing statement.txt", docType: "contracts", mimeType: "text/plain", content: "Sample sold-project closing statement summary for onboarding metrics and document storage demonstration." },
    ],
  },
];

export async function seedSampleWorkspace(user: CurrentUser) {
  const existingProjects = await listProjects(user);
  const existingSampleProjects = existingProjects.filter((project) => SAMPLE_PROJECT_NAMES.includes(project.name as (typeof SAMPLE_PROJECT_NAMES)[number]));
  if (existingSampleProjects.length > 0) {
    return {
      created: false,
      projectCount: existingSampleProjects.length,
      message: "Sample onboarding data is already available in this Workcycle workspace.",
      projectIds: existingSampleProjects.map((project) => project.id),
    };
  }

  const seededProjectIds: number[] = [];
  for (const template of sampleProjects) {
    const project = await createProject(user, template.project);
    if (!project) continue;
    seededProjectIds.push(project.id);

    for (const expense of template.expenses) {
      await addExpense(user, { projectId: project.id, ...expense });
    }
    for (const comp of template.comps) {
      await addComp(user, { projectId: project.id, ...comp });
    }
    for (const collaborator of template.collaborators) {
      await inviteCollaborator(user, { projectId: project.id, ...collaborator });
    }
    for (const document of template.documents) {
      const key = `sample-data/${user.id}/${project.id}/${document.name.replace(/[^a-zA-Z0-9._-]/g, "-")}`;
      const uploaded = await storagePut(key, document.content, document.mimeType);
      await addDocument(user, { projectId: project.id, createdById: user.id, name: document.name, docType: document.docType, fileKey: uploaded.key, url: uploaded.url, mimeType: document.mimeType, size: Buffer.byteLength(document.content) });
    }
  }

  return {
    created: true,
    projectCount: seededProjectIds.length,
    message: "Sample onboarding data has been added to your Workcycle dashboard.",
    projectIds: seededProjectIds,
  };
}
'''

if 'export async function seedSampleWorkspace' not in db:
    db = db.rstrip() + sample_block + '\n'

db_path.write_text(db)

# Add router mutation.
router = router_path.read_text()
if 'seedSampleData:' not in router:
    router = router.replace('
