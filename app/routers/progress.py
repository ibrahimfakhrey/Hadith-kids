"""
Progress router for tracking children's hadith learning progress.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.auth import ProgressCreate, ProgressUpdate, ProgressResponse, ProgressWithHadith
from app.services.auth_service import get_current_user
from app.models import User, Child, ChildHadithProgress, Hadith, LearningStatus

router = APIRouter(prefix="/children/{child_id}/progress", tags=["Learning Progress"])


def get_child_for_user(child_id: int, current_user: User, db: Session) -> Child:
    """Helper to verify child belongs to current user."""
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


@router.get("", response_model=List[ProgressResponse])
async def list_progress(
    child_id: int,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all hadith progress for a child.

    Optionally filter by status: new, reading, memorizing, memorized, reviewing
    """
    child = get_child_for_user(child_id, current_user, db)

    query = db.query(ChildHadithProgress).filter(ChildHadithProgress.child_id == child.id)

    if status_filter:
        query = query.filter(ChildHadithProgress.status == status_filter)

    return query.all()


@router.get("/stats")
async def get_progress_stats(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress statistics for a child.

    Returns counts for each learning status.
    """
    child = get_child_for_user(child_id, current_user, db)

    stats = {}
    for status in LearningStatus:
        count = db.query(ChildHadithProgress).filter(
            ChildHadithProgress.child_id == child.id,
            ChildHadithProgress.status == status.value
        ).count()
        stats[status.value] = count

    total = sum(stats.values())
    stats["total"] = total

    return {
        "child_id": child.id,
        "child_name": child.name,
        "stats": stats
    }


@router.post("", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
async def start_learning(
    child_id: int,
    progress_data: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start tracking a hadith for a child.

    This creates a new progress record with status 'new'.
    """
    child = get_child_for_user(child_id, current_user, db)

    # Check if hadith exists
    hadith = db.query(Hadith).filter(Hadith.id == progress_data.hadith_id).first()
    if not hadith:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hadith not found"
        )

    # Check if progress already exists
    existing = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == progress_data.hadith_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress already exists for this hadith"
        )

    progress = ChildHadithProgress(
        child_id=child.id,
        hadith_id=progress_data.hadith_id,
        status=LearningStatus.NEW.value
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


@router.get("/{hadith_id}", response_model=ProgressWithHadith)
async def get_progress(
    child_id: int,
    hadith_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress for a specific hadith.
    """
    child = get_child_for_user(child_id, current_user, db)

    progress = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == hadith_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this hadith"
        )

    # Get hadith details
    hadith = db.query(Hadith).filter(Hadith.id == hadith_id).first()

    result = ProgressResponse.model_validate(progress)
    return ProgressWithHadith(
        **result.model_dump(),
        hadith={
            "id": hadith.id,
            "text_ar": hadith.text_ar[:200] + "..." if len(hadith.text_ar or "") > 200 else hadith.text_ar,
            "text_en": hadith.text_en[:200] + "..." if len(hadith.text_en or "") > 200 else hadith.text_en,
            "book_id": hadith.book_id,
            "hadith_number": hadith.hadith_number
        } if hadith else None
    )


@router.put("/{hadith_id}", response_model=ProgressResponse)
async def update_progress(
    child_id: int,
    hadith_id: int,
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update progress status for a hadith.

    Status flow: new -> reading -> memorizing -> memorized -> reviewing
    """
    child = get_child_for_user(child_id, current_user, db)

    progress = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == hadith_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this hadith"
        )

    # Update status
    old_status = progress.status
    progress.status = progress_data.status

    # Track timestamps based on status changes
    if progress_data.status == LearningStatus.MEMORIZED.value and old_status != LearningStatus.MEMORIZED.value:
        progress.memorized_at = datetime.utcnow()

    if progress_data.status == LearningStatus.REVIEWING.value:
        progress.last_reviewed_at = datetime.utcnow()
        progress.review_count += 1

    # Update notes if provided
    if progress_data.notes is not None:
        progress.notes = progress_data.notes

    db.commit()
    db.refresh(progress)
    return progress


@router.delete("/{hadith_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress(
    child_id: int,
    hadith_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove progress tracking for a hadith.
    """
    child = get_child_for_user(child_id, current_user, db)

    progress = db.query(ChildHadithProgress).filter(
        ChildHadithProgress.child_id == child.id,
        ChildHadithProgress.hadith_id == hadith_id
    ).first()

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this hadith"
        )

    db.delete(progress)
    db.commit()
    return None
