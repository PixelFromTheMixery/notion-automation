from utils.api_tools import make_call_with_retry
from config import Config


class ClockifySync:
    def __init__(self):
        self.url = Config().data["system"]["clockify_url"]

    def project_sync(self, notion_projects: list):
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
                + f'workspaces/{config.data["clockify"]["workspace"]}/projects/{config.data["clockify"]["projects"][project]}'
            )
            make_call_with_retry(
                "put", project_url, data, info="archive project in clockify"
            )

    def setup_tasks(self, clockify_utils, notion_utils, config):
        workspace_id = config.data["clockify"]["workspace"]
        prop_name = config.data["notion"]["mover"]["type"]
        for project in config.data["clockify"]["projects"].keys():
            project_id = config.data["clockify"]["projects"][project]
            notion_tasks, notion_done= notion_utils.get_tasks(
                config, 
                project
            )
            
            clockify_tasks, clockify_done = clockify_utils.get_tasks_by_project(
                workspace_id,
                project_id,
                project
            )

            to_create_notion = [
                task for task in clockify_tasks 
                if task not in notion_tasks.keys()
                and task not in notion_done.keys()
            ]
            to_update_notion = [
                task for task in clockify_done 
                if task not in notion_done.keys()
                ]

            to_update_clockify = [
                task for task in notion_done
                if task not in clockify_done.keys()
            ]

            to_create_clockify = [
                task
                for task in notion_tasks
                if task not in clockify_tasks.keys()
                and task not in notion_done.keys()
                and task not in to_update_clockify.keys()
            ]


            for task in to_create_notion:
                task_data = {
                    "parent": {"database_id": config.data["notion"]["task_db"]},
                    "properties": {
                        "Name": {"title": [{"text": {"content": task}}]},
                        "Status": {"status": {"name": "Imported"}},
                        "Project": {"select": {"name": project}},
                        "Assignee": {
                            "people": [{
                                "object": "user", 
                                "id": config.data["notion"]["user"] 
                            }]
                        }
                    },
                }
                notion_utils.create_page(task_data)

            for task in to_update_notion:
                if config.data["notion"]["mover"]["type"] == "status":
                    task_data = {"properties": {prop_name: {"status": {"name": "Done"}}}}
                else:
                    task_data = {"properties": {prop_name: {"checkbox": True}}}
                try:
                    notion_utils.update_page(task_data, notion_tasks[task], task)
                except:
                    task_data = {
                    "parent": {"database_id": config.data["notion"]["task_db"]},
                    "properties": {
                        "Name": {"title": [{"text": {"content": task}}]},
                        "Status": {"status": {"name": "Done"}},
                        "Project": {"select": {"name": project}},
                        "Assignee": {
                            "people": [{
                                "object": "user", 
                                "id": config.data["notion"]["user"] 
                            }]
                        }
                    },
                }
                notion_utils.create_page(task_data)



            for task in to_create_clockify:
                data = {"name": task}
                create_url = (
                    self.url
                    + f'/{workspace_id}/projects/{project_id}/tasks'
                )
                make_call_with_retry(
                    "post", 
                    create_url, 
                    "create task in clockify",
                    data
                )

            for task in to_update_clockify:
                data = {
                    "name": task,
                    "status": "DONE"
                }
                update_url = (
                    self.url
                    + f'/{workspace_id}/projects/{project_id}/tasks/{clockify_tasks[task]}'
                )
                make_call_with_retry(
                    "put", 
                    update_url, 
                    "update a task in clockify",
                    data
                )