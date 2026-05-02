from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.router import api_router
from .services.data_store import initialize_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_store(months=12)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise-grade AI Performance & FinOps Intelligence Framework. "
        "Provides KPI analytics, AOVI scoring, ROI modeling, and executive insights "
        "for CIO-level AI governance and decision-making."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "platform": settings.APP_NAME,
    }
