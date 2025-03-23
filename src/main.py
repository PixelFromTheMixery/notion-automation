import sys
import argparse
from clockify.clockify import Clockify
from notion.move_tasks import MoveTasks
from notion.notion_utils import NotionUtils
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Notion Automation Python Script with CLI flags")
    
    parser.add_argument(
        "-db", "--db",
        action="store_true",
        help="Set source and destination databases"
        )

    parser.add_argument(
        "-dbm", "--dbmatch",
        action="store_true",
        help="Check database synchronicity"
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
    utils = NotionUtils()
    task_mover = MoveTasks()
    clockify = Clockify()

    try:
        if args.db:
            utils.get_databases()
        
        if args.dbmatch:
            source, dest = utils.get_db_structure()
            utils.match_mt_structure(source, dest)

        if args.move:
            task_mover.move_mt_tasks()
        
        if args.clockify:
            clockify.get_user()
        
        if not any(vars(args).values()):
            print("No flags provided. Please provide a flag to run a specific function.")
            parser.print_help()

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
    
    