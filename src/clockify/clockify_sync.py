from utils.api_tools import make_call_with_retry
from utils.config import Config

class ClockifySync:
    def __init__(self):
        self.url = Config().clockify_url
    
    def project_sync(self, clockify_utils, settings: dict, source_struct: dict):        
        notion_project_select = source_struct["Project"]["select"]["options"]
        notion_project_list = [project["name"] for project in notion_project_select]

        clockify_projects = settings["clockify"]["projects"].keys()

        to_create = [project for project in notion_project_list if project not in clockify_projects]
        to_archive = [project for project in clockify_projects if project not in notion_project_list]

        data = {
            "billable": False,
            "isPublic": True,
        }

        project_url = self.url + f'workspaces/{settings["clockify"]["id"]}/projects'
        for project in to_create:
            data["name"]= project
            make_call_with_retry("post", project_url, data)["results"]

        data = {"archived": True}
        
        for project in to_archive:
            project_url = self.url + f'workspaces/{settings["clockify"]["id"]}/projects/{settings["clockify"]["projects"][project]}'
            make_call_with_retry("put", project_url, data)["results"]
        
        settings = clockify_utils.get_projects(settings)
        return settings
    
    def task_sync(self, clockify_utils, notion_utils, settings:dict):
        for project in settings["clockify"]["projects"].keys():
            notion_tasks = notion_utils.get_tasks_by_project(settings["notion"]["source"], project)
            clockify_tasks, clockify_done = clockify_utils.get_tasks_by_project(settings, project)
            
            to_import = [task for task in clockify_tasks if task not in notion_tasks.keys()]
            to_update = [task for task in clockify_done if task in notion_tasks.keys()]
            to_create = [task for task in notion_tasks if task not in clockify_tasks.keys() and task not in to_update]

            for task in to_create:
                data = {"name":task }
                create_url = self.url + f'/{settings["clockify"]["id"]}/projects/{settings["clockify"]["projects"][project]}/tasks'
                make_call_with_retry("post", create_url, data)
                
            for task in to_import:
                task_data = {
                    "parent": { "database_id": settings["notion"]["source"]},
                    "properties":{
                        "Name": { "title": [{ "text": { "content": task }}]},
                        "Status": {"status": { "name": "Imported" }},
                        "Project": { "select": { "name": project }},
                    }
                }
                notion_utils.create_page( task_data )
            
            for task in to_update:
                task_data = {"properties": {"Status": {"status": { "name": "Done" }}}}
                notion_utils.update_page( task_data, notion_tasks[task] )