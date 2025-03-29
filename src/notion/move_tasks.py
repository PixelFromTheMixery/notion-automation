from utils.api_tools import make_call_with_retry
from config import Config
from utils.time import get_current_time
from datetime import timedelta
import re


class MoveTasks:
    def __init__(self):
        self.url = Config().data["system"]["notion_url"]

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

    def delete_or_reset_tm_task(self, config, task: dict, now_datetime, offset):
        update_url = self.url + f'pages/{task["id"]}'
        reset_type = config.data["notion"]["mover"]["type"]
        if task["properties"]["Every"]["select"] is not None:
            new_date = self.new_due_date(task, now_datetime, offset)
            data = {"properties": {"Due Date": {"date": {"start": new_date}}}}

            if reset_type=="checkbox":
                data["properties"][config.data["notion"]["mover"]["name"]] = (
                    {"checkbox": "false"},
                )

            else:
                data["properties"][config.data["notion"]["mover"]["name"]] = {
                    "status": {"name": config.data["notion"]["mover"]["text"]}
                }
                make_call_with_retry(
                    "patch",
                    update_url,
                    f'reset task {task["properties"]["Name"]["title"][0]["text"]["content"]}',
                    data
                )
        else:
            data = {"archived": True}
            make_call_with_retry(
                "patch",
                update_url,
                f'delete task {task["properties"]["Name"]["title"][0]["text"]["content"]}',
                data
            )

    def move_tasks(self, notion_utils):
        now_datetime, offset = get_current_time()
        config = Config()
        tasks_to_move = notion_utils.get_tasks(config, "Done")
        for task in tasks_to_move:
            notion_utils.recreate_task(task, config.data["notion"]["mover"]["history"])
            self.delete_or_reset_tm_task(config, task, now_datetime, offset)
