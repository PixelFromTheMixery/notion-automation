from utils.notion import NotionUtils
from utils.instance import InstanceData

import re
from datetime import datetime, timedelta

class NotionService:

    def __init__(self):
        self.data = InstanceData.load()
        self.notion = NotionUtils()
        
    def new_due_date(self, task: dict, now_datetime):
        freq = task["properties"]["Frequency"]["number"]
        scale = task["properties"]["Rate"]["select"]["name"].lower()
        datetime_str = task["properties"]["Due Date"]["date"]["start"]
        new_time = re.search(r"\d{2}:\d{2}:\d{2}.\d{3}", datetime_str)

        if "day" in scale:
                new_start_datetime = now_datetime + timedelta(days=freq)
        if "week" in scale:
                new_start_datetime = now_datetime + timedelta(weeks=freq)
        if "month" in scale:
                # Add months manually
                new_month = (now_datetime.month - 1 + freq) % 12 + 1
                year_delta = (now_datetime.month - 1 + freq) // 12
                new_year = now_datetime.year + year_delta
                new_start_datetime = now_datetime.replace(
                    year=new_year, month=new_month
                )
        if new_time is not None:
            new_due_value = new_start_datetime.strftime(
                f"%Y-%m-%dT{new_time}+{now_datetime.utcoffset()}"
            )[:-3]
        else:
            new_due_value = new_start_datetime.strftime(f"%Y-%m-%d")
        return new_due_value

    def delete_or_reset_task(self, task: dict):
        if task["properties"]["Rate"]["select"] is not None:
            new_date = self.new_due_date(task, datetime.now())
            data = {"properties": {"Due Date": {"date": {"start": new_date}}}}

            if self.notion.reset_type == "checkbox":
                data["properties"][self.notion.reset_name] = (
                    {"checkbox": "false"},
                )

            else:
                data["properties"][self.notion.reset_name] = {
                    "status": {
                        "name": self.data.databases["tasks"]["reset_value"]
                    }
                }
                self.notion.update_page(
                    data,
                    task["id"],
                    task["properties"]["Name"]["title"][0]["text"]["content"],
                )
        else:
            data = {"archived": True}
            self.notion.update_page(
                data,
                task["id"],
                task["properties"]["Name"]["title"][0]["text"]["content"],
            )

    async def task_status_reset(self):
        tasks_to_update = self.notion.get_tasks("Done")
        if len(tasks_to_update) == 0:
            self.data.last_auto_sync = (datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
            self.data.save()
            return (False, 200)
        if self.data.databases["log"]["enabled"]:
            for task in tasks_to_update:
                try:
                    self.notion.recreate_task(
                        task, self.data.databases["log"]["id"]
                    )
                except:
                    source_database = await self.notion.get_database(self.data.databases["tasks"]["id"])
                    target_database = await self.notion.get_database(self.data.databases["log"]["id"])
                    self.notion.match_db_structure(
                        source_database, target_database
                    )
                    self.notion.recreate_task(
                        task, self.data.databases["log"]["id"]
                    )

        for task in tasks_to_update:
            self.delete_or_reset_task(task)
        self.data.update(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        return (True, 200)

    def task_date_update(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        tasks_to_update = self.notion.get_tasks("Overdue", today_str)
        if len(tasks_to_update) == 0:
            return (False, 200)
        for task in tasks_to_update:
            update = {"properties":{"Due Date":{"date":{"start": today_str}}}}
            if task["properties"]["Name"]["title"] != []:
                page_name = task["properties"]["Name"]["title"][0]["text"]["content"]
            else:
                page_name = task["id"]
            self.notion.update_page(update, task["id"], page_name)
        return (True, 200)