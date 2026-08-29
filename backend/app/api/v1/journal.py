"""
Journal API — Private thoughts, reflections, and emotional journaling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import uuid
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.journal import JournalEntry
from app.schemas.journal import JournalCreate, JournalUpdate, JournalResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/journal", tags=["Journal"])

@router.post("", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    data: JournalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new private journal entry."""
    entry = JournalEntry(
        user_id=current_user.id,
        title=data.title.strip() if data.title else "Untitled Reflection",
        content=data.content.strip(),
        mood_tag=data.mood_tag.strip() if data.mood_tag else None,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

@router.get("", response_model=List[JournalResponse])
async def list_journal_entries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all journal entries for the current authenticated user."""
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(desc(JournalEntry.created_at))
    )
    return result.scalars().all()

@router.get("/{entry_id}", response_model=JournalResponse)
async def get_journal_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single journal entry by ID."""
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found.")
    return entry

@router.put("/{entry_id}", response_model=JournalResponse)
async def update_journal_entry(
    entry_id: uuid.UUID,
    data: JournalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing journal entry."""
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found.")

    if data.title is not None:
        entry.title = data.title.strip()
    if data.content is not None:
        entry.content = data.content.strip()
    if data.mood_tag is not None:
        entry.mood_tag = data.mood_tag.strip()

    await db.commit()
    await db.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a journal entry."""
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found.")

    await db.delete(entry)
    await db.commit()
    return None
