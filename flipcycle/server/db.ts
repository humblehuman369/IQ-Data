import { and, eq, or } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { collaborators, comps, documents, expenses, InsertCollaborator, InsertComp, InsertDocument, InsertExpense, InsertProject, InsertUser, Project, projects, users } from "../drizzle/schema";
import { calculateDeal, CollaboratorRole, estimateArvFromComps } from "./workcycle";
import { storagePut } from "./storage";
import { ENV } from './_core/env';

type CurrentUser = { id: number; email?: string | null; name?: string | null };
type AccessRole = CollaboratorRole;
const roleRank: Record<AccessRole, number> = { viewer: 1, editor: 2, owner: 3 };

let _db: ReturnType<typeof drizzle> | null = null;

export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) throw new Error("User openId is required for upsert");
  const db = await getDb();
  if (!db) return;
  const values: InsertUser = { openId: user.openId };
  const updateSet: Record<string, unknown> = {};
  (["name", "email", "loginMethod"] as const).forEach((field) => {
    if (user[field] !== undefined) {
      const normalized = user[field] ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    }
  });
  if (user.lastSignedIn !== undefined) { values.lastSignedIn = user.lastSignedIn; updateSet.lastSignedIn = user.lastSignedIn; }
  if (user.role !== undefined) { values.role = user.role; updateSet.role = user.role; }
  else if (user.openId === ENV.ownerOpenId) { values.role = 'admin'; updateSet.role = 'admin'; }
  if (!values.lastSignedIn) values.lastSignedIn = new Date();
  if (Object.keys(updateSet).length === 0) updateSet.lastSignedIn = new Date();
  await db.insert(users).values(values).onDuplicateKeyUpdate({ set: updateSet });
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

function assertAccess(role: AccessRole | null, minimum: AccessRole) {
  if (!role || roleRank[role] < roleRank[minimum]) throw new Error("You do not have permission for this FlipCycle project action");
}

async function getProjectAccess(projectId: number, user: CurrentUser, minimum: AccessRole = "viewer"): Promise<{ project: Project; role: AccessRole } | null> {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const project = (await db.select().from(projects).where(eq(projects.id, projectId)).limit(1))[0];
  if (!project) return null;
  let role: AccessRole | null = null;
  if (project.ownerId === user.id) role = "owner";
  else if (user.email) {
    const collab = (await db.select().from(collaborators).where(and(eq(collaborators.projectId, projectId), eq(collaborators.email, user.email))).limit(1))[0];
    if (collab) role = collab.role;
  }
  assertAccess(role, minimum);
  return { project, role: role ?? "viewer" };
}

export async function createProject(user: CurrentUser, input: Omit<InsertProject, "ownerId">) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const result = await db.insert(projects).values({ ...input, ownerId: user.id });
  const insertId = Number(result[0].insertId);
  await db.insert(collaborators).values({ projectId: insertId, createdById: user.id, userId: user.id, email: user.email || `${user.id}@flipcycle.local`, role: "owner", status: "active", name: user.name || "Project owner" });
  return getProject(insertId, user);
}

export async function getProject(projectId: number, user: CurrentUser) {
  const access = await getProjectAccess(projectId, user, "viewer");
  return access?.project ?? null;
}

export async function listProjects(user: CurrentUser) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const owned = await db.select().from(projects).where(eq(projects.ownerId, user.id));
  if (!user.email) return owned;
  const membershipRows = await db.select().from(collaborators).where(eq(collaborators.email, user.email));
  const accessible: Project[] = [...owned];
  for (const membership of membershipRows) {
    if (accessible.some((project) => project.id === membership.projectId)) continue;
    const row = (await db.select().from(projects).where(eq(projects.id, membership.projectId)).limit(1))[0];
    if (row) accessible.push(row);
  }
  return accessible;
}

export async function updateProjectStage(user: CurrentUser, projectId: number, stage: InsertProject["stage"]) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  await getProjectAccess(projectId, user, "editor");
  await db.update(projects).set({ stage }).where(eq(projects.id, projectId));
  return getProject(projectId, user);
}

export async function addExpense(user: CurrentUser, input: Omit<InsertExpense, "createdById">) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  await getProjectAccess(input.projectId, user, "editor");
  await db.insert(expenses).values({ ...input, createdById: user.id });
  return listExpenses(user, input.projectId);
}

export async function listExpenses(user: CurrentUser, projectId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const access = await getProjectAccess(projectId, user, "viewer");
  if (!access) return [];
  return db.select().from(expenses).where(eq(expenses.projectId, projectId));
}

export async function addComp(user: CurrentUser, input: Omit<InsertComp, "createdById">) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  await getProjectAccess(input.projectId, user, "editor");
  await db.insert(comps).values({ ...input, createdById: user.id });
  return getCompsWithEstimate(user, input.projectId);
}

export async function getCompsWithEstimate(user: CurrentUser, projectId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const access = await getProjectAccess(projectId, user, "viewer");
  if (!access) return { comps: [], estimate: estimateArvFromComps([]) };
  const rows = await db.select().from(comps).where(eq(comps.projectId, projectId));
  return { comps: rows, estimate: estimateArvFromComps(rows, access.project.sqft) };
}

export async function addDocument(user: CurrentUser, input: Omit<InsertDocument, "createdById">) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  await getProjectAccess(input.projectId, user, "editor");
  await db.insert(documents).values({ ...input, createdById: user.id });
  return listDocuments(user, input.projectId);
}

export async function listDocuments(user: CurrentUser, projectId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const access = await getProjectAccess(projectId, user, "viewer");
  if (!access) return [];
  return db.select().from(documents).where(eq(documents.projectId, projectId));
}

export async function inviteCollaborator(user: CurrentUser, input: Omit<InsertCollaborator, "createdById">) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  await getProjectAccess(input.projectId, user, "owner");
  await db.insert(collaborators).values({ ...input, createdById: user.id });
  return listCollaborators(user, input.projectId);
}

export async function updateCollaboratorRole(user: CurrentUser, collaboratorId: number, role: CollaboratorRole) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const collab = (await db.select().from(collaborators).where(eq(collaborators.id, collaboratorId)).limit(1))[0];
  if (!collab) throw new Error("Collaborator not found");
  await getProjectAccess(collab.projectId, user, "owner");
  await db.update(collaborators).set({ role }).where(eq(collaborators.id, collaboratorId));
  return listCollaborators(user, collab.projectId);
}

export async function removeCollaborator(user: CurrentUser, collaboratorId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const collab = (await db.select().from(collaborators).where(eq(collaborators.id, collaboratorId)).limit(1))[0];
  if (!collab) throw new Error("Collaborator not found");
  await getProjectAccess(collab.projectId, user, "owner");
  await db.delete(collaborators).where(and(eq(collaborators.id, collaboratorId), or(eq(collaborators.role, "editor"), eq(collaborators.role, "viewer"))));
  return listCollaborators(user, collab.projectId);
}

export async function listCollaborators(user: CurrentUser, projectId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const access = await getProjectAccess(projectId, user, "viewer");
  if (!access) return [];
  return db.select().from(collaborators).where(eq(collaborators.projectId, projectId));
}


export async function searchComps(user: CurrentUser, projectId: number, query: string) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  const access = await getProjectAccess(projectId, user, "viewer");
  if (!access) return { comps: [], estimate: estimateArvFromComps([]) };
  const rows = await db.select().from(comps).where(eq(comps.projectId, projectId));
  const normalized = query.trim().toLowerCase();
  const matches = normalized ? rows.filter((row) => row.address.toLowerCase().includes(normalized) || String(row.salePrice).includes(normalized)) : rows;
  return { comps: matches, estimate: estimateArvFromComps(matches, access.project.sqft) };
}

export async function acceptInvitation(user: CurrentUser, projectId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database is not available");
  if (!user.email) throw new Error("A verified email is required to accept a FlipCycle project invitation");
  await getProjectAccess(projectId, user, "viewer");
  await db.update(collaborators).set({ status: "active", userId: user.id }).where(and(eq(collaborators.projectId, projectId), eq(collaborators.email, user.email)));
  return listCollaborators(user, projectId);
}

export async function getDashboardSummary(user: CurrentUser) {
  const userProjects = await listProjects(user);
  const activeDeals = userProjects.filter((project) => project.stage !== "Sold").length;
  const completedFlips = userProjects.filter((project) => project.stage === "Sold").length;
  const totalInvested = userProjects.reduce((sum, project) => sum + calculateDeal(project).cashInvested, 0);
  const projectedProfit = userProjects.reduce((sum, project) => sum + calculateDeal(project).profit, 0);
  return { activeDeals, totalInvested, projectedProfit, completedFlips };
}

export const SAMPLE_PROJECT_NAMES = [
  "Onboarding Sample · Maple Street Flip",
  "Onboarding Sample · Riverbend Rehab",
  "Onboarding Sample · Cedar Court Listing",
  "Onboarding Sample · Pine Ridge Sold",
] as const;

type SampleProjectTemplate = {
  project: Omit<InsertProject, "ownerId">;
  expenses: Array<Omit<InsertExpense, "projectId" | "createdById">>;
  comps: Array<Omit<InsertComp, "projectId" | "createdById">>;
  collaborators: Array<Omit<InsertCollaborator, "projectId" | "createdById">>;
  documents: Array<{ name: string; docType: InsertDocument["docType"]; mimeType: string; content: string }>;
};

const samplePhotoSvg = (label: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#0465F2"/><stop offset="1" stop-color="#0FA4E9"/></linearGradient></defs><rect width="900" height="520" fill="#f8fafc"/><rect x="165" y="120" width="570" height="300" rx="24" fill="url(#g)" opacity=".16"/><path d="M220 245 L450 95 L680 245 Z" fill="#0465F2"/><rect x="250" y="245" width="400" height="170" rx="16" fill="#ffffff" stroke="#0FA4E9" stroke-width="8"/><rect x="305" y="300" width="78" height="115" fill="#bae6fd"/><rect x="510" y="295" width="95" height="72" fill="#38bdf8"/><text x="450" y="480" text-anchor="middle" font-family="Inter,Arial" font-size="28" fill="#0f172a">${label}</text></svg>`;

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
      { name: "Maple purchase contract.txt", docType: "contracts", mimeType: "text/plain", content: "Sample purchase contract summary for the Maple Street acquisition. This onboarding file demonstrates S3-backed FlipCycle contract storage." },
      { name: "Maple inspection report.txt", docType: "inspection_reports", mimeType: "text/plain", content: "Sample inspection notes: roof remaining life 8 years, HVAC service recommended, electrical panel replacement budgeted." },
      { name: "Maple before photo.svg", docType: "photos", mimeType: "image/svg+xml", content: samplePhotoSvg("Maple Street sample photo") },
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
      { name: "Cedar listing photo.svg", docType: "photos", mimeType: "image/svg+xml", content: samplePhotoSvg("Cedar Court listing sample") },
      { name: "Cedar seller disclosure.txt", docType: "contracts", mimeType: "text/plain", content: "Sample seller disclosure packet for onboarding. Replace with actual transaction files when using FlipCycle live." },
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
      message: "Sample onboarding data is already available in this FlipCycle workspace.",
      projectIds: existingSampleProjects.map((project) => project.id),
    };
  }

  const seededProjectIds: number[] = [];
  for (const template of sampleProjects) {
    const project = await createProject(user, template.project);
    if (!project) continue;
    seededProjectIds.push(project.id);
    for (const expense of template.expenses) await addExpense(user, { projectId: project.id, ...expense });
    for (const comp of template.comps) await addComp(user, { projectId: project.id, ...comp });
    for (const collaborator of template.collaborators) await inviteCollaborator(user, { projectId: project.id, ...collaborator });
    for (const document of template.documents) {
      const key = `sample-data/${user.id}/${project.id}/${document.name.replace(/[^a-zA-Z0-9._-]/g, "-")}`;
      const uploaded = await storagePut(key, document.content, document.mimeType);
      await addDocument(user, { projectId: project.id, name: document.name, docType: document.docType, fileKey: uploaded.key, url: uploaded.url, mimeType: document.mimeType, size: Buffer.byteLength(document.content) });
    }
  }

  return {
    created: true,
    projectCount: seededProjectIds.length,
    message: "Sample onboarding data has been added to your FlipCycle dashboard.",
    projectIds: seededProjectIds,
  };
}
