from fastapi.middleware.cors import CORSMiddleware

from app import app as application

cors_middleware = CORSMiddleware(
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    app=application
)
