from clockify.clockify_sync import ClockifySync
from clockify.clockify_utils import ClockifyUtils
from notion.reset_tasks import ResetTasks
from notion.notion_utils import NotionUtils
from config import Config

import argparse, sys, time, yaml

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Notion Automation Python Script with CLI flags")

    parser.add_argument(
        "-setup", "--setup", type=str, help="Set up the Notion and Clockify API keys"
    )

    parser.add_argument(
        "-dbm",
        "--dbMatch",
        action="store_true",
        help="Ensure notion database synchronicity",
    )

    parser.add_argument(
        "-notion",
        "--notion",
        action="store_true",
        help="Automate Notion Tasks",
    )

    parser.add_argument(
        "-clockify", "--clockify", action="store_true", help="Clockify Integration"
    )

    parser.add_argument(
        "-tei",
        "--timeEntryImport",
        action="store_true",
        help="Import time entries into a notion database",
    )

    parser.add_argument(
        "-settings", "--settings", action="store_true", help="Update Settings"
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

    try:
        notion_utils = NotionUtils()
        config.set_utils("notion", notion_utils)
        task_reset = ResetTasks()
        if args.clockify:
            clockify_utils = ClockifyUtils()
            config.set_utils("clockify", clockify_utils)
            clockify_sync = ClockifySync()
        if args.setup:
            config.select_from_list("notion_source")
            if "notion" in args.setup.split(","):
                config.setup_notion()
                if config.data["notion"]["log"]:
                    notion_utils.match_db_structure(
                        config.data["notion"]["task_db"],
                        config.data["notion"]["history"],
                    )
                task_reset.automate_tasks()
            if "clockify" in args.setup.split(","):
                clockify_utils = ClockifyUtils()
                config.set_utils("clockify", clockify_utils)
                clockify_sync = ClockifySync()
                config.setup_clockify()
                clockify_sync.project_sync(
                    notion_utils.get_project_list(config.data["notion"]["task_db"]),
                )
                clockify_sync.setup_tasks()
            print("Setup complete")
            time.sleep(5)

        if args.dbMatch:
            notion_utils.match_db_structure(
                config.data["notion"]["task_db"], config.data["notion"]["history"]
            )

        if args.timeEntryImport and not args.clockify:
            print("Please set up clockify to use this featrure")
            time.sleep(5)

        if args.timeEntryImport and args.clockify:
            pass

        if args.clockify:
            clockify_sync.project_sync(
                notion_utils.get_project_list(config.data["notion"]["task_db"]),
            )
            clockify_sync.task_sync()
            config.set_sync("clockify")
            print("Clockify synced", file=sys.stderr)
            time.sleep(5)

        if args.notion:
            task_reset.automate_tasks()
            config.set_sync("notion")
            print("Notion synced", file=sys.stderr)

        if args.settings:
            config.change_settings()

        if args.test:
            clockify_sync.import_time_entries()
            print()

        if not any(vars(args).values()):
            print("No flags provided. Please provide a flag to run a specific function.")
            parser.print_help()

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
