from services.notion_utils import NotionUtils
from utils.logger import logger

from fastapi import APIRouter, Depends

router = APIRouter()

def get_notion_utils():
    return NotionUtils()

@router.get("/users")
async def get_users(notion_utils: NotionUtils = Depends(get_notion_utils)):
    """Get all users in workspace (including bots)"""
    logger.info("Notion users endpoint called")
    return await notion_utils.get_users()

@router.get("/databases")
async def get_users(notion_utils: NotionUtils = Depends(get_notion_utils)):
    """Get all notion databases and their properties"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_databases()