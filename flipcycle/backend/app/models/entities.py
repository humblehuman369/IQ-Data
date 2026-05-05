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
    file_key: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(Text)
    doc_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), default=DocumentType.OTHER)
    mime_type: Mapped[str | None] = mapped_column(String(128), default=None)
    size: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    project: Mapped[Project] = relationship(back_populates='documents', default=None)


class Collaborator(Base):
    __tablename__ = 'collaborators'
    __table_args__ = (UniqueConstraint('project_id', 'email', name='uq_project_collaborator_email'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'))
    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    email: Mapped[str] = mapped_column(String(320), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), default=None)
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
