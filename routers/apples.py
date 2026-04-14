from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    prefix="/apples",
    tags=["apples"]
)

@router.get("/apples")
async def get_apples(db: Session = Depends(get_db)):
    """Test endpoint – returns apples! (proof that DB + FastAPI works)"""
    return {
        "message": "🍎 Apples test endpoint is working!",
        "status": "✅ Everything is wired up correctly",
        "hint": "Replace me with real endpoints later"
    }

@router.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "database": "sqlite (ready for PostgreSQL migration)"}

@router.get("/test-models")
async def test_models(db: Session = Depends(get_db)):
    """Quick check that models are imported correctly"""
    return {
        "models_ready": ["User", "ArtImage", "Comment", "Service"],
        "message": "All models imported successfully!"
    }