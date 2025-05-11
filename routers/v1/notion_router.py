from services.notion_utils import NotionUtils
from services.task_automation import TaskAutomation
from utils.logger import logger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

notion_utils = NotionUtils()
reset_tasks = TaskAutomation()

@router.get("/users")
async def get_users_endpoint():
    """Get all users in workspace (including bots)"""
    logger.info("Notion users endpoint called")
    return await notion_utils.get_users()

@router.get("/databases")
async def get_databases_endpoint():
    """Get all notion databases and their properties"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_databases()

@router.get("/databases/{database}")
async def get_databases_endpoint(database_id:str = "10d62907-d7c2-8036-8428-e8afc8ab261f"):
    """Get a notion databases and its properties by id"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_database(database_id)

@router.get("/pages/{page_id}")
async def get_page_endpoint(page_id:str = "1c462907d7c281f4b9f7e8201ce0d135"):
    """Get a notion page and its properties by id"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_page(page_id)

@router.get("/reset")
async def reset_tasks_endpoint():
    """Reset or delete tasks"""
    logger.info("Notion tasks reset endpoint called")
    result = reset_tasks.task_status_reset()
    return JSONResponse(result[0],result[1])