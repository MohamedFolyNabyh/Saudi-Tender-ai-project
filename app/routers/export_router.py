from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)


from fastapi.responses import FileResponse


from app.schemas.export_schema import ExportRequest

from app.services.export_service import ExportService

from app.database.models.tender import Tender

from app.database.session import get_db



router = APIRouter(

    prefix="/export",

    tags=["Export"]

)



@router.post("/")
def export_report(
    request: ExportRequest,
    db=Depends(get_db)
):


    tender = db.query(Tender).filter(
        Tender.id == request.tender_id
    ).first()



    if not tender:

        raise HTTPException(
            status_code=404,
            detail="Tender not found"
        )



    result = ExportService.generate_pdf(
        tender,
        request.report_type
    )



    return FileResponse(
        result["file"],
        media_type="application/pdf",
        filename=result["file"].split("/")[-1]
    )