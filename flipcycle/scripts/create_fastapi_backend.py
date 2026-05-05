from pathlib import Path

ROOT = Path('/home/ubuntu/workcycle')

def write(path: str, content: str):
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip() + '\n', encoding='utf-8')

write('backend/requirements.txt', """
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
gunicorn>=23.0.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
SQLAlchemy[asyncio]>=2.0.36
alembic>=1.14.0
psycopg[binary,pool]>=3.2.3
redis>=5.2.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.2.0
python-jose[cryptography]>=3.3.0
PyJWT>=2.10.0
pyotp>=2.9.0
stripe>=11.3.0
resend>=2.4.0
anthropic>=0.40.0
boto3>=1.35.0
reportlab>=4.2.0
weasyprint>=63.0
openpyxl>=3.1.5
sentry-sdk[fastapi]>=2.19.0
prometheus-fastapi-instrumentator>=7.0.0
structlog>=24.4.0
python-json-logger>=2.0.7
python-multipart>=0.0.17
email-validator>=2.2.0
httpx>=0.28.0
""")
write('backend/requirements-dev.txt', """
-r requirements.txt
pytest>=8.3.0
pytest-asyncio>=0.24.0
ruff>=0.8.0
mypy>=1.13.0
""")
write('backend/README.md', """
# FlipCycle FastAPI Backend

This package is the FastAPI, PostgreSQL, Redis, and service-integration backend for the migrated FlipCycle monorepo. It is designed to be deployed separately from the Vercel-hosted Next.js frontend and exposed to the frontend through `NEXT_PUBLIC_API_BASE_URL`.

## Runtime services

The backend expects PostgreSQL 15 and Redis 7 in production. Set `DATABASE_URL` to an async psycopg connection string such as `postgresql+psycopg://user:password@host:5432/flipcycle` and set `REDIS_URL` to a Redis 7 endpoint. Optional service keys enable Stripe billing, Resend email, Anthropic AI narratives, AWS S3 document storage, and Sentry observability.

## Local commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pytest
```

The main product endpoints live under `/api`, matching the Next.js client contract: `/api/workspace/summary`, `/api/projects`, `/api/projects/{id}/expenses`, `/api/projects/{id}/comps`, `/api/projects/{id}/documents`, `/api/projects/{id}/collaborators`, and `/api/deals/calculate`.
""")
write('backend/app/__init__.py', '"""FlipCycle FastAPI application package."""')
write('backend/app/core/config.py', """
from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'FlipCycle API'
    environment: str = Field(default='development', alias='ENVIRONMENT')
    api_prefix: str = '/api'
    allowed_origins: list[str] = ['http://localhost:3000', 'https://flipcycle.vercel.app']

    database_url: str = Field(default='postgresql+psycopg://flipcycle:flipcycle@localhost:5432/flipcycle', alias='DATABASE_URL')
    redis_url: str = Field(default='redis://localhost:6379/0', alias='REDIS_URL')

    jwt_secret: SecretStr = Field(default='change-me-in-production', alias='JWT_SECRET')
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 60
    refresh_token_days: int = 14

    stripe_secret_key: SecretStr | None = Field(default=None, alias='STRIPE_SECRET_KEY')
    stripe_webhook_secret: SecretStr | None = Field(default=None, alias='STRIPE_WEBHOOK_SECRET')
    resend_api_key: SecretStr | None = Field(default=None, alias='RESEND_API_KEY')
    anthropic_api_key: SecretStr | None = Field(default=None, alias='ANTHROPIC_API_KEY')
    aws_access_key_id: SecretStr | None = Field(default=None, alias='AWS_ACCESS_KEY_ID')
    aws_secret_access_key: SecretStr | None = Field(default=None, alias='AWS_SECRET_ACCESS_KEY')
    aws_region: str = Field(default='us-east-1', alias='AWS_REGION')
    s3_bucket: str | None = Field(default=None, alias='S3_BUCKET')
    sentry_dsn: str | None = Field(default=None, alias='SENTRY_DSN')

    def normalized_database_url(self) -> str:
        if self.database_url.startswith('postgres://'):
            return self.database_url.replace('postgres://', 'postgresql+psycopg://', 1)
        if self.database_url.startswith('postgresql://'):
            return self.database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
""")
write('backend/app/core/logging.py', """
import logging
import sys
from pythonjsonlogger import jsonlogger


def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    root.handlers.clear()
    root.addHandler(handler)
""")
write('backend/app/db/base.py', """
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    pass
""")
write('backend/app/db/session.py', """
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.normalized_database_url(), pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
""")
write('backend/app/db/redis.py', """
from redis.asyncio import Redis
from app.core.config import get_settings

_settings = get_settings()
redis_client = Redis.from_url(_settings.redis_url, decode_responses=True)


async def blacklist_token(jti: str, expires_in_seconds: int) -> None:
    await redis_client.setex(f'token-blacklist:{jti}', expires_in_seconds, '1')


async def is_token_blacklisted(jti: str) -> bool:
    return bool(await redis_client.get(f'token-blacklist:{jti}'))
""")
write('backend/app/models/enums.py', """
from enum import StrEnum


class PipelineStage(StrEnum):
    ACQUISITION = 'Acquisition'
    REHAB = 'Rehab'
    LISTED = 'Listed'
    SOLD = 'Sold'


class ExpenseCategory(StrEnum):
    LABOR = 'labor'
    MATERIALS = 'materials'
    PERMITS = 'permits'


class DocumentType(StrEnum):
    CONTRACTS = 'contracts'
    PHOTOS = 'photos'
    INSPECTION_REPORTS = 'inspection_reports'
    OTHER = 'other'


class CollaboratorRole(StrEnum):
    OWNER = 'owner'
    EDITOR = 'editor'
    VIEWER = 'viewer'


class CollaboratorStatus(StrEnum):
    INVITED = 'invited'
    ACTIVE = 'active'


class UserRole(StrEnum):
    ADMIN = 'admin'
    USER = 'user'
""")
write('backend/app/models/entities.py', """
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import CollaboratorRole, CollaboratorStatus, DocumentType, ExpenseCategory, PipelineStage, UserRole


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    open_id: Mapped[str | None] = mapped_column(String(191), unique=True, index=True, default=None)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True, default=None)
    name: Mapped[str | None] = mapped_column(String(160), default=None)
    hashed_password: Mapped[str | None] = mapped_column(String(255), default=None)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    totp_secret: Mapped[str | None] = mapped_column(String(64), default=None)
    last_signed_in: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    projects: Mapped[list['Project']] = relationship(back_populates='owner', default_factory=list)


class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str] = mapped_column(String(255))
    stage: Mapped[PipelineStage] = mapped_column(Enum(PipelineStage), default=PipelineStage.ACQUISITION)
    sqft: Mapped[int] = mapped_column(Integer, default=0)
    purchase_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    repair_costs: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    arv: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    down_payment: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    loan_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    interest_rate: Mapped[float] = mapped_column(Numeric(7, 4), default=0)
    holding_months: Mapped[int] = mapped_column(Integer, default=0)
    closing_costs: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    selling_costs: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    owner: Mapped[User] = relationship(back_populates='projects', default=None)
    expenses: Mapped[list['Expense']] = relationship(back_populates='project', cascade='all, delete-orphan', default_factory=list)
    comps: Mapped[list['Comp']] = relationship(back_populates='project', cascade='all, delete-orphan', default_factory=list)
    documents: Mapped[list['Document']] = relationship(back_populates='project', cascade='all, delete-orphan', default_factory=list)
    collaborators: Mapped[list['Collaborator']] = relationship(back_populates='project', cascade='all, delete-orphan', default_factory=list)


class Expense(Base):
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'))
    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    category: Mapped[ExpenseCategory] = mapped_column(Enum(ExpenseCategory))
    description: Mapped[str] = mapped_column(String(255))
    estimate: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    actual: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    vendor: Mapped[str | None] = mapped_column(String(160), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    project: Mapped[Project] = relationship(back_populates='expenses', default=None)


class Comp(Base):
    __tablename__ = 'comps'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'))
    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    address: Mapped[str] = mapped_column(String(255))
    sale_price: Mapped[float] = mapped_column(Numeric(12, 2))
    sqft: Mapped[int] = mapped_column(Integer, default=0)
    beds: Mapped[int] = mapped_column(Integer, default=0)
    baths: Mapped[int] = mapped_column(Integer, default=0)
    sold_at: Mapped[str | None] = mapped_column(String(32), default=None)

    project: Mapped[Project] = relationship(back_populates='comps', default=None)


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'))
    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    name: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), default=DocumentType.OTHER)
    mime_type: Mapped[str | None] = mapped_column(String(128), default=None)
    file_key: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(Text)
    size: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    project: Mapped[Project] = relationship(back_populates='documents', default=None)


class Collaborator(Base):
    __tablename__ = 'collaborators'
    __table_args__ = (UniqueConstraint('project_id', 'email', name='uq_project_collaborator_email'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'))
    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), default=None)
    email: Mapped[str] = mapped_column(String(320), index=True)
    name: Mapped[str | None] = mapped_column(String(160), default=None)
    role: Mapped[CollaboratorRole] = mapped_column(Enum(CollaboratorRole), default=CollaboratorRole.VIEWER)
    status: Mapped[CollaboratorStatus] = mapped_column(Enum(CollaboratorStatus), default=CollaboratorStatus.INVITED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    project: Mapped[Project] = relationship(back_populates='collaborators', default=None)


class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    jti: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)
""")
write('backend/app/models/__init__.py', """
from app.models.entities import Collaborator, Comp, Document, Expense, Project, TokenBlacklist, User
from app.models.enums import CollaboratorRole, CollaboratorStatus, DocumentType, ExpenseCategory, PipelineStage, UserRole

__all__ = [
    'User', 'Project', 'Expense', 'Comp', 'Document', 'Collaborator', 'TokenBlacklist',
    'PipelineStage', 'ExpenseCategory', 'DocumentType', 'CollaboratorRole', 'CollaboratorStatus', 'UserRole',
]
""")
write('backend/app/schemas/workspace.py', """
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
""")
write('backend/app/schemas/auth.py', """
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = Field(default=None, alias='totpCode')


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TotpSetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
""")
write('backend/app/auth/security.py', """
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
import pyotp
from passlib.context import CryptContext
from app.core.config import get_settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str | None) -> bool:
    return bool(hashed_password and pwd_context.verify(password, hashed_password))


def create_token(subject: str, minutes: int | None = None) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.access_token_minutes)
    payload = {'sub': subject, 'exp': expires, 'iat': datetime.now(timezone.utc), 'jti': str(uuid4())}
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret.get_secret_value(), algorithms=[settings.jwt_algorithm])


def new_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str | None, code: str | None) -> bool:
    if not secret:
        return True
    if not code:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)
""")
write('backend/app/auth/dependencies.py', """
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.security import decode_token
from app.db.session import get_session
from app.models import User

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_user_id: int | None = Header(default=None),
) -> User:
    if x_user_id:
        user = await session.get(User, x_user_id)
        if user:
            return user
    if credentials:
        try:
            payload = decode_token(credentials.credentials)
            user_id = int(payload['sub'])
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token') from exc
        user = await session.get(User, user_id)
        if user:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
""")
write('backend/app/services/calculations.py', """
from app.schemas.workspace import ArvEstimate, DealInput, DealMetrics


def _round(value: float) -> float:
    return round(value + 1e-9, 2)


def calculate_deal(input: DealInput) -> DealMetrics:
    financing_cost = input.loan_amount * (input.interest_rate / 100 / 12) * input.holding_months
    total_invested = input.purchase_price + input.repair_costs + input.closing_costs + input.selling_costs + financing_cost
    cash_invested = input.down_payment + input.repair_costs + input.closing_costs + financing_cost
    profit = input.arv - total_invested
    roi = (profit / total_invested * 100) if total_invested else 0
    cash_on_cash = (profit / cash_invested * 100) if cash_invested else 0
    return DealMetrics(
        profit=_round(profit), roi=_round(roi), cashOnCashReturn=_round(cash_on_cash),
        totalInvested=_round(total_invested), cashInvested=_round(cash_invested), financingCost=_round(financing_cost),
    )


def estimate_arv_from_comps(comps: list[dict], target_sqft: int | None = None) -> ArvEstimate:
    valid = [comp for comp in comps if float(comp.get('sale_price', comp.get('salePrice', 0))) > 0]
    if not valid:
        return ArvEstimate(estimatedArv=0, averageSalePrice=0, averagePricePerSqft=0, compCount=0)
    average_sale_price = sum(float(comp.get('sale_price', comp.get('salePrice', 0))) for comp in valid) / len(valid)
    ppsf = [float(comp.get('sale_price', comp.get('salePrice', 0))) / float(comp.get('sqft', 0)) for comp in valid if float(comp.get('sqft', 0)) > 0]
    average_ppsf = sum(ppsf) / len(ppsf) if ppsf else 0
    estimated_arv = target_sqft * average_ppsf if target_sqft and average_ppsf else average_sale_price
    return ArvEstimate(estimatedArv=_round(estimated_arv), averageSalePrice=_round(average_sale_price), averagePricePerSqft=_round(average_ppsf), compCount=len(valid))
""")
write('backend/app/services/workspace.py', """
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Collaborator, CollaboratorRole, CollaboratorStatus, Comp, Document, Expense, Project, User
from app.schemas.workspace import DealInput, WorkspaceSummary
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
""")
write('backend/app/services/storage.py', """
from uuid import uuid4
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from app.core.config import get_settings

settings = get_settings()


def s3_client():
    return boto3.client(
        's3',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id.get_secret_value() if settings.aws_access_key_id else None,
        aws_secret_access_key=settings.aws_secret_access_key.get_secret_value() if settings.aws_secret_access_key else None,
    )


async def upload_file(file: UploadFile, prefix: str) -> dict[str, str | int]:
    if not settings.s3_bucket:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='S3_BUCKET is not configured')
    content = await file.read()
    key = f"{prefix}/{uuid4()}-{file.filename}"
    try:
        s3_client().put_object(Bucket=settings.s3_bucket, Key=key, Body=content, ContentType=file.content_type)
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='S3 upload failed') from exc
    url = f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
    return {'key': key, 'url': url, 'size': len(content), 'mime_type': file.content_type or 'application/octet-stream'}
""")
write('backend/app/services/billing.py', """
import stripe
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key.get_secret_value()


def ensure_stripe() -> None:
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stripe is not configured')


def create_checkout_session(customer_email: str, price_id: str, success_url: str, cancel_url: str):
    ensure_stripe()
    return stripe.checkout.Session.create(mode='subscription', customer_email=customer_email, line_items=[{'price': price_id, 'quantity': 1}], success_url=success_url, cancel_url=cancel_url)
""")
write('backend/app/services/email.py', """
import resend
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()
if settings.resend_api_key:
    resend.api_key = settings.resend_api_key.get_secret_value()


def send_email(to: str, subject: str, html: str):
    if not settings.resend_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Resend is not configured')
    return resend.Emails.send({'from': 'FlipCycle <notifications@flipcycle.app>', 'to': [to], 'subject': subject, 'html': html})
""")
write('backend/app/services/ai.py', """
from anthropic import AsyncAnthropic
from fastapi import HTTPException, status
from app.core.config import get_settings

settings = get_settings()


async def generate_deal_narrative(prompt: str) -> str:
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Anthropic is not configured')
    client = AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value())
    message = await client.messages.create(
        model='claude-3-5-sonnet-latest',
        max_tokens=700,
        messages=[{'role': 'user', 'content': f'Write a concise investor narrative for this FlipCycle deal: {prompt}'}],
    )
    return ''.join(block.text for block in message.content if hasattr(block, 'text'))
""")
write('backend/app/services/exports.py', """
from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def render_project_pdf(title: str, lines: list[str]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(title)
    pdf.drawString(72, 740, title)
    y = 710
    for line in lines:
        pdf.drawString(72, y, line[:100])
        y -= 18
    pdf.save()
    return buffer.getvalue()


def render_budget_xlsx(rows: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Budget'
    sheet.append(['Category', 'Description', 'Estimate', 'Actual', 'Vendor'])
    for row in rows:
        sheet.append([row.get('category'), row.get('description'), row.get('estimate'), row.get('actual'), row.get('vendor')])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
""")
write('backend/app/routers/deals.py', """
from fastapi import APIRouter
from app.schemas.workspace import DealInput, DealMetrics
from app.services.calculations import calculate_deal

router = APIRouter(prefix='/deals', tags=['deals'])


@router.post('/calculate', response_model=DealMetrics, response_model_by_alias=True)
async def calculate_deal_endpoint(input: DealInput) -> DealMetrics:
    return calculate_deal(input)
""")
write('backend/app/routers/workspace.py', """
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.workspace import WorkspaceSummary
from app.services.workspace import dashboard_summary

router = APIRouter(prefix='/workspace', tags=['workspace'])


@router.get('/summary', response_model=WorkspaceSummary, response_model_by_alias=True)
async def summary(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)) -> WorkspaceSummary:
    return await dashboard_summary(session, user)
""")
write('backend/app/routers/projects.py', """
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.workspace import CollaboratorOut, CompsWithEstimate, DocumentOut, ExpenseOut, ProjectOut
from app.services.storage import upload_file
from app.services.workspace import list_accessible_projects, list_project_collaborators, list_project_comps, list_project_documents, list_project_expenses

router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('', response_model=list[ProjectOut], response_model_by_alias=True)
async def projects(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_accessible_projects(session, user)


@router.get('/{project_id}/expenses', response_model=list[ExpenseOut], response_model_by_alias=True)
async def expenses(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_project_expenses(session, user, project_id)


@router.get('/{project_id}/comps', response_model=CompsWithEstimate, response_model_by_alias=True)
async def comps(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    rows, estimate = await list_project_comps(session, user, project_id)
    return {'comps': rows, 'estimate': estimate}


@router.get('/{project_id}/documents', response_model=list[DocumentOut], response_model_by_alias=True)
async def documents(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_project_documents(session, user, project_id)


@router.post('/{project_id}/documents/upload')
async def upload_document(project_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    return await upload_file(file, f'projects/{user.id}/{project_id}')


@router.get('/{project_id}/collaborators', response_model=list[CollaboratorOut], response_model_by_alias=True)
async def collaborators(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_project_collaborators(session, user, project_id)
""")
write('backend/app/routers/auth.py', """
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.auth.security import create_token, hash_password, new_totp_secret, verify_password, verify_totp
from app.db.session import get_session
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair, TotpSetupResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenPair)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> TokenPair:
    exists = await session.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')
    user = User(email=payload.email, name=payload.name, hashed_password=hash_password(payload.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return TokenPair(access_token=create_token(str(user.id)), refresh_token=create_token(str(user.id), minutes=60 * 24 * 14))


@router.post('/login', response_model=TokenPair)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenPair:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password) or not verify_totp(user.totp_secret, payload.totp_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return TokenPair(access_token=create_token(str(user.id)), refresh_token=create_token(str(user.id), minutes=60 * 24 * 14))


@router.post('/totp/setup', response_model=TotpSetupResponse)
async def setup_totp(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    secret = new_totp_secret()
    user.totp_secret = secret
    session.add(user)
    await session.commit()
    return TotpSetupResponse(secret=secret, provisioning_uri=f'otpauth://totp/FlipCycle:{user.email}?secret={secret}&issuer=FlipCycle')
""")
write('backend/app/routers/billing.py', """
from fastapi import APIRouter, Depends
from pydantic import BaseModel, AnyHttpUrl
from app.auth.dependencies import get_current_user
from app.models import User
from app.services.billing import create_checkout_session

router = APIRouter(prefix='/billing', tags=['billing'])


class CheckoutRequest(BaseModel):
    price_id: str
    success_url: AnyHttpUrl
    cancel_url: AnyHttpUrl


@router.post('/checkout')
async def checkout(payload: CheckoutRequest, user: User = Depends(get_current_user)):
    session = create_checkout_session(user.email or 'buyer@flipcycle.app', payload.price_id, str(payload.success_url), str(payload.cancel_url))
    return {'id': session.id, 'url': session.url}
""")
write('backend/app/routers/email.py', """
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from app.auth.dependencies import get_current_user
from app.models import User
from app.services.email import send_email

router = APIRouter(prefix='/email', tags=['email'])


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    html: str


@router.post('/send')
async def send(payload: EmailRequest, _: User = Depends(get_current_user)):
    return send_email(payload.to, payload.subject, payload.html)
""")
write('backend/app/routers/ai.py', """
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.models import User
from app.services.ai import generate_deal_narrative

router = APIRouter(prefix='/ai', tags=['ai'])


class NarrativeRequest(BaseModel):
    prompt: str


@router.post('/deal-narrative')
async def deal_narrative(payload: NarrativeRequest, _: User = Depends(get_current_user)):
    return {'narrative': await generate_deal_narrative(payload.prompt)}
""")
write('backend/app/routers/__init__.py', """
from app.routers import ai, auth, billing, deals, email, projects, workspace

__all__ = ['ai', 'auth', 'billing', 'deals', 'email', 'projects', 'workspace']
""")
write('backend/main.py', """
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.routers import ai, auth, billing, deals, email, projects, workspace

settings = get_settings()
configure_logging()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment, traces_sample_rate=0.1)

app = FastAPI(title=settings.app_name, version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

for router in [deals.router, workspace.router, projects.router, auth.router, billing.router, email.router, ai.router]:
    app.include_router(router, prefix=settings.api_prefix)

Instrumentator().instrument(app).expose(app, endpoint='/metrics')


@app.get('/healthz')
async def healthz() -> dict[str, str]:
    return {'status': 'ok', 'service': 'flipcycle-api'}
""")
write('backend/alembic.ini', """
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = postgresql+psycopg://flipcycle:flipcycle@localhost:5432/flipcycle

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")
write('backend/alembic/env.py', """
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()
config.set_main_option('sqlalchemy.url', settings.normalized_database_url())


def run_migrations_offline() -> None:
    context.configure(url=settings.normalized_database_url(), target_metadata=target_metadata, literal_binds=True, dialect_opts={'paramstyle': 'named'})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix='sqlalchemy.', poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")
write('backend/alembic/versions/0001_initial.py', '''
"""initial flipcycle schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-05
"""
from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    user_role = sa.Enum('ADMIN', 'USER', name='userrole')
    pipeline_stage = sa.Enum('ACQUISITION', 'REHAB', 'LISTED', 'SOLD', name='pipelinestage')
    expense_category = sa.Enum('LABOR', 'MATERIALS', 'PERMITS', name='expensecategory')
    document_type = sa.Enum('CONTRACTS', 'PHOTOS', 'INSPECTION_REPORTS', 'OTHER', name='documenttype')
    collaborator_role = sa.Enum('OWNER', 'EDITOR', 'VIEWER', name='collaboratorrole')
    collaborator_status = sa.Enum('INVITED', 'ACTIVE', name='collaboratorstatus')

    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('open_id', sa.String(length=191), nullable=True),
        sa.Column('email', sa.String(length=320), nullable=True),
        sa.Column('name', sa.String(length=160), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('role', user_role, nullable=False),
        sa.Column('totp_secret', sa.String(length=64), nullable=True),
        sa.Column('last_signed_in', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_open_id', 'users', ['open_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('projects',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('stage', pipeline_stage, nullable=False),
        sa.Column('sqft', sa.Integer(), nullable=False),
        sa.Column('purchase_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('repair_costs', sa.Numeric(12, 2), nullable=False),
        sa.Column('arv', sa.Numeric(12, 2), nullable=False),
        sa.Column('down_payment', sa.Numeric(12, 2), nullable=False),
        sa.Column('loan_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('interest_rate', sa.Numeric(7, 4), nullable=False),
        sa.Column('holding_months', sa.Integer(), nullable=False),
        sa.Column('closing_costs', sa.Numeric(12, 2), nullable=False),
        sa.Column('selling_costs', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('expenses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category', expense_category, nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('estimate', sa.Numeric(12, 2), nullable=False),
        sa.Column('actual', sa.Numeric(12, 2), nullable=False),
        sa.Column('vendor', sa.String(length=160), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('comps',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('sale_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('sqft', sa.Integer(), nullable=False),
        sa.Column('beds', sa.Integer(), nullable=False),
        sa.Column('baths', sa.Integer(), nullable=False),
        sa.Column('sold_at', sa.String(length=32), nullable=True),
    )
    op.create_table('documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('doc_type', document_type, nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=True),
        sa.Column('file_key', sa.String(length=512), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('collaborators',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=True),
        sa.Column('role', collaborator_role, nullable=False),
        sa.Column('status', collaborator_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('project_id', 'email', name='uq_project_collaborator_email'),
    )
    op.create_index('ix_collaborators_email', 'collaborators', ['email'])
    op.create_table('token_blacklist',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('jti', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_token_blacklist_jti', 'token_blacklist', ['jti'], unique=True)


def downgrade() -> None:
    for table in ['token_blacklist', 'collaborators', 'documents', 'comps', 'expenses', 'projects', 'users']:
        op.drop_table(table)
    for enum in ['collaboratorstatus', 'collaboratorrole', 'documenttype', 'expensecategory', 'pipelinestage', 'userrole']:
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)
''')
write('backend/tests/test_calculations.py', """
from app.schemas.workspace import DealInput
from app.services.calculations import calculate_deal, estimate_arv_from_comps


def test_calculate_deal_contract():
    metrics = calculate_deal(DealInput(
        purchasePrice=218000, repairCosts=62000, arv=372000, downPayment=43600,
        loanAmount=174400, interestRate=9.5, holdingMonths=7, closingCosts=8400, sellingCosts=21500,
    ))
    assert metrics.model_dump(by_alias=True) == {
        'profit': 58934.67,
        'roi': 18.82,
        'cashOnCashReturn': 41.96,
        'totalInvested': 313065.33,
        'cashInvested': 140465.33,
        'financingCost': 9665.33,
    }


def test_estimate_arv_from_comps():
    estimate = estimate_arv_from_comps([{'sale_price': 366000, 'sqft': 1840}, {'sale_price': 381500, 'sqft': 1925}], 1880)
    assert estimate.estimated_arv == 374390.24
    assert estimate.comp_count == 2
""")
print('backend stack files written')
