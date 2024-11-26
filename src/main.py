import sys
import argparse
from db_manipulation import get_databases, move_mt_tasks, get_db_structure, match_mt_structure

url = "https://api.notion.com/v1/"

def main():
    parser = argparse.ArgumentParser(description="Notion Automation Python Script with CLI flags")
    
    parser.add_argument(
        "-dbm", "--dbmatch",
        action="store_true",
        help="Check database synchronicity"
        )
    
    args = parser.parse_args()
    
    if args.dbmatch:
        source = get_db_structure(url, True)
        dest = get_db_structure(url, False)
        match_mt_structure(url, source, dest)
        
if __name__ == "__main__":
    try:
        #get_databases(url)
        move_mt_tasks(url)
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
    
    