from fastapi.middleware.cors import CORSMiddleware
from theregram_proj.app import app as application




cors_middleware = CORSMiddleware(
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    app=application
)

