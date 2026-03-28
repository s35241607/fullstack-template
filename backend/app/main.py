from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all models so SQLAlchemy registers them before create_all
import app.infrastructure.database.models.item_model  # noqa: F401
import app.infrastructure.database.models.process_definition_model  # noqa: F401
import app.infrastructure.database.models.process_instance_model  # noqa: F401
import app.infrastructure.database.models.procurement_plan_model  # noqa: F401
from app.infrastructure.database.session import Base, engine, wait_for_db
from app.interfaces.api.v1.routers import bpmn_router, item_router, procurement_plan_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await wait_for_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Backend API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(item_router.router, prefix="/api/v1")
app.include_router(bpmn_router.router, prefix="/api/v1")
app.include_router(procurement_plan_router.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}
