from pydantic import BaseModel
import yaml

class InstanceData(BaseModel): 
    last_auto_sync: str
    databases: dict[str, dict]
    break_banks: list[dict[str, str|int]]
    settings: dict[str, str|int|bool]
    
    _instance = None
    
    @classmethod
    def load(cls):
        with open("instance.yaml") as f:
            return cls(**yaml.safe_load(f))

    def update(self, sync: str):
        self.last_auto_sync = sync
        with open("instance.yaml", "w") as f:
            yaml.safe_dump(self.model_dump(), f)
    