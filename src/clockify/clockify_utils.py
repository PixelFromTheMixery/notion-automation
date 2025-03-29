from utils.api_tools import make_call_with_retry
from config import Config
from utils.files import write_yaml
from utils.helper import list_options


class ClockifyUtils:
    def __init__(self):
        self.url = Config().data["system"]["clockify_url"]

    def create_or_assign(settings: dict, variable: str, data: str, obj_list: list):
        if variable not in settings[data].keys():
            settings[data][variable] = {}
        for obj in obj_list:
            settings[data][variable][obj["name"]] = obj["id"]

    def get_workspaces(self):
        workspace_url = self.url
        workspaces = make_call_with_retry(
            "get", workspace_url, "fetch clockify workspaces for selection"
        )
        
        return workspaces

    def get_clients(self, workspace_id):
        client_url = self.url + f'/{workspace_id}/clients'
        clients = make_call_with_retry(
            "get", client_url, info="fetch clockify workspace clients"
        )
        return clients

    def get_projects(self, workspace_id):
        project_url = self.url + f'/{workspace_id}/projects'
        projects = make_call_with_retry(
            "get", project_url, info="fetch clockify workspace projects"
        )
        return projects

    def get_users(self, workspace_id):
        user_url = self.url + f'/{workspace_id}/users'
        users = make_call_with_retry(
            "get", user_url, info="fetch workspace users for selection"
        )
        
        return users

    def get_tasks_by_project(self, workspace_id: str, project_id: str, project: str):
        tasks_url = (
            self.url
            + f'/{workspace_id}/projects/{project_id}/tasks?'
        )
        tasks = make_call_with_retry(
            "get", tasks_url, info=f"fetch tasks within clockify project: {project}"
        )
        task_list = {
            task["name"]: task["id"] 
            for task in tasks 
            if task["status"] != "DONE"
        }
        done_list = {
            task["name"]: task["id"] 
            for task in tasks 
            if task["status"] == "DONE"
        }
        return task_list, done_list
