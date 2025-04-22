from datetime import datetime
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

scheduler = BackgroundScheduler()

def scheduled_task():
    print(f"task ran at {datetime.now()}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    #scheduler.add_job(scheduled_task, 'interval', seconds=10)
    scheduler.start()
    yield
    scheduler.shutdown()
