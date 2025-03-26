from utils.api_tools import make_call_with_retry
from utils.config import Config
from utils.time import get_current_time
from datetime import timedelta
import re


class MoveTasks:
    def __init__(self):
        self.url = Config().notion_url

    def get_mt_tasks(self, settings: dict):
        get_tasks_url = self.url + f'databases/{settings["notion"]["source"]}/query'
        data = {"filter": {"property": "Status", "status": {"equals": "Done"}}}
        return make_call_with_retry(
            "post", get_tasks_url, data, info="fetch tasks from source database"
        )

    def new_due_date(self, task: dict, now_datetime, offset):
        freq = task["properties"]["Repeats"]["number"]
        scale = task["properties"]["Every"]["select"]["name"]
        datetime_str = task["properties"]["Due Date"]["date"]["start"]
        new_time = re.search("\d{2}:\d{2}:\d{2}.\d{3}", datetime_str)

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
                f"%Y-%m-%dT{new_time}+{offset}"
            )[:-3]
        else:
            new_due_value = new_start_datetime.strftime(f"%Y-%m-%d")
        return new_due_value

    def delete_or_reset_tm_task(self, task: dict, now_datetime, offset, settings):
        update_url = self.url + f'pages/{task["id"]}'
        if task["properties"]["Every"]["select"] is not None:
            new_date = self.new_due_date(task, now_datetime, offset)
            data = {"properties": {"Due Date": {"date": {"start": new_date}}}}

            if settings["notion"]["checkbox"]:
                data["properties"][settings["notion"]["prop_name"]] = (
                    {"checkbox": "false"},
                )

            else:
                data["properties"][settings["notion"]["prop_name"]] = {
                    "status": {"name": settings["notion"]["reset_text"]}
                }
                make_call_with_retry(
                    "patch",
                    update_url,
                    data,
                    info=f' reset task {task["properties"]["Name"]["title"][0]["text"]["content"]}',
                )
        else:
            data = {"archived": True}
            make_call_with_retry(
                "patch",
                update_url,
                data,
                info=f'delete task {task["properties"]["Name"]["title"][0]["text"]["content"]}',
            )

    def move_mt_tasks(self, notion_utils, settings: dict):
        now_datetime, offset = get_current_time()
        tasks_to_move = self.get_mt_tasks(settings)
        for task in tasks_to_move:
            notion_utils.recreate_task(task, settings["notion"]["destination"])
            self.delete_or_reset_tm_task(task, now_datetime, offset, settings)
