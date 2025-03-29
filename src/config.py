from utils.helper import list_options

import yaml

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

    def setup(self, setup_values):
        print("File not found, making fresh file")
        self.data["system"] = {}
        self.data["system"]["notion_url"] = "https://api.notion.com/v1/"
        self.data["system"]["notion_key"] = input("Paste your Notion API key: ")
        if "clockify" in setup_values:
            self.data["system"]["clockify_url"] = "https://api.clockify.me/api/v1/workspaces"
            self.data["system"]["clockify_key"] = input("Paste your Clockify API key: ")
        self.save_to_yaml()

    def set_master_db(self, notion_utils):
        if "notion" not in self.data.keys():
            self.data["notion"] = {}
        self.data["notion"]["task_db"] = list_options(
            notion_utils.get_databases(),
            "Enter the number of the database: ",
            "Please select the database you want completed tasks to be moved from:",
            "notion"
        )["id"]
        self.save_to_yaml()

    
    def setup_mover(self, notion_utils):
        if "mover" not in self.data["notion"].keys():
            self.data["notion"]["mover"] = {}

        self.data["notion"]["user"] = list_options(
                notion_utils.get_users(),
                "Enter the number of the user: ",
                "Please select your name:"
            )["id"]
        
        self.data["notion"]["mover"]["history"] = list_options(
                notion_utils.get_databases(),
                "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved to:",
                "notion"
            )["id"]

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
        self.data["notion"]["mover"]["name"] = status_prop["name"]
        self.data["notion"]["mover"]["type"] = status_prop["type"]
        self.data["notion"]["mover"]["text"] = reset_text
        self.save_to_yaml()
    
    def setup_clockify(self, clockify_utils):
        if "clockify" not in self.data.keys():
            self.data["clockify"] = {}

        workspaces = clockify_utils.get_workspaces()
        self.data["clockify"]["workspace"] = list_options(
            workspaces,
            "Enter the number of the workspace: ",
            "Please select the workspace you'd like to sync with: ",
        )["id"]
        
        users = clockify_utils.get_users(self.data["clockify"]["workspace"])
        self.data["clockify"]["user"] = list_options(
            users,
            "Enter the number of the user: ",
            "Please select your name:"
        )["id"]

        projects = clockify_utils.get_projects(self.data["clockify"]["workspace"])
        self.data.setdefault("clockify", {})["projects"] = {
            project["name"]: project["id"]
            for project in projects
            if not project["archived"]
        }
        
        self.save_to_yaml()
    
    def save_to_yaml(self):
        with open(Config.file_path, "w") as f:
            yaml.dump(self.data, f)
        print("State saved")
