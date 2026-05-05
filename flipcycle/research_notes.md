# Workcycle Reference Analysis Notes

Source reviewed: https://flipperforce.com/ on 2026-05-05.

## Public Product Structure

The reference site positions itself as an all-in-one operating system for house flipping and rehabs. The primary public flow uses a top navigation with Pricing, Features, Solutions, Learn, Updates, Log in, and Sign Up. The hero emphasizes all-in-one deal analysis, project management, and bookkeeping, then follows with trial/demo calls to action.

## Feature Areas to Reinterpret for Workcycle

| Reference Area | Observed Capabilities | Workcycle Implementation Direction |
|---|---|---|
| Business Management | Teams, collaboration, project tracking, budgeting, reporting | Build dashboard overview, project pipeline, team roles, and portfolio metrics. |
| Deal Analysis | Cost analysis, maximum purchase price, rehab estimates, comps, investment reports | Build deal analyzer with purchase price, repair costs, ARV, financing details, profit, ROI, and cash-on-cash return. |
| Project Management | Calendars, schedules, tasks, milestones, photo logs, daily updates | Build a Kanban-style pipeline with exact stages Acquisition, Rehab, Listed, Sold and project detail workspace. |
| Accounting | Expenses, receipt upload, AI receipt analyzer, budget vs actuals, reports | Build budget and expense tracker with labor/materials/permits categories and S3-backed document storage. |
| Dashboards | Leads, active projects, portfolio summaries | Build authenticated dashboard summary showing active deals, total invested, projected profit, and completed flips. |
| Mobile/Field Updates | Project managers and contractors upload photos and updates | Build responsive document/photo upload surfaces; avoid copying proprietary app UI. |

## Branding Interpretation

The Workcycle implementation should avoid copying the exact Flipperforce visual assets, logo, screenshots, copy, or proprietary media. It should preserve comparable user value through an original minimal design system using primary #0465F2, accent #0FA4E9, highlight #38bdf8, and smooth blue-to-cyan gradients.

## User-Specified Non-Negotiables

| Constraint | Implementation Requirement |
|---|---|
| Product name | Use "Workcycle" consistently. |
| Authentication | Use Manus OAuth only. |
| Storage | Use S3-backed storage helpers/references. |
| Pipeline stages | Use exactly Acquisition, Rehab, Listed, Sold. |
| Team roles | Use exactly owner, editor, viewer. |
| Deal outputs | Surface profit, ROI, and cash-on-cash return. |

## Additional Pricing and Deal Analysis Findings

Pricing page reviewed: https://flipperforce.com/pricing. The reference site offers an all-in-one pricing presentation with Solo, Teams, and Business tiers, monthly/yearly toggles, trial calls to action, and a feature comparison section. Workcycle should present original pricing copy and visual cards while preserving a familiar SaaS structure: individual users, growing teams, and larger businesses.

Deal analysis page reviewed: https://flipperforce.com/software-solutions/deal-analysis. The reference deal-analysis flow emphasizes comps, flip analysis, BRRRR analysis, rehab estimation, and investment reports. Workcycle should implement the user-specified subset as a working deal analyzer with comps/ARV estimation and not copy proprietary report templates or screenshots.

| Area | Workcycle Scope |
|---|---|
| Pricing | Three original tiers suitable for Solo, Team, and Business customers, each with a signup CTA. |
| Trial/demo flow | Use Manus OAuth entry points for signup/login; demo links can route to landing/dashboard sections. |
| Deal analyzer | Build a practical calculator that computes profit, ROI, and cash-on-cash return from user inputs. |
| Comps/ARV | Provide a comparable sales entry table and calculate estimated ARV from average comp price. |
| Reports | Provide summary cards inside the dashboard rather than duplicating proprietary report-builder flows. |

