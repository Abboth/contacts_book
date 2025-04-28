from typing import Optional

from pydantic import BaseModel, EmailStr


class UserVerifyingRequest(BaseModel):
    email: EmailStr


class EmailTemplateSchema(BaseModel):
    subject: str
    template_name: str
    params: Optional[dict]
