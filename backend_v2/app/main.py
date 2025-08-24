from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from .database import engine, get_db
from .models import Base
from .routers import professions
from .schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Backend V2 - ConceptBridge API",
    description="AI-Powered Adaptive Learning System Backend",
    version="2.0.0",
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
from .routers import topics
app.include_router(topics.router, prefix="/api/v1")

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
    """Root endpoint"""
    return {
        "message": "Backend V2 - ConceptBridge API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Checks API status and database connectivity
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
        message="Backend V2 API is running",
        database=db_status
    )

@app.get("/api/v1/health")
async def api_health():
    """API v1 health check"""
    return {"status": "healthy", "api_version": "v1"}