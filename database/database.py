"""
Database connection and session management.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import settings
from database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str = None):
        """
        Initialize database manager.

        Args:
            database_url: Optional database URL override
        """
        self.database_url = database_url or settings.DATABASE_URL

        # Create engine
        if "sqlite" in self.database_url:
            # SQLite specific settings
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            # Other databases
            self.engine = create_engine(
                self.database_url,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=10,
            )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        logger.info(f"Database initialized: {self.database_url}")

    def create_all(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("All tables created")

    def drop_all(self):
        """Drop all tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All tables dropped")

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db() -> Session:
    """Get a database session for dependency injection."""
    db = get_db_manager().get_session()
    try:
        yield db
    finally:
        db.close()
