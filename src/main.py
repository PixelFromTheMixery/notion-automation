import sys
import argparse
from clockify.clockify_sync import ClockifySync
from clockify.clockify_utils import ClockifyUtils
from notion.move_tasks import MoveTasks
from notion.notion_utils import NotionUtils
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


    args = parser.parse_args()
    notion_utils = NotionUtils()
    task_mover = MoveTasks()
    clockify_utils = ClockifyUtils()
    clockify_sync = ClockifySync()


    try:
        if args.setup:
            setup_values = args.setup.split(",")
            if "notion" in setup_values:
                notion_utils.setup_notion()
        
        if args.dbmatch:
            source, dest = notion_utils.get_db_structure()
            notion_utils.match_mt_structure(source, dest)

        if args.move:
            try:
                task_mover.move_mt_tasks()
            except:
                notion_utils.get_databases()
                task_mover.move_mt_tasks()
        
        if args.clockify:
            clockify_utils.get_projects()
        
        if not any(vars(args).values()):
            print("No flags provided. Please provide a flag to run a specific function.")
            parser.print_help()

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
    
    