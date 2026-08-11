from pydantic import BaseModel


class ChatRequest(BaseModel):

    tender_id: int

    question: str


class SourceResponse(BaseModel):

    page: int

    source: str


class ChatResponse(BaseModel):

    answer: str

    sources: list[SourceResponse]