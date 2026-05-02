from fastapi import APIRouter
from .endpoints import analytics, finops, insights, teams

api_router = APIRouter()
api_router.include_router(analytics.router)
api_router.include_router(finops.router)
api_router.include_router(insights.router)
api_router.include_router(teams.router)
