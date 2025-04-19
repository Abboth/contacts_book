from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from bdaybot.src.bd_connect.database.connection import get_db
from bdaybot.src.routes.contacts import router as contact_route
from bdaybot.src.routes.contact_emails import router as email_route
from bdaybot.src.routes.contact_phones import router as phone_route

app = FastAPI()

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
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
