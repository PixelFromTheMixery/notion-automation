from utils.api_tools import make_call_with_retry
from utils.config import Config
from utils.files import write_yaml, read_yaml

class ClockifyUtils:
    def __init__(self):
        self.url = Config().clockify_url
    
    def get_workspace(self):
        workspace_url = self.url + "workspaces"
        clockify_info = {'workspaces':[]}
        workspaces = make_call_with_retry("get", workspace_url)
        for ws in workspaces:
            clockify_info['workspaces'].append(
                {"id":ws['id'],"name":ws['name'],"projects":[]}
            )
        
        print('Please select the workspace you want to sync with:')
        for ws in clockify_info['workspaces']:
            print(f"{clockify_info['workspaces'].index(ws)+1}. {ws['name']}")
        to_sync = int(input("Enter the number of the workspace: "))
        clockify_info['syncing'] = to_sync-1
        
        clockify_info['workspaces'][to_sync-1]['clients'] = []
        client_url = self.url + f"workspaces/{clockify_info['workspaces'][to_sync-1]['id']}/clients"
        clients = make_call_with_retry("get", client_url)
        for client in clients:
            clockify_info['workspaces'][to_sync-1]['clients'].append(
                {"id":client['id'],"name":client['name']}
            )
        
        
        write_yaml(clockify_info, "src/data/clockify.yaml")
        return clockify_info

    def get_projects(self):
        try:
            clockify_info = read_yaml("src/data/clockify.yaml")
        except FileNotFoundError:
            clockify_info = ClockifyUtils().get_workspace()
        print()
        self.url += f"workspaces/{clockify_info['workspaces'][clockify_info['syncing']]['id']}/projects"
        projects = make_call_with_retry("get", self.url)
        for project in projects:
            clockify_info['workspaces'][clockify_info['syncing']]['projects'].append(
                {"id":project['id'],"name":project['name']}
            )
        write_yaml(clockify_info, "src/data/clockify.yaml")
        
        return clockify_info