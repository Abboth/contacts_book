from fastapi import APIRouter, HTTPException, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from bdaybot.src.bd_connect.database.connection import get_db
from bdaybot.src.repository import bday_bot as repositories
from bdaybot.src.schemas.request_schema import AddEmailSchema, EmailUpdateSchema
from bdaybot.src.schemas.response_schema import EmailResponseSchema

router = APIRouter(tags=["Emails"])


@router.post("/{contact_id}", response_model=EmailResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_email(body: AddEmailSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    try:
        person_email = await repositories.add_email(body, contact_id, db)
        return person_email
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{contact_id}/tag/{tag}", response_model=EmailResponseSchema)
async def update_email(body: EmailUpdateSchema, contact_id: int = Path(ge=1), tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db)):
    try:
        person_email = await repositories.update_email(body, contact_id, tag, db)
        return person_email
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
