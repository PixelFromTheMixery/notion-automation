from utils.files import write_yaml

class Config:
    def __init__(self):
        self.notion_url = "https://api.notion.com/v1/"
        self.clockify_url = "https://api.clockify.me/api/v1/"
    
    def setup(self, settings: dict, services: list):
        if "notion" in services:
            notion_dbs = settings['notion']['database list']
            
            # Database selection for source and destination
            print('Please select the database you want completed tasks to be moved from:')
            for db in notion_dbs:
                print(f"{notion_dbs.index(db)+1}. {db['name']}")
            source_db = int(input("Enter the number of the database: "))
            settings['notion']['source'] = notion_dbs[source_db-1]['id']

            print('Please select the database you want completed tasks to be moved to:')
            for db in notion_dbs:
                print(f"{notion_dbs.index(db)+1}. {db['name']}")
            destination_db = int(input("Enter the number of the database: "))
            settings['notion']['destination'] = notion_dbs[destination_db-1]['id']

            # Notion Settings
            prop_name = input("Enter the name of the property to check for completion: ")
            settings['notion']['prop_name'] = prop_name
            checkbox = bool(input("Does this property use a checkbox? (1 for yes, 0 for no): "))
            if checkbox:
                settings['notion']['checkbox'] = False
                reset_text = input("Enter the name of the option you'd like to reset the status to: ")
                settings['notion']['reset_text'] = reset_text
            elif checkbox:
                settings['notion']['checkbox'] = True
                settings['notion']['reset_text'] = "Not started"

        write_yaml(settings, "src/data/settings.yaml")