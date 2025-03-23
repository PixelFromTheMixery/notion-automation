from utils.api_tools import make_call_with_retry
from utils.files import read_json
from utils.time import get_current_time
from notion.notion_utils import NotionUtils
from datetime import timedelta
import json, re

class MoveTasks:
    def __init__(self):
        self.url = "https://api.notion.com/v1/"
        try:
            self.databases = read_json("src/data/databases.json")
                
        except FileNotFoundError:
            self.databases = NotionUtils().get_databases()

    def get_mt_tasks(self):
        self.url += f"databases/{self.databases['source']}/query"
        data = {
            "filter": { "property": "Status", "status": {"equals": "Done"} }
        }
        return make_call_with_retry("post", self.url, data)['results']


    def create_task(self, task: dict, parent: str):
        self.url += "pages"
        new_props = self.unpack_db_page(self.url, task)
        parent_name = list(self.databases.keys())[list(self.databases.values()).index(parent)]
        data = {"parent": { "database_id": parent }, "properties": new_props}
        print(f"Creating task: {new_props['Name']['title'][0]['text']['content']} in {parent_name}" )
        make_call_with_retry("post", self.url, data)

    def new_due_date (task:dict, now_datetime, offset):
        freq = task['properties']['Repeats']['number']
        scale = task['properties']['Every']['select']['name']
        datetime_str = task['properties']['Due Date']['date']['start']
        new_time = re.search('\d{2}:\d{2}:\d{2}.\d{3}', datetime_str)

        match scale:
            case "Days":
                new_start_datetime = now_datetime + timedelta(days=freq)
            case "Weeks":
                new_start_datetime = now_datetime + timedelta(weeks=freq)
            case "Months":
                # Add months manually
                new_month = (now_datetime.month - 1 + freq) % 12 + 1
                year_delta = (now_datetime.month - 1 + freq) // 12
                new_year = now_datetime.year + year_delta
                new_start_datetime = now_datetime.replace(year=new_year, month=new_month)
        if new_time is not None:
            new_due_value = new_start_datetime.strftime(f"%Y-%m-%dT{new_time}+{offset}")[:-3]
        else:
            new_due_value = new_start_datetime.strftime(f"%Y-%m-%d")
        return new_due_value

    def delete_or_reset_mt_task(self, task:dict, now_datetime, offset):
        if task['properties']['Every']['select'] is not None:
            new_date = self.new_due_date(task, now_datetime, offset)
            self.url += f"pages/{task['id']}"
            data = { 
                "properties": {
                    "Done": {
                        "checkbox": False
                    },
                    "Due Date": {
                        "date": { "start": new_date }
                    }
                }
            }
        else:
            print(f"Deleting old task: {task['properties']['Name']['title'][0]['text']['content']}")
            self.url += f"pages/{task['id']}"
            data = { "archived": True }
        make_call_with_retry("patch", self.url, data)

    def move_mt_tasks(self):    
        now_datetime, offset = get_current_time()
        tasks_to_move = self.get_mt_tasks()
        for task in tasks_to_move:
            self.create_task(task, self.databases["destination"])
            self.delete_or_reset_mt_task(task, now_datetime, offset)
