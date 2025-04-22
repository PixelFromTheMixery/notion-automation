from pydantic import BaseModel
from typing import List

class User(BaseModel):
    id: str
    name: str
    type: str

class Users(BaseModel):
    users: List[User]