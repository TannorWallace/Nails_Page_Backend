import os
from typing import List
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from database import get_db
from models import ArtImage, Comment, User
from schemas import AdminCommentOut, ArtImageCreate, ArtImageOut
from security import get_current_user, get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)]
    ) #might need to take off the dependency until later.

UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#ADMIN POST IMAGES
@router.post("/images/",response_model=ArtImageOut)
async def admin_upload_images(
    title:str =Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)
):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    db_image = ArtImage(
        title = title,
        image_url=f"/static/images/{file.filename}",
        uploaded_by_id= current_admin.id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

#GET ALL IMAGES
@router.get("/images")
async def get_all_images(db:Session=Depends(get_db)):
    image_list = db.query(ArtImage).order_by(ArtImage.created_at.asc()).all()
    return image_list

#GET IMAGE BY ID
@router.get("/images/{image_id}")
async def get_user_by_id(image_id:int, db: Session=Depends(get_db)):
    image = db.query(User).filter(User.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user by that Id could be found.")
    return image


#delete IMAGE
@router.delete("/images/{image_id}")
async def admin_delete_img(image_id:int,
                    db:Session = Depends(get_db),
                    current_admin: User = Depends(get_current_admin)):
    image = db.query(ArtImage).filter(ArtImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image could not be located")

    #Delete from /images folder
    file_path = image.image_url.replace("/static/images/", "static/images/")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.delete(image)
    db.commit()
    return {"message":"Item removed."}

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
    """ADMIN ONLY - Delete any user (cannot delete yourself)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #prevent deleting yo'self
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.username} deleted successfully"}

#ADMIN GET COMMENTS
@router.get("/comments", response_model=List[AdminCommentOut]) #List not list...dang that took a while :/
async def get_all_comments(db: Session = Depends(get_db)):

    comments = (
         db.query(Comment)
        .join(User, Comment.user_id == User.id)
        .join(ArtImage, Comment.image_id == ArtImage.id)
        .order_by(Comment.created_at.desc())   # newest first
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
    

#ADMIN DELETE COMMENT
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return {"message": f"Comment {comment_id} deleted by admin"}