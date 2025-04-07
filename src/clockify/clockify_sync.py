from clockify.clockify_utils import ClockifyUtils
from notion.notion_utils import NotionUtils
from utils.api_tools import make_call_with_retry

from config import Config


class ClockifySync:

    def __init__(self):
        self.config = Config()
        self.clockify_utils = ClockifyUtils()
        self.notion_utils = NotionUtils()

    def project_sync(self, notion_projects: list):
        clockify_projects = self.config.data["clockify"]["projects"]["name"].keys()

        to_create = [
            project
            for project in notion_projects
            if project not in clockify_projects
        ]
        to_archive = [
            project
            for project in clockify_projects
            if project not in notion_projects
        ]

        data = {
            "billable": False,
            "isPublic": True,
        }

        workspace_url = self.clockify_utils.url + f"/projects"
        for project in to_create:
            data["name"] = project
            make_call_with_retry(
                "post", workspace_url, "create project in clockify", data
            )

        data = {"archived": True}

        for project in to_archive:
            project_url = (
                self.clockify_utils.url
                + f'/projects/{self.config.data["clockify"]["projects"][project]}'
            )
            make_call_with_retry(
                "put", project_url, "archive project in clockify", data
            )
        self.config.clockify_projects()

    def setup_tasks(self):
        prop_type = self.config.data["notion"]["reset_prop"]["type"]
        prop_name = self.config.data["notion"]["reset_prop"]["name"]
        for project in self.config.data["clockify"]["projects"]["name"].keys():
            project_id = self.config.data["clockify"]["projects"]["name"][project]["id"]
            notion_tasks, notion_done = self.notion_utils.get_tasks(project, True)
            history_tasks = self.notion_utils.get_tasks(project, history=True)

            clockify_tasks, clockify_done = self.clockify_utils.get_tasks_by_project(
                project_id, project
            )

            all_notion = [
                task["properties"]["Name"]["title"][0]["text"]["content"]
                for task in notion_tasks + notion_done
            ]

            all_clockify = [task["name"] for task in clockify_tasks + clockify_done]

            create_clockify = [task for task in all_notion if task not in all_clockify]
            create_notion = [
                task
                for task in all_clockify
                if task not in all_notion and task in history_tasks
            ]

            for task in create_clockify:
                self.clockify_utils.create_task(project_id, task)

            for task in create_notion:
                task_data = {
                    "parent": {"database_id": self.config.data["notion"]["task_db"]},
                    "properties": {
                        "Name": {"title": [{"text": {"content": task}}]},
                        prop_name: {"status": {"name": "Imported"}},
                        "Project": {"select": {"name": project}},
                        "Category": {
                            "select": {
                                "name": self.config.data["clockify"]["projects"][
                                    "name"
                                ][project]["client"]
                            }
                        },
                        "Assignee": {
                            "people": [
                                {
                                    "object": "user",
                                    "id": self.config.data["notion"]["user"],
                                }
                            ]
                        },
                    },
                }
                if prop_type == "checkbox":
                    task["properties"][prop_name]["checkbox"] = False
                self.notion_utils.create_page(task_data)

    def task_sync(self):
        clockify_tasks, clockify_done = self.clockify_utils.get_tasks_from_entries()
        notion_tasks, notion_done = self.notion_utils.get_tasks("Time", True)

        notion_done = [
            task for task in notion_done if task["properties"]["Rate"]["select"] == None
        ]

        for task in clockify_tasks:
            page = self.notion_utils.check_for_page(task["task"]["name"])
            if page == []:
                task_data = {
                    "parent": {"database_id": self.config.data["notion"]["task_db"]},
                    "properties": {
                        "Name": {
                            "title": [{"text": {"content": task["task"]["name"]}}]
                        },
                        "Project": {
                            "select": {
                                "name": self.config.data["clockify"]["projects"]["id"][
                                    task["project"]
                                ]["name"]
                            }
                        },
                        "Category": {
                            "select": {
                                "name": self.config.data["clockify"]["projects"]["id"][
                                    task["project"]
                                ]["client"]
                            }
                        },
                        "Status": {"status": {"name": "Imported"}},
                        "Assignee": {
                            "people": [
                                {
                                    "object": "user",
                                    "id": self.config.data["notion"]["user"],
                                }
                            ]
                        },
                    },
                }
                self.notion_utils.create_page(task_data)

        for task in clockify_done:
            history_tasks = self.notion_utils.get_tasks(task, history=True)
            if history_tasks == []:
                page = self.notion_utils.check_for_page(task)[0]
                task_data = {}
                if self.notion_utils.reset_prop_type == "status":
                    if (
                        page["properties"][self.notion_utils.reset_prop_name]["status"][
                            "name"
                        ]
                        != "Done"
                    ):
                        task_data = {
                            "properties": {
                                self.notion_utils.reset_prop_name: {
                                    "status": {"name": "Done"}
                                }
                            }
                        }
                    else:
                        print("Task already marked done, skipping")
                else:
                    if (
                        page["properties"][self.notion_utils.reset_prop_name][
                            "checkbox"
                        ]
                        != True
                    ):
                        task_data = {
                            "properties": {
                                self.notion_utils.reset_prop_name: {"checkbox": True}
                            }
                        }
                    else:
                        print("Task already marked done, skipping")
                try:
                    self.notion_utils.update_page(task_data, page["id"], task)
                except:
                    print(
                        f"Notion task {task} does not exist, add manually if required"
                    )

        for task in notion_tasks:
            project = task["properties"]["Project"]["select"]["name"]
            task_obj, done_obj = self.clockify_utils.get_tasks_by_project(
                self.config.data["clockify"]["projects"]["name"][project]["id"],
                project,
                task["properties"]["Name"]["title"][0]["text"]["content"],
            )

            if task_obj == [] and done_obj == []:
                self.clockify_utils.create_task(
                    self.config.data["clockify"]["projects"]["name"][project]["id"],
                    task["properties"]["Name"]["title"][0]["text"]["content"],
                )
        for task in notion_done:
            project = task["properties"]["Project"]["select"]["name"]
            task_obj, done_obj = self.clockify_utils.get_tasks_by_project(
                self.config.data["clockify"]["projects"]["name"][project]["id"],
                project,
                task["properties"]["Name"]["title"][0]["text"]["content"],
            )

            if task_obj != []:
                self.clockify_utils.update_task(
                    self.config.data["clockify"]["projects"]["name"][project]["id"],
                    task_obj[0]["id"],
                    task["properties"]["Name"]["title"][0]["text"]["content"],
                )

    def import_time_entries(self):

        entries = self.clockify_utils.get_time_entries(
            self.config.data["clockify"]["user"],
            self.config.data["system"]["locked"]["clockify_sync"],
        )
        data = {"parent": self.config.data["notion"]["time_entries"]}
        for entry in entries:
            self.clockify_utils.get_task_by_id()
            self.notion_utils.create_page()
