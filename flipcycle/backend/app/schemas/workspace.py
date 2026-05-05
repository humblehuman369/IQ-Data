from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import CollaboratorRole, CollaboratorStatus, DocumentType, ExpenseCategory, PipelineStage


class DealInput(BaseModel):
    purchase_price: float = Field(alias='purchasePrice', ge=0)
    repair_costs: float = Field(alias='repairCosts', ge=0)
    arv: float = Field(ge=0)
    down_payment: float = Field(alias='downPayment', ge=0)
    loan_amount: float = Field(alias='loanAmount', ge=0)
    interest_rate: float = Field(alias='interestRate', ge=0, le=50)
    holding_months: int = Field(alias='holdingMonths', ge=0, le=120)
    closing_costs: float = Field(alias='closingCosts', ge=0)
    selling_costs: float = Field(alias='sellingCosts', ge=0)

    model_config = ConfigDict(populate_by_name=True)


class DealMetrics(BaseModel):
    profit: float
    roi: float
    cash_on_cash_return: float = Field(alias='cashOnCashReturn')
    total_invested: float = Field(alias='totalInvested')
    cash_invested: float = Field(alias='cashInvested')
    financing_cost: float = Field(alias='financingCost')

    model_config = ConfigDict(populate_by_name=True)


class ProjectOut(DealInput):
    id: int
    name: str
    address: str
    stage: PipelineStage
    sqft: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ExpenseOut(BaseModel):
    id: int
    project_id: int = Field(alias='projectId')
    category: ExpenseCategory
    description: str
    estimate: float
    actual: float
    vendor: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CompOut(BaseModel):
    id: int
    project_id: int = Field(alias='projectId')
    address: str
    sale_price: float = Field(alias='salePrice')
    sqft: int
    beds: int
    baths: int
    sold_at: str | None = Field(default=None, alias='soldAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DocumentOut(BaseModel):
    id: int
    project_id: int = Field(alias='projectId')
    name: str
    doc_type: DocumentType = Field(alias='docType')
    url: str
    mime_type: str | None = Field(default=None, alias='mimeType')
    size: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CollaboratorOut(BaseModel):
    id: int
    project_id: int = Field(alias='projectId')
    email: EmailStr
    name: str | None = None
    role: CollaboratorRole
    status: CollaboratorStatus

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class WorkspaceSummary(BaseModel):
    active_deals: int = Field(alias='activeDeals')
    total_invested: float = Field(alias='totalInvested')
    projected_profit: float = Field(alias='projectedProfit')
    completed_flips: int = Field(alias='completedFlips')

    model_config = ConfigDict(populate_by_name=True)


class ArvEstimate(BaseModel):
    estimated_arv: float = Field(alias='estimatedArv')
    average_sale_price: float = Field(alias='averageSalePrice')
    average_price_per_sqft: float = Field(alias='averagePricePerSqft')
    comp_count: int = Field(alias='compCount')

    model_config = ConfigDict(populate_by_name=True)


class CompsWithEstimate(BaseModel):
    comps: list[CompOut]
    estimate: ArvEstimate

    model_config = ConfigDict(populate_by_name=True)


class ProjectStageUpdate(BaseModel):
    stage: PipelineStage


class ExpenseCreate(BaseModel):
    category: ExpenseCategory
    description: str = Field(min_length=1, max_length=255)
    estimate: float = Field(ge=0)
    actual: float = Field(ge=0)
    vendor: str | None = Field(default=None, max_length=160)


class DocumentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    doc_type: DocumentType = Field(alias='docType')
    url: str = Field(min_length=1)
    mime_type: str | None = Field(default=None, alias='mimeType')
    size: int = Field(default=0, ge=0)

    model_config = ConfigDict(populate_by_name=True)


class CollaboratorInvite(BaseModel):
    email: EmailStr
    role: CollaboratorRole = CollaboratorRole.VIEWER
    name: str | None = Field(default=None, max_length=160)


class SeedSampleDataResponse(BaseModel):
    seeded: bool
    projects: int
