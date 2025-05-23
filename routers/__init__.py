from routers.v1 import debug_router, general_router, local_router, notion_router

from fastapi import APIRouter

v1_router = APIRouter()

v1_router.include_router(general_router.router, prefix="/v1", tags=["v1", "general"])
v1_router.include_router(local_router.router, prefix="/v1/local", tags=["v1", "local"])
v1_router.include_router(notion_router.router, prefix="/v1/notion", tags=["v1", "notion"])
v1_router.include_router(debug_router.router, prefix="/v1/debug", tags=["v1", "debug"])