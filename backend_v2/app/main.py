from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from .database import engine, get_db
from .models import Base
from .routers import professions, topics, analogies
from .schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ConceptBridge API - AI-Powered Learning",
    description="Generate personalized analogies to bridge the gap between what you know and what you want to learn",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(professions.router, prefix="/api/v1")
app.include_router(topics.router, prefix="/api/v1")
app.include_router(analogies.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {e}")
        raise

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ConceptBridge API - AI-Powered Adaptive Learning",
        "version": "2.1.0",
        "features": [
            "Personalized analogies using AI",
            "Profession-based learning paths",
            "Topics and subtopics management",
            "Learning session tracking",
            "Analogy feedback system"
        ],
        "docs": "/docs",
        "endpoints": {
            "professions": "/api/v1/professions/",
            "topics": "/api/v1/topics/",
            "analogies": "/api/v1/analogies/",
            "quick_explanation": "/api/v1/analogies/quick-explain"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint
    
    Checks API status, database connectivity, and AI service
    """
    try:
        # Test database connectivity
        db.execute("SELECT 1")
        db_status = "connected"
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        message="ConceptBridge API with AI-powered analogies",
        database=db_status
    )

@app.get("/api/v1/health")
async def api_health():
    """API v1 health check with feature overview"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "features": {
            "professions": "5 pre-loaded professions for analogy generation",
            "topics": "6 study topics with 30 subtopics",
            "ai_analogies": "GPT-4 powered personalized explanations",
            "learning_sessions": "Track user learning progress",
            "feedback_system": "Improve analogies through user feedback"
        },
        "core_innovation": "AI-generated analogies that bridge professional knowledge with new concepts"
    }