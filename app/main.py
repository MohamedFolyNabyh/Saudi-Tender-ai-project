from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import os

from app.database.session import get_db

from app.routers.auth_router import router as auth_router
from app.routers.project_router import router as project_router
from app.routers.tender_router import router as tender_router
from app.routers.chat_router import router as chat_router
from app.routers.compare_router import router as compare_router
from app.routers.export_router import router as export_router
from app.routers.report_router import router as reports_router
app = FastAPI(
    title="Tender AI API"
)

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(tender_router)
app.include_router(chat_router)
app.include_router(export_router)
app.include_router(compare_router)


app.include_router(reports_router)

@app.get("/health")
def health():

    return {
        "status": "running",
        "database": os.getenv("DATABASE_URL"),
        "redis": os.getenv("REDIS_URL"),
        "qdrant": os.getenv("QDRANT_URL")
    }


@app.get("/test-db")
def test_db(
    db: Session = Depends(get_db)
):

    return {
        "database": "connected"
    }