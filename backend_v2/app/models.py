from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
    

class Profession(Base):
    __tablename__ = "professions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Profession(id={self.id}, name='{self.name}')>"

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # For UI icons
    color = Column(String(7), nullable=True)  # Hex color for UI
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}')>"

class Subtopic(Base):
    __tablename__ = "subtopics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(20), nullable=False, default="beginner")  # beginner, intermediate, advanced
    estimated_time_minutes = Column(Integer, nullable=True)  # Estimated learning time
    prerequisites = Column(Text, nullable=True)  # JSON string of prerequisite subtopic IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    topic = relationship("Topic", back_populates="subtopics")

    def __repr__(self):
        return f"<Subtopic(id={self.id}, name='{self.name}', topic='{self.topic.name if self.topic else None}')>"
    
class LearningSession(Base):
    """Track user learning sessions and preferences"""
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String(100), nullable=False, index=True)  # For demo: simple string ID
    profession_id = Column(Integer, ForeignKey("professions.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    
    # Session metadata
    session_start = Column(DateTime(timezone=True), server_default=func.now())
    session_end = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profession = relationship("Profession")
    topic = relationship("Topic")
    subtopic = relationship("Subtopic")
    analogies = relationship("GeneratedAnalogy", back_populates="session")
    
    def __repr__(self):
        return f"<LearningSession(id={self.id}, user='{self.user_identifier}', profession='{self.profession.name if self.profession else None}')>"   
    
class GeneratedAnalogy(Base):
    """Store AI-generated analogies for reuse and improvement"""
    __tablename__ = "generated_analogies"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=False)
    
    # What was explained
    concept_name = Column(String(200), nullable=False)
    concept_description = Column(Text, nullable=False)
    
    # How it was explained
    analogy_title = Column(String(300), nullable=False)
    analogy_explanation = Column(Text, nullable=False)
    analogy_examples = Column(Text, nullable=True)  # JSON string of examples
    
    # AI metadata
    ai_model_used = Column(String(50), default="gpt-4")
    generation_time_seconds = Column(Float, nullable=True)
    prompt_template_version = Column(String(20), default="v1.0")
    
    # Quality metrics
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    understanding_score = Column(Float, nullable=True)  # AI-assessed comprehension
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    session = relationship("LearningSession", back_populates="analogies")
    
    def __repr__(self):
        return f"<GeneratedAnalogy(id={self.id}, concept='{self.concept_name}', title='{self.analogy_title[:50]}...')>"     