from typing import List
from database import get_db
from security import get_current_user
from models import Comment, ArtImage, User
from sqlalchemy.orm import Session, joinedload
from schemas import CommentCreate, CommentOut, UpdateComment
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

# POST A COMMENT
@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_content: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image = db.query(ArtImage).filter(ArtImage.id == comment_content.image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image could not be found.")
    
    #comment body
    new_comment = Comment(
        text = comment_content.text,
        image_id = comment_content.image_id,
        user_id =  current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "id": new_comment.id,
        "text": new_comment.text,
        "created_at": new_comment.created_at,
        "updated_at": new_comment.updated_at,
        "username": current_user.username
    }



#GET COMMENT(S) FOR IMAGE ID
@router.get("/image/{image_id}", response_model=List[CommentOut])
async def get_image_comments(image_id:int, db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .filter(Comment.image_id == image_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [
        {
            "id": com.id,
            "text": com.text,
            "created_at": com.created_at,
            "updated_at": com.updated_at,
            "username": com.user.username if hasattr(com, 'user') and com.user else "Unknown"
        }
        for com in comments
    ]
 

#UPDATE COMMENT(S)
@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id:int,
    comment_data: UpdateComment,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments.")
    comment.text = comment_data.text
    db.commit()
    db.refresh(comment)

    return {
            "id": comment.id,
            "text": comment.text,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "username": comment.user.username
    }
#region KEEP THIS JIC
# #DELETE COMMENT - keep if admin delete doesnt work
# @router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_comment(comment_id:int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
#     comment= db.query(Comment).filter(Comment.id == comment_id).first()
#     if not comment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not Locate Comment.")
    
#     if comment.user_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comments.")
    
#     db.delete(comment)
#     db.commit()
#endregion    

# DELETE COMMENT / ADMIN DELETE ANY (REDUEX)
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Comment not found."
        )

    # Allow delete if: user owns the comment OR user is admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments."
        )

    db.delete(comment)
    db.commit()