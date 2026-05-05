from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Collaborator, CollaboratorRole, CollaboratorStatus, Comp, Document, DocumentType, Expense, ExpenseCategory, PipelineStage, Project, User
from app.schemas.workspace import CollaboratorInvite, DealInput, DocumentCreate, ExpenseCreate, ProjectStageUpdate, WorkspaceSummary
from app.services.calculations import calculate_deal, estimate_arv_from_comps

ROLE_RANK = {CollaboratorRole.VIEWER: 1, CollaboratorRole.EDITOR: 2, CollaboratorRole.OWNER: 3}


def project_to_deal_input(project: Project) -> DealInput:
    return DealInput(
        purchasePrice=float(project.purchase_price), repairCosts=float(project.repair_costs), arv=float(project.arv),
        downPayment=float(project.down_payment), loanAmount=float(project.loan_amount), interestRate=float(project.interest_rate),
        holdingMonths=project.holding_months, closingCosts=float(project.closing_costs), sellingCosts=float(project.selling_costs),
    )


async def list_accessible_projects(session: AsyncSession, user: User) -> list[Project]:
    stmt = select(Project).where(Project.owner_id == user.id)
    if user.email:
        stmt = select(Project).outerjoin(Collaborator).where(or_(Project.owner_id == user.id, Collaborator.email == user.email))
    result = await session.execute(stmt)
    return list(dict.fromkeys(result.scalars().all()))


async def get_project_access(session: AsyncSession, project_id: int, user: User, minimum: CollaboratorRole = CollaboratorRole.VIEWER) -> Project:
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Project not found')
    role: CollaboratorRole | None = CollaboratorRole.OWNER if project.owner_id == user.id else None
    if not role and user.email:
        row = await session.execute(select(Collaborator).where(Collaborator.project_id == project_id, Collaborator.email == user.email))
        collaborator = row.scalar_one_or_none()
        if collaborator:
            role = collaborator.role
    if not role or ROLE_RANK[role] < ROLE_RANK[minimum]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission for this FlipCycle project action')
    return project


async def dashboard_summary(session: AsyncSession, user: User) -> WorkspaceSummary:
    projects = await list_accessible_projects(session, user)
    active_deals = len([project for project in projects if project.stage.value != 'Sold'])
    completed_flips = len(projects) - active_deals
    metrics = [calculate_deal(project_to_deal_input(project)) for project in projects]
    return WorkspaceSummary(activeDeals=active_deals, completedFlips=completed_flips, totalInvested=sum(metric.cash_invested for metric in metrics), projectedProfit=sum(metric.profit for metric in metrics))


async def list_project_expenses(session: AsyncSession, user: User, project_id: int) -> list[Expense]:
    await get_project_access(session, project_id, user)
    return list((await session.execute(select(Expense).where(Expense.project_id == project_id))).scalars().all())


async def list_project_comps(session: AsyncSession, user: User, project_id: int):
    project = await get_project_access(session, project_id, user)
    rows = list((await session.execute(select(Comp).where(Comp.project_id == project_id))).scalars().all())
    estimate = estimate_arv_from_comps([{'sale_price': float(row.sale_price), 'sqft': row.sqft} for row in rows], project.sqft)
    return rows, estimate


async def list_project_documents(session: AsyncSession, user: User, project_id: int) -> list[Document]:
    await get_project_access(session, project_id, user)
    return list((await session.execute(select(Document).where(Document.project_id == project_id))).scalars().all())


async def list_project_collaborators(session: AsyncSession, user: User, project_id: int) -> list[Collaborator]:
    await get_project_access(session, project_id, user)
    return list((await session.execute(select(Collaborator).where(Collaborator.project_id == project_id))).scalars().all())


async def update_project_stage(session: AsyncSession, user: User, project_id: int, input: ProjectStageUpdate) -> Project:
    project = await get_project_access(session, project_id, user, CollaboratorRole.EDITOR)
    project.stage = input.stage
    await session.commit()
    await session.refresh(project)
    return project


async def create_project_expense(session: AsyncSession, user: User, project_id: int, input: ExpenseCreate) -> Expense:
    await get_project_access(session, project_id, user, CollaboratorRole.EDITOR)
    expense = Expense(
        project_id=project_id,
        created_by_id=user.id,
        category=input.category,
        description=input.description,
        estimate=input.estimate,
        actual=input.actual,
        vendor=input.vendor,
    )
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def create_project_document(session: AsyncSession, user: User, project_id: int, input: DocumentCreate) -> Document:
    await get_project_access(session, project_id, user, CollaboratorRole.EDITOR)
    document = Document(
        project_id=project_id,
        created_by_id=user.id,
        name=input.name,
        file_key=f'projects/{user.id}/{project_id}/{input.name}',
        url=input.url,
        doc_type=input.doc_type,
        mime_type=input.mime_type,
        size=input.size,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def invite_project_collaborator(session: AsyncSession, user: User, project_id: int, input: CollaboratorInvite) -> Collaborator:
    await get_project_access(session, project_id, user, CollaboratorRole.OWNER)
    collaborator = Collaborator(
        project_id=project_id,
        created_by_id=user.id,
        email=str(input.email),
        name=input.name,
        role=input.role,
        status=CollaboratorStatus.INVITED,
    )
    session.add(collaborator)
    await session.commit()
    await session.refresh(collaborator)
    return collaborator


async def seed_sample_data(session: AsyncSession, user: User) -> dict[str, int | bool]:
    existing = await session.execute(select(Project).where(Project.owner_id == user.id))
    if existing.scalars().first():
        projects = await list_accessible_projects(session, user)
        return {'seeded': False, 'projects': len(projects)}

    maple = Project(
        owner_id=user.id,
        name='Maple Street Flip',
        address='428 Maple Street, Richmond, VA',
        stage=PipelineStage.ACQUISITION,
        sqft=1880,
        purchase_price=218000,
        repair_costs=62000,
        arv=372000,
        down_payment=43600,
        loan_amount=174400,
        interest_rate=9.5,
        holding_months=7,
        closing_costs=8400,
        selling_costs=21500,
    )
    riverbend = Project(
        owner_id=user.id,
        name='Riverbend Rehab',
        address='1197 Riverbend Drive, Norfolk, VA',
        stage=PipelineStage.REHAB,
        sqft=2160,
        purchase_price=264000,
        repair_costs=78000,
        arv=445000,
        down_payment=52800,
        loan_amount=211200,
        interest_rate=10.25,
        holding_months=8,
        closing_costs=9200,
        selling_costs=25800,
    )
    session.add_all([maple, riverbend])
    await session.flush()
    session.add_all([
        Expense(project_id=maple.id, created_by_id=user.id, category=ExpenseCategory.LABOR, description='Framing and trim crew', estimate=18000, actual=17250, vendor='Precision Build Co.'),
        Expense(project_id=maple.id, created_by_id=user.id, category=ExpenseCategory.MATERIALS, description='Cabinets and fixtures', estimate=22000, actual=24100, vendor='ProSource Supply'),
        Comp(project_id=maple.id, created_by_id=user.id, address='413 Maple Street', sale_price=366000, sqft=1840, beds=3, baths=2, sold_at='2026-03-12'),
        Comp(project_id=maple.id, created_by_id=user.id, address='440 Maple Street', sale_price=381500, sqft=1925, beds=4, baths=2, sold_at='2026-02-18'),
        Document(project_id=maple.id, created_by_id=user.id, name='Purchase agreement.pdf', file_key=f'projects/{user.id}/{maple.id}/purchase-agreement.pdf', url='#', doc_type=DocumentType.CONTRACTS, mime_type='application/pdf', size=482000),
        Collaborator(project_id=maple.id, created_by_id=user.id, email='gc@example.com', name='General Contractor', role=CollaboratorRole.EDITOR, status=CollaboratorStatus.INVITED),
    ])
    await session.commit()
    return {'seeded': True, 'projects': 2}
