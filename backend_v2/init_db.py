import logging
import time
from app.database import SessionLocal, engine, create_db_engine
from app.models import Base, Profession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_db(max_retries=30, retry_delay=2):
    """Wait for database to be ready"""
    for attempt in range(max_retries):
        try:
            engine.connect()
            logger.info("✅ Database is ready!")
            return True
        except Exception as e:
            logger.info(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("❌ Database connection timeout")
                return False
    return False

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

def seed_professions():
    """Seed the database with initial professions"""
    db = SessionLocal()
    
    try:
        # Check if professions already exist
        existing_count = db.query(Profession).count()
        if existing_count > 0:
            logger.info(f"⚠️  Database already has {existing_count} professions. Skipping seed.")
            return True
        
        # Define the 5 initial professions based on your proposal
        professions_data = [
            {
                "name": "Cooking",
                "description": "Perfect for procedural thinking and step-by-step processes. Great for understanding algorithms through recipe analogies, cooking techniques, and kitchen workflows."
            },
            {
                "name": "Sports",
                "description": "Ideal for strategy, teamwork, and competitive algorithms. Perfect for game theory, optimization concepts, and performance analytics through athletic analogies."
            },
            {
                "name": "Gaming",
                "description": "Natural fit for data structures, progression systems, and interactive learning. Perfect for understanding complex systems through game mechanics and virtual worlds."
            },
            {
                "name": "Music",
                "description": "Great for patterns, sequences, and harmonic relationships. Perfect for understanding algorithms through musical compositions, rhythm, and sound processing."
            },
            {
                "name": "Business",
                "description": "Excellent for organizational structures and workflows. Ideal for database design, system architecture, and process optimization through corporate analogies."
            }
        ]
        
        # Create profession objects
        professions = [Profession(**data) for data in professions_data]
        
        # Add to database
        db.add_all(professions)
        db.commit()
        
        logger.info("✅ Successfully seeded 5 professions:")
        for profession in professions:
            logger.info(f"   - {profession.name}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error seeding professions: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_setup():
    """Verify that everything is set up correctly"""
    db = SessionLocal()
    try:
        count = db.query(Profession).count()
        professions = db.query(Profession).all()
        
        logger.info(f"📊 Database verification:")
        logger.info(f"   - Total professions: {count}")
        for prof in professions:
            logger.info(f"   - {prof.id}: {prof.name}")
            
        return count > 0
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function to initialize database"""
    logger.info("🚀 Initializing Backend V2 database...")
    
    # Wait for database to be ready
    if not wait_for_db():
        logger.error("💀 Database not ready, exiting...")
        return False
    
    # Create tables
    if not create_tables():
        logger.error("💀 Failed to create tables, exiting...")
        return False
    
    # Seed data
    if not seed_professions():
        logger.error("💀 Failed to seed professions, exiting...")
        return False
    
    # Verify setup
    if not verify_setup():
        logger.error("💀 Setup verification failed, exiting...")
        return False
    
    logger.info("🎉 Backend V2 database initialization completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)