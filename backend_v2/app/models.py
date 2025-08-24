from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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