import logging
import time
from app.database import SessionLocal, engine, create_db_engine
from app.models import Base, Profession, Topic, Subtopic

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
        
        # Define the 5 initial professions
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
        
        logger.info("✅ Successfully seeded 5 professions")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error seeding professions: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def seed_topics():
    """Seed the database with study topics"""
    db = SessionLocal()
    
    try:
        # Check if topics already exist
        existing_count = db.query(Topic).count()
        if existing_count > 0:
            logger.info(f"⚠️  Database already has {existing_count} topics. Skipping seed.")
            # Still need to return topic_dict for subtopic seeding
            topics = db.query(Topic).all()
            topic_dict = {topic.name: topic.id for topic in topics}
            return True, topic_dict
        
        # Define the 6 study topics
        topics_data = [
            {
                "name": "Computer Science",
                "description": "Programming, algorithms, data structures, software engineering, and computational thinking",
                "icon": "💻",
                "color": "#3B82F6"
            },
            {
                "name": "Mathematics",
                "description": "Algebra, calculus, statistics, discrete math, and mathematical reasoning",
                "icon": "🔢",
                "color": "#10B981"
            },
            {
                "name": "Physics",
                "description": "Classical mechanics, quantum physics, thermodynamics, and natural phenomena",
                "icon": "⚛️",
                "color": "#8B5CF6"
            },
            {
                "name": "Spaceships",
                "description": "Rocket science, orbital mechanics, spacecraft design, and space exploration",
                "icon": "🚀",
                "color": "#EF4444"
            },
            {
                "name": "Comics",
                "description": "Storytelling, character development, visual narrative, and creative expression",
                "icon": "💥",
                "color": "#F59E0B"
            },
            {
                "name": "Law",
                "description": "Legal principles, constitutional law, contracts, and judicial reasoning",
                "icon": "⚖️",
                "color": "#6B7280"
            }
        ]
        
        # Create topic objects
        topics = [Topic(**data) for data in topics_data]
        
        # Add to database
        db.add_all(topics)
        db.commit()
        
        # Refresh objects to get their IDs
        for topic in topics:
            db.refresh(topic)
        
        # Create topic_dict for subtopic creation
        topic_dict = {topic.name: topic.id for topic in topics}
        
        logger.info("✅ Successfully seeded 6 topics")
        return True, topic_dict
        
    except Exception as e:
        logger.error(f"❌ Error seeding topics: {e}")
        db.rollback()
        return False, {}
    finally:
        db.close()

def seed_subtopics(topic_dict):
    """Seed the database with subtopics for each topic"""
    db = SessionLocal()
    
    try:
        # Check if subtopics already exist
        existing_count = db.query(Subtopic).count()
        if existing_count > 0:
            logger.info(f"⚠️  Database already has {existing_count} subtopics. Skipping seed.")
            return True
        
        # Define subtopics for each topic (4-5 per topic)
        subtopics_data = {
            "Computer Science": [
                {"name": "Data Structures", "description": "Arrays, linked lists, trees, graphs, and hash tables", "difficulty_level": "beginner", "estimated_time_minutes": 45},
                {"name": "Algorithms", "description": "Sorting, searching, dynamic programming, and optimization", "difficulty_level": "intermediate", "estimated_time_minutes": 60},
                {"name": "Object-Oriented Programming", "description": "Classes, objects, inheritance, and polymorphism", "difficulty_level": "beginner", "estimated_time_minutes": 40},
                {"name": "Database Design", "description": "Relational databases, SQL, normalization, and indexing", "difficulty_level": "intermediate", "estimated_time_minutes": 50},
                {"name": "System Design", "description": "Scalability, distributed systems, and architecture patterns", "difficulty_level": "advanced", "estimated_time_minutes": 90}
            ],
            "Mathematics": [
                {"name": "Linear Algebra", "description": "Vectors, matrices, eigenvalues, and transformations", "difficulty_level": "intermediate", "estimated_time_minutes": 60},
                {"name": "Calculus", "description": "Derivatives, integrals, limits, and applications", "difficulty_level": "intermediate", "estimated_time_minutes": 75},
                {"name": "Statistics", "description": "Probability, distributions, hypothesis testing, and regression", "difficulty_level": "beginner", "estimated_time_minutes": 45},
                {"name": "Discrete Mathematics", "description": "Logic, sets, combinatorics, and graph theory", "difficulty_level": "beginner", "estimated_time_minutes": 50},
                {"name": "Number Theory", "description": "Prime numbers, modular arithmetic, and cryptography", "difficulty_level": "advanced", "estimated_time_minutes": 65}
            ],
            "Physics": [
                {"name": "Classical Mechanics", "description": "Newton's laws, motion, energy, and momentum", "difficulty_level": "beginner", "estimated_time_minutes": 55},
                {"name": "Thermodynamics", "description": "Heat, temperature, entropy, and energy transfer", "difficulty_level": "intermediate", "estimated_time_minutes": 50},
                {"name": "Electromagnetism", "description": "Electric fields, magnetic fields, and electromagnetic waves", "difficulty_level": "intermediate", "estimated_time_minutes": 65},
                {"name": "Quantum Mechanics", "description": "Wave-particle duality, uncertainty principle, and quantum states", "difficulty_level": "advanced", "estimated_time_minutes": 80},
                {"name": "Relativity", "description": "Special and general relativity, spacetime, and gravity", "difficulty_level": "advanced", "estimated_time_minutes": 70}
            ],
            "Spaceships": [
                {"name": "Rocket Propulsion", "description": "Thrust, fuel systems, and rocket equation", "difficulty_level": "beginner", "estimated_time_minutes": 40},
                {"name": "Orbital Mechanics", "description": "Kepler's laws, orbits, and spacecraft trajectories", "difficulty_level": "intermediate", "estimated_time_minutes": 55},
                {"name": "Spacecraft Design", "description": "Structure, thermal control, and life support systems", "difficulty_level": "intermediate", "estimated_time_minutes": 60},
                {"name": "Mission Planning", "description": "Launch windows, delta-v budgets, and trajectory optimization", "difficulty_level": "advanced", "estimated_time_minutes": 70},
                {"name": "Space Exploration", "description": "Planetary missions, deep space probes, and space telescopes", "difficulty_level": "beginner", "estimated_time_minutes": 35}
            ],
            "Comics": [
                {"name": "Visual Storytelling", "description": "Panel layouts, page composition, and visual flow", "difficulty_level": "beginner", "estimated_time_minutes": 30},
                {"name": "Character Design", "description": "Creating memorable characters, costumes, and visual identity", "difficulty_level": "beginner", "estimated_time_minutes": 40},
                {"name": "Narrative Structure", "description": "Story arcs, pacing, dialogue, and plot development", "difficulty_level": "intermediate", "estimated_time_minutes": 45},
                {"name": "Art Techniques", "description": "Drawing, inking, coloring, and digital art tools", "difficulty_level": "intermediate", "estimated_time_minutes": 60},
                {"name": "Publishing & Distribution", "description": "Industry insights, self-publishing, and marketing comics", "difficulty_level": "advanced", "estimated_time_minutes": 50}
            ],
            "Law": [
                {"name": "Constitutional Law", "description": "Bill of rights, separation of powers, and judicial review", "difficulty_level": "beginner", "estimated_time_minutes": 50},
                {"name": "Contract Law", "description": "Formation, performance, breach, and remedies", "difficulty_level": "beginner", "estimated_time_minutes": 45},
                {"name": "Criminal Law", "description": "Elements of crimes, defenses, and criminal procedure", "difficulty_level": "intermediate", "estimated_time_minutes": 55},
                {"name": "Civil Procedure", "description": "Court systems, litigation process, and legal procedures", "difficulty_level": "intermediate", "estimated_time_minutes": 60},
                {"name": "Legal Research", "description": "Case law, statutes, legal databases, and citation", "difficulty_level": "advanced", "estimated_time_minutes": 40}
            ]
        }
        
        all_subtopics = []
        
        # Create subtopic objects for each topic
        for topic_name, subtopics_list in subtopics_data.items():
            topic_id = topic_dict.get(topic_name)
            if topic_id:
                for subtopic_data in subtopics_list:
                    subtopic = Subtopic(
                        topic_id=topic_id,
                        **subtopic_data
                    )
                    all_subtopics.append(subtopic)
        
        # Add to database
        db.add_all(all_subtopics)
        db.commit()
        
        logger.info(f"✅ Successfully seeded {len(all_subtopics)} subtopics across 6 topics")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error seeding subtopics: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_setup():
    """Verify that everything is set up correctly"""
    db = SessionLocal()
    try:
        profession_count = db.query(Profession).count()
        topic_count = db.query(Topic).count()
        subtopic_count = db.query(Subtopic).count()
        
        logger.info(f"📊 Database verification:")
        logger.info(f"   - Total professions: {profession_count}")
        logger.info(f"   - Total topics: {topic_count}")
        logger.info(f"   - Total subtopics: {subtopic_count}")
        
        # Show topics with subtopic counts
        topics = db.query(Topic).all()
        for topic in topics:
            sub_count = db.query(Subtopic).filter(Subtopic.topic_id == topic.id).count()
            logger.info(f"   - {topic.name}: {sub_count} subtopics")
            
        return profession_count > 0 and topic_count > 0 and subtopic_count > 0
        
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
    
    # Seed professions
    if not seed_professions():
        logger.error("💀 Failed to seed professions, exiting...")
        return False
    
    # Seed topics - Fixed return value handling
    result = seed_topics()
    if isinstance(result, tuple):
        success, topic_dict = result
    else:
        success = result
        topic_dict = {}
    
    if not success:
        logger.error("💀 Failed to seed topics, exiting...")
        return False
    
    # Seed subtopics only if we have topic_dict
    if topic_dict:
        if not seed_subtopics(topic_dict):
            logger.error("💀 Failed to seed subtopics, exiting...")
            return False
    else:
        logger.info("⚠️  No topic_dict available, skipping subtopic seeding")
    
    # Verify setup
    if not verify_setup():
        logger.error("💀 Setup verification failed, exiting...")
        return False
    
    logger.info("🎉 Backend V2 database initialization completed successfully!")
    logger.info("🎯 Ready for milestone 2: Topics and Subtopics API")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)