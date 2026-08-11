from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.tender_status import TenderStatus


class TenderResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    tender_name: str

    pdf_path: str

    qdrant_collection: str

    status: TenderStatus

    project_id: int

    uploaded_at: datetime