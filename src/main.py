from clockify.clockify_sync import ClockifySync
from clockify.clockify_utils import ClockifyUtils
from notion.move_tasks import MoveTasks
from notion.notion_utils import NotionUtils
from config import Config

import argparse, sys, time, yaml

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
    try:
        with open(config.file_path, "r") as f:
            config.data = yaml.load(f, Loader=yaml.SafeLoader)
        print("State loaded")
    except FileNotFoundError:
        if args.setup:
            setup_values = args.setup.split(",")
            config.setup(setup_values)
        else:
            print("-"*30)
            print("Please run setup.bat first")
            print("-"*30)
            time.sleep(5)
            sys.exit()
        
    notion_utils = NotionUtils()
    task_mover = MoveTasks()
    try:
        clockify_utils = ClockifyUtils()
    except:
        pass
    try:
        clockify_sync = ClockifySync()
    except:
        pass

    try:
        if args.setup:
            setup_values = args.setup.split(",")
            config.set_master_db(notion_utils)
            if "mover" in setup_values:
                config.setup_mover(notion_utils)
                notion_utils.match_mt_structure()
                task_mover.move_tasks(config, notion_utils)
            if "clockify" in setup_values:
                config.setup_clockify(clockify_utils)
                clockify_sync.project_sync(
                    notion_utils.get_project_list(
                        config.data["notion"]["task_db"]
                    )
                )
                clockify_sync.setup_tasks(config, clockify_utils, notion_utils)
        
        if args.dbmatch:
            notion_utils.match_mt_structure()

        if args.clockify:
            clockify_sync.project_sync(
                notion_utils.get_project_list(
                        config.data["notion"]["task_db"]
                    )
            )
            clockify_sync.setup_tasks(config, clockify_utils,notion_utils)

        if args.move:
            task_mover.move_tasks(config, notion_utils)

        if args.test:
            config.change_settings(notion_utils, clockify_utils)
            pass

        if not any(vars(args).values()):
            print("No flags provided. Please provide a flag to run a specific function.")
            parser.print_help()

    except FileNotFoundError as e:
        print(f"Settings file not found. Please rerun with '-s' or '--setup' flag: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
