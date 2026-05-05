from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.workspace import CollaboratorInvite, CollaboratorOut, CompsWithEstimate, DocumentCreate, DocumentOut, ExpenseCreate, ExpenseOut, ProjectOut, ProjectStageUpdate
from app.services.storage import upload_file
from app.services.workspace import create_project_document, create_project_expense, invite_project_collaborator, list_accessible_projects, list_project_collaborators, list_project_comps, list_project_documents, list_project_expenses, update_project_stage

router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('', response_model=list[ProjectOut], response_model_by_alias=True)
async def projects(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_accessible_projects(session, user)


@router.get('/{project_id}/expenses', response_model=list[ExpenseOut], response_model_by_alias=True)
async def expenses(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_project_expenses(session, user, project_id)


@router.patch('/{project_id}/stage', response_model=ProjectOut, response_model_by_alias=True)
async def update_stage(project_id: int, input: ProjectStageUpdate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await update_project_stage(session, user, project_id, input)


@router.post('/{project_id}/expenses', response_model=ExpenseOut, response_model_by_alias=True)
async def create_expense(project_id: int, input: ExpenseCreate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await create_project_expense(session, user, project_id, input)


@router.get('/{project_id}/comps', response_model=CompsWithEstimate, response_model_by_alias=True)
async def comps(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    rows, estimate = await list_project_comps(session, user, project_id)
    return {'comps': rows, 'estimate': estimate}


@router.get('/{project_id}/documents', response_model=list[DocumentOut], response_model_by_alias=True)
async def documents(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_project_documents(session, user, project_id)


@router.post('/{project_id}/documents', response_model=DocumentOut, response_model_by_alias=True)
async def create_document(project_id: int, input: DocumentCreate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await create_project_document(session, user, project_id, input)


@router.post('/{project_id}/documents/upload')
async def upload_document(project_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    return await upload_file(file, f'projects/{user.id}/{project_id}')


@router.get('/{project_id}/collaborators', response_model=list[CollaboratorOut], response_model_by_alias=True)
async def collaborators(project_id: int, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await list_project_collaborators(session, user, project_id)


@router.post('/{project_id}/collaborators', response_model=CollaboratorOut, response_model_by_alias=True)
async def invite_collaborator(project_id: int, input: CollaboratorInvite, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    return await invite_project_collaborator(session, user, project_id, input)
