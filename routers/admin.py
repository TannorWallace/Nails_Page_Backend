import asyncio
import cloudinary
import cloudinary.uploader
from typing import List
from database import get_db
from datetime import datetime
from typing import List, Optional
from models import ArtImage, Comment, User
from sqlalchemy.orm import Session, joinedload
from security import get_current_user, get_current_admin, get_password_hash
from schemas import AdminCommentOut, AdminUserCreate, ArtImageOut, UserOut
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

# Router has NO global dependency so /admin/users/ can stay open
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ====================== ADMIN USER CREATION (FULLY OPEN - NO AUTH) ======================

@router.post("/users/", response_model=UserOut)
def admin_create_user(
    user: AdminUserCreate,
    db: Session = Depends(get_db),
):
    """Completely open endpoint for testing - Create admin users at will"""
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ====================== CLOUDINARY IMAGE UPLOADS (PROTECTED) ======================

@router.post("/images/cloudinary", response_model=ArtImageOut, dependencies=[Depends(get_current_admin)])
async def admin_upload_images_cloudinary(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)
):
    result = cloudinary.uploader.upload(
        file.file,
        folder="nails_by_mykala",
        public_id=f"nail_art_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    db_image = ArtImage(
        title=title,
        image_url=result["secure_url"],
        artist="Mykala Wallace",
        uploaded_by_id=current_admin.id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image




@router.post(
    "/images/upload_mult/cloudinary", 
    response_model=List[ArtImageOut],
    dependencies=[Depends(get_current_admin)],
    summary="Upload multiple images at once (faster)"
)
async def admin_post_mult_imgs_cloudinary(
    files: List[UploadFile] = File(..., description="Select multiple images"),
    title: str = Form("Nail Art by Mykala", description="Default title if none provided per image"),
    artist: str = Form("Mykala Wallace"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No images uploaded.")

    uploaded_images = []

    async def upload_single(file: UploadFile):
        """Upload one image to Cloudinary"""
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file.file,
            folder="nails_by_mykala",
            public_id=f"nail_art_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        )

        new_image = ArtImage(
            title=title,
            image_url=result["secure_url"],
            artist=artist,
            uploaded_by_id=current_admin.id
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        return new_image

    # Upload all images in parallel (much faster)
    tasks = [upload_single(file) for file in files]
    uploaded_images = await asyncio.gather(*tasks)

    return uploaded_images


# ====================== OTHER PROTECTED ADMIN ROUTES ======================

@router.get("/images", dependencies=[Depends(get_current_admin)])
async def get_all_images(db: Session = Depends(get_db)):
    return db.query(ArtImage).order_by(ArtImage.created_at.asc()).all()


@router.delete("/images/{image_id}", dependencies=[Depends(get_current_admin)])
async def admin_delete_img(
    image_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    image = db.query(ArtImage).filter(ArtImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image could not be located")
    db.delete(image)
    db.commit()
    return {"message": "Item removed."}


@router.get("/users", dependencies=[Depends(get_current_admin)])
async def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.asc()).all()


@router.delete("/users/{user_id}", dependencies=[Depends(get_current_admin)])
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully"}


@router.get("/comments", response_model=List[AdminCommentOut], dependencies=[Depends(get_current_admin)])
async def get_all_comments(db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .join(User, Comment.user_id == User.id)
        .join(ArtImage, Comment.image_id == ArtImage.id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return [
        {
            "id": com.id,
            "text": com.text,
            "created_at": com.created_at,
            "updated_at": com.updated_at,
            "username": com.user.username,
            "image_id": com.image_id,
            "image_title": com.image.title
        }
        for com in comments
    ]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)])
async def admin_delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()