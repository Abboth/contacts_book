import contacts_book.src.core.models

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.core.connection import get_db
from contacts_book.src.contacts.routes.contacts import router as contact_route
from contacts_book.src.contacts.routes.contact_emails import router as email_route
from contacts_book.src.contacts.routes.contact_phones import router as phone_route
from contacts_book.src.auth.routes import router as auth_route

app = FastAPI()

app.include_router(auth_route, prefix="/auth", tags=["Authorization"])

app.include_router(contact_route, prefix="/contact", tags=["Contacts"])
app.include_router(email_route, prefix="/contact/email", tags=["Emails"])
app.include_router(phone_route, prefix="/contact/phone", tags=["Phones"])


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
