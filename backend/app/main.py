from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.endpoints import users

app = FastAPI(
    title="TeleWebManager API",
    description="API для управления пользователями TeleWebManager",
    version="1.0.0",
)

# Подключение CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ограничьте в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включение маршрутов
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])