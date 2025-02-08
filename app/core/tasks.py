from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.session_service import SessionService

scheduler = AsyncIOScheduler()

async def cleanup_expired_sessions():
    async with AsyncSessionLocal() as db:
        session_service = SessionService(db)
        await session_service.cleanup_expired_sessions()

def setup_periodic_tasks(app: FastAPI):
    # Clean up expired sessions every hour
    scheduler.add_job(
        cleanup_expired_sessions,
        trigger=IntervalTrigger(hours=1),
        id="cleanup_sessions",
        name="Clean up expired sessions",
        replace_existing=True
    )

    @app.on_event("startup")
    async def start_scheduler():
        scheduler.start()

    @app.on_event("shutdown")
    async def shutdown_scheduler():
        scheduler.shutdown() 