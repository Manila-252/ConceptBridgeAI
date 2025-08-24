from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ProfessionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Profession name")
    description: Optional[str] = Field(None, max_length=1000, description="Profession description")

class ProfessionCreate(ProfessionBase):
    pass

class ProfessionResponse(ProfessionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Topic Schemas
class TopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Topic name")
    description: Optional[str] = Field(None, max_length=1000, description="Topic description")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name for UI")
    color: Optional[str] = Field(None, max_length=7, description="Hex color for UI")

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Subtopic Schemas
class SubtopicBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Subtopic name")
    description: Optional[str] = Field(None, max_length=1000, description="Subtopic description")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER, description="Difficulty level")
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=300, description="Estimated learning time in minutes")
    prerequisites: Optional[str] = Field(None, description="JSON string of prerequisite subtopic IDs")

class SubtopicCreate(SubtopicBase):
    topic_id: int = Field(..., description="Topic ID this subtopic belongs to")

class SubtopicResponse(SubtopicBase):
    id: int
    topic_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Combined response for topics with their subtopics
class TopicWithSubtopics(TopicResponse):
    subtopics: List[SubtopicResponse] = []

class HealthResponse(BaseModel):
    status: str
    message: str
    database: str