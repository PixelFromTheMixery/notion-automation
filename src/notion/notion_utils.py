from utils.api_tools import make_call_with_retry
from config import Config

class NotionUtils:

    def __init__(self):
        self.config = Config()
        self.reset_prop_type = self.config.data["notion"]["reset_prop"]["type"]
        self.reset_prop_name = self.config.data["notion"]["reset_prop"]["name"]
        self.url = self.config.data["system"]["locked"]["notion_url"]

    def get_users(self):
        user_url = self.url + "users"
        users = make_call_with_retry(
            "get", user_url, "get users from notion"
        )
        return users

    def get_databases(self):
        data = {"filter": {"value": "database", "property": "object"}}
        search_url = self.url + "search"
        databases = make_call_with_retry(
            "post", search_url, "fetch databases for selection", data
        )
        return databases

    def get_db_structure(self, database_id):
        url = self.url + "databases/"

        source_url = url + database_id
        struct = make_call_with_retry("get", source_url, f"fetch database structure")[
            "properties"
        ]

        filtered = {k: v for k, v in struct.items() if struct[k]["type"] != "relation"}

        return filtered

    def match_db_structure(self, source, history):
        source_struct = self.get_db_structure(source)
        for prop in source_struct:
            del source_struct[prop]["id"]

        dest_struct = self.get_db_structure(history)
        for prop in dest_struct.keys():
            del dest_struct[prop]["id"]

        to_create = {k: source_struct[k] for k in source_struct if k not in dest_struct}
        to_destroy = {k: dest_struct[k] for k in dest_struct if k not in source_struct}

        props_to_destroy = {}

        # Create a dictionary where each property in dest_struct is a key, with None as its value
        props_to_destroy = {prop: None for prop in to_destroy}

        db_url = self.url + f"databases/{history}"

        if len(props_to_destroy) != 0:
            data = {"properties": props_to_destroy}
            make_call_with_retry(
                "patch",
                db_url,
                "delete destination database properties not in source database",
                data
            )

        new_prop = {}
        for prop in to_create:
            prop_dict = to_create[prop]
            prop_type = prop_dict["type"]
            new_prop = {prop: {prop_type: prop_dict[prop_type]}}

            data = {"properties": new_prop}
            make_call_with_retry(
                "patch",
                db_url,
                "create source properties in history database",
                data,
            )

    def get_project_list(self, database_id):
        notion_projects = self.get_db_structure(
            database_id
        )["Project"]["select"]["options"]
        return [project["name"] for project in notion_projects]

    def unpack_db_page(self, task: dict):
        unpacked_data = {}
        for prop in task["properties"]:
            prop_dict = task["properties"][prop]
            prop_type = prop_dict["type"]

            if prop == "Sub-item":
                pass
            match prop_type:
                case "title":
                    title = prop_dict[prop_type][0]["text"]["content"]
                    unpacked_data[prop] = {"title": [{"text": {"content": title}}]}
                case "multi_select":
                    tag_list = [
                        {"name": select["name"]} for select in prop_dict[prop_type]
                    ]
                    unpacked_data[prop] = {prop_type: tag_list}
                case "select":
                    if prop_dict[prop_type] != None:
                        unpacked_data[prop] = {
                            prop_type: {"name": prop_dict[prop_type]["name"]}
                        }
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
                        unpacked_data[prop] = {
                            "rich_text": [{"text": {"content": content}}]
                        }
                case "relation":
                    pass
        return unpacked_data

    def recreate_task(self, task: dict, parent: str):
        pages_url = self.url + "pages"
        new_props = self.unpack_db_page(task)
        data = {"parent": {"database_id": parent}, "properties": new_props}
        make_call_with_retry(
            "post",
            pages_url,
            f'recreate task {task["properties"]["Name"]["title"][0]["text"]["content"]} in destination database',
            data
        )

    def task_data_filter(self, query: str, arg_one: str = None, arg_two: str = None):
        data = {}
        if query == "Done":
            if arg_one == "status":
                data = {"filter": {"property": arg_two, "status": {"equals": "Done"}}}
            else:
                data = {"filter": {"property": arg_two, "checkbox": True}}
        elif query == "Time":
            data = {
                "filter": {
                    "timestamp": "last_edited_time",
                    "last_edited_time": {"on_or_after": arg_one},
                }
            }
        elif query == "Name":
            data = {"filter": {"property": "Name", "rich_text": {"equals": arg_one}}}
        return data

    def get_tasks(self, project: str, double_list: bool = False, history: bool = False):
        tasks_url = (
            self.url + f'databases/{self.config.data["notion"]["task_db"]}/query'
        )
        if history:
            tasks_url = (
                self.url + f'databases/{self.config.data["notion"]["history"]}/query'
            )
        if project == "Done":
            data = self.task_data_filter(
                "Done", self.reset_prop_type, self.reset_prop_name
            )
            url_info = "get all completed tasks"
        elif project == "Time":
            data = self.task_data_filter(
                "Time", self.config.data["system"]["locked"]["notion_sync"]
            )
            url_info = "get all completed tasks"
        elif project not in self.config.data["clockify"]["projects"]["name"].keys():
            data = self.task_data_filter("Name", project)
            url_info = f"check for task {project}"
        else:
            data = {"filter": {"property": "Project", "select": {"equals": project}}}
            url_info = f"get all tasks in notion project: {project}"
        tasks = make_call_with_retry(
            "post", 
            tasks_url, 
            url_info,
            data
        )
        if double_list:
            if self.reset_prop_type == "status":
                task_list = [
                    task
                    for task in tasks
                    if task["properties"][self.reset_prop_name]["status"]["name"]
                    != "Done"
                ]
                done_list = [
                    task
                    for task in tasks
                    if task["properties"][self.reset_prop_name]["status"]["name"]
                    == "Done"
                ]
            if self.reset_prop_type == "checkbox":
                task_list = [
                    task
                    for task in tasks
                    if task["properties"][self.reset_prop_name]["checkbox"] == False
                ]
                done_list = [
                    task
                    for task in tasks
                    if task["properties"][self.reset_prop_name]["checkbox"] == True
                ]
            return task_list, done_list
        else:
            return tasks

    def update_page(self, data: dict, page_id: str, name: str):
        page_url = self.url + f"pages/{page_id}"
        make_call_with_retry(
            "patch", 
            page_url, 
            f"updating notion page {name}", 
            data
        )

    def create_page(self, data: dict):
        page_url = self.url + f"pages"
        make_call_with_retry(
            "post",
            page_url,
            f'creating notion page {data["properties"]["Name"]["title"][0]["text"]["content"]}',
            data
        )

    def check_for_page(self, name):
        page_url = self.url + f'databases/{self.config.data["notion"]["task_db"]}/query'
        data = self.task_data_filter("Name", name)
        page = make_call_with_retry(
            "post",
            page_url,
            f"looking for notion page {name} in source database",
            data,
        )
        return page
