from utils.schedule import scheduler

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/scheduled_jobs")
async def get_scheduled_jobs_endpoint():
    """Get all scehduled jobs"""
    schedules = []
    for job in scheduler.get_jobs():
      schedules.append({"name": job.name, 
                        "trigger": str(job.trigger),
                        "next run time": str(job.next_run_time)})
    return JSONResponse(schedules,200)