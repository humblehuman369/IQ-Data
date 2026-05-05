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
