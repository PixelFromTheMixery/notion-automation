from pydantic import BaseModel
import yaml

class InstanceData(BaseModel): 
    last_auto_sync: str
    databases: dict[str, dict]
    break_banks: list[dict[str, str|int]]
    settings: dict[str, str|int|bool]
    ttime: dict[str, bool|dict]
    
    _instance = None
    
    @classmethod
    def load(cls):
        with open("instance.yaml") as f:
            return cls(**yaml.safe_load(f))
    
    def save(self):
        with open("instance.yaml", "w") as f:
            yaml.safe_dump(self.model_dump(), f)