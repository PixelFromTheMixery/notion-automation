from clockify.clockify_utils import ClockifyUtils
from notion.notion_utils import NotionUtils
from utils.api_tools import make_call_with_retry
from utils.config import Config
from utils.files import read_yaml, write_yaml

import random

class ClockifySync:
    def __init__(self):
        self.url = Config().clockify_url
    
    def project_sync(self, settings: dict, source_struct: dict):
        project_url = self.url + f'workspaces/{settings["clockify"]["id"]}/projects'
        
        notion_project_select = source_struct["Project"]["select"]["options"]
        notion_project_list = [project["name"] for project in notion_project_select]

        clockify_projects = settings["clockify"]["projects"].keys()
                
        to_create = [project for project in notion_project_list if project not in clockify_projects]
        to_archive = [project for project in clockify_projects if project not in notion_project_list]


        data = {
            "billable": True,
            "clientId": settings["clockify"]["clients"]["Inbox"],
            "costRate": {
                "amount": 0,
                "since": "2020-01-01T00:00:00Z"
            },
            "estimate": {
                "estimate": "PT1H30M",
                "type": "AUTO"
            },
            "hourlyRate": {
                "amount": 20000,
                "since": "2020-01-01T00:00:00Z"
            },
            
        }

        for project in to_create:
            r = lambda: random.randint(0,255)
            colour = ("#%02X%02X%02X" % (r(),r(),r()))
            data["colour"] = colour
            make_call_with_retry("patch", self.url)
        return settings