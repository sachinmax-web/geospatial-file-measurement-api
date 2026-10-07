from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint verifying database connectivity and API status.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "database": db_status,
        "service": "Geospatial File Measurement API"
    }
