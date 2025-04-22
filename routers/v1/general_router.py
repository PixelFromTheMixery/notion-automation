from services.health_service import HealthService
from utils.logger import logger

from fastapi import APIRouter, Depends
from http import HTTPStatus

router = APIRouter()

def get_health_service():
    return HealthService()

@router.get("/health", status_code=HTTPStatus.ACCEPTED)
async def get_health(health_service: HealthService = Depends(get_health_service)):
    """Health Endpoint, should always return 200 OK"""
    logger.info("Health endpoint called")
    return await health_service.check_health("OK")