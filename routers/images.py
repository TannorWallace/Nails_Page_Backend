from database import get_db
from sqlalchemy.orm import Session
from models import ArtImage, Comment
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/images",
    tags=["Images"]
)

#GET ALL IMAGES
@router.get("/")
async def get_all_images(db:Session = Depends(get_db)):
    images = (
        db.query(ArtImage)
        .order_by(ArtImage.created_at.desc())
        .all()
    )
    return [
        # ArtImageOut.model_validate
        {
            "id": img.id,
            "title": img.title,
            "image_url": img.image_url,
            "artist": img.artist,
            "created_at": img.created_at
        }
        for img in images
    ]

#get single image and comments
@router.get("/{image_id}")
async def get_image_with_comments(image_id: int, db: Session = Depends(get_db)):
    """Returns one image AND all its comments"""
    image = db.query(ArtImage).filter(ArtImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    comments = (
        db.query(Comment)
        .filter(Comment.image_id == image_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    comment_list = [
        {
            "id": c.id,
            "text": c.text,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "username": c.user.username if c.user else "Unknown"
        }
        for c in comments
    ]

    return {
        "id": image.id,
        "title": image.title,
        "image_url": image.image_url,
        "artist": image.artist,
        "created_at": image.created_at,
        "comments": comment_list
    }