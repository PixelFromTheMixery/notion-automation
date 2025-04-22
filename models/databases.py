from pydantic import BaseModel
from typing import List

class Property(BaseModel):
    name: str
    type: str
    possible_values: List = None

class Database(BaseModel):
    id: str
    title: str
    properties: List[Property]
    
class Databases(BaseModel):
    databases: List[Database]