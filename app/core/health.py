from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import psutil
import time

from app.core.database import get_db
from app.core.redis import redis_client

router = APIRouter()

async def check_database(db: AsyncSession) -> Dict[str, Any]:
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis(redis: Redis) -> Dict[str, Any]:
    try:
        start_time = time.time()
        await redis.ping()
        latency = (time.time() - start_time) * 1000
        return {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    db_status = await check_database(db)
    redis_status = await check_redis(redis_client.redis)
    
    # System metrics
    system_metrics = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
    
    return {
        "status": "healthy" if all(s["status"] == "healthy" for s in [db_status, redis_status]) else "unhealthy",
        "database": db_status,
        "redis": redis_status,
        "system": system_metrics
    } 