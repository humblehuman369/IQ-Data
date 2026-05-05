import { COOKIE_NAME } from "@shared/const";
import { z } from "zod";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";
import * as db from "./db";
import { storagePut } from "./storage";
import { calculateDeal, COLLABORATOR_ROLES, DOCUMENT_TYPES, EXPENSE_CATEGORIES, PIPELINE_STAGES } from "./workcycle";

const money = z.number().finite().min(0).max(100_000_000);
const dealInput = z.object({
  purchasePrice: money,
  repairCosts: money,
  arv: money,
  downPayment: money,
  loanAmount: money,
  interestRate: z.number().finite().min(0).max(50),
  holdingMonths: z.number().int().min(0).max(120),
  closingCosts: money,
  sellingCosts: money,
});

const projectInput = dealInput.extend({
  name: z.string().min(2).max(160),
  address: z.string().min(4).max(255),
  stage: z.enum(PIPELINE_STAGES).default("Acquisition"),
  sqft: z.number().int().min(0).max(100_000).default(0),
});

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  workcycle: router({
    calculateDeal: publicProcedure.input(dealInput).query(({ input }) => calculateDeal(input)),
    summary: protectedProcedure.query(({ ctx }) => db.getDashboardSummary(ctx.user)),
    projects: protectedProcedure.query(({ ctx }) => db.listProjects(ctx.user)),
    seedSampleData: protectedProcedure.mutation(({ ctx }) => db.seedSampleWorkspace(ctx.user)),
    createProject: protectedProcedure.input(projectInput).mutation(({ ctx, input }) => db.createProject(ctx.user, input)),
    updateStage: protectedProcedure.input(z.object({ projectId: z.number().int().positive(), stage: z.enum(PIPELINE_STAGES) })).mutation(({ ctx, input }) => db.updateProjectStage(ctx.user, input.projectId, input.stage)),
    expenses: protectedProcedure.input(z.object({ projectId: z.number().int().positive() })).query(({ ctx, input }) => db.listExpenses(ctx.user, input.projectId)),
    addExpense: protectedProcedure.input(z.object({ projectId: z.number().int().positive(), category: z.enum(EXPENSE_CATEGORIES), description: z.string().min(2).max(255), estimate: money, actual: money, vendor: z.string().max(160).optional() })).mutation(({ ctx, input }) => db.addExpense(ctx.user, input)),
    comps: protectedProcedure.input(z.object({ projectId: z.number().int().positive() })).query(({ ctx, input }) => db.getCompsWithEstimate(ctx.user, input.projectId)),
    searchComps: protectedProcedure.input(z.object({ projectId: z.number().int().positive(), query: z.string().max(255).default("") })).query(({ ctx, input }) => db.searchComps(ctx.user, input.projectId, input.query)),
    addComp: protectedProcedure.input(z.object({ projectId: z.number().int().positive(), address: z.string().min(4).max(255), salePrice: money, sqft: z.number().int().min(0).max(100_000), beds: z.number().int().min(0).max(30), baths: z.number().int().min(0).max(30), soldAt: z.string().max(32).optional() })).mutation(({ ctx, input }) => db.addComp(ctx.user, input)),
    documents: protectedProcedure.input(z.object({ projectId: z.number().int().positive() })).query(({ ctx, input }) => db.listDocuments(ctx.user, input.projectId)),
    uploadDocument: protectedProcedure.input(z.object({ projectId: z.number().int().positive(), name: z.string().min(2).max(255), docType: z.enum(DOCUMENT_TYPES), mimeType: z.string().max(128).optional(), base64Content: z.string().min(1) })).mutation(async ({ ctx, input }) => {
      const bytes = Buffer.from(input.base64Content, "base64");
      const key = `projects/${ctx.user.id}/${input.projectId}/${Date.now()}-${input.name.replace(/[^a-zA-Z0-9._-]/g, "-")}`;
      const uploaded = await storagePut(key, bytes, input.mimeType);
      return db.addDocument(ctx.user, { projectId: input.projectId, name: input.name, docType: input.docType, mimeType: input.mimeType, fileKey: uploaded.key, url: uploaded.url, size: bytes.length });
    }),
    collaborators: protectedProcedure.input(z.object({ projectId: z.number().int().positive() })).query(({ ctx, input }) => db.listCollaborators(ctx.user, input.projectId)),
    inviteCollaborator: protectedProcedure.input(z.object({ projectId: z.number().int().positive(), email: z.string().email(), name: z.string().max(160).optional(), role: z.enum(COLLABORATOR_ROLES) })).mutation(({ ctx, input }) => db.inviteCollaborator(ctx.user, { ...input, status: "invited" })),
    updateCollaboratorRole: protectedProcedure.input(z.object({ collaboratorId: z.number().int().positive(), role: z.enum(COLLABORATOR_ROLES) })).mutation(({ ctx, input }) => db.updateCollaboratorRole(ctx.user, input.collaboratorId, input.role)),
    removeCollaborator: protectedProcedure.input(z.object({ collaboratorId: z.number().int().positive() })).mutation(({ ctx, input }) => db.removeCollaborator(ctx.user, input.collaboratorId)),
    acceptInvitation: protectedProcedure.input(z.object({ projectId: z.number().int().positive() })).mutation(({ ctx, input }) => db.acceptInvitation(ctx.user, input.projectId)),
  }),
});

export type AppRouter = typeof appRouter;
