from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
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
    
# Analogy System Schemas
class AnalogyRequest(BaseModel):
    """Request to generate a personalized analogy"""
    user_identifier: str = Field(..., min_length=1, max_length=100, description="User identifier for session tracking")
    profession_id: int = Field(..., description="User's profession/background for analogy context")
    topic_id: int = Field(..., description="Topic to learn")
    subtopic_id: Optional[int] = Field(None, description="Specific subtopic (optional)")
    concept_name: Optional[str] = Field(None, description="Custom concept name (overrides subtopic)")
    concept_description: Optional[str] = Field(None, description="Custom concept description")
    difficulty_preference: Optional[str] = Field("intermediate", description="Preferred difficulty level")
    creative_level: Optional[int] = Field(3, ge=1, le=5, description="Creativity level 1-5 (5 = most creative)")

class AnalogyExample(BaseModel):
    """Individual example within an analogy"""
    title: str
    description: str
    code_snippet: Optional[str] = None
    visual_metaphor: Optional[str] = None

class GeneratedAnalogyResponse(BaseModel):
    """AI-generated analogy response"""
    analogy_id: int
    session_id: int
    
    # What was explained
    concept_name: str
    concept_description: str
    
    # The personalized explanation
    analogy_title: str
    analogy_explanation: str
    examples: List[AnalogyExample] = []
    
    # Context
    profession_context: str
    topic_context: str
    difficulty_level: str
    
    # Metadata
    ai_model_used: str
    generation_time_seconds: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class LearningSessionResponse(BaseModel):
    """Learning session details"""
    session_id: int
    user_identifier: str
    profession_name: str
    topic_name: str
    subtopic_name: Optional[str] = None
    session_start: datetime
    is_active: bool
    analogies_count: int
    
    class Config:
        from_attributes = True

class AnalogyFeedback(BaseModel):
    """User feedback on generated analogy"""
    analogy_id: int
    user_rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    understanding_improved: bool = Field(..., description="Did this analogy improve understanding?")

class ConceptExplanationRequest(BaseModel):
    """Simplified request for quick concept explanations"""
    profession: str = Field(..., description="User's profession (e.g., 'gaming', 'cooking')")
    concept: str = Field(..., description="Concept to explain (e.g., 'recursion', 'binary trees')")
    context: Optional[str] = Field(None, description="Additional context or specific aspect to focus on")
    creativity_level: Optional[int] = Field(3, ge=1, le=5, description="How creative should the analogy be?")

class QuickAnalogyResponse(BaseModel):
    """Quick analogy response without database storage"""
    concept: str
    profession_context: str
    analogy_title: str
    explanation: str
    practical_examples: List[str] = []
    key_connections: List[str] = []
    next_steps: List[str] = []
    generation_time: float