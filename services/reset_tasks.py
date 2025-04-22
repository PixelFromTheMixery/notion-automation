from services.notion_utils import NotionUtils

import re
from datetime import datetime, timedelta

class ResetTasks:

    def new_due_date(self, task: dict, now_datetime):
        freq = task["properties"]["Frequency"]["number"]
        scale = task["properties"]["Rate"]["select"]["name"]
        datetime_str = task["properties"]["Due Date"]["date"]["start"]
        new_time = re.search(r"\d{2}:\d{2}:\d{2}.\d{3}", datetime_str)

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

            if self.notion_utils.reset_prop_type == "checkbox":
                data["properties"][self.notion_utils.reset_prop_name] = (
                    {"checkbox": "false"},
                )

            else:
                data["properties"][self.notion_utils.reset_prop_name] = {
                    "status": {
                        "name": self.config.data["notion"]["log"]["reset_prop"]["text"]
                    }
                }
                self.notion_utils.update_page(
                    data,
                    task["id"],
                    task["properties"]["Name"]["title"][0]["text"]["content"],
                )
        else:
            data = {"archived": True}
            self.notion_utils.update_page(
                data,
                task["id"],
                task["properties"]["Name"]["title"][0]["text"]["content"],
            )

    def automate_tasks(self):
        tasks_to_update = self.notion_utils.get_tasks("Done")

        if self.config.data["notion"]["log"]["active"]:
            for task in tasks_to_update:
                self.notion_utils.recreate_task(
                    task, self.config.data["notion"]["log"]["history"]
                )
                self.delete_or_reset_task(task)
        else:
            for task in tasks_to_update:
                self.delete_or_reset_task(task)
