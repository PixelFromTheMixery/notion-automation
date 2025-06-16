from utils.api_tools import make_call_with_retry
from utils.instance import InstanceData

class TtimeUtils:
    def __init__(self):
        self.url = "https://api.trackingtime.co/api/v4/"
        self.data = InstanceData.load()
        
    async def get_users(self):
        user_url = self.url + "users"
        ttime_users = make_call_with_retry("get", user_url, "fetching ttime users")["data"]
        user_list = []
        for user in ttime_users:
            user_list.append({
                "id": user["id"],
                "name": f'{user["name"]} {user["surname"]}'
            })
        return user_list

    async def get_projects(self):
        project_url = self.url + "projects"
        ttime_projects = make_call_with_retry("get", project_url, "fetching ttime projects")["data"]
        project_list = []
        for project in ttime_projects:
            project_list.append({
                "name": project["name"],
                "archived": project["is_archived"],
                "category": project["customer"]["name"],
            })
        return project_list

    async def get_tasks(self):
        tasks_url = self.url = "tasks/paginated?include_custom_fields=true"
        ttime_taskinfo = make_call_with_retry("get", tasks_url, "fetching ttime tasks")
        ttime_tasks = ttime_taskinfo["data"]
        task_list = []
        for task in ttime_tasks:
            task_list.append({
                "name": task["name"],
                "project": task["project"],
                "category": task["customer"],
                "id": task["id"],
                "archived": task["is_archived"],
                "properties": {}
            })
        
        ttime_fields = ttime_taskinfo["set_custom_fields"]
        for task in task_list:
            for field in ttime_fields:
                if task["id"] == field["task_id"]:
                    pass

    async def create_enum_option(self, field_id, option_name):
        fields_url = self.url + f"enum_options/add/?index=0&enabled=true&color=0&custom_field={field_id}&name={option_name}"
        make_call_with_retry("post", fields_url, "creating ttime enum option")

    async def delete_custom_field(self, field_id):
        field_url = self.url + f"custom_fields/{field_id}/delete"
        make_call_with_retry("get", field_url, "deleting ttime custom field")

    async def create_custom_field(self, field_data):
        fields_url = self.url + "custom_fields/add/?"+ field_data
        return make_call_with_retry("post", fields_url, "creating ttime custom field")

    async def update_custom_field(self, field_id, field_data):
        fields_url = self.url + f"custom_fields/{field_id}/?{field_data}"
        make_call_with_retry("post", fields_url, "updating ttime custom field")

    async def get_custom_fields(self):
        fields_url = self.url + "custom_fields?include_enum_options=true"
        all_fields = make_call_with_retry("get", fields_url, "fetching ttime custom fields")["data"]
        fields_list = {}
        for field in all_fields:
            if field["type"] == None: 
                options = [option["name"] for option in field["enum_options"] if field["enum_options"] != []]
                fields_list[field["name"]]= {
                    "id": field["id"],
                    "type": field["value_type"],
                    "enum_options": options,
                    "object": field["filter_object_class"]
                }
        return fields_list