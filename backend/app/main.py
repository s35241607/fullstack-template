from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.notification import router as notification_router
from app.core.config import settings
from app.core.database import Base, engine, wait_for_db
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestLogMiddleware

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Ensure database is ready
    await wait_for_db()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Middlewares
app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Register routers
app.include_router(notification_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.APP_NAME}"}
