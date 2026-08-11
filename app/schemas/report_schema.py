from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Literal


class ReportResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )
    

    id: int

    tender_id: int

    technical_proposal: str

    financial_proposal: str

    pdf_path: str

    created_at: datetime



class ReportRequest(BaseModel):

    report_type: Literal[
        "summary",
        "risk"
    ]