from services.health_service import HealthService
from utils.logger import logger

import json
from fastapi import APIRouter, Depends
from http import HTTPStatus
from pathlib import Path

router = APIRouter()

data ={}
files = [f.name.split(".")[0] for f in Path("app/responses").iterdir() if f.is_file()]
for file in files:
    with open(f"app/responses/{file}.json") as f:
        contents = f.read()
        data[file] = json.loads(contents)

@router.get("/databases")
async def get_database():
    """Locally cached Databases Example Response"""
    return data["databases"]

@router.get("/database")
async def get_database():
    """Locally cached Database Example Response"""
    return data["database"]

@router.get("/task")
async def get_database():
    """Locally cached Task Example Response"""
    return data["task"]