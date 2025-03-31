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
        "-opt", "--options", action="store_true", help="Update Settings"
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
            config.setup(args.setup.split(","))
        else:
            print("-"*30)
            print("Please run setup.bat first")
            print("-"*30)
            time.sleep(5)
            sys.exit()

    notion_utils = NotionUtils(config)
    task_mover = MoveTasks()
    try:
        clockify_utils = ClockifyUtils(config)
    except:
        pass
    try:
        clockify_sync = ClockifySync(config)
    except:
        pass

    try:
        if args.setup:
            config.select_from_list(notion_utils, "notion_source")
            if "mover" in args.setup.split(","):
                config.setup_mover(notion_utils)
                notion_utils.match_db_structure(
                    config.data["notion"]["task_db"], config.data["notion"]["history"]
                )
                task_mover.move_tasks(config, notion_utils)
            if "clockify" in args.setup.split(","):
                config.setup_clockify(clockify_utils)
                clockify_sync.project_sync(
                    clockify_utils,
                    notion_utils.get_project_list(config.data["notion"]["task_db"]),
                )
                clockify_sync.setup_tasks(config, clockify_utils, notion_utils)
            print("Setup complete")
            time.sleep(5)

        if args.dbmatch:
            notion_utils.match_db_structure(
                config.data["notion"]["task_db"], config.data["notion"]["history"]
            )

        if args.clockify:
            clockify_sync.project_sync(
                clockify_utils,
                notion_utils.get_project_list(config.data["notion"]["task_db"]),
            )
            clockify_sync.task_sync(config, clockify_utils, notion_utils)
            config.set_sync("clockify")

        if args.move:
            task_mover.move_tasks(config, notion_utils)
            config.set_sync("notion")

        if args.options:
            config.change_settings(notion_utils, clockify_utils)

        if args.test:
            print()

        if not any(vars(args).values()):
            print("No flags provided. Please provide a flag to run a specific function.")
            parser.print_help()

    except FileNotFoundError as e:
        print(f"Settings file not found. Please rerun with '-s' or '--setup' flag: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
