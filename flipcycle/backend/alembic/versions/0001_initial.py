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
