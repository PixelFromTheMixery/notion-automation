from utils.api_tools import make_call_with_retry
from utils.instance import InstanceData
from utils.notion import NotionUtils
from utils.ttime import TtimeUtils

import copy

class TtimeService:

    def __init__(self):
        self.data = InstanceData.load()
        self.ttime = TtimeUtils()
        self.notion = NotionUtils()
    
    def convert_property_type(self, prop_type):
        type_mapping = {
            "checkbox": "boolean",
            "select": "enum",
            "rich_text":"text",
            "url": "text",
            "number":"number"
        }
        return type_mapping.get(prop_type, prop_type)
    
    def match_notion_props(self, level, notion_props):
        matched_notion_props = {}
        for notion_name, prop in notion_props:
            notion_type = list(prop.keys())[0]
            prop_dict = {}
            if notion_name in ["Category", "Project", "DoD"]:
                continue
            if notion_type in ["checkbox", "select", "rich_text", "url", "number"]:
                prop_dict = {
                    "object": level,
                    "type": self.convert_property_type(notion_type),
                    "enum_options": []
                }
            if notion_type == "select":
                for option in prop["options"]:
                    prop_dict["enum_options"].append(option["name"])

            if prop_dict != {}:
                matched_notion_props[notion_name]=prop_dict
        return matched_notion_props
    
    async def update_custom_fields(self, level):
        ttime_fields_id = await self.ttime.get_custom_fields()
        ttime_fields = copy.deepcopy(ttime_fields_id)
        for props in ttime_fields.values():
            del props["id"]
        notion_db = await self.notion.get_database(self.data.databases["tasks"]["id"])
        matched_notion_props = self.match_notion_props(level, notion_db["properties"].items())

        to_create = [prop for prop in matched_notion_props if prop not in ttime_fields]
        to_delete = [field for field in ttime_fields if field not in matched_notion_props]

        to_update = []
        for prop in matched_notion_props:
            if prop in to_create or prop in to_delete:
                continue
            if ttime_fields[prop] == matched_notion_props[prop]:
                continue
            else: 
                to_update.append(prop)
        
        for field in to_delete:
            self.ttime.delete_custom_field(field)
        
        field_data = "filter_object_class=" + level
        
        for field in to_create:
            field_data += "&name=" + field
            field_data += "&value_type=" + matched_notion_props[field]["type"]
            result = await self.ttime.create_custom_field(field_data)
            if matched_notion_props[field]["type"] == "enum":
                for option in matched_notion_props[field]["enum_options"]:
                    try:
                        await self.ttime.create_enum_option(result["data"]["id"], option)
                    except Exception as e:
                        print(f"Error creating enum option {option} for field {field}: {e}")
                        continue
        
        for field in to_update:
            if matched_notion_props[field]["type"] == "enum":
                for option in matched_notion_props[field]["enum_options"]:
                    try:
                        await self.ttime.create_enum_option(ttime_fields_id[field]["id"], option)
                    except Exception as e:
                        print(f"Error creating enum option {option} for field {field}: {e}")
                        continue
        

        fields = await self.ttime.get_custom_fields()

        self.data.ttime["custom_fields"] = fields
        self.data.save()