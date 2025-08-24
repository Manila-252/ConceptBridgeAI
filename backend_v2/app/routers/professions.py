from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
from ..database import get_db
from ..models import Profession
from ..schemas import ProfessionResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/professions",
    tags=["professions"]
)

@router.get("/", response_model=List[ProfessionResponse])
async def get_professions(db: Session = Depends(get_db)):
    """
    Get all available professions
    
    Returns a list of all professions with their details including:
    - ID
    - Name  
    - Description
    - Creation timestamp
    - Last update timestamp
    """
    try:
        professions = db.query(Profession).order_by(Profession.id).all()
        logger.info(f"Retrieved {len(professions)} professions")
        return professions
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving professions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve professions from database"
        )

@router.get("/{profession_id}", response_model=ProfessionResponse)
async def get_profession(profession_id: int, db: Session = Depends(get_db)):
    """
    Get a specific profession by ID
    
    Args:
        profession_id: The unique identifier for the profession
        
    Returns:
        Profession details if found
        
    Raises:
        404: If profession with given ID doesn't exist
    """
    try:
        profession = db.query(Profession).filter(Profession.id == profession_id).first()
        if not profession:
            logger.warning(f"Profession with ID {profession_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Profession with ID {profession_id} not found"
            )
        
        logger.info(f"Retrieved profession: {profession.name}")
        return profession
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving profession {profession_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profession from database"
        )
