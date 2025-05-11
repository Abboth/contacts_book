from pydantic import BaseModel, ConfigDict


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    device_type: str

    model_config = ConfigDict(from_attributes=True)
