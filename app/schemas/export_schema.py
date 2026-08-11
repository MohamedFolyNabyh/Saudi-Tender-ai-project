from pydantic import BaseModel

class ExportRequest(BaseModel):

    content: str

    filename: str