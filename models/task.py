from pydantic import BaseModel
from typing import Any, Dict, List

class Task(BaseModel):
    id: str
    name: str
    properties: Dict[str, Any]
    contents: List = None