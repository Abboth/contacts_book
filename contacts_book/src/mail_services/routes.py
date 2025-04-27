from fastapi import APIRouter, Depends, status, HTTPException, Request, Form, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from contacts_book.src.core.connection import get_db
from contacts_book.src.auth.security import auth_security
from contacts_book.src.users import repository as user_repository
from contacts_book.src.users.repository import get_user_by_email
from contacts_book.src.mail_services.schemas import UserVerifyingRequest
from contacts_book.src.mail_services.service import verification_letter, send_email
from contacts_book.src.mail_services import repository as mail_repository

router = APIRouter(tags=["Email_services"])

templates = Jinja2Templates(directory="templates")


@router.get("/confirm_email/{token}")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
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
                         db: AsyncSession = Depends(get_db)):
    user = await user_repository.get_user_by_email(str(body.email), db)

    if not user.is_verified:
        await verification_letter(user, str(request.base_url))
        return {"message": "Check your email for confirmation."}
    if user:
        return {"message": "Your email is already confirmed"}


@router.post('/reset_password')  # TODO CHANGE ARGUMENTS AND MAKE GOOD CHAIN
async def password_change_request(body: UserVerifyingRequest, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(str(body.email), db)
    if user:
        mail_type = "reset"
        send_email.delay(user.email, str(request.base_url), mail_type, db)
    return {"message": "Password reset form has been sent to your email."}


@router.patch("/reset_password/{token}")
async def password_change_response(
        token: str,
        new_password: str = Form(),
        repeat_password: str = Form(),
        db: AsyncSession = Depends(get_db)
):
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
    try:
        mail_id = await auth_security.decode_tracking_token(tracking_token)
        print(mail_id)
    except Exception:
        return FileResponse("contacts_book/src/statics/open_letter_indicator.png", media_type="image/png",
                            content_disposition_type="inline")
    await mail_repository.mark_letter_as_opened(mail_id, db)
    return FileResponse("contacts_book/src/statics/open_letter_indicator.png", media_type="image/png",
                            content_disposition_type="inline")
