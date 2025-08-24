# app/routers/analogies.py
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
        logger.info(f"Generating analogy: {profession.name} -> {concept_name} (tokens: {request.max_tokens}, format: {request.response_format})")
        
        analogy_title, analogy_explanation, examples, generation_time = analogy_service.generate_analogy(
            profession=profession.name,
            concept_name=concept_name,
            concept_description=concept_description,
            topic_context=topic.name,
            difficulty_level=request.difficulty_preference,
            creativity_level=request.creative_level,
            max_tokens=request.max_tokens,
            response_format=request.response_format
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
            detail="Failed to retrieve session analogies"
        )

@router.post("/feedback", response_model=dict)
async def submit_analogy_feedback(feedback: AnalogyFeedback, db: Session = Depends(get_db)):
    """
    Submit user feedback on a generated analogy
    
    This helps improve future analogy generation by learning what works well.
    """
    try:
        analogy = db.query(GeneratedAnalogy).filter(GeneratedAnalogy.id == feedback.analogy_id).first()
        if not analogy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analogy {feedback.analogy_id} not found"
            )
        
        # Update analogy with feedback
        analogy.user_rating = feedback.user_rating
        
        # Calculate understanding score based on rating and feedback
        understanding_score = feedback.user_rating / 5.0
        if feedback.understanding_improved:
            understanding_score = min(understanding_score + 0.2, 1.0)
        
        analogy.understanding_score = understanding_score
        
        db.commit()
        
        logger.info(f"Received feedback for analogy {feedback.analogy_id}: {feedback.user_rating}/5 stars")
        
        return {
            "message": "Feedback submitted successfully",
            "analogy_id": feedback.analogy_id,
            "rating": feedback.user_rating,
            "understanding_score": understanding_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )

@router.get("/analytics/popular-combinations", response_model=List[dict])
async def get_popular_analogy_combinations(db: Session = Depends(get_db)):
    """
    Get analytics on most popular profession-topic combinations
    
    Useful for understanding which analogies work best and for what audiences.
    """
    try:
        from sqlalchemy import func
        
        query = db.query(
            Profession.name.label("profession"),
            Topic.name.label("topic"),
            func.count(GeneratedAnalogy.id).label("analogy_count"),
            func.avg(GeneratedAnalogy.user_rating).label("avg_rating"),
            func.avg(GeneratedAnalogy.understanding_score).label("avg_understanding")
        ).join(
            LearningSession, GeneratedAnalogy.session_id == LearningSession.id
        ).join(
            Profession, LearningSession.profession_id == Profession.id
        ).join(
            Topic, LearningSession.topic_id == Topic.id
        ).group_by(
            Profession.name, Topic.name
        ).order_by(
            func.count(GeneratedAnalogy.id).desc()
        ).limit(20).all()
        
        results = []
        for row in query:
            results.append({
                "profession": row.profession,
                "topic": row.topic,
                "analogy_count": row.analogy_count,
                "average_rating": round(float(row.avg_rating or 0), 2),
                "average_understanding_score": round(float(row.avg_understanding or 0), 2)
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get analogy analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

@router.get("/examples", response_model=List[dict])
async def get_analogy_examples():
    """
    Get example analogies for demo purposes
    
    Shows the power of ConceptBridge with pre-crafted examples
    """
    examples = [
        {
            "profession": "Gaming",
            "concept": "Recursion",
            "analogy_title": "Recursion is Like Dungeon Crawling with Nested Instances",
            "preview": "Just like how some RPGs have dungeons that contain smaller dungeons, recursion is a function that calls itself to solve smaller versions of the same problem...",
            "difficulty": "intermediate",
            "rating": 4.8
        },
        {
            "profession": "Cooking",
            "concept": "Binary Trees",
            "analogy_title": "Binary Trees are Like Recipe Organization Systems",
            "preview": "Imagine organizing your recipes where each main category can only have two subcategories - like 'Quick Meals' splitting into 'Under 15 min' and 'Under 30 min'...",
            "difficulty": "beginner",
            "rating": 4.6
        },
        {
            "profession": "Sports",
            "concept": "Hash Tables",
            "analogy_title": "Hash Tables Work Like Team Position Assignments",
            "preview": "Think of assigning players to positions using their jersey numbers. A hash function is like a formula that determines which position a player goes to...",
            "difficulty": "intermediate",
            "rating": 4.5
        },
        {
            "profession": "Music",
            "concept": "Dynamic Programming",
            "analogy_title": "Dynamic Programming is Like Building Musical Arrangements",
            "preview": "When composing a symphony, you don't rewrite the entire piece every time. You build upon previous sections, reusing themes and motifs...",
            "difficulty": "advanced",
            "rating": 4.9
        },
        {
            "profession": "Business",
            "concept": "Graph Traversal",
            "analogy_title": "Graph Traversal is Like Organizational Network Analysis",
            "preview": "Imagine mapping out how information flows through your company. Graph traversal algorithms are like systematic ways to visit every department...",
            "difficulty": "intermediate",
            "rating": 4.4
        }
    ]
    
    return examples

@router.get("/health", response_model=dict)
async def analogy_service_health():
    """Health check for the analogy generation service"""
    try:
        # Test AI service
        test_result = analogy_service.generate_quick_analogy(
            profession="gaming",
            concept="test",
            creativity_level=1
        )
        
        ai_status = "healthy" if test_result else "unhealthy"
        
        return {
            "status": "healthy",
            "ai_service": ai_status,
            "model": analogy_service.model,
            "supported_professions": list(analogy_service.profession_contexts.keys())
        }
        
    except Exception as e:
        logger.error(f"Analogy service health check failed: {e}")
        return {
            "status": "unhealthy",
            "ai_service": "unhealthy",
            "error": str(e)
        },
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
        logger.info(f"Quick explanation: {request.profession} -> {request.concept} (tokens: {request.max_tokens}, length: {request.response_length})")
        
        result = analogy_service.generate_quick_analogy(
            profession=request.profession,
            concept=request.concept,
            context=request.context or "",
            creativity_level=request.creativity_level,
            max_tokens=request.max_tokens,
            response_length=request.response_length
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