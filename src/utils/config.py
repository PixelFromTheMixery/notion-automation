from utils.files import write_yaml
from utils.helper import list_options

class Config:
    def __init__(self):
        self.notion_url = "https://api.notion.com/v1/"
        self.clockify_url = "https://api.clockify.me/api/v1/"
    
    def setup(self, settings: dict, services: list, databases=None):
        if "mover" in services:
            if "notion" not in settings.keys():
                settings["notion"] = {}
            
            notion_dbs = [{"name":name} for name in databases]
            
            settings["notion"]["source"] = databases[list_options(
                notion_dbs, "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved from:"
                )]

            settings["notion"]["destination"] = databases[list_options(
                notion_dbs, "Enter the number of the database: ",
                "Please select the database you want completed tasks to be moved to:"
                )]
            
            # Notion Settings
            prop_name = input("Enter the name of the property to check for completion: ")
            settings["notion"]["prop_name"] = prop_name
            checkbox = bool(input("Does this property use a checkbox? (1 for yes, 0 for no): "))
            if checkbox:
                settings["notion"]["checkbox"] = False
                reset_text = input("Enter the name of the option you'd like to reset the status to: ")
                settings["notion"]["reset_text"] = reset_text
            elif checkbox:
                settings["notion"]["checkbox"] = True
                settings["notion"]["reset_text"] = "Not started"
        write_yaml(settings, "src/data/settings.yaml")