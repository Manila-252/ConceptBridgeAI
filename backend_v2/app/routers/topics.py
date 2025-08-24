from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging
from ..database import get_db
from ..models import Topic, Subtopic
from ..schemas import TopicResponse, TopicWithSubtopics, SubtopicResponse, DifficultyLevel

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/topics",
    tags=["topics"]
)

@router.get("/", response_model=List[TopicResponse])
async def get_topics(db: Session = Depends(get_db)):
    """
    Get all available topics for studying
    
    Returns a list of all topics including:
    - ID
    - Name (CS, Math, Physics, etc.)
    - Description
    - UI metadata (icon, color)
    - Creation/update timestamps
    """
    try:
        topics = db.query(Topic).order_by(Topic.name).all()
        logger.info(f"Retrieved {len(topics)} topics")
        return topics
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving topics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve topics from database"
        )

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Get a specific topic by ID
    
    Args:
        topic_id: The unique identifier for the topic
        
    Returns:
        Topic details if found
        
    Raises:
        404: If topic with given ID doesn't exist
    """
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {topic_id} not found"
            )
        
        logger.info(f"Retrieved topic: {topic.name}")
        return topic
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving topic {topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve topic from database"
        )

@router.get("/{topic_id}/subtopics", response_model=List[SubtopicResponse])
async def get_topic_subtopics(
    topic_id: int,
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    limit: Optional[int] = Query(None, ge=1, le=50, description="Limit number of results"),
    db: Session = Depends(get_db)
):
    """
    Get subtopics for a specific topic
    
    This endpoint returns personalized subtopics based on the topic.
    For the hackathon, we return pre-defined subtopics.
    
    Args:
        topic_id: The topic ID to get subtopics for
        difficulty: Optional filter by difficulty level
        limit: Optional limit on number of results
        
    Returns:
        List of subtopics for the topic
        
    Raises:
        404: If topic doesn't exist
    """
    try:
        # Verify topic exists
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {topic_id} not found"
            )
        
        # Build query for subtopics
        query = db.query(Subtopic).filter(Subtopic.topic_id == topic_id)
        
        # Apply difficulty filter if provided
        if difficulty:
            query = query.filter(Subtopic.difficulty_level == difficulty.value)
        
        # Apply limit if provided
        if limit:
            query = query.limit(limit)
        
        # Order by difficulty and name
        subtopics = query.order_by(
            Subtopic.difficulty_level,
            Subtopic.name
        ).all()
        
        logger.info(f"Retrieved {len(subtopics)} subtopics for topic '{topic.name}'")
        return subtopics
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving subtopics for topic {topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subtopics from database"
        )

@router.get("/{topic_id}/with-subtopics", response_model=TopicWithSubtopics)
async def get_topic_with_subtopics(
    topic_id: int,
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter subtopics by difficulty"),
    db: Session = Depends(get_db)
):
    """
    Get a topic with all its subtopics in one response
    
    Args:
        topic_id: The topic ID
        difficulty: Optional filter for subtopics by difficulty
        
    Returns:
        Topic with nested subtopics
        
    Raises:
        404: If topic doesn't exist
    """
    try:
        # Get topic with subtopics using joinedload for efficiency
        from sqlalchemy.orm import joinedload
        
        topic = db.query(Topic).options(
            joinedload(Topic.subtopics)
        ).filter(Topic.id == topic_id).first()
        
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {topic_id} not found"
            )
        
        # Filter subtopics by difficulty if provided
        subtopics = topic.subtopics
        if difficulty:
            subtopics = [st for st in subtopics if st.difficulty_level == difficulty.value]
        
        # Sort subtopics by difficulty and name
        subtopics.sort(key=lambda x: (x.difficulty_level, x.name))
        
        # Create response
        response = TopicWithSubtopics(
            id=topic.id,
            name=topic.name,
            description=topic.description,
            icon=topic.icon,
            color=topic.color,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
            subtopics=subtopics
        )
        
        logger.info(f"Retrieved topic '{topic.name}' with {len(subtopics)} subtopics")
        return response
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving topic with subtopics {topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve topic with subtopics from database"
        )