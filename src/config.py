from utils.helper import list_options

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

    def set_key(self, service:str):
        if service == "notion":
            self.data["system"]["notion_key"] = input("Paste your Notion API key: ")
        elif service == "clockify":
            self.data["system"]["clockify_key"] = input("Paste your Clockify API key: ")
        self.save_to_yaml()    

    def set_time(self):
        timezones = [{"name":zone} for zone in pytz.all_timezones]
        self.data["system"]["timezone"] = list_options(
            timezones,
            "Enter the number of the timezone: ",
            "Please select your timezone: ",
        )["name"]
        self.save_to_yaml()

    def select_from_list(self, utils, list_name):
        if list_name == "notion_user":
            self.data["notion"]["user"] = list_options(
                utils.get_users(),
                "Enter the number of the user: ",
                "Please select your name:"
            )["id"]
        
        elif list_name == "notion_master":
            self.data["notion"]["task_db"] = list_options(
                utils.get_databases(),
                "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved from:",
                "notion"
            )["id"]
        
        elif list_name == "notion_history":
            self.data["notion"]["history"] = list_options(
                utils.get_databases(),
                "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved to:",
                "notion"
            )["id"]
        
        elif list_name == "clockify_workspace":
            self.data["clockify"]["workspace"] = list_options(
                utils.get_workspaces(),
                "Enter the number of the workspace: ",
                "Please select the workspace you'd like to sync with: ",
            )["id"]
        
        elif list_name == "clockify_user":
            self.data["clockify"]["user"] = list_options(
                utils.get_users(self.data["clockify"]["workspace"]),
                "Enter the number of the user: ",
                "Please select your name:"
            )["id"]
            
        self.save_to_yaml()

    def setup(self, setup_values):
        print("File not found, making fresh file")
        self.data["system"] = {}
        self.set_time()
        self.data["system"]["notion_url"] = "https://api.notion.com/v1"
        self.set_key("notion")
        if "clockify" in setup_values:
            self.data["system"]["clockify_url"] = "https://api.clockify.me/api/v1/workspaces"
            self.set_key("clockify")
        self.save_to_yaml()

    def set_master_db(self, notion_utils):
        if "notion" not in self.data.keys():
            self.data["notion"] = {}
        self.select_from_list(notion_utils, "notion_master")

    def notion_reset_prop(self, notion_utils):
        properties = notion_utils.get_db_structure(self.data["notion"]["task_db"])
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
        self.data["notion"]["reset_prop"] = {
            "name": status_prop["name"],
            "type": status_prop["type"],
            "text": reset_text
        }
        self.save_to_yaml()

    def setup_mover(self, notion_utils):
        if "mover" not in self.data["notion"].keys():
            self.data["notion"] = {}
        self.select_from_list(notion_utils, "notion_user")        
        self.select_from_list(notion_utils, "notion_history")
        self.notion_reset_prop(notion_utils)

    def clockify_projects(self, clockify_utils):
        projects = clockify_utils.get_projects(self.data["clockify"]["workspace"])
        self.data["clockify"]["projects"] = {
            project["name"]: project["id"]
            for project in projects
            if not project["archived"]
        }
        self.save_to_yaml()

    def setup_clockify(self, clockify_utils):
        if "clockify" not in self.data.keys():
            self.data["clockify"] = {}

        self.select_from_list(clockify_utils, "clockify_workspace")    
        self.select_from_list(clockify_utils, "clockify_user")
        self.clockify_projects(clockify_utils)        

    def change_settings (self, notion_utils = None, clockify_utils = None):
        settings = True
        settings_list = [{"name": key} for key in self.data.keys()]
        settings_list.append({"name":"quit"})
        while settings == True:
            setting_type = list_options(
                settings_list,
                "Enter the number of the option: ",
                "Please select the type of setting you'd like to change:",
            )["name"]

            if setting_type == "clockify":
                clockify_list = [{"name": key} for key in self.data["clockify"].keys()]
                clockify_list.append({"name":"go back"})
                clockify_setting = list_options(
                    clockify_list,
                    "Enter the number of the option: ",
                    "Please select the type of setting you'd like to change:",
                )["name"]

                if clockify_setting == "projects":
                    self.clockify_projects(clockify_utils)

                elif clockify_setting == "user":
                    self.select_from_list(clockify_utils, "clockify_user")

                elif clockify_setting == "workspace":
                    self.select_from_list(clockify_utils, "clockify_workspace")
                
                elif clockify_setting == "go back":
                    break
            
            elif setting_type =="notion":
                notion_list = [{"name": key} for key in self.data["notion"].keys()]
                notion_list.append({"name":"go back"})
                notion_setting = list_options(
                    notion_list,
                    "Enter the number of the option: ",
                    "Please select the type of setting you'd like to change:",
                )["name"]
                if notion_setting == "history":
                    self.select_from_list(notion_utils, "notion_history")

                elif notion_setting == "reset_prop":
                    self.notion_reset_prop(notion_utils)

                elif notion_setting == "go back":
                    break
            
            elif setting_type == "system":
                system_list = [{"name": key} for key in self.data["system"].keys()]
                system_list.append({"name":"go back"})
                system_setting = list_options(
                    system_list,
                    "Enter the number of the option: ",
                    "Please select the type of setting you'd like to change:",
                )["name"]

                if system_setting == "clockify_key":
                    self.set_key("clockify")
                elif system_setting == "clockify_url":
                    print("clockify_url setting locked, manually edit at own risk")
                elif system_setting == "notion_key":
                    self.set_key("notion")
                elif system_setting == "notion_url":
                    print("notion_url setting locked, manually edit at own risk")
                elif system_setting == "timezone":
                    self.set_time()
                elif system_setting == "go back":
                    break
            
            elif setting_type == "quit":
                break
    
    def save_to_yaml(self):
        with open(Config.file_path, "w") as f:
            yaml.dump(self.data, f)
        print("State saved")
