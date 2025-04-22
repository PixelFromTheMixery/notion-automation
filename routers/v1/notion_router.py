from services.notion_utils import NotionUtils
from utils.logger import logger

from fastapi import APIRouter, Depends

router = APIRouter()

notion_utils = NotionUtils()

@router.get("/users")
async def get_users():
    """Get all users in workspace (including bots)"""
    logger.info("Notion users endpoint called")
    return await notion_utils.get_users()

@router.get("/databases")
async def get_databases():
    """Get all notion databases and their properties"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_databases()

@router.get("/databases/{database}")
async def get_databases(database_id:str = "10d62907-d7c2-8036-8428-e8afc8ab261f"):
    """Get a notion databases and its properties by id"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_database(database_id)

@router.get("/pages/{page_id}")
async def get_page(page_id:str = "1c462907d7c281f4b9f7e8201ce0d135"):
    """Get a notion page and its properties by id"""
    logger.info("Notion database endpoint called")
    return await notion_utils.get_page(page_id)
