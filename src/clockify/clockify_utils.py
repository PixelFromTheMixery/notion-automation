from utils.api_tools import make_call_with_retry
from utils.config import Config
from utils.files import write_yaml
from utils.helper import list_options

class ClockifyUtils:
    def __init__(self):
        self.url = Config().clockify_url
    
    def create_or_assign(settings: dict, variable: str, data: str, obj_list: list):
        if variable not in settings[data].keys():
                settings[data][variable] = {}
        for obj in obj_list:
            settings[data][variable][obj["name"]] = obj["id"]
    
    def get_workspaces(self,settings: dict = None):
        workspace_url = self.url + "workspaces"
        workspaces = make_call_with_retry("get", workspace_url)
        workspace_list = {}
        for ws in workspaces:
            workspace_list[ws['name']] = ws['id']
        
        workspace_id = workspace_list[list_options(workspaces,"Enter the number of the workspace: ",
                            "Please select the workspace you want to sync with:")]
        
        if "clockify" not in settings.keys():
            settings = {"clockify":{"id": workspace_id}}    
        else:
            settings["clockify"]["id"] = workspace_id
        
        write_yaml(settings, "src/data/settings.yaml")
        return settings

    def get_projects(self, settings: dict):
        project_url = self.url + f'workspaces/{settings["clockify"]["id"]}/projects'
        projects = make_call_with_retry("get", project_url)
        if "projects" not in settings["clockify"].keys():
            settings["clockify"]["projects"] = {}
        for project in projects:
            settings["clockify"]["projects"][project["name"]] = project["id"]
        write_yaml(settings, "src/data/settings.yaml")
        
        return settings

    def get_clients(self,settings: dict):
        client_url = self.url + f'workspaces/{settings["clockify"]["id"]}/clients'
        clients = make_call_with_retry("get", client_url)
        if "clients" not in settings["clockify"].keys():
            settings["clockify"]["clients"] = {}
        for client in clients:
            settings["clockify"]["clients"][client["name"]] = client["id"]
        write_yaml(settings, "src/data/settings.yaml")
        
        return settings
    
    def get_user(self, settings: dict):
        user_url = self.url + f'workspaces/{settings["clockify"]["id"]}/users'
        users = make_call_with_retry("get", user_url)
        user_list ={}
        for user in users:
            user_list[user["name"]] = user["id"]
        user_id = user_list[list_options(users,"Enter the number of your user: ",
                            "Please select the user you want to identify as:")]
        if "user" not in settings["clockify"].keys():
            settings["clockify"]["user"] = user_id
        write_yaml(settings, "src/data/settings.yaml")
        
        return settings


    def setup_clockify(self, settings:dict):
        settings = self.get_workspaces(settings)
        settings = self.get_projects(settings)
        settings = self.get_clients(settings)
        settings = self.get_user(settings)
        return settings