from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging
import json
from ..database import get_db
from ..models import Profession, Topic, Subtopic, LearningSession, GeneratedAnalogy
from ..schemas import (
    AnalogyRequest, GeneratedAnalogyResponse, LearningSessionResponse,
    AnalogyFeedback, ConceptExplanationRequest, QuickAnalogyResponse
)
from ..services.analogy_service import AnalogyGenerationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analogies",
    tags=["analogies"]
)

# Initialize AI service
analogy_service = AnalogyGenerationService()

@router.post("/generate", response_model=GeneratedAnalogyResponse)
async def generate_personalized_analogy(
    request: AnalogyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate a personalized analogy for a concept based on user's profession
    
    This is the core ConceptBridge feature that creates tailored explanations
    using AI to bridge the gap between what users know and what they want to learn.
    """
    try:
        # Validate profession exists
        profession = db.query(Profession).filter(Profession.id == request.profession_id).first()
        if not profession:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profession with ID {request.profession_id} not found"
            )
        
        # Validate topic exists
        topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {request.topic_id} not found"
            )
        
        # Get subtopic if specified
        subtopic = None
        if request.subtopic_id:
            subtopic = db.query(Subtopic).filter(Subtopic.id == request.subtopic_id).first()
            if not subtopic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Subtopic with ID {request.subtopic_id} not found"
                )
        
        # Determine what concept to explain
        concept_name = request.concept_name or (subtopic.name if subtopic else topic.name)
        concept_description = request.concept_description or (subtopic.description if subtopic else topic.description)
        
        # Create or get learning session
        session = db.query(LearningSession).filter(
            LearningSession.user_identifier == request.user_identifier,
            LearningSession.profession_id == request.profession_id,
            LearningSession.topic_id == request.topic_id,
            LearningSession.is_active == True
        ).first()
        
        if not session:
            session = LearningSession(
                user_identifier=request.user_identifier,
                profession_id=request.profession_id,
                topic_id=request.topic_id,
                subtopic_id=request.subtopic_id,
                is_active=True
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Generate analogy using AI
        logger.info(f"Generating analogy: {profession.name} -> {concept_name}")
        
        analogy_title, analogy_explanation, examples, generation_time = analogy_service.generate_analogy(
            profession=profession.name,
            concept_name=concept_name,
            concept_description=concept_description,
            topic_context=topic.name,
            difficulty_level=request.difficulty_preference,
            creativity_level=request.creative_level
        )
        
        # Store generated analogy
        generated_analogy = GeneratedAnalogy(
            session_id=session.id,
            concept_name=concept_name,
            concept_description=concept_description,
            analogy_title=analogy_title,
            analogy_explanation=analogy_explanation,
            analogy_examples=json.dumps([ex.dict() for ex in examples]) if examples else "[]",
            ai_model_used=analogy_service.model,
            generation_time_seconds=generation_time,
            prompt_template_version="v1.0"
        )
        
        db.add(generated_analogy)
        db.commit()
        db.refresh(generated_analogy)
        
        # Log success
        logger.info(f"Successfully generated analogy {generated_analogy.id} for session {session.id}")
        
        # Return response
        return GeneratedAnalogyResponse(
            analogy_id=generated_analogy.id,
            session_id=session.id,
            concept_name=concept_name,
            concept_description=concept_description,
            analogy_title=analogy_title,
            analogy_explanation=analogy_explanation,
            examples=examples,
            profession_context=profession.name,
            topic_context=topic.name,
            difficulty_level=request.difficulty_preference,
            ai_model_used=analogy_service.model,
            generation_time_seconds=generation_time,
            created_at=generated_analogy.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate analogy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analogy. Please try again."
        )

@router.post("/quick-explain", response_model=QuickAnalogyResponse)
async def quick_concept_explanation(request: ConceptExplanationRequest):
    """
    Generate a quick concept explanation without database storage
    
    Perfect for testing and rapid prototyping of analogies.
    Uses profession and concept directly without requiring database IDs.
    """
    try:
        logger.info(f"Quick explanation: {request.profession} -> {request.concept}")
        
        result = analogy_service.generate_quick_analogy(
            profession=request.profession,
            concept=request.concept,
            context=request.context or "",
            creativity_level=request.creativity_level
        )
        
        return QuickAnalogyResponse(**result)
        
    except Exception as e:
        logger.error(f"Quick explanation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quick explanation: {str(e)}"
        )

@router.get("/sessions/{user_identifier}", response_model=List[LearningSessionResponse])
async def get_user_sessions(user_identifier: str, db: Session = Depends(get_db)):
    """Get all learning sessions for a user"""
    try:
        sessions = db.query(LearningSession).filter(
            LearningSession.user_identifier == user_identifier
        ).order_by(LearningSession.session_start.desc()).all()
        
        response = []
        for session in sessions:
            analogies_count = db.query(GeneratedAnalogy).filter(
                GeneratedAnalogy.session_id == session.id
            ).count()
            
            response.append(LearningSessionResponse(
                session_id=session.id,
                user_identifier=session.user_identifier,
                profession_name=session.profession.name,
                topic_name=session.topic.name,
                subtopic_name=session.subtopic.name if session.subtopic else None,
                session_start=session.session_start,
                is_active=session.is_active,
                analogies_count=analogies_count
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user sessions"
        )

@router.get("/sessions/{session_id}/analogies", response_model=List[GeneratedAnalogyResponse])
async def get_session_analogies(session_id: int, db: Session = Depends(get_db)):
    """Get all analogies for a specific learning session"""
    try:
        session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning session {session_id} not found"
            )
        
        analogies = db.query(GeneratedAnalogy).filter(
            GeneratedAnalogy.session_id == session_id
        ).order_by(GeneratedAnalogy.created_at.desc()).all()
        
        response = []
        for analogy in analogies:
            examples = json.loads(analogy.analogy_examples) if analogy.analogy_examples else []
            
            response.append(GeneratedAnalogyResponse(
                analogy_id=analogy.id,
                session_id=analogy.session_id,
                concept_name=analogy.concept_name,
                concept_description=analogy.concept_description,
                analogy_title=analogy.analogy_title,
                analogy_explanation=analogy.analogy_explanation,
                examples=examples,
                profession_context=session.profession.name,
                topic_context=session.topic.name,
                difficulty_level="intermediate",  # Default for now
                ai_model_used=analogy.ai_model_used,
                generation_time_seconds=analogy.generation_time_seconds,
                created_at=analogy.created_at
            ))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session analogies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)