from utils.logger import logger

import json
from fastapi import APIRouter, Depends
from http import HTTPStatus
from pathlib import Path

router = APIRouter()

data ={}
files = [f.name.split(".")[0] for f in Path("responses").iterdir() if f.is_file()]
for file in files:
    with open(f"responses/{file}.json") as f:
        contents = f.read()
        data[file] = json.loads(contents)

@router.get("/databases")
async def get_database_endpoint():
    """Locally cached Databases Example Response"""
    return data["databases"]

@router.get("/database")
async def get_database_endpoint():
    """Locally cached Database Example Response"""
    return data["database"]

@router.get("/task")
async def get_database_endpoint():
    """Locally cached Task Example Response"""
    return data["task"]