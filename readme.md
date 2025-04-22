# Notion Automation

A web server for interacting with notion databases that runs both scheduled activities and recieved REST requests.

## Disclaimer
A discontinued version of this software that exists as bat scripts that can be run locally with the Task scheduler or other cron tool can be found in the Cron-Scripts branch

## Description
I wanted to perform numerous notion actions and found the Notion's native automation to be restrictive so I made my own. It uses FastAPI as a base with as well as APscheduler to perform the following activies as of (04/2025):

- Fetch the following data from notion and package it nicely for reuse:
  - Users
  - Databases
  - A database (provide id)
  - A page (provide id)

Code written in prior version needs to updated to allow following capacity: 
- Collects all editted tasks edited since the last sync time
  - If the task has been completed
    - If the task is marked as a repeating task, update the status and due date
    - If the task does not repeat, it deletes the task
    - Adds an entry to a task completion log, including props and content

## Installation
### Notion
Duplicate this notion database: #TODO: Insert link to starter database

### Web Server
Written for Python3.13.3, unsure of prior versions
**Docker coming soon**

Copy/Paste into terminal or copy one line at a time
```shell
# Clone repository
git clone https://github.com/PixelFromTheMixery/notion-automation
# Navigate to cloned repository
cd notion-automation
# Create virtual environment
python -m venv venv
# Activate virtual environment
. venv/Scripts/activate
# Install required modules
pip install -r reqs.txt
```

## Running the application
- Suggested launch.json for VS Code:
``` json
{
    "name": "Python Debugger: FastAPI",
    "type": "debugpy",
    "request": "launch",
    "module": "uvicorn",
    "args": ["main:app", "--reload", "--port", "8001"],
    "jinja": true,
}
```
- run the following command in the terminal
`uvicorn main:app --reload`