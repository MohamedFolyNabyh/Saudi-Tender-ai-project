from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums.tender_status import TenderStatus


class Tender(Base):
    __tablename__ = "tenders"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Tender Information
    tender_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    pdf_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    # Qdrant
    qdrant_collection: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    # Status
    status: Mapped[TenderStatus] = mapped_column(
        SQLEnum(TenderStatus),
        default=TenderStatus.UPLOADED,
        nullable=False
    )

    # Foreign Keys & Relationships
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tenders"
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="tender",
        cascade="all, delete-orphan"
    )

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )