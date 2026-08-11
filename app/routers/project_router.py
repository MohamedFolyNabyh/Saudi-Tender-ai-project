# from fastapi import APIRouter, Depends

# from sqlalchemy.orm import Session

# from app.core.dependencies import get_current_user
# from app.database.models.user import User
# from app.database.session import get_db

# from app.schemas.project_schema import ProjectCreate
# from app.services.project_service import ProjectService



# router = APIRouter(
#     prefix="/projects",
#     tags=["Projects"]
# )



# @router.post("/")
# def create_project(
#     project_data: ProjectCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):


#     project = ProjectService.create_project(
#         db,
#         project_data,
#         current_user.id
#     )


#     return project


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.user import User
from app.core.dependencies import get_current_user

from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)

from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return ProjectService.create_project(
        db=db,
        project_data=project_data,
        user_id=current_user.id
    )


@router.get(
    "",
    response_model=list[ProjectResponse]
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return ProjectService.get_projects(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return ProjectService.get_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return ProjectService.update_project(
        db=db,
        project_id=project_id,
        project_data=project_data,
        user_id=current_user.id
    )


@router.delete(
    "/{project_id}"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return ProjectService.delete_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id
    )