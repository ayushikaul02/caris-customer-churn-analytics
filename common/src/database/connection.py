from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from common.src.database.schema import Base
from common.src.config.config import DATABASE_URL


class DatabaseManager:
    def __init__(self, db_url=None):
        self.db_url = db_url or DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.db_url, poolclass=QueuePool, pool_size=10, max_overflow=20, pool_pre_ping=True)
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            print("Database connection established successfully")
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_session_sync(self):
        """Get database session directly"""
        return self.SessionLocal()

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()


# Singleton instance
db_manager = DatabaseManager()
