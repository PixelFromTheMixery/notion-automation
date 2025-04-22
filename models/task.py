from pydantic import BaseModel
from typing import Dict, Any

class Task(BaseModel):
    id: str
    name: str
    properties: Dict[str, Any]