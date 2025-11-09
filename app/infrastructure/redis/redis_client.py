# app/infrastructure/redis/redis_client.py
import redis
from app.core.config import settings

# One shared Redis client for the whole app
redis_client = redis.from_url(settings.REDIS_URL)
