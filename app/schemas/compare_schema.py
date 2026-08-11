from pydantic import BaseModel


class CompareRequest(BaseModel):

    tender_id_1: int

    tender_id_2: int