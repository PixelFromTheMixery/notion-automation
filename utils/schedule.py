from services.task_automation import TaskAutomation

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

scheduler = AsyncIOScheduler()
task_automation = TaskAutomation()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(task_automation.task_status_reset, 'cron', hour="*/1")
    scheduler.add_job(task_automation.task_date_update, 'cron', day="*/1")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)    