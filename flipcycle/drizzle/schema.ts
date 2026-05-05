import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export const projects = mysqlTable("projects", {
  id: int("id").autoincrement().primaryKey(),
  ownerId: int("ownerId").notNull(),
  name: varchar("name", { length: 160 }).notNull(),
  address: varchar("address", { length: 255 }).notNull(),
  stage: mysqlEnum("stage", ["Acquisition", "Rehab", "Listed", "Sold"]).default("Acquisition").notNull(),
  purchasePrice: int("purchasePrice").default(0).notNull(),
  repairCosts: int("repairCosts").default(0).notNull(),
  arv: int("arv").default(0).notNull(),
  downPayment: int("downPayment").default(0).notNull(),
  loanAmount: int("loanAmount").default(0).notNull(),
  interestRate: int("interestRate").default(0).notNull(),
  holdingMonths: int("holdingMonths").default(6).notNull(),
  closingCosts: int("closingCosts").default(0).notNull(),
  sellingCosts: int("sellingCosts").default(0).notNull(),
  sqft: int("sqft").default(0).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export const expenses = mysqlTable("expenses", {
  id: int("id").autoincrement().primaryKey(),
  projectId: int("projectId").notNull(),
  createdById: int("createdById").notNull(),
  category: mysqlEnum("category", ["labor", "materials", "permits"]).notNull(),
  description: varchar("description", { length: 255 }).notNull(),
  estimate: int("estimate").default(0).notNull(),
  actual: int("actual").default(0).notNull(),
  vendor: varchar("vendor", { length: 160 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export const comps = mysqlTable("comps", {
  id: int("id").autoincrement().primaryKey(),
  projectId: int("projectId").notNull(),
  createdById: int("createdById").notNull(),
  address: varchar("address", { length: 255 }).notNull(),
  salePrice: int("salePrice").default(0).notNull(),
  sqft: int("sqft").default(0).notNull(),
  beds: int("beds").default(0).notNull(),
  baths: int("baths").default(0).notNull(),
  soldAt: varchar("soldAt", { length: 32 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const documents = mysqlTable("documents", {
  id: int("id").autoincrement().primaryKey(),
  projectId: int("projectId").notNull(),
  createdById: int("createdById").notNull(),
  name: varchar("name", { length: 255 }).notNull(),
  docType: mysqlEnum("docType", ["contracts", "photos", "inspection_reports", "other"]).default("other").notNull(),
  fileKey: varchar("fileKey", { length: 512 }).notNull(),
  url: varchar("url", { length: 1024 }).notNull(),
  mimeType: varchar("mimeType", { length: 128 }),
  size: int("size").default(0).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export const collaborators = mysqlTable("collaborators", {
  id: int("id").autoincrement().primaryKey(),
  projectId: int("projectId").notNull(),
  createdById: int("createdById").notNull(),
  userId: int("userId"),
  email: varchar("email", { length: 320 }).notNull(),
  name: varchar("name", { length: 160 }),
  role: mysqlEnum("collaboratorRole", ["owner", "editor", "viewer"]).default("viewer").notNull(),
  status: mysqlEnum("collaboratorStatus", ["invited", "active"]).default("invited").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;
export type Project = typeof projects.$inferSelect;
export type InsertProject = typeof projects.$inferInsert;
export type Expense = typeof expenses.$inferSelect;
export type InsertExpense = typeof expenses.$inferInsert;
export type Comp = typeof comps.$inferSelect;
export type InsertComp = typeof comps.$inferInsert;
export type Document = typeof documents.$inferSelect;
export type InsertDocument = typeof documents.$inferInsert;
export type Collaborator = typeof collaborators.$inferSelect;
export type InsertCollaborator = typeof collaborators.$inferInsert;
