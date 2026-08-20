from datetime import datetime
import time
from typing import Dict, Any
from backend.app.tools.base import BaseTool

class TimeTool(BaseTool):
    name = "current_time"
    description = "Returns the current date, local time, day of the week, and timezone information."
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        now = datetime.now()
        tz_name = time.tzname[0]
        formatted = now.strftime("%A, %B %d, %Y - %I:%M:%S %p")
        return {
            "success": True,
            "datetime": formatted,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M %p"),
            "day": now.strftime("%A"),
            "timezone": tz_name,
            "message": f"It is currently {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')} ({tz_name})."
        }
