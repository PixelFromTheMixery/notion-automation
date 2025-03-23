import sys
import argparse
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
    
    args = parser.parse_args()
    utils = NotionUtils()
    task_mover = MoveTasks()
    
    if args.db:
        utils.get_databases()
    
    if args.dbmatch:
        source, dest = utils.get_db_structure(True)
        utils.match_mt_structure(source, dest)

    if args.move:
        try:
            task_mover.move_mt_tasks()
        except Exception as e:
            print(f"An error occurred: {str(e)}", file=sys.stderr)
    
    