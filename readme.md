# !This project has been discontinued!
While operational, the notion aspects are being migrated to Intervalia for a webserver with web/android app to replace Clockify dependency.

# Notion Task Automation

A cron-based notion automation tool with a few integrations and configutation options.

## Description

I had a few tasks I wanted to automate in Notion and found Notion's automation to be limiting so I've added some api based tools.

At the core, you select a task database can be set as your 'My tasks' databased used by the notion Home Page. From this database you can:

### Base
- Keep a database from being cluttered
  - Delete tasks you have completed
  - Reset recurring tasks with a new due date

### Optional
- Keep a completion log of your tasks in a log
  - Add the completed task to a similar database for review, with content

- Two-way sync with Clockify
  - Import your tasks into Clockify by Client and Project
  - Mark a task as done on either, it will be updated in both
  - Create tasks in Clockify and they'll import into a matching project select option in Notion

## Getting Started

### Dependencies

- Windows 10
- Python 3.12 - [Download here](https://www.python.org/downloads/)
- A Notion database that follows [this template](https://pixelmixery.notion.site/1ce62907d7c28041914adb26db9b8754?v=1ce62907d7c28037bb6f000c025c033a&pvs=4)
 
### Installing

1. Download one of the zips and extract it wherever you like
1. Get an API key from Notion by creating a integration [here](https://www.notion.so/profile/integrations)
1. Connect your database by selecting your new integration as a connection
1. Run setup.bat to choose your settings
1. (Optional) Run your selected features with Task Scheduler on Windows. 

### Executing program

* Double click on the bat files to run the app and to log issues 

**OR**
* Run through python yourself to review output

|Name|Argument|Possible Values|
|:-|:-|:-|
|Intial Setup|`-setup`|`notion,clockify`, `notion`, `clockify`|
|Change Settings Menu|`-settings`||
|Notion Task automater|`-notion`||

#### Example
```
python3 main.py -clockify -notion
```

## Help

Common Problems:

**Logs are kept in the base folder under Logs/year/month/day.txt. Most problems can be determined from this.**

Some problems can be fixed by running setup.bat again or the argument with 

Properties between databases must match where specified, e.g. if you have a Progess property that is a Checkbox, it must be a checkbox, not a status.
```
python3 main.py -help
```
