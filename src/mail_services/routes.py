from fastapi import APIRouter, Depends, status, HTTPException, Request, Form, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from src.core.connection import get_db
from src.auth.security import auth_security
from src.mail_services.prepare_letters_template import prepare_email_verification, prepare_password_reset
from src.users import repository as user_repository
from src.users.repository import get_user_by_email
from src.mail_services.schemas import UserVerifyingRequest
from src.mail_services import repository as mail_repository

router = APIRouter(tags=["Email_services"])

templates = Jinja2Templates(directory="templates")


@router.get("/confirm_email/{token}")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Confirm a user's email using the verification token.

    :param token: JWT token used for email verification.
    :type token: str
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Message indicating the result of verification.
    :rtype: dict
    """

    email = await auth_security.get_email_from_token(token)
    user = await user_repository.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.is_verified:
        return {"message": "Your email is already confirmed"}
    await user_repository.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/verify_request")
async def verify_request(body: UserVerifyingRequest, request: Request,
                         db: AsyncSession = Depends(get_db)) -> dict:
    """
    Initiate email verification process for unverified user.

    :param body: Request body containing user's email.
    :type body: UserVerifyingRequest
    :param request: FastAPI request object to extract base URL.
    :type request: Request
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Message indicating verification email was sent or already confirmed.
    :rtype: dict
    """

    user = await user_repository.get_user_by_email(str(body.email), db)

    if user and not user.is_verified:
        await prepare_email_verification(user, str(request.base_url), db)
        return {"message": "Check your email for confirmation."}

    return {"message": "Your email is already confirmed"}


@router.post('/reset_password')
async def password_change_request(body: UserVerifyingRequest, request: Request,
                                  db: AsyncSession = Depends(get_db)) -> dict:
    """
    Initiate password reset process by sending reset form to user's email.

    :param body: Request body with the user's email.
    :type body: UserVerifyingRequest
    :param request: FastAPI request object to extract base URL.
    :type request: Request
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Message indicating the result of password reset request.
    :rtype: dict
    """

    user = await get_user_by_email(str(body.email), db)
    if user:
        await prepare_password_reset(user, str(request.base_url), db)
    return {"message": "Password reset form has been sent to your email."}


@router.patch("/reset_password/{token}")
async def password_change_response(token: str, new_password: str = Form(), repeat_password: str = Form(),
                                   db: AsyncSession = Depends(get_db)) -> dict:
    """
    Reset user's password using token from email.

    :param token: JWT token for password reset.
    :type token: str
    :param new_password: New password provided by the user.
    :type new_password: str
    :param repeat_password: Repeated password to confirm match.
    :type repeat_password: str
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Message indicating the result of the password reset.
    :rtype: dict
    """

    email = await auth_security.get_email_from_token(token)
    user = await user_repository.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if new_password != repeat_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    hashed_pwd = auth_security.get_password_hash(new_password)
    await user_repository.change_password(email, hashed_pwd, db)
    return {"message": "Password successfully changed"}


@router.get("/mark_open/{tracking_token}")
async def open_letter_marker(tracking_token: str, db: AsyncSession = Depends(get_db)):
    """
    Mark a letter as opened using a tracking token.

    :param tracking_token: Encoded token containing letter ID.
    :type tracking_token: str
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Transparent PNG image indicating the tracking pixel.
    :rtype: FileResponse
    """

    try:
        mail_id = await auth_security.decode_tracking_token(tracking_token)
        print(mail_id)
    except HTTPException:
        return FileResponse("src/statics/open_letter_indicator.png", media_type="image/png",
                            content_disposition_type="inline")
    await mail_repository.mark_letter_as_opened(mail_id, db)
    return FileResponse("src/statics/open_letter_indicator.png", media_type="image/png",
                        content_disposition_type="inline")
