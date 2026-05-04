import cloudinary
import cloudinary.uploader
from typing import List
from datetime import datetime
from database import get_db
from models import ArtImage, Comment, User
from sqlalchemy.orm import Session, joinedload
from security import get_current_user, get_current_admin
from schemas import AdminCommentOut, ArtImageOut
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)]
)

# ====================== CLOUDINARY UPLOADS (ONLY) ======================

# ADMIN POST SINGLE IMAGE
@router.post("/images/", response_model=ArtImageOut)
async def admin_upload_images(
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


# ADMIN POST MULTIPLE IMAGES (recommended)
@router.post("/images/upload_mult", response_model=List[ArtImageOut])
async def admin_post_mult_imgs(
    files: List[UploadFile] = File(...),
    title: str = "Nail Art by Mykala",
    artist: str = "Mykala Wallace",
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No images loaded.")

    uploaded_imgs = []

    for file in files:
        result = cloudinary.uploader.upload(
            file.file,
            folder="nails_by_mykala",
            public_id=f"nail_art_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        new_image = ArtImage(
            title=title,
            image_url=result["secure_url"],
            artist=artist
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        uploaded_imgs.append(new_image)

    return uploaded_imgs


# ====================== ALL OTHER EXISTING ENDPOINTS (unchanged) ======================

#GET ALL IMAGES
@router.get("/images")
async def get_all_images(db:Session=Depends(get_db)):
    image_list = db.query(ArtImage).order_by(ArtImage.created_at.asc()).all()
    return image_list

#GET IMAGE BY ID
@router.get("/images/{image_id}")
async def get_image_by_id(image_id:int, db: Session=Depends(get_db)):
    image = db.query(ArtImage).filter(ArtImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return image

#DELETE IMAGE (no local file deletion anymore)
@router.delete("/images/{image_id}")
async def admin_delete_img(image_id:int,
                    db:Session = Depends(get_db),
                    current_admin: User = Depends(get_current_admin)):
    image = db.query(ArtImage).filter(ArtImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image could not be located")
    
    db.delete(image)
    db.commit()
    return {"message":"Image removed."}

#GET ALL USERS
@router.get("/users")
async def get_all_users(db:Session=Depends(get_db)):
    users_list = db.query(User).order_by(User.id.asc()).all()
    return users_list

#GET USER BY ID
@router.get("/users/{user_id}")
async def get_user_by_id(user_id:int, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user by that Id could be found.")
    return user

#delete USER
@router.delete("/users/{user_id}")
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

#ADMIN GET COMMENTS
@router.get("/comments", response_model=List[AdminCommentOut])
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

#ADMIN GET COMMENT BY ID
@router.get("/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def admin_get_comment_by_id(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

#ADMIN GET COMMENTS BY USER ID    
@router.get("/user/{user_id}", response_model=List[AdminCommentOut])
async def get_user_comments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    comments = (
        db.query(Comment)
        .filter(Comment.user_id == user_id)
        .options(joinedload(Comment.image))
        .order_by(Comment.created_at.desc())
        .all()
    )

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comments found for this user.")

    return [
        {
            "id": com.id,
            "username": com.user.username,
            "text": com.text,
            "image_id": com.image_id,
            "image_title": com.image.title,
            "created_at": com.created_at,
            "updated_at": com.updated_at,
        }
        for com in comments
    ]

# ADMIN DELETE COMMENT
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully by admin"}