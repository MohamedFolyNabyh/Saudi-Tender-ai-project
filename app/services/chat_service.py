from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models.project import Project
from app.database.models.tender import Tender
from app.database.models.user import User

from app.schemas.chat_schema import ChatRequest

from app.graph.graph import graph

from app.services.memory_service import MemoryService


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
        # Load Conversation History
        # =====================================

        history = MemoryService.get_history(
            user_id=current_user.id
        )

        # =====================================
        # Initial Graph State
        # =====================================

        state = {
            "db": db,
            "tender": tender,
            "current_user": current_user,
            "question": request.question,
            "history": history,
            "intent": "",
            "answer": "",
            "sources": []
        }

        # =====================================
        # Run LangGraph
        # =====================================

        result = graph.invoke(state)

        answer = result.get("answer", "")

        # =====================================
        # Save Conversation
        # =====================================

        MemoryService.add_message(
            user_id=current_user.id,
            role="user",
            content=request.question
        )

        MemoryService.add_message(
            user_id=current_user.id,
            role="assistant",
            content=answer
        )

        # =====================================
        # Return Answer
        # =====================================

        return {
            "answer": answer,
            "sources": result.get("sources", [])
        }
