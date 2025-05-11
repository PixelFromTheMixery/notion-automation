from services.task_automation import TaskAutomation

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

scheduler = BackgroundScheduler()
reset_tasks = TaskAutomation()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(reset_tasks.task_status_reset, 'cron', hour="*/1")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)    