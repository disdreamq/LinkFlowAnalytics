from abc import ABC, abstractmethod
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from app.core.exceptions import AlreadyExistsException, ConnectionException, DatabaseException, IntegrityException, NotFoundException
from app.src.user.models import User
from app.src.user.schemas import SUserCreate

logger = logging.getLogger(__name__)

class abstract_repository(ABC):
    @abstractmethod
    async def create_user():
        raise NotImplementedError
    
    @abstractmethod
    async def get_user():
        raise NotImplementedError
    
    @abstractmethod
    async def update_user():
        raise NotImplementedError
    
    @abstractmethod
    async def delete_user():
        raise NotImplementedError

class user_repository(abstract_repository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: SUserCreate) -> User:
        try:
            if await self.get_user_by_email(user.email) is not None:
                raise AlreadyExistsException(message='User already exists.')

            user_to_add = User(**user.model_dump())
            self.session.add(user_to_add)
            await self.session.commit()
            return user_to_add

        except IntegrityError as e:
            logger.error(f"Integrity error while adding user: {str(e)}")
            raise IntegrityException(message="Data integrity error", detail=str(e))

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {str(e)}")
            raise ConnectionException(
                message="Database connection error",
                detail="Unable to retrieve user data",
            )

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {str(e)}")
            raise DatabaseException(
                message="Internal database error", detail="An unexpected error occurred"
            )

    async def get_user(self, user_id: int) -> Optional[User]:
        try:
            stmt = select(User).filter(User.id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return user

        except NoResultFound:
            raise NotFoundException(
                message='User not found.', 
                detail=f'User with id {id} does not exists.'
            )

        except IntegrityError as e:
            logger.error(f"Integrity error while getting user {user_id}: {str(e)}")
            raise IntegrityException(message="Data integrity error", detail=str(e))

        except SQLAlchemyError as e:
            logger.error(f"Database error while getting user {user_id}: {str(e)}")
            raise ConnectionException(
                message="Database connection error",
                detail="Unable to retrieve user data",
            )

        except Exception as e:
            logger.critical(f"Unexpected error while getting user {user_id}: {str(e)}")
            raise DatabaseException(
                message="Internal database error", detail="An unexpected error occurred"
            )

    async def get_user_by_email(self, email: str ):
        return 
