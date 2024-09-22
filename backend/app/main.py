from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.endpoints import users
from backend.app.core.logger import setup_logger

logger = setup_logger()

app = FastAPI(
    title="TeleWebManager API",
    description="API for managing TeleWebManager users",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Limit the production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])