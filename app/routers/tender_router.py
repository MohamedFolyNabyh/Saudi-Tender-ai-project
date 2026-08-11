from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.tender_schema import TenderResponse
from app.services.tender_service import TenderService


router = APIRouter(
    prefix="/tenders",
    tags=["Tenders"]
)


@router.post(
    "/upload/{project_id}",
    response_model=TenderResponse
)
def upload_tender(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TenderService.create_tender(
        db=db,
        project_id=project_id,
        file=file,
        current_user=current_user
    )


@router.get(
    "/project/{project_id}",
    response_model=list[TenderResponse]
)
def get_tenders(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TenderService.get_tenders(
        db=db,
        project_id=project_id,
        current_user=current_user
    )


@router.get(
    "/{tender_id}",
    response_model=TenderResponse
)
def get_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TenderService.get_tender(
        db=db,
        tender_id=tender_id,
        current_user=current_user
    )


@router.delete(
    "/{tender_id}"
)
def delete_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TenderService.delete_tender(
        db=db,
        tender_id=tender_id,
        current_user=current_user
    )