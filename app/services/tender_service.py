import os
import shutil

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database.models.project import Project
from app.database.models.tender import Tender
from app.database.models.user import User
from app.enums.tender_status import TenderStatus

UPLOAD_FOLDER = "storage/pdfs"


class TenderService:

    @staticmethod
    def create_tender(
        db: Session,
        project_id: int,
        file: UploadFile,
        current_user: User
    ):
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        collection_name = (
            f"project_{project_id}_{file.filename}"
            .replace(".", "_")
            .replace(" ", "_")
            .lower()
        )

        tender = Tender(
            project_id=project_id,
            tender_name=file.filename,
            pdf_path=file_path,
            qdrant_collection=collection_name,
            status=TenderStatus.UPLOADED
        )

        db.add(tender)
        db.commit()
        db.refresh(tender)

        return tender

    @staticmethod
    def get_tenders(
        db: Session,
        project_id: int,
        current_user: User
    ):
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        return db.query(Tender).filter(
            Tender.project_id == project_id
        ).all()

    @staticmethod
    def get_tender(
        db: Session,
        tender_id: int,
        current_user: User
    ):
        tender = (
            db.query(Tender)
            .join(Project)
            .filter(
                Tender.id == tender_id,
                Project.user_id == current_user.id
            )
            .first()
        )

        if not tender:
            raise HTTPException(
                status_code=404,
                detail="Tender not found"
            )

        return tender

    @staticmethod
    def delete_tender(
        db: Session,
        tender_id: int,
        current_user: User
    ):
        tender = TenderService.get_tender(
            db,
            tender_id,
            current_user
        )

        if os.path.exists(tender.pdf_path):
            os.remove(tender.pdf_path)

        db.delete(tender)
        db.commit()

        return {
            "message": "Tender deleted successfully"
        }