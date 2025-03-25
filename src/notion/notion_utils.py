from utils.api_tools import make_call_with_retry
from utils.config import Config
from utils.files import read_yaml, write_yaml

class NotionUtils:
    def __init__(self):
        self.url = Config().notion_url
    
    def get_databases(self, settings: dict = None):
        # Filter to search only for databases
        data = {
            "filter": {
                "value": "database",
                "property": "object"
            }
        }
        search_url = self.url + "search"
        databases = make_call_with_retry("post", search_url, data)["results"]
        # Dictionary of database id"s and names
        database_list= {}
        for db in databases:
            db_name = db["title"][0]["text"]["content"]
            database_list[db_name] = db["id"]
        return database_list

    def get_db_structure(self, settings: dict):
        url = self.url+"databases/"
        
        source_url = url + settings["notion"]["source"]
        source_struct = make_call_with_retry("get", source_url)["properties"]
        for prop in source_struct:
            del source_struct[prop]["id"]
        destination_url = url + settings["notion"]["destination"]
        destination_struct = make_call_with_retry("get", destination_url)["properties"]
        for prop in destination_struct:
            del destination_struct[prop]["id"]
        return source_struct, destination_struct
        
    def match_mt_structure(self, destination, 
                           source_struct: dict, dest_struct: dict):
        url = self.url+f"databases/{destination}"
        
        to_create = {k: source_struct[k] for k in source_struct if k not in dest_struct}
        to_destroy = {k: dest_struct[k] for k in dest_struct if k not in source_struct}
        
        props_to_destroy = {}
        
        # Create a dictionary where each property in dest_struct is a key, with None as its value
        props_to_destroy = {prop: None for prop in to_destroy}
        if len(props_to_destroy) != 0:
            data = {
                "properties": props_to_destroy
            }
            make_call_with_retry("patch", url, data)["results"]
        
        new_prop = {}
        for prop in to_create:
            prop_dict = to_create[prop]
            prop_type = prop_dict["type"]
            new_prop = {
                prop: {prop_type: prop_dict[prop_type]}
            } 

            data = {
                "properties": new_prop
            }
            make_call_with_retry("patch", url, data)["results"]

    def unpack_db_page(self, task: dict):
        unpacked_data = {}
        for prop in task["properties"]:
            prop_dict = task["properties"][prop]
            prop_type = prop_dict["type"]

            if prop == "Sub-item":
                print()
            match prop_type:
                case "title":
                    title = prop_dict[prop_type][0]["text"]["content"]
                    unpacked_data[prop] = { "title": [{ "text": { "content": title }}]}
                case "multi_select":
                    tag_list = [{"name": select["name"]} for select in prop_dict[prop_type]]
                    unpacked_data[prop] = {prop_type: tag_list}
                case "select":
                    if prop_dict[prop_type] != None:
                        unpacked_data[prop] = {prop_type: {"name": prop_dict[prop_type]["name"]}}
                case "checkbox":
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case "number":
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case "self.url":
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case "date":
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case "rich_text":
                    if prop_dict[prop_type] != []:
                        content = prop_dict[prop_type][0]["text"]["content"]
                        unpacked_data[prop] = { "rich_text": [{ "text": { "content": content }}]}
                case "relation":
                    if prop_dict[prop_type] != [] and prop != "Sub-item":
                        page_id = prop_dict[prop_type][0]["id"]
                        response = make_call_with_retry("get",f"{self.url}/{page_id}")["results"]
                        page_name = response["properties"]["Name"]["title"][0]["text"]["content"]
                        unpacked_data[prop] = { "rich_text": [{ "text": { "content": page_name }}]}
        return unpacked_data
    
    def recreate_task(self, task: dict, parent: str):
        pages_url = self.url + "pages"
        new_props = self.unpack_db_page(task)
        data = {"parent": { "database_id": parent }, "properties": new_props}
        print(f'Creating task: {new_props["Name"]["title"][0]["text"]["content"]} in destination database')
        make_call_with_retry("post", pages_url, data)["results"]

    def get_tasks_by_project(self, database:str, project:str):
        data = {
            "filter": {
                "property": "Project",
                "select": { "equals" :project }
            }
        }
        
        tasks_url = self.url + f"databases/{database}/query"
        tasks = make_call_with_retry("post", tasks_url, data)["results"]
        task_dict = {}
        for task in tasks:
            task_dict[task["properties"]["Name"]["title"][0]["text"]["content"]] = task["id"]
        return task_dict
    
    def update_page(self, data:dict, page_id:str):
        page_url = self.url + f"pages/{page_id}"
        make_call_with_retry("patch", page_url, data)
    
    def create_page(self, data:dict):
        page_url = self.url + f"pages"
        make_call_with_retry("post", page_url, data)