import contacts_book.src.core.models

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from contacts_book.src.core.connection import get_db
from contacts_book.src.auth.routes import router as auth_route
from contacts_book.src.mail_services.routes import router as service_route

app = FastAPI()

app.mount("/statics", StaticFiles(directory="contacts_book/src/statics"), name="statics")

app.include_router(auth_route, prefix="/auth", tags=["Authorization"])

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
