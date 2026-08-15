from pydantic import BaseModel


class ExportRequest(BaseModel):

    tender_id: int

    content: str

    filename: str