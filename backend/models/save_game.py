from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.database import Base


class SaveGame(Base):
    __tablename__ = "save_games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    
    # Save metadata
    save_name = Column(String, nullable=False)
    current_node_id = Column(Integer, ForeignKey("story_nodes.id"), nullable=False)
    
    # Game state
    choices_made = Column(JSON, default=list)  # List of choice objects with node_id, option_text, timestamp
    nodes_visited = Column(JSON, default=list)  # List of visited node IDs
    play_time_minutes = Column(Integer, default=0)
    
    # Save info
    is_auto_save = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    story = relationship("Story")
    current_node = relationship("StoryNode")


class UserStoryProgress(Base):
    __tablename__ = "user_story_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    
    # Progress tracking
    total_nodes_visited = Column(Integer, default=1)
    endings_reached = Column(JSON, default=list)  # List of ending node IDs reached
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Timestamps
    first_played_at = Column(DateTime(timezone=True), server_default=func.now())
    last_played_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    story = relationship("Story")
