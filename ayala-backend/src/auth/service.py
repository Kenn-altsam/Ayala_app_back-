from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt
from uuid import UUID

from src.core.config import settings
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, user_id: UUID) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "exp": expire.timestamp()
        }
        return jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
        google_id: Optional[str] = None
    ) -> User:
        hashed_password = self.get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
            google_id=google_id
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_last_login(self, user: User) -> None:
        user.last_login = datetime.utcnow()
        await self.session.commit()

    async def create_password_reset_token(self, user: User) -> str:
        # Create a password reset token that expires in 24 hours
        expire = datetime.utcnow() + timedelta(hours=24)
        token = jwt.encode(
            {"user_id": str(user.id), "exp": expire.timestamp()},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        user.password_reset_token = token
        user.password_reset_expires = expire
        await self.session.commit()
        
        return token

    async def verify_password_reset_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("user_id")
            exp = payload.get("exp")
            
            if not user_id or not exp:
                return None
                
            if datetime.utcnow().timestamp() > exp:
                return None
                
            user = await self.get_user_by_id(user_id)
            if not user or user.password_reset_token != token:
                return None
                
            return user
            
        except jwt.JWTError:
            return None

    async def reset_password(self, user: User, new_password: str) -> None:
        user.hashed_password = self.get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await self.session.commit() 