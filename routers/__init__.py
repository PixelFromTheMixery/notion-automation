from routers.v1 import general_router, notion_router

from fastapi import APIRouter

v1_router = APIRouter()

v1_router.include_router(general_router.router, prefix="/v1", tags=["v1", "general"])
v1_router.include_router(notion_router.router, prefix="/v1/notion", tags=["v1", "notion"])