from utils.api_tools import make_call_with_retry
from config import Config


class ClockifySync:
    def __init__(self, config):
        self.url = config.data["system"]["locked"]["clockify_url"]

    def project_sync(self, clockify_utils, notion_projects: list):
        config = Config()
        clockify_projects = config.data["clockify"]["projects"].keys()

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

        workspace_url = self.url + f'workspaces/{config.data["clockify"]["workspace"]}/projects'
        for project in to_create:
            data["name"] = project
            make_call_with_retry(
                "post", workspace_url, "create project in clockify", data
            )

        data = {"archived": True}

        for project in to_archive:
            project_url = (
                self.url
                + f'/{config.data["clockify"]["workspace"]}/projects/{config.data["clockify"]["projects"][project]}'
            )
            make_call_with_retry(
                "put", project_url, "archive project in clockify", data
            )
        config.clockify_projects(clockify_utils)

    def setup_tasks(self, config, clockify_utils, notion_utils):
        workspace_id = config.data["clockify"]["workspace"]
        prop_type = config.data["notion"]["reset_prop"]["type"]
        prop_name = config.data["notion"]["reset_prop"]["name"]
        for project in config.data["clockify"]["projects"].keys():
            project_id = config.data["clockify"]["projects"][project]
            notion_tasks, notion_done= notion_utils.get_tasks(
                config, 
                project,
                True
            )

            clockify_tasks, clockify_done = clockify_utils.get_tasks_by_project(
                workspace_id,
                project_id,
                project
            )

            all_notion = [
                task["properties"]["Name"]["title"][0]["text"]["content"]
                for task in notion_tasks + notion_done
            ]

            all_clockify = [task["name"] for task in clockify_tasks + clockify_done]

            create_clockify = [task for task in all_notion if task not in all_clockify]
            create_notion = [task for task in all_clockify if task not in all_notion]

            for task in create_clockify:
                clockify_utils.create_task(workspace_id, project_id, task)

            for task in create_notion:
                task_data = {
                    "parent": {"database_id": config.data["notion"]["task_db"]},
                    "properties": {
                        "Name": {"title": [{"text": {"content": task}}]},
                        prop_name: {"status": {"name": "Imported"}},
                        "Project": {"select": {"name": project}},
                        "Assignee": {
                            "people": [
                                {"object": "user", "id": config.data["notion"]["user"]}
                            ]
                        },
                    },
                }
                if prop_type == "checkbox":
                    task["properties"][prop_name]["checkbox"] = False
                notion_utils.create_page(task_data)

    def task_sync(self, config, clockify_utils, notion_utils):
        clockify_tasks, clockify_done = clockify_utils.get_tasks_from_entries(
                config, clockify_utils
            )
        notion_tasks, notion_done = notion_utils.get_tasks(config, "Time", True)

        notion_done = [task for task in notion_done if task["properties"]["Every"]["select"] == None]

        reset_type = config.data["notion"]["reset_prop"]["type"]
        prop_name = config.data["notion"]["reset_prop"]["name"]

        for task in clockify_tasks:
            page = notion_utils.check_for_page(config, task)
            if page == []:
                task_data = {
                    "parent": {"database_id": config.data["notion"]["task_db"]},
                    "properties": {
                        "Name": {"title": [{"text": {"content": task}}]},
                        "Status": {"status": {"name": "Imported"}},
                        "Assignee": {
                            "people": [
                                {
                                    "object": "user",
                                    "id": config.data["notion"]["user"],
                                }
                            ]
                        },
                    },
                }
                notion_utils.create_page(task_data)

        for task in clockify_done:
            history_tasks = notion_utils.get_tasks(config, task, history=True)
            if history_tasks == []:
                page = notion_utils.check_for_page(config, task)[0]
                task_data = {}
                if reset_type == "status":
                    if page["properties"][prop_name]["status"]["name"] != "Done":
                        task_data = {
                            "properties": {prop_name: {"status": {"name": "Done"}}}
                        }
                    else:
                        print("Task already marked done, skipping")
                else:
                    if page["properties"][prop_name]["checkbox"] != True:
                        task_data = {"properties": {prop_name: {"checkbox": True}}}
                    else:
                        print("Task already marked done, skipping")
                try:
                    notion_utils.update_page(task_data, page["id"], task)
                except:
                    print(
                        f"Notion task {task} does not exist, add manually if required"
                    )

        for task in notion_tasks:
            project = task["properties"]["Project"]["select"]["name"]
            task_obj, done_obj = clockify_utils.get_tasks_by_project(
                config.data["clockify"]["workspace"],
                config.data["clockify"]["projects"][project],
                project,
                task["properties"]["Name"]["title"][0]["text"]["content"],
            )

            if task_obj == [] and done_obj == []:
                clockify_utils.create_task(
                    config.data["clockify"]["workspace"],
                    config.data["clockify"]["projects"][project],
                    project,
                    task["properties"]["Name"]["title"][0]["text"]["content"],
                )
        for task in notion_done:
            project = task["properties"]["Project"]["select"]["name"]
            task_obj, done_obj = clockify_utils.get_tasks_by_project(
                config.data["clockify"]["workspace"],
                config.data["clockify"]["projects"][project],
                project,
                task["properties"]["Name"]["title"][0]["text"]["content"],
            )

            if task_obj != []:
                clockify_utils.update_task(
                    config.data["clockify"]["workspace"],
                    config.data["clockify"]["projects"][project],
                    task_obj[0]["id"],
                    task["properties"]["Name"]["title"][0]["text"]["content"],
                )
