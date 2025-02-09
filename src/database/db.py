import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages database sessions using SQLAlchemy async engine.

    This class is responsible for creating and handling database sessions
    in an asynchronous environment.
    """

    def __init__(self, url: str):
        """
        Initializes the database session manager.

        Args:
            url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides an asynchronous context manager for database sessions.

        Yields:
            AsyncSession: The database session instance.

        Raises:
            Exception: If the session manager is not properly initialized.
            SQLAlchemyError: If an error occurs during session operations.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DATABASE_URL)


async def get_db():
    """
    Dependency function for retrieving a database session.

    Yields:
        AsyncSession: The database session instance.
    """
    async with sessionmanager.session() as session:
        yield session
