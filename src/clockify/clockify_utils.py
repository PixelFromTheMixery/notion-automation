from config import Config
from utils.api_tools import make_call_with_retry


class ClockifyUtils:

    def __init__(self):
        self.config = Config()
        try:
            self.workspace_id = self.config.data["clockify"]["workspace"]
            self.url = f'{self.config.data["system"]["locked"]["clockify_url"]}/{self.config.data["clockify"]["workspace"]}'
        except:
            print(
                "ClockifyUtils says: Couldn't find workspace id, please set up clockify"
            )

    def set_worskpace(self):
        self.workspace_id = self.config.data["clockify"]["workspace"]
        self.url = self.config.data["system"]["locked"]["clockify_url"]
        +"/" + self.config.data["clockify"]["workspace"]

    def get_workspaces(self):
        workspace_url = self.url
        workspaces = make_call_with_retry(
            "get", workspace_url, "fetch clockify workspaces for selection"
        )

        return workspaces

    def get_clients(self):
        client_url = self.url + f"/clients"
        clients = make_call_with_retry(
            "get", client_url, "fetch clockify workspace clients"
        )
        return clients

    def get_projects(self):
        project_url = self.url + f"/projects"
        projects = make_call_with_retry(
            "get", project_url, "fetch clockify workspace projects"
        )
        return projects

    def get_users(self):
        user_url = self.url + f"/users"
        users = make_call_with_retry(
            "get", user_url, "fetch workspace users for selection"
        )

        return users

    def get_time_entries(self, user_id: str, time: str):
        entries_url = self.url + f"/user/{user_id}/time-entries"
        entries_url += f"?start={time}"
        entries = make_call_with_retry(
            "get", entries_url, "fetch clockify entries since last sync"
        )
        return entries

    def get_tasks_by_project(self, project_id: str, project: str, name: str = None):
        tasks_url = self.url + f"/projects/{project_id}/tasks"
        if name:
            tasks_url += f"?name={name}"
        tasks = make_call_with_retry(
            "get", tasks_url, f"fetch tasks within clockify project: {project}"
        )
        task_list = [task for task in tasks if task["status"] != "DONE"]
        done_list = [task for task in tasks if task["status"] == "DONE"]
        return task_list, done_list

    def get_task_by_id(self, project_id: str, task_id: str):
        task_url = self.url + f"/projects/{project_id}/tasks/{task_id}"
        task = make_call_with_retry(
            "get", task_url, f"fetch clockify task using id: {task_id}"
        )
        return task

    def create_task(self, project_id: str, name: str):
        project_url = self.url + f"/projects/{project_id}/tasks"
        data = {"name": name}
        make_call_with_retry("post", project_url, "create task in clockify", data)

    def update_task(self, project_id: str, task_id: str, task_name: str):
        task_url = self.url + f"/projects/{project_id}/tasks/{task_id}"
        data = {"name": task_name, "status": "DONE"}
        make_call_with_retry("put", task_url, "update task in clockify", data)

    def get_tasks_from_entries(self):
        entries = self.get_time_entries(
            self.config.data["clockify"]["user"],
            self.config.data["system"]["locked"]["clockify_sync"],
        )
        task_urls = [
            {"task_id": entry["taskId"], "project": entry["projectId"]}
            for entry in entries
        ]

        for task in task_urls:
            task["task"] = self.get_task_by_id(task["project"], task["task_id"])

        task_list = [task for task in task_urls if task["task"]["status"] != "DONE"]
        done_list = [task for task in task_urls if task["task"]["status"] == "DONE"]
        return task_list, done_list
