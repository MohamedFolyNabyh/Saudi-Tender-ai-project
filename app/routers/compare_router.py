from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.tender import Tender
from app.schemas.compare_schema import CompareRequest
from app.services.compare_service import CompareService


router = APIRouter(
    prefix="/compare",
    tags=["Compare"]
)


@router.post("/")
def compare_tenders(
    request: CompareRequest,
    db: Session = Depends(get_db)
):

    # Prevent comparing the same tender
    if request.tender_id_1 == request.tender_id_2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot compare a tender with itself."
        )

    # Get Tender A
    tender1 = db.query(Tender).filter(
        Tender.id == request.tender_id_1
    ).first()

    if not tender1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender {request.tender_id_1} not found."
        )

    # Get Tender B
    tender2 = db.query(Tender).filter(
        Tender.id == request.tender_id_2
    ).first()

    if not tender2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender {request.tender_id_2} not found."
        )

    # Make comparison
    try:

        result = CompareService.compare(
            tender1=tender1,
            tender2=tender2
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )
