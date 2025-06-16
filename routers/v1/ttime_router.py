from services.ttime_service import TtimeService
from utils.api_tools import make_call_with_retry
from utils.logger import logger
from utils.ttime import TtimeUtils

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

ttime_service = TtimeService()
ttime_utils = TtimeUtils()

@router.get("/users")
async def get_users_endpoint():
    """Get all users in workspace"""
    logger.info("Ttime users endpoint called")
    return ttime_utils.get_users()
    

@router.get("/projects")
async def get_projects_endpoint():
    """Get all ttime projects in workspace"""
    logger.info("Ttime projects endpoint called")
    return ttime_utils.get_projects()


@router.get("/tasks")
async def get_tasks_endpoint():
    """Get a ttime tasks"""
    logger.info("Titme task endpoint called")
    return make_call_with_retry("get", "https://api.trackingtime.co/api/v4/tasks/paginated?include_custom_fields=true","fetching ttime tasks")


@router.get("/task/{id}")
async def get_page_endpoint(task_id):
    """Get a notion database page and its properties by id"""
    return make_call_with_retry("get", f"https://api.trackingtime.co/api/v4/tasks/{task_id}"," deleting rogue task")
    # return await notion_utils.get_page(page_id)

@router.get("/delete/{id}")
async def delete_endpoint(task_id):
    """Get a notion database page and its properties by id"""
    return make_call_with_retry("get", f"https://api.trackingtime.co/api/v4/custom_fields/{task_id}/delete"," deleting rogue task")
    # return await notion_utils.get_page(page_id)

@router.get("/reassign/{id}")
async def reassign_page_endpoint(task_id):
    """Get a notion database page and its properties by id"""
    return make_call_with_retry("get", f"https://api.trackingtime.co/api/v4/tasks/update/{task_id}?project_name=Career"," reassigning rogue task")
    # return await notion_utils.get_page(page_id)

@router.get("/custom_fields")
async def get_fields_endpoint():
    """updates instance data with ttime custom fields"""
    logger.info("Ttime custom fields endpoint called")
    await ttime_service.update_custom_fields("task")