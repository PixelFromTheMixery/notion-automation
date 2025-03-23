from utils.api_tools import make_call_with_retry
from utils.files import read_json, write_json

class NotionUtils:
    def __init__(self):
        self.url = "https://api.notion.com/v1/"
        self.databases = {}
    
    def get_databases(self):
        # Filter to search only for databases
        data = {
            "filter": {
                "value": "database",
                "property": "object"
            }
        }
        self.url += "search"
        databases = make_call_with_retry("post", self.url, data)["results"]
        database_data = {"database list":[]}
        for db in databases:
            database = {}
            database["id"] = db['id']
            database["Name"]= db['title'][0]['text']['content']
            database_data['database list'].append(database)
        
        print('Please select the database you want completed tasks to be moved from:')
        for db in database_data['database list']:
            print(f"{database_data['database list'].index(db)+1}. {db['Name']}")
        source_db = int(input("Enter the number of the database: "))
        database_data['source'] = database_data['database list'][source_db-1]['id']

        print('Please select the database you want completed tasks to be moved to:')
        for db in database_data['database list']:
            print(f"{database_data['database list'].index(db)+1}. {db['Name']}")
        destination_db = int(input("Enter the number of the database: "))
        database_data['destination'] = database_data['database list'][destination_db-1]['id']
        
        write_json(database_data, "src/data/databases.json")
        self.databases = database_data

        return database_data

    def get_db_structure(self):
        try:
            self.databases = read_json("src/data/databases.json")
                
        except FileNotFoundError:
            self.databases = NotionUtils().get_databases()

        url = self.url+"databases/"
        
        source_url = url + self.databases["source"]
        source_struct = make_call_with_retry("get", source_url)['properties']
        for prop in source_struct:
            del source_struct[prop]['id']
        destination_url = url + self.databases["destination"]
        destination_struct = make_call_with_retry("get", destination_url)['properties']
        for prop in destination_struct:
            del destination_struct[prop]['id']
        return source_struct, destination_struct
        

    def match_mt_structure(self,source_struct: dict, dest_struct: dict):
        url = self.url+"databases/"
        url += f"{self.databases['destination']}"
        
        to_create = {k: source_struct[k] for k in source_struct if k not in dest_struct}
        to_destroy = {k: dest_struct[k] for k in dest_struct if k not in source_struct}
        
        props_to_destroy = {}
        
        # Create a dictionary where each property in dest_struct is a key, with None as its value
        props_to_destroy = {prop: None for prop in to_destroy}
        if len(props_to_destroy) != 0:
            data = {
                'properties': props_to_destroy
            }
            make_call_with_retry("patch", url, data)
        
        new_prop = {}
        for prop in to_create:
            prop_dict = to_create[prop]
            prop_type = prop_dict['type']
            new_prop = {
                prop: {prop_type: prop_dict[prop_type]}
            } 

            data = {
                'properties': new_prop
            }
            make_call_with_retry("patch", url, data)

    def unpack_db_page(self, task: dict):
        unpacked_data = {}
        for prop in task['properties']:
            prop_dict = task['properties'][prop]
            prop_type = prop_dict['type']

            if prop == 'Sub-item':
                print()
            match prop_type:
                case 'title':
                    title = prop_dict[prop_type][0]['text']['content']
                    unpacked_data[prop] = { "title": [{ "text": { "content": title }}]}
                case 'multi_select':
                    tag_list = [{'name': select['name']} for select in prop_dict[prop_type]]
                    unpacked_data[prop] = {prop_type: tag_list}
                case 'select':
                    if prop_dict[prop_type] != None:
                        unpacked_data[prop] = {prop_type: {'name': prop_dict[prop_type]['name']}}
                case 'checkbox':
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case 'number':
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case 'self.url':
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case 'date':
                    unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
                case 'rich_text':
                    if prop_dict[prop_type] != []:
                        content = prop_dict[prop_type][0]['text']['content']
                        unpacked_data[prop] = { "rich_text": [{ "text": { "content": content }}]}
                case 'relation':
                    if prop_dict[prop_type] != [] and prop != 'Sub-item':
                        page_id = prop_dict[prop_type][0]['id']
                        response = make_call_with_retry("get",f'{self.url}/{page_id}')
                        page_name = response['properties']['Name']['title'][0]['text']['content']
                        unpacked_data[prop] = { "rich_text": [{ "text": { "content": page_name }}]}
        return unpacked_data