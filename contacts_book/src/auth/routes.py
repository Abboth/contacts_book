from fastapi import Security, Depends, HTTPException, status, APIRouter, Request
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.auth.services import get_user_device
from contacts_book.src.core.connection import get_db
from contacts_book.src.auth.schemas import TokenSchema  # TODO
from contacts_book.src.auth import repository as auth_repository
from contacts_book.src.users import repository as user_repository
from contacts_book.src.users.models import User
from contacts_book.src.users.schemas import UserResponseSchema, UserSchema  # TODO
from contacts_book.src.auth.security import auth_security

router = APIRouter(tags=["Authorization"])


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    exist_user = await user_repository.get_user_by_email(str(body.email), db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_security.get_password_hash(body.password)
    new_user = await user_repository.create_new_user(body, db)
    return new_user


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(),
                request: Request = None,
                db: AsyncSession = Depends(get_db)):
    user = await user_repository.get_user_by_email(str(body.username), db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_security.verify_password(body.password, user.hashed_pwd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    user_agent = request.headers.get("user-agent")
    user_device = await get_user_device(user_agent)

    access_token = await auth_security.create_access_token(data={"sub": user.email})
    refresh_token_data = await auth_security.create_refresh_token(data={"sub": user.email})

    refresh_token = refresh_token_data["token"]
    expires_at = refresh_token_data["expires_at"]

    await auth_repository.update_token(user, user_device, refresh_token, expires_at, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "device_type": user_device
    }
#
#
# @router.get('/refresh_token')
# async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(), db: AsyncSession = Depends(get_db)):
#     token = credentials.credentials
#     email = await auth_security.decode_refresh_token(token)
#     user = db.query(User).filter(User.email == email).first()
#     if user.refresh_token != token:
#         user.refresh_token = None
#         db.commit()
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
#
#     access_token = await auth_security.create_access_token(data={"sub": email})
#     refresh_token = await auth_security.create_refresh_token(data={"sub": email})
#     user.refresh_token = refresh_token
#     db.commit()
#     return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
