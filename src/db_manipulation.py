from api_tools import make_call_with_retry
from datetime import datetime, timedelta

# Source and target database IDs
mt_source = "10d62907-d7c2-8036-8428-e8afc8ab261f" # Master Tasker
mt_dest = "14662907-d7c2-809f-beaf-e23c4eb5302b" # Master Tasker History

#mt_source = "14762907-d7c2-8062-922d-d8dde76da52b" # Test Source
#mt_dest = "14762907-d7c2-80b6-99e8-e860239cf3cd" # Test Dest

def get_databases(url:str):
    # Filter to search only for databases
    data = {
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    url += "search"
    databases = make_call_with_retry("post", url, data)["results"]
    for db in databases:
        print("ID:", db['id'])
        print("Name: ", db['title'][0]['text']['content'])
        print("-" *40)

def get_db_structure(url: str, source: bool):
    url += "databases/"
    if source:
        url += mt_source
    else:
        url += mt_dest
    struct = make_call_with_retry("get", url)['properties']
    for prop in struct:
        del struct[prop]['id']
    return struct

def match_mt_structure(url: str, source_struct: dict, dest_struct: dict):
    url += f"databases/{mt_dest}"
    props_to_destroy = {}
    
    # Create a dictionary where each property in dest_struct is a key, with None as its value
    props_to_destroy = {prop: None for prop in dest_struct}
    del props_to_destroy['Name']
    if len(props_to_destroy) != 0:
        data = {
            'properties': props_to_destroy
        }
        make_call_with_retry("patch", url, data)
    
    new_prop = {}
    for prop in source_struct:
        prop_dict = source_struct[prop]
        prop_type = prop_dict['type']
        new_prop = {
            prop: {prop_type: prop_dict[prop_type]}
        } 

        data = {
            'properties': new_prop
        }
        print()
        make_call_with_retry("patch", url, data)

def get_mt_tasks(url: str):
    url += f"databases/{mt_source}/query"
    data = {
        "filter": {
            "or": [
                {"property": "Every", "select": 
                    { "is_not_empty": True }
                },
            ]
        }
    }
    return make_call_with_retry("post", url, data)['results']

def unpack_db_page(url: str, task: dict):
    unpacked_data = {}
    for prop in task['properties']:
        prop_dict = task['properties'][prop]
        prop_type = prop_dict['type']
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
            case 'url':
                unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
            case 'date':
                unpacked_data[prop] = {prop_type: prop_dict[prop_type]}
            case 'rich_text':
                if prop_dict[prop_type] != []:
                    content = prop_dict[prop_type][0]['text']['content']
                    unpacked_data[prop] = { "rich_text": [{ "text": { "content": content }}]}
            case 'relation':
                if prop_dict[prop_type] != []:
                    page_id = prop_dict[prop_type][0]['id']
                    content = make_call_with_retry("get",f'{url}/pages/{page_id}')
                    unpacked_data[prop] = { "rich_text": [{ "text": { "content": content }}]}
    return unpacked_data

def create_task(url: str, task: dict, parent: str, task_name: str = None):
    url += "pages"
    new_props = unpack_db_page(url, task)
    data = {"parent": { "database_id": parent }, "properties": new_props}
    print(f"Creating task: {task_name}")
    make_call_with_retry("post", url, data)

def new_due_date (task:dict):
    now_datetime = datetime.now().replace(microsecond=0)
    freq = task['properties']['Repeats']['number']
    scale = task['properties']['Every']['select']['name']

    match scale:
        case "Days":
            new_start_datetime = now_datetime + timedelta(days=freq)
        case "Weeks":
            new_start_datetime = now_datetime + timedelta(weeks=freq)
        case "Months":
            # Add months manually
            new_month = (now_datetime.month - 1 + freq) % 12 + 1
            year_delta = (now_datetime.month - 1 + freq) // 12
            new_year = now_datetime.year + year_delta
            new_start_datetime = now_datetime.replace(year=new_year, month=new_month)
    new_due_value = new_start_datetime.strftime("%Y-%m-%dT%H:%M:%S.000%z")
    task['properties']['Due Date']['date']['start'] = new_due_value
    task['properties']['Done']['checkbox'] = False
    return task

def delete_or_reset_mt_task(url: str, task:dict):
    if task['properties']['Status']['select']['name'] == 'Reset':
        if task['properties']['Every']['select'] is not None:
            task = new_due_date(task)
        create_task(url, task, mt_source)
    
    url += f"pages/{task['id']}"
    data = {
        "in_trash": True
    }
    make_call_with_retry("patch", url, data)

def move_mt_tasks(url):
    tasks_to_move = get_mt_tasks(url)
    for task in tasks_to_move:
        task_name = task['properties']['Name']['title'][0]['text']['content']
        print(f"Moving task {task_name} to history")
        create_task(url, task, mt_dest, task_name)
        delete_or_reset_mt_task(url, task)