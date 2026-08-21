import os
import shutil
import uuid
from typing import List, Dict, Any

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models.project import Project
from app.database.models.tender import Tender
from app.database.models.user import User
from app.enums.tender_status import TenderStatus

from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

UPLOAD_FOLDER = "storage/pdfs"


class TenderService:

    @staticmethod
    def create_tender(
        db: Session,
        project_id: int,
        file: UploadFile,
        current_user: User
    ) -> Tender:
        """
        تستقبل ملف PDF الخاص بالمناقصة، وتتحقق من المشروع، ثم تقوم بحفظ الملف، 
        وتجزئته، وإنشاء Embeddings له، وتخزينه في Qdrant.
        """
        # 1. التحقق من وجود المشروع وملكيته للمستخدم
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        # 2. إنشاء مجلد الحفظ
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # 3. حفظ ملف الـ PDF محلياً
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. توليد اسم عشوائي وفريد لـ Qdrant Collection
        collection_name = f"tender_{uuid.uuid4().hex}"

        # 5. إنشاء سجل المناقصة في قاعدة البيانات بالحالة INITIAL/PROCESSING
        tender = Tender(
            project_id=project_id,
            tender_name=file.filename,
            pdf_path=file_path,
            qdrant_collection=collection_name,
            status=TenderStatus.PROCESSING
        )
        db.add(tender)
        db.commit()
        db.refresh(tender)

        try:
            # 6. قراءة وتقسيم الـ PDF إلى النصوص (Chunks)
            documents = DocumentService.split_pdf(tender.pdf_path)
            if not documents:
                raise ValueError("No text could be extracted from PDF")

            # 7. توليد ה-Embeddings للـ Chunks
            embeddings = EmbeddingService.embed_documents(documents)
            if len(embeddings) == 0:
                raise ValueError("No embeddings were generated")

            # 8. رفع الـ Vectors والـ Metadata إلى Qdrant
            VectorService.upload(
                collection_name=tender.qdrant_collection,
                documents=documents,
                embeddings=embeddings,
                tender=tender
            )

            # 9. تحديث حالة المناقصة إلى جاهز (READY)
            tender.status = TenderStatus.COMPLETED
            db.commit()
            db.refresh(tender)

        except Exception as e:
            # 10. في حالة حدوث خطأ، يتم تعليم المناقصة كـ FAILED
            db.rollback()
            tender.status = TenderStatus.FAILED
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Tender processing failed: {str(e)}"
            )

        return tender

    @staticmethod
    def get_tenders(
        db: Session,
        project_id: int,
        current_user: User
    ) -> List[Tender]:
        """جلب جميع المناقصات التابعة لمشروع معين."""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        return db.query(Tender).filter(Tender.project_id == project_id).all()

    @staticmethod
    def get_tender(
        db: Session,
        tender_id: int,
        current_user: User
    ) -> Tender:
        """جلب مناقصة محددة مع التأكد من ملكيتها عبر المشروع."""
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tender not found"
            )

        return tender

    @staticmethod
    def delete_tender(
        db: Session,
        tender_id: int,
        current_user: User
    ) -> Dict[str, str]:
        """حذف ملف الـ PDF المحلي، ومجموعة Qdrant، وسجل قاعدة البيانات."""
        tender = TenderService.get_tender(db, tender_id, current_user)

        # 1. حذف الملف الفيزيائي من السيرفر
        if os.path.exists(tender.pdf_path):
            os.remove(tender.pdf_path)

        # 2. حذف الـ Collection من Qdrant
        try:
            if tender.qdrant_collection:
                if VectorService.client.collection_exists(tender.qdrant_collection):
                    VectorService.client.delete_collection(tender.qdrant_collection)
        except Exception as e:
            print(f"Qdrant deletion warning/failed: {e}")

        # 3. حذف السجل من قاعدة البيانات
        db.delete(tender)
        db.commit()

        return {"message": "Tender deleted successfully"}
