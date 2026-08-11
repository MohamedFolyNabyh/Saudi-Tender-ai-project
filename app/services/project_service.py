# from sqlalchemy.orm import Session

# from app.database.models.project import Project
# from app.schemas.project_schema import ProjectCreate, ProjectUpdate


# class ProjectService:


#     @staticmethod
#     def create_project(
#         db: Session,
#         project_data: ProjectCreate,
#         user_id: int
#     ):

#         project = Project(

#             name=project_data.name,

#             description=project_data.description,

#             user_id=user_id
#         )


#         db.add(project)

#         db.commit()

#         db.refresh(project)


#         return project

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.models.project import Project
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate
)


class ProjectService:

    @staticmethod
    def create_project(
        db: Session,
        project_data: ProjectCreate,
        user_id: int
    ):

        project = Project(
            name=project_data.name,
            description=project_data.description,
            user_id=user_id
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def get_projects(
        db: Session,
        user_id: int
    ):

        return (
            db.query(Project)
            .filter(Project.user_id == user_id)
            .all()
        )

    @staticmethod
    def get_project(
        db: Session,
        project_id: int,
        user_id: int
    ):

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == user_id
            )
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )

        return project

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        project_data: ProjectUpdate,
        user_id: int
    ):

        project = ProjectService.get_project(
            db,
            project_id,
            user_id
        )

        if project_data.name is not None:
            project.name = project_data.name

        if project_data.description is not None:
            project.description = project_data.description

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete_project(
        db: Session,
        project_id: int,
        user_id: int
    ):

        project = ProjectService.get_project(
            db,
            project_id,
            user_id
        )

        db.delete(project)
        db.commit()

        return {
            "message": "Project deleted successfully"
        }



