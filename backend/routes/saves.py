from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from db.database import get_db
from models.user import User
from models.story import Story, StoryNode
from models.save_game import SaveGame, UserStoryProgress
from schemas.save_game import (
    SaveGameCreate, SaveGameUpdate, SaveGameResponse, 
    UserProgressResponse, ContinueGameResponse
)
from core.auth import get_current_user

router = APIRouter(
    prefix="/saves",
    tags=["save_games"]
)


@router.post("/", response_model=SaveGameResponse)
def create_save_game(
    save_data: SaveGameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user owns the story session or story exists
    story = db.query(Story).filter(Story.id == save_data.story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Verify current node exists and belongs to story
    current_node = db.query(StoryNode).filter(
        StoryNode.id == save_data.current_node_id,
        StoryNode.story_id == save_data.story_id
    ).first()
    if not current_node:
        raise HTTPException(status_code=404, detail="Invalid current node")
    
    # Delete existing auto-save for this user/story if creating new auto-save
    if save_data.is_auto_save:
        existing_auto_save = db.query(SaveGame).filter(
            SaveGame.user_id == current_user.id,
            SaveGame.story_id == save_data.story_id,
            SaveGame.is_auto_save == True
        ).first()
        if existing_auto_save:
            db.delete(existing_auto_save)
    
    # Create save game
    save_game = SaveGame(
        user_id=current_user.id,
        story_id=save_data.story_id,
        save_name=save_data.save_name,
        current_node_id=save_data.current_node_id,
        choices_made=save_data.choices_made,
        nodes_visited=save_data.nodes_visited,
        play_time_minutes=save_data.play_time_minutes,
        is_auto_save=save_data.is_auto_save
    )
    
    db.add(save_game)
    db.commit()
    db.refresh(save_game)
    
    # Update user progress
    update_user_progress(db, current_user.id, save_data.story_id, save_data.nodes_visited)
    
    return format_save_game_response(db, save_game)


@router.get("/", response_model=List[SaveGameResponse])
def get_user_saves(
    story_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SaveGame).filter(SaveGame.user_id == current_user.id)
    
    if story_id:
        query = query.filter(SaveGame.story_id == story_id)
    
    saves = query.order_by(SaveGame.updated_at.desc()).all()
    
    return [format_save_game_response(db, save) for save in saves]


@router.get("/{save_id}", response_model=SaveGameResponse)
def get_save_game(
    save_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    save = db.query(SaveGame).filter(
        SaveGame.id == save_id,
        SaveGame.user_id == current_user.id
    ).first()
    
    if not save:
        raise HTTPException(status_code=404, detail="Save game not found")
    
    return format_save_game_response(db, save)


@router.put("/{save_id}", response_model=SaveGameResponse)
def update_save_game(
    save_id: int,
    save_data: SaveGameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    save = db.query(SaveGame).filter(
        SaveGame.id == save_id,
        SaveGame.user_id == current_user.id
    ).first()
    
    if not save:
        raise HTTPException(status_code=404, detail="Save game not found")
    
    # Update fields
    update_data = save_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(save, field, value)
    
    save.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(save)
    
    # Update user progress if nodes_visited changed
    if save_data.nodes_visited:
        update_user_progress(db, current_user.id, save.story_id, save_data.nodes_visited)
    
    return format_save_game_response(db, save)


@router.delete("/{save_id}")
def delete_save_game(
    save_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    save = db.query(SaveGame).filter(
        SaveGame.id == save_id,
        SaveGame.user_id == current_user.id
    ).first()
    
    if not save:
        raise HTTPException(status_code=404, detail="Save game not found")
    
    db.delete(save)
    db.commit()
    
    return {"message": "Save game deleted successfully"}


@router.post("/{save_id}/load", response_model=ContinueGameResponse)
def load_save_game(
    save_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    save = db.query(SaveGame).filter(
        SaveGame.id == save_id,
        SaveGame.user_id == current_user.id
    ).first()
    
    if not save:
        raise HTTPException(status_code=404, detail="Save game not found")
    
    # Get complete story data
    story = db.query(Story).filter(Story.id == save.story_id).first()
    story_nodes = db.query(StoryNode).filter(StoryNode.story_id == save.story_id).all()
    
    # Build story structure
    node_dict = {}
    root_node = None
    
    for node in story_nodes:
        node_response = {
            "id": node.id,
            "content": node.content,
            "is_ending": node.is_ending,
            "is_winning_ending": node.is_winning_ending,
            "options": node.options or []
        }
        node_dict[node.id] = node_response
        if node.is_root:
            root_node = node_response
    
    story_data = {
        "id": story.id,
        "title": story.title,
        "session_id": story.session_id,
        "created_at": story.created_at,
        "root_node": root_node,
        "all_nodes": node_dict
    }
    
    # Get current node
    current_node = node_dict.get(save.current_node_id)
    
    return {
        "save_game": format_save_game_response(db, save),
        "story": story_data,
        "current_node": current_node
    }


@router.get("/progress/stories", response_model=List[UserProgressResponse])
def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    progress_records = db.query(UserStoryProgress).filter(
        UserStoryProgress.user_id == current_user.id
    ).order_by(UserStoryProgress.last_played_at.desc()).all()
    
    result = []
    for progress in progress_records:
        story = db.query(Story).filter(Story.id == progress.story_id).first()
        progress_response = UserProgressResponse(
            id=progress.id,
            user_id=progress.user_id,
            story_id=progress.story_id,
            total_nodes_visited=progress.total_nodes_visited,
            endings_reached=progress.endings_reached,
            completion_percentage=progress.completion_percentage,
            first_played_at=progress.first_played_at,
            last_played_at=progress.last_played_at,
            story_title=story.title if story else "Unknown Story"
        )
        result.append(progress_response)
    
    return result


# Helper functions
def format_save_game_response(db: Session, save: SaveGame) -> SaveGameResponse:
    story = db.query(Story).filter(Story.id == save.story_id).first()
    current_node = db.query(StoryNode).filter(StoryNode.id == save.current_node_id).first()
    
    return SaveGameResponse(
        id=save.id,
        user_id=save.user_id,
        story_id=save.story_id,
        save_name=save.save_name,
        current_node_id=save.current_node_id,
        choices_made=save.choices_made,
        nodes_visited=save.nodes_visited,
        play_time_minutes=save.play_time_minutes,
        is_auto_save=save.is_auto_save,
        created_at=save.created_at,
        updated_at=save.updated_at,
        story_title=story.title if story else "Unknown Story",
        current_node_content=current_node.content[:100] + "..." if current_node and len(current_node.content) > 100 else current_node.content if current_node else None
    )


def update_user_progress(db: Session, user_id: int, story_id: int, nodes_visited: List[int]):
    progress = db.query(UserStoryProgress).filter(
        UserStoryProgress.user_id == user_id,
        UserStoryProgress.story_id == story_id
    ).first()
    
    if not progress:
        progress = UserStoryProgress(
            user_id=user_id,
            story_id=story_id,
            total_nodes_visited=len(nodes_visited)
        )
        db.add(progress)
    else:
        progress.total_nodes_visited = max(progress.total_nodes_visited, len(nodes_visited))
        progress.last_played_at = datetime.utcnow()
    
    # Calculate completion percentage (rough estimate)
    total_story_nodes = db.query(StoryNode).filter(StoryNode.story_id == story_id).count()
    if total_story_nodes > 0:
        progress.completion_percentage = min(100, int((len(nodes_visited) / total_story_nodes) * 100))
    
    db.commit()
