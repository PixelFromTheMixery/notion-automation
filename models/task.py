from pydantic import BaseModel

class Task(BaseModel):
    name: str
    optional_value: bool = None