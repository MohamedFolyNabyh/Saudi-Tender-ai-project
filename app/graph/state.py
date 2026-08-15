from typing import TypedDict,Any

from app.database.models.tender import Tender
from app.database.models.user import User


class GraphState(TypedDict):
    db: Any

    tender: Tender

    current_user: User

    question: str

    history: list

    intent: str

    answer: str

    sources: list