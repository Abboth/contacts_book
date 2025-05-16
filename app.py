import src.core.models

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi_limiter import FastAPILimiter

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.connection import get_db
from src.core import message
from src.auth.routes import router as auth_route
from src.mail_services.routes import router as service_route
from src.users.routes import router as user_route
from src.contacts.routes.contacts import router as contact_route
from src.contacts.routes.contact_emails import router as contact_email_route
from src.contacts.routes.contact_phones import router as contact_phone_route
from src.admin.posts.routes import router as admin_post_route
from src.admin.comments.routes import router as admin_comment_route
from src.admin.users.routes import router as admin_user_route
from src.posts.routes.post_routes import router as post_route
from src.posts.routes.comments_routes import router as comments_route
from src.services.redis_service import redis_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    await FastAPILimiter.init(redis_manager)
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)


BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("statics")

app.mount("/statics", StaticFiles(directory=directory), name="statics")

app.include_router(post_route, prefix="/post", tags=["Posts"])
app.include_router(user_route, prefix="/users", tags=["Users"])
app.include_router(auth_route, prefix="/auth", tags=["Authorization"])
app.include_router(contact_route, prefix="/contact", tags=["Contacts"])
app.include_router(admin_post_route, prefix="/staff", tags=["Staff manage panel"])
app.include_router(admin_comment_route, prefix="/staff", tags=["Staff manage panel"])
app.include_router(admin_user_route, prefix="/staff", tags=["Staff manage panel"])
app.include_router(service_route, prefix="/service", tags=["Email services"])
app.include_router(contact_phone_route, prefix="/contact/phone", tags=["Phones"])
app.include_router(contact_email_route, prefix="/contact/email", tags=["Emails"])
app.include_router(comments_route, prefix="/post", tags=["Comments"])


@app.get("/")
def index():
    return {"message": "In development"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail=message.INCORRECT_DB_CONFIGURATION)
        return {"message": "Welcome to FastAPI!"}
    except Exception:
        raise HTTPException(status_code=500, detail=message.DB_CONNECTION_ERROR)
