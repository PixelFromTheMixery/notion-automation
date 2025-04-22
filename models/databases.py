from pydantic import BaseModel
from typing import List

class DatabaseProperty(BaseModel):
    name: str
    type: str
    possible_values: List = None

class Database(BaseModel):
    id: str
    title: str
    properties: List[DatabaseProperty]
    
class Databases(BaseModel):
    databases: List[Database]