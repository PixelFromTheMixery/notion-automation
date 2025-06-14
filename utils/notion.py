from models.databases import Databases, Database
from models.task import Task
from models.users import Users
from utils.api_tools import make_call_with_retry
from utils.instance import InstanceData

class NotionUtils:
    def __init__(self):
        self.url = "https://api.notion.com/v1/"
        self.data = InstanceData.load()
        self.reset_name = self.data.databases["tasks"]["reset_name"]
        self.reset_type = self.data.databases["tasks"]["reset_type"]
        self.reset_value = self.data.databases["tasks"]["reset_value"]

    async def get_users(self):
        user_url = self.url + "users"
        notion_users = make_call_with_retry(
            "get", user_url, "get users from notion"
        )
        user_list = []
        for user in notion_users:
            user_list.append({
                "name": user["name"],
                "id": user["id"],
                "type": user["type"],
            })
        return Users(users=user_list)

    async def get_databases(self):
        data = {"filter": {"value": "database", "property": "object"}}
        search_url = self.url + "search"
        notion_databases = make_call_with_retry(
            "post", search_url, "fetch databases for selection", data
        )
        databases = []
        for database in notion_databases:
            database_obj = {
                "id": database["id"],
                "title": database["title"][0]['text']['content'],
                "properties": []
            }
            for prop in database["properties"]:
                prop_type = database["properties"][prop]["type"]
                prop_obj = {
                   "name": database["properties"][prop]["name"],
                   "type": prop_type,
                }
                if prop_type in ["status", "select", "multi_select"]:
                    prop_obj["possible_values"] = database["properties"][prop][prop_type]["options"]
                database_obj["properties"].append(prop_obj)
            databases.append(database_obj)
        return Databases(databases=databases)

    async def get_database(self, database_id, obj: bool = False):
        database_url = self.url + f"databases/{database_id}"
        notion_database = make_call_with_retry(
            "get", database_url, "fetch databases for selection"
        )
        database = {
            "id": database_id,
            "title": notion_database["title"][0]['text']['content'],
            "properties": {}
        }
        for prop in notion_database["properties"]:
            prop_name = notion_database["properties"][prop]["name"]
            prop_type = notion_database["properties"][prop]["type"]
            prop_dict = { prop_type : {}}
            if prop_type in ["status", "select", "multi_select"]:
                prop_dict["options"] = notion_database["properties"][prop][prop_type]["options"]
            database["properties"][prop_name] = prop_dict
        if obj: return Database(**database)
        else: return database

    def match_db_structure(self, source, target):
        to_create = {
            k: source["properties"][k]
            for k in source["properties"]
            if k not in target["properties"]
            and k != "relation"
        }
        to_destroy = {
            k: target["properties"][k]
            for k in target["properties"]
            if k not in source["properties"]
        }

        props_to_destroy = {prop: None for prop in to_destroy}

        db_url = self.url + f"databases/{target['id']}"


        if len(props_to_destroy) != 0:
            data = {"properties": props_to_destroy}
            make_call_with_retry(
                "patch",
                db_url,
                "delete destination database properties not in source database",
                data
            )

        for prop in to_create:
            data = {"properties": {prop: to_create[prop]}}
            make_call_with_retry(
                "patch",
                db_url,
                "create source properties in history database",
                data,
            )

    async def get_page(self, page_id):
        page_url = self.url + f"pages/{page_id}"
        notion_page = make_call_with_retry("get", page_url, f"fetch page")
        
        if notion_page["parent"]["type"] == "database_id":
            page = {
                "id": page_id,
                "name": notion_page["properties"]["Name"]["title"][0]['text']['content'],
                "properties": {}
            }
            page_details = self.extract_page_props(notion_page)
            page["properties"] = page_details['props']
        else:
            page = {
                "id": page_id,
                "name": notion_page["properties"]["title"]["title"][0]['text']['content'],
                "properties": {},
                "contents": self.get_page_contents(page_id)
            }
        return Task(**page)

    def get_page_contents(self, page_id):
        children_url = self.url + f"blocks/{page_id}/children"
        children = make_call_with_retry("get", children_url, f"fetch page contents")
        return children

    def extract_page_props(self, task:dict):
        extracted_props = {}
        for prop in task["properties"]:
            prop_dict = task["properties"][prop]
            prop_type = prop_dict["type"]

            if prop_type in ["relation", "last_edited_time", "created_time"]:
                pass

            elif prop_type in ["checkbox", "number", "self.url"]:
                extracted_props[prop] = prop_dict[prop_type]

            elif prop_type in ["select", "status"]:
                extracted_props[prop] = prop_dict[prop_type]["name"]

            elif prop_type == "date":
                extracted_props[prop] = prop_dict[prop_type]["start"]

            elif prop_type == "people":
                extracted_props[prop] = prop_dict[prop_type][0]["id"]

            elif prop_type == "title":
                extracted_props[prop] = prop_dict[prop_type][0]["text"]["content"]

            elif prop_type == "multi_select":
                extracted_props[prop] = [select["name"] for select in prop_dict[prop_type]]

            elif prop_type == "rich_text":
                if prop_dict[prop_type] != []:
                    extracted_props[prop] = prop_dict[prop_type][0]["text"]["content"]

        return {"props": extracted_props}


    def db_page_to_dict(self, task: dict):
        unpacked_props = {}

        for prop in task["properties"]:
            prop_dict = task["properties"][prop]
            prop_type = prop_dict["type"]

            if prop_dict[prop_type] is None:
                pass

            elif prop_type in ["checkbox", "number", "self.url", "date"]:
                unpacked_props[prop] = {prop_type: prop_dict[prop_type]}

            elif prop_type in ["select", "status"]:
                unpacked_props[prop] = {
                    prop_type: {"name": prop_dict[prop_type]["name"]}
                }

            elif prop_type == "people_unused":
                people_list = [
                    {"object": "user", "id": user["id"]}
                    for user in prop_dict[prop_type]
                ]
                unpacked_props[prop] = {"people": people_list}

            elif prop_type == "title":
                title = prop_dict[prop_type][0]["text"]["content"]
                unpacked_props[prop] = {"title": [{"text": {"content": title}}]}

            elif prop_type == "multi_select":
                tag_list = [{"name": select["name"]} for select in prop_dict[prop_type]]
                unpacked_props[prop] = {prop_type: tag_list}

            elif prop_type == "rich_text":
                if prop_dict[prop_type] != []:
                    content = prop_dict[prop_type][0]["text"]["content"]
                    unpacked_props[prop] = {
                        "rich_text": [{"text": {"content": content}}]
                    }
            elif prop_type == "relation":
                pass

        if task["properties"]["Notes"]["checkbox"] == True:
            page_contents = self.get_page_contents(task["id"])
            return {"props": unpacked_props, "contents": page_contents}
        else:
            return {"props": unpacked_props}

    def recreate_task(self, task: dict, parent: str):
        pages_url = self.url + "pages"
        page = self.db_page_to_dict(task)
        new_page = {
            prop: page["props"][prop]
            for prop in page["props"]
        }
        data = {
            "parent": {"database_id": parent},
            "properties": new_page,
        }

        if "contents" in page.keys():
            data["children"] = page["contents"]

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
        elif query == "Overdue":
            data = {
                "filter": {
                    "property": "Due Date",
                    "date": {"before": arg_one},
                }
            }
        elif query == "Name":
            data = {"filter": {"property": "Name", "rich_text": {"equals": arg_one}}}
        return data

    def get_tasks(self, project: str, optional: str = None, double_list: bool = False, history: bool = False):
        tasks_url = (
            self.url + f'databases/{self.data.databases["tasks"]["id"]}/query'
        )
        if history:
            tasks_url = (
                self.url
                + f'databases/{self.data.databases["log"]}/query'
            )
        if project == "Done":
            data = self.task_data_filter(
                project, self.reset_type, self.reset_name
            )
            url_info = "get all completed tasks"
        elif project == "Overdue":
            data = self.task_data_filter(
                project, optional
            )
            url_info = "get all overdue tasks"
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
