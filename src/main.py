import sys
import argparse
from clockify.clockify_sync import ClockifySync
from clockify.clockify_utils import ClockifyUtils
from notion.move_tasks import MoveTasks
from notion.notion_utils import NotionUtils
from config import Config

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

    setup_values = args.setup.split(",")
    config = Config()
    config.setup(setup_values)
    notion_utils = NotionUtils()
    task_mover = MoveTasks()
    if args.clockify or "clockify" in args.setup:
        clockify_utils = ClockifyUtils()
        clockify_sync = ClockifySync()

    try:
        if args.setup:
            config.set_master_db(notion_utils)
            if "mover" in setup_values:
                config.setup_mover(notion_utils)
                notion_utils.match_mt_structure()
                task_mover.move_tasks(notion_utils)
            if "clockify" in setup_values:
                config.setup_clockify(clockify_utils)
                clockify_sync.project_sync(
                    notion_utils.get_project_list(
                        config.data["notion"]["task_db"]
                    )
                )
                clockify_sync.setup_tasks(clockify_utils,notion_utils, config)

        if args.dbmatch:
            notion_utils.match_mt_structure()

        if args.clockify:
            clockify_sync.project_sync(
                notion_utils.get_project_list(
                        config.data["notion"]["task_db"]
                    )
            )
            clockify_sync.setup_tasks(clockify_utils,notion_utils, config)

        if args.move:
            task_mover.move_tasks(notion_utils)

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
