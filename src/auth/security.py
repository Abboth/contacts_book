import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt, ExpiredSignatureError

from src.core import message
from src.core.connection import get_db
from src.core.config import configuration
from src.services.redis_service import redis_manager
from src.users import repository as user_repository
from src.users.models import User

logging.basicConfig(level=logging.INFO)


class Auth:
    """
    Security service for handling authentication and authorization operations.

    Responsibilities:
    - Password hashing and verification
    - JWT access/refresh/email/tracking token creation and decoding
    - Retrieving the current user from token
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    SECRET_KEY = configuration.SECRET_KEY_JWT
    ALGORITHM = configuration.ALGORITHM

    def verify_password(self, plain_password: str, hashed_password: str):
        """
        Verify that the provided plain password matches the hashed password.

        :param plain_password: Raw password from user input
        :type plain_password: str
        :param hashed_password: Hashed password from the database
        :type hashed_password: str
        :return: True if passwords match, otherwise False
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a hashed password using the configured algorithm.

        :param password: Raw password to hash
        :type password: str
        :return: Hashed password as string
        :rtype: str
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Create a JWT access token with an optional expiration.

        :param data: Payload data to encode in the token
        :type data: dict
        :param expires_delta: Expiration time in seconds (optional)
        :type expires_delta: float | None
        :return: Encoded JWT access token
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(), "exp": expire, "scope": "access_token", "jti": str(uuid.uuid4())})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> dict:
        """
        Create a JWT refresh token with an optional expiration.

        :param data: Payload data to encode in the token
        :type data: dict
        :param expires_delta: Expiration time in seconds (optional)
        :type expires_delta: float | None
        :return: Dictionary with token and expiration timestamp
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(days=7)
        to_encode.update({"iat": datetime.now(), "exp": expire, "scope": "refresh_token", "jti": str(uuid.uuid4())})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return {"token": encoded_refresh_token, "expires_at": expire}

    async def create_email_token(self, data: dict) -> str:
        """
        Create a token for email verification purposes.

        :param data: Payload data to encode in the token
        :type data: dict
        :return: Encoded JWT token for email verification
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=7)
        to_encode.update({"iat": datetime.now(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Extract the email (subject) from a given email verification token.

        :param token: JWT token to decode
        :return: Email address (subject)
        :rtype: str
        :raises HTTPException: If token is invalid or malformed
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as err:
            logging.info(err)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decode and validate a refresh token.

        :param refresh_token: JWT refresh token
        :type refresh_token: str
        :return: Email (subject) from the token
        :rtype: str
        :raises HTTPException: If the token is invalid, expired, or has incorrect scope
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message.INVALID_TOKEN_SCOPE)
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message.EXPIRED_TOKEN)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message.BAD_CREDENTIALS)

    async def create_tracking_token(self, mail_id: str) -> str:
        """
        Create a token for tracking mail activity.

        :param mail_id: Identifier of the mail to track
        :type mail_id: str
        :return: Encoded JWT token
        :rtype: str
        """
        payload = {"mail_id": mail_id}
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def decode_tracking_token(self, token: str) -> str | None:
        """
        Decode a tracking token and extract the mail ID.

        :param token: JWT token to decode
        :type token: str
        :return: Mail ID or None if invalid
        :rtype: str | None
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload["mail_id"]
        except JWTError as err:
            logging.info(err)
            return None

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        """
        Retrieve the current authenticated user using the access token.

        :param token: Access token from the Authorization header
        :type token: str
        :param db: The database session.
        :type db: AsyncSession
        :return: User object
        :rtype: User
        :raises HTTPException: If token is invalid, expired, or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = await redis_manager.get_obj(f"user:{email}")

        if not user:
            logging.info("im from database")
            user = await user_repository.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await redis_manager.set_obj(f"user:{email}", user, ex=300)
        else:
            logging.info("im from cache")
        return user


auth_security = Auth()
get_refresh_token = HTTPBearer()


class AccessLevel(str, Enum):
    """
    Enum representing user access levels.
    """
    admin = "admin"
    moderator = "moderator"
    public = "public"


class RoleVerification:
    """
    Dependency class for route-level role-based access control.

    :param allowed_roles: List of role names allowed to access the route
    :type allowed_roles: list[str]
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_security.get_current_user)):
        """
        Validate that the current user has one of the allowed roles.

        :param request: Request object
        :type request: Request
        :param current_user: Injected user from token
        :type current_user: User
        :raises HTTPException: If user's role is not allowed
        """
        if current_user.role.role_name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message.FORBIDDEN
            )


access = {
    AccessLevel.public: RoleVerification(["admin", "moderator", "user"]),
    AccessLevel.moderator: RoleVerification(["admin", "moderator"]),
    AccessLevel.admin: RoleVerification(["admin"]),
}
