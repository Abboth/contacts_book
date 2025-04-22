import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-unsafe-key")
    DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/bday_bot_DB"


configuration = Config