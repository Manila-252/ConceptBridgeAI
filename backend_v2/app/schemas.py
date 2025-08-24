from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

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

class HealthResponse(BaseModel):
    status: str
    message: str
    database: str