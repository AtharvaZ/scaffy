"""Rate limiting middleware with daily cap support"""
import time
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from config import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_HOUR, RATE_LIMIT_PER_DAY

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.request_log = defaultdict(list)
        self.daily_totals = defaultdict(int)
        self.last_cleanup = time.time()

    def _cleanup_old_records(self):
        current_time = time.time()
        if current_time - self.last_cleanup < 300:
            return
        cutoff_time = current_time - 3600
        for ip in list(self.request_log.keys()):
            self.request_log[ip] = [(ts, count) for ts, count in self.request_log[ip] if ts > cutoff_time]
            if not self.request_log[ip]:
                del self.request_log[ip]
        today = datetime.now().date()
        for (ip, date) in list(self.daily_totals.keys()):
            if date < today - timedelta(days=7):
                del self.daily_totals[(ip, date)]
        self.last_cleanup = current_time

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"

    def _count_requests_in_window(self, ip: str, window_seconds: int) -> int:
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        return sum(count for ts, count in self.request_log[ip] if ts > cutoff_time)

    def _get_daily_count(self, ip: str) -> int:
        today = datetime.now().date()
        return self.daily_totals[(ip, today)]

    def _increment_daily_count(self, ip: str):
        today = datetime.now().date()
        self.daily_totals[(ip, today)] += 1

    async def check_rate_limit(self, request: Request):
        self._cleanup_old_records()
        ip = self._get_client_ip(request)
        current_time = time.time()

        daily_count = self._get_daily_count(ip)
        if daily_count >= RATE_LIMIT_PER_DAY:
            logger.warning(f"Daily limit exceeded: {ip} ({daily_count} requests)")
            raise HTTPException(status_code=429, detail={"error": "Daily rate limit exceeded", "message": f"Daily limit of {RATE_LIMIT_PER_DAY} requests exceeded. Try again tomorrow.", "retry_after": self._get_seconds_until_midnight()})

        hourly_count = self._count_requests_in_window(ip, 3600)
        if hourly_count >= RATE_LIMIT_PER_HOUR:
            logger.warning(f"Hourly limit exceeded: {ip} ({hourly_count} requests)")
            raise HTTPException(status_code=429, detail={"error": "Hourly rate limit exceeded", "message": f"Limit of {RATE_LIMIT_PER_HOUR} requests/hour exceeded.", "retry_after": 3600})

        minute_count = self._count_requests_in_window(ip, 60)
        if minute_count >= RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Per-minute limit exceeded: {ip} ({minute_count} requests)")
            raise HTTPException(status_code=429, detail={"error": "Rate limit exceeded", "message": f"Limit of {RATE_LIMIT_PER_MINUTE} requests/minute exceeded.", "retry_after": 60})

        self.request_log[ip].append((current_time, 1))
        self._increment_daily_count(ip)

    def _get_seconds_until_midnight(self) -> int:
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(days=1)
        return int((tomorrow - now).total_seconds())

    def get_rate_limit_headers(self, ip: str) -> dict:
        return {
            "X-RateLimit-Limit-Daily": str(RATE_LIMIT_PER_DAY),
            "X-RateLimit-Remaining-Daily": str(max(0, RATE_LIMIT_PER_DAY - self._get_daily_count(ip))),
            "X-RateLimit-Limit-Hourly": str(RATE_LIMIT_PER_HOUR),
            "X-RateLimit-Remaining-Hourly": str(max(0, RATE_LIMIT_PER_HOUR - self._count_requests_in_window(ip, 3600))),
        }

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    try:
        await rate_limiter.check_rate_limit(request)
        response = await call_next(request)
        ip = rate_limiter._get_client_ip(request)
        headers = rate_limiter.get_rate_limit_headers(ip)
        for key, value in headers.items():
            response.headers[key] = value
        return response
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content=e.detail)
