from utils.docs import description, tags_metadata
from utils.logger import logger
from utils.schedule import lifespan
from middlewares.exception_middleware import ExceptionMiddleware
import routers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus

app = FastAPI(
    title="🍅 Intervalia Endpoints",
    description=description,
    summary="API endpoints for the Intervalia App",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.add_middleware(ExceptionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["general"], status_code=HTTPStatus.ACCEPTED)
async def get_root():
    """Root Endpoint"""
    logger.info("Root endpoint called")
    return {"Intervalia": "Currently maintained by Pixel from the Mixery"}

app.include_router(routers.v1_router, prefix="/api")

