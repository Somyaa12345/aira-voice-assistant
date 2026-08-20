import webbrowser
import os
import subprocess
import urllib.parse
from typing import Dict, Any
from backend.app.tools.base import BaseTool

class AppLauncherTool(BaseTool):
    name = "app_launcher"
    description = "Opens websites, web apps, or desktop applications like YouTube, Spotify, Google, or custom URLs."
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "enum": ["youtube", "spotify", "google", "calculator_app", "custom_url"],
                "description": "The target app or platform to open: 'youtube', 'spotify', 'google', or 'custom_url'"
            },
            "query": {
                "type": "string",
                "description": "Optional search term or query to search inside YouTube/Spotify/Google (e.g. 'LoFi music' or 'Python tutorial')"
            },
            "url": {
                "type": "string",
                "description": "Optional direct URL to open if app_name is 'custom_url'"
            }
        },
        "required": ["app_name"]
    }

    async def execute(self, app_name: str, query: str = "", url: str = "", **kwargs) -> Dict[str, Any]:
        target_url = None
        app_clean = app_name.lower().strip()

        if app_clean == "youtube":
            if query:
                encoded_q = urllib.parse.quote(query)
                target_url = f"https://www.youtube.com/results?search_query={encoded_q}"
            else:
                target_url = "https://www.youtube.com"

        elif app_clean == "spotify":
            if query:
                encoded_q = urllib.parse.quote(query)
                target_url = f"https://open.spotify.com/search/{encoded_q}"
            else:
                target_url = "https://open.spotify.com"

        elif app_clean == "google":
            if query:
                encoded_q = urllib.parse.quote(query)
                target_url = f"https://www.google.com/search?q={encoded_q}"
            else:
                target_url = "https://www.google.com"

        elif app_clean == "custom_url":
            target_url = url if url.startswith("http") else f"https://{url}"

        elif app_clean == "calculator_app":
            try:
                if os.name == "nt":  # Windows
                    subprocess.Popen(["calc.exe"])
                else:
                    subprocess.Popen(["gnome-calculator"])
                return {"success": True, "message": "Opened desktop Calculator application."}
            except Exception as e:
                return {"success": False, "error": f"Failed to launch desktop calculator: {str(e)}"}

        if target_url:
            try:
                if os.name == "nt":
                    # Force Windows shell to open default browser
                    os.system(f'start {target_url}')
                else:
                    webbrowser.open(target_url)
                display_msg = f"Opening {app_name.capitalize()}" + (f" with query '{query}'" if query else "")
                return {"success": True, "message": display_msg, "url": target_url}
            except Exception as e:
                webbrowser.open(target_url)
                return {"success": True, "message": f"Opening {app_name.capitalize()}", "url": target_url}

        return {"success": False, "error": f"Unsupported app_name: {app_name}"}
