import src.core.models

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi_limiter import FastAPILimiter

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.connection import get_db
from src.auth.routes import router as auth_route
from src.mail_services.routes import router as service_route
from src.users.routes import router as user_route
from src.contacts.routes.contacts import router as contact_route
from src.contacts.routes.contact_emails import router as contact_email_route
from src.contacts.routes.contact_phones import router as contact_phone_route
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

app.include_router(user_route, prefix="/users", tags=["Users"])
app.include_router(auth_route, prefix="/auth", tags=["Authorization"])
app.include_router(contact_route, prefix="/contact", tags=["Contacts"])
app.include_router(contact_phone_route, prefix="/contact/phone", tags=["Phones"])
app.include_router(contact_email_route, prefix="/contact/email", tags=["Emails"])
app.include_router(service_route, prefix="/service", tags=["Email_services"])


@app.get("/")
def index():
    return {"message": "In development"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
