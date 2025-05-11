from pydantic import BaseModel, EmailStr


class UserVerifyingRequest(BaseModel):
    email: EmailStr


