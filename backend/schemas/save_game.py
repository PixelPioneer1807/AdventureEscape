from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ChoiceMade(BaseModel):
    node_id: int
    option_text: str
    next_node_id: int
    timestamp: datetime


class SaveGameCreate(BaseModel):
    story_id: int
    current_node_id: int
    save_name: str
    choices_made: List[Dict[str, Any]] = []
    nodes_visited: List[int] = []
    play_time_minutes: int = 0
    is_auto_save: bool = False


class SaveGameUpdate(BaseModel):
    save_name: Optional[str] = None
    current_node_id: Optional[int] = None
    choices_made: Optional[List[Dict[str, Any]]] = None
    nodes_visited: Optional[List[int]] = None
    play_time_minutes: Optional[int] = None


class SaveGameResponse(BaseModel):
    id: int
    user_id: int
    story_id: int
    save_name: str
    current_node_id: int
    choices_made: List[Dict[str, Any]]
    nodes_visited: List[int]
    play_time_minutes: int
    is_auto_save: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Story info for display
    story_title: Optional[str] = None
    current_node_content: Optional[str] = None

    class Config:
        from_attributes = True


class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    story_id: int
    total_nodes_visited: int
    endings_reached: List[int]
    completion_percentage: int
    first_played_at: datetime
    last_played_at: Optional[datetime]
    
    # Story info
    story_title: Optional[str] = None

    class Config:
        from_attributes = True


class ContinueGameResponse(BaseModel):
    save_game: SaveGameResponse
    story: Dict[str, Any]  # Complete story data
    current_node: Dict[str, Any]  # Current node with options
