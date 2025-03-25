import sys
import argparse
from clockify.clockify_sync import ClockifySync
from clockify.clockify_utils import ClockifyUtils
from notion.move_tasks import MoveTasks
from notion.notion_utils import NotionUtils
from utils.config import Config
from utils.files import read_yaml
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Notion Automation Python Script with CLI flags")
    
    parser.add_argument(
        "-s", "--setup",
        type=str,
        help="Set up the Notion and Clockify API keys"
    )
    
    parser.add_argument(
        "-dbm", "--dbmatch",
        action="store_true",
        help="Ensure notion database synchronicity"
        )
    
    parser.add_argument(
        "-m", "--move",
        action="store_true",
        help="Move tasks from one database to another"
        )
    
    parser.add_argument(
        "-c", "--clockify",
        action="store_true",
        help="Clockify Integration"
        )

    parser.add_argument(
        "-t", "--test",
        action="store_true",
        help="Test Ground"
        )

    args = parser.parse_args()

    config = Config()
    notion_utils = NotionUtils()
    task_mover = MoveTasks()
    clockify_utils = ClockifyUtils()
    clockify_sync = ClockifySync()

    try:
        if args.setup:
            try:
                settings = read_yaml("src/data/settings.yaml")
            except FileNotFoundError:
                settings = {}
            setup_values = args.setup.split(",")
            if "mover" in setup_values:
                databases = notion_utils.get_databases(settings)
            if "clockify" in setup_values:
                settings = clockify_utils.setup_clockify(settings)
                
            config.setup(settings, setup_values, databases)
            source, dest = notion_utils.get_db_structure(settings)
            settings = clockify_utils.get_projects(settings)
            settings = clockify_sync.project_sync(clockify_utils, settings)
  
        else:
            settings = read_yaml("src/data/settings.yaml")
        
        if args.dbmatch:
            source, dest = notion_utils.get_db_structure(settings)
            notion_utils.match_mt_structure(settings["notion"]["destination"], 
                                            source, dest)
        
        if args.clockify:
            clockify_sync.task_sync(clockify_utils, notion_utils, settings)
        
        if args.move:
            task_mover.move_mt_tasks(notion_utils, settings)

        if args.test:
            pass
            
        if not any(vars(args).values()):
            print("No flags provided. Please provide a flag to run a specific function.")
            parser.print_help()

    except FileNotFoundError as e:
        print(f"Settings file not found. Please rerun with '-s' or '--setup' flag: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
    
    