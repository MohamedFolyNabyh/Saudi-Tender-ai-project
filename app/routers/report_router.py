from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.user import User
from fastapi import HTTPException

from app.schemas.report_schema import ReportRequest

from app.services.report_service import ReportService
from app.services.risk_service import RiskService

from app.core.dependencies import get_current_user
from app.database.models.project import Project
from app.database.models.tender import Tender

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("/{tender_id}")
def generate_report(
    tender_id: int,
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ==========================
    # Get Tender
    # ==========================

   

    tender = (
        db.query(Tender)
        .join(Project)
        .filter(
            Tender.id == tender_id,
            Project.user_id == current_user.id
        )
        .first()
    )

    if not tender:

        

        raise HTTPException(
            status_code=404,
            detail="Tender not found"
        )

    # ==========================
    # Generate Report
    # ==========================

    if request.report_type == "summary":

        result = ReportService.generate(
            tender=tender
        )

    else:

        result = RiskService.analyze(
            tender=tender
        )

    return {
        "report_type": request.report_type,
        "answer": result["answer"],
        "sources": result.get(
            "sources",
            []
        )
    }