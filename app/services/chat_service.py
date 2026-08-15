from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models.project import Project
from app.database.models.tender import Tender
from app.database.models.user import User
from app.schemas.chat_schema import ChatRequest

from app.graph.graph import graph


class ChatService:

    @staticmethod
    def chat(
        db: Session,
        request: ChatRequest,
        current_user: User
    ):

        tender = (
            db.query(Tender)
            .join(Project)
            .filter(
                Tender.id == request.tender_id,
                Project.user_id == current_user.id
            )
            .first()
        )

        if not tender:
            raise HTTPException(
                status_code=404,
                detail="Tender not found"
            )

        # =====================================
        # Initial Graph State
        # =====================================

        state = {
            "db": db,
            "tender": tender,
            "current_user": current_user,
            "question": request.question,
            "history": [],
            "intent": "",
            "answer": "",
            "sources": []
        }

        # =====================================
        # Run LangGraph
        # =====================================

        result = graph.invoke(state)

        # =====================================
        # Return Answer
        # =====================================

        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", [])
        }