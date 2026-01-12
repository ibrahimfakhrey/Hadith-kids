"""
Children router for managing user's children.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.auth import ChildCreate, ChildUpdate, ChildResponse
from app.services.auth_service import get_current_user
from app.models import User, Child

router = APIRouter(prefix="/children", tags=["Children"])


@router.get("", response_model=List[ChildResponse])
async def list_children(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all children for the current user.

    Requires authentication.
    """
    return current_user.children


@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(
    child_data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new child for the current user.

    - **name**: Child's name (required)
    - **avatar**: Optional avatar identifier
    """
    child = Child(
        user_id=current_user.id,
        name=child_data.name,
        avatar=child_data.avatar
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific child by ID.

    Only returns children belonging to the current user.
    """
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    return child


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: int,
    child_data: ChildUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a child's information.

    Only updates children belonging to the current user.
    """
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    # Update only provided fields
    if child_data.name is not None:
        child.name = child_data.name
    if child_data.avatar is not None:
        child.avatar = child_data.avatar

    db.commit()
    db.refresh(child)
    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a child.

    This will also delete all hadith progress for this child.
    Only deletes children belonging to the current user.
    """
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.user_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child not found"
        )

    db.delete(child)
    db.commit()
    return None
