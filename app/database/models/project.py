from datetime import datetime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base

class Project(Base):
    __tablename__="projects"
    
    id:Mapped[int]=mapped_column(
        primary_key=True
    )
    user_id:Mapped[int]=mapped_column(
        ForeignKey("users.id",ondelete='CASCADE')
    )
    name:Mapped[str]=mapped_column(
        String(200)
    )
    description:Mapped[str | None]=mapped_column(
        Text,
        nullable=True
    )
    created_at:Mapped[DateTime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    owner: Mapped["User"] = relationship(
    back_populates="projects")

    tenders: Mapped[list["Tender"]] = relationship(
    back_populates="project",
    cascade="all, delete-orphan")