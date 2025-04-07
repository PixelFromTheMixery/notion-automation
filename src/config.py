from utils.helper import list_options, multi_options

import pytz, yaml
from datetime import datetime

class Config:
    instance = None
    initialized = False  
    file_path = "settings.yaml" 
    data = {}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance  

    def __init__(self):
        if not Config.initialized:
            Config.initialized = True

    def set_utils(self, util_type: str, utils):
        if util_type == "notion":
            self.notion_utils = utils
        if util_type == "clockify":
            self.clockify_utils = utils

    def set_key(self, service:str):
        if service == "notion":
            self.data["system"]["notion_key"] = input("Paste your Notion API key: ")
        elif service == "clockify":
            self.data["system"]["clockify_key"] = input("Paste your Clockify API key: ")
        self.save_to_yaml(f"{service.capitalize()} key saved")

    def set_timezone(self):
        timezones = [zone for zone in pytz.all_timezones]
        self.data["system"]["timezone"] = list_options(
            timezones,
            "Enter the number of the timezone: ",
            "Please select your timezone: ",
        )["name"]
        self.save_to_yaml(f'Timezone saved to {self.data["system"]["timezone"]}')

    def set_sync(self, service):
        datetime_obj = datetime.now(pytz.timezone(self.data["system"]["timezone"]))
        if service == "notion":
            self.data["system"]["locked"]["notion_sync"] = datetime_obj.isoformat()
        elif service == "clockify":
            self.data["system"]["locked"]["clockify_sync"] = datetime_obj.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        self.save_to_yaml(f"{service.capitalize()} sync saved")

    def select_from_list(self, list_name):
        message = ""
        if list_name == "notion_user":
            self.data["notion"]["user"] = list_options(
                self.notion_utils.get_users(),
                "Enter the number of the user: ",
                "Please select your name:",
            )["id"]
            message = "Notion user saved"

        elif list_name == "notion_source":
            self.data["notion"]["task_db"] = list_options(
                self.notion_utils.get_databases(),
                "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved from/synced to:",
                "notion",
            )["id"]
            message = "Notion source database saved"

        elif list_name == "notion_history":
            self.data["notion"]["log"]["history"] = list_options(
                self.notion_utils.get_databases(),
                "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved to:",
                "notion",
            )["id"]
            message = "Notion history database saved"

        elif list_name == "clockify_workspace":
            self.data["clockify"]["workspace"] = list_options(
                [self.clockify_utils.get_workspaces()],
                "Enter the number of the workspace: ",
                "Please select the workspace you'd like to sync with: ",
            )["id"]
            message = "Clockify workspace saved"

        elif list_name == "clockify_user":
            self.data["clockify"]["user"] = list_options(
                self.clockify_utils.get_users(),
                "Enter the number of the user: ",
                "Please select your name:",
            )["id"]
            message = "Clockify user saved"

        self.save_to_yaml(message)

    def multiselect_from_list(self, list_name):
        message = ""
        if list_name == "notion_prop_sync":
            props = self.notion_utils.get_db_structure(self.data["notion"]["task_db"])
            prop_list = [prop for prop in props if prop]
            self.data["notion"]["log"]["sync_props"] = multi_options(
                prop_list,
                "List the properties: ",
                "Select which properties you'd like to sync: ",
            )
            message = "Notion sync props saved"
        self.save_to_yaml(message)

    def setup(self, setup_values):
        print("File not found, making fresh file")
        self.data["system"] = {"locked": {}}
        self.set_timezone()
        self.data["notion"] = {}
        self.set_sync("notion")
        self.data["system"]["locked"]["notion_url"] = "https://api.notion.com/v1/"
        self.set_key("notion")
        if "clockify" in setup_values:
            self.data["system"]["locked"][
                "clockify_url"
            ] = "https://api.clockify.me/api/v1/workspaces"
            self.set_key("clockify")
            self.set_sync("clockify")
        self.save_to_yaml("Boilerplate complete")

    def notion_reset_prop(self):
        properties = self.notion_utils.get_db_structure(self.data["notion"]["task_db"])
        prop_list = [properties[prop] for prop in properties if properties[prop]["type"] in ["status","checkbox"]]
        status_prop = properties[list_options(
            prop_list,
            "Enter the number of the property: ",
            "Please select the property you want to use to track completion of a task:"
        )["name"]]

        reset_text = "Not started"
        if status_prop["type"] == "status":    
            reset_text = list_options(
                status_prop["status"]["options"],
                "Enter the number of the option: ",
                "Please select the reset option you would like for repeating tasks",
            )["name"]
        self.data["notion"]["log"]["reset_prop"] = {
            "name": status_prop["name"],
            "type": status_prop["type"],
            "text": reset_text,
        }
        self.save_to_yaml("Notion reset property set")

    def notion_logging(self):
        log = input("Would you like to log completed tasks (y/n)? ")
        if log == "y":
            self.data["notion"]["log"] = {}
            self.data["notion"]["log"]["active"] = True
            self.select_from_list("notion_history")
            self.multiselect_from_list("notion_prop_sync")
            self.notion_utils.match_db_structure()
            self.notion_reset_prop()
        else:
            self.data["notion"]["log"]["active"] = False

        self.save_to_yaml(
            f"Notion logging set to {self.data["notion"]["log"]["active"]}"
        )

    def setup_notion(self):
        self.select_from_list("notion_user")
        self.notion_logging()

    def clockify_clients(self):
        if "clients" not in self.data["clockify"].keys():
            self.data["clockify"]["clients"] = {}
        clients = self.clockify_utils.get_clients()
        for client in clients:
            self.data["clockify"]["clients"][client["id"]] = client["name"]

        self.save_to_yaml("Clockify clients saved")

    def clockify_projects(self):
        if "name" or "id" not in self.data["clockify"]["projects"].keys():
            self.data["clockify"]["projects"] = {"name": {}, "id": {}}
        projects = self.clockify_utils.get_projects()
        for project in projects:
            if not project["archived"]:
                self.data["clockify"]["projects"]["name"][project["name"]] = {
                    "id": project["id"],
                    "client": self.data["clockify"]["clients"][project["clientId"]],
                }
                self.data["clockify"]["projects"]["id"][project["id"]] = {
                    "name": project["name"],
                    "client": self.data["clockify"]["clients"][project["clientId"]],
                }

        self.save_to_yaml("Clockify projects setup")

    def setup_clockify(self):
        if "clockify" not in self.data.keys():
            self.data["clockify"] = {}

        self.select_from_list("clockify_workspace")
        self.select_from_list("clockify_user")
        self.clockify_clients()
        self.clockify_projects()

    def change_settings(self):
        settings = True
        settings_list = [key for key in self.data.keys()]
        settings_list.append("quit")
        while settings == True:
            setting_type = list_options(
                settings_list,
                "Enter the number of the option: ",
                "Please select the type of setting you'd like to change:",
                "basic",
            )

            if setting_type == "clockify":
                clockify_list = [key for key in self.data["clockify"].keys()]
                clockify_list.append("go back")
                clockify_setting = list_options(
                    clockify_list,
                    "Enter the number of the option: ",
                    "Please select the type of setting you'd like to change:",
                    "basic",
                )

                if clockify_setting == "projects":
                    self.clockify_projects()

                elif clockify_setting == "user":
                    self.select_from_list("clockify_user")

                elif clockify_setting == "workspace":
                    self.select_from_list("clockify_workspace")

                elif clockify_setting == "go back":
                    pass

            elif setting_type =="notion":
                notion_list = [key for key in self.data["notion"].keys()]
                notion_list.append("go back")
                notion_setting = list_options(
                    notion_list,
                    "Enter the number of the option: ",
                    "Please select the type of setting you'd like to change:",
                    "basic",
                )
                if notion_setting == "log":
                    self.notion_logging()

                elif notion_setting == "task_db":
                    self.select_from_list("notion_source")

                elif notion_setting == "user":
                    self.select_from_list("notion_user")

                elif notion_setting == "go back":
                    pass

            elif setting_type == "system":
                system_list = [key for key in self.data["system"].keys()]
                system_list.append("go back")
                system_setting = list_options(
                    system_list,
                    "Enter the number of the option: ",
                    "Please select the type of setting you'd like to change:",
                    "basic",
                )

                if system_setting == "clockify_key":
                    self.set_key("clockify")
                if system_setting == "locked":
                    print("Editing unadvised")
                elif system_setting == "notion_key":
                    self.set_key("notion")
                elif system_setting == "timezone":
                    self.set_timezone()
                elif system_setting == "go back":
                    pass

            elif setting_type == "quit":
                break

    def save_to_yaml(self, message):
        with open(Config.file_path, "w") as f:
            yaml.dump(self.data, f)
        print(message)
