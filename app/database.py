from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import settings
try:
    from app.config import settings
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
except Exception as e:
    logger.warning(f"Could not load settings: {e}")
    SQLALCHEMY_DATABASE_URL = "postgresql://consultation_user:consultation_pass@postgres:5432/consultation_platform"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Disable SQL logging for now
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    try:
        logger.info("📋 Creating database tables...")

        # Import models to register them
        try:
            from app.models import (
                User,
                UserProfile,
                ActivityLog,
                Consultant,
                ConsultationCategory,
                ConsultationRequest,
                ConsultationSession,
                Wallet,
                Transaction,
                PaymentMethod,
                Rating,
                Review,
                ReviewHelpful,
            )
            logger.info("✅ Models imported successfully")
        except Exception as e:
            logger.error(f"❌ Failed to import models: {e}")
            raise

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"📊 Created tables: {sorted(tables)}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False