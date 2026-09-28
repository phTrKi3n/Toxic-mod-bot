import logging
import os
import time
from collections import deque
import aiohttp

logger = logging.getLogger("bot.monitoring")

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", "5"))
WINDOW_SECONDS = 300  # 5 minutes


class ErrorTracker:
    def __init__(self, threshold: int = ALERT_THRESHOLD, window_seconds: int = WINDOW_SECONDS):
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.error_timestamps = deque()

    def record_error(self, error_detail: str):
        now = time.time()
        self.error_timestamps.append(now)
        self._clean_old_errors(now)

        logger.warning(
            f"[MONITOR] Recorded error. Total in 5m window: {len(self.error_timestamps)}/{self.threshold}"
        )

        if len(self.error_timestamps) >= self.threshold:
            self._trigger_alert(error_detail, len(self.error_timestamps))

    def _clean_old_errors(self, now: float):
        cutoff = now - self.window_seconds
        while self.error_timestamps and self.error_timestamps[0] < cutoff:
            self.error_timestamps.popleft()

    def _trigger_alert(self, error_detail: str, count: int):
        message = (
            f"🚨 **OPS EMERGENCY ALERT**: High failure rate detected!\n"
            f"- **Error count**: {count} errors within 5 minutes (Threshold: {self.threshold})\n"
            f"- **Latest Error**: {error_detail}\n"
            f"- **Action Required**: Inspect inference_service logs and network connection."
        )
        logger.error(f"[OPS ALERT TRIGGERED] {message}")
        
        if WEBHOOK_URL:
            import asyncio
            asyncio.create_task(send_ops_alert(message))
        else:
            logger.warning("[OPS ALERT] DISCORD_WEBHOOK_URL not configured.")


error_tracker = ErrorTracker()


async def send_ops_alert(error_detail: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        return False

    payload = {
        "username": "DevSecOps Monitor Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/564/564619.png",
        "embeds": [
            {
                "title": "🚨 Cảnh báo Vận hành Hạ tầng DevSecOps",
                "description": error_detail,
                "color": 15158332,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as resp:
                return resp.status in (200, 204)
    except Exception as e:
        logger.error(f"Exception while sending Ops Webhook Alert: {e}")
        return False
