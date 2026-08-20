import json
import logging
from typing import Dict, List, Any, Optional
from backend.app.tools.base import BaseTool
from backend.app.tools.calculator import CalculatorTool
from backend.app.tools.time_tool import TimeTool
from backend.app.tools.notes_tool import NotesTool
from backend.app.tools.reminders_tool import RemindersTool
from backend.app.tools.app_launcher import AppLauncherTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry managing available tools and tool execution for LLM."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: '{tool.name}'")

    def _register_default_tools(self):
        self.register(CalculatorTool())
        self.register(TimeTool())
        self.register(NotesTool())
        self.register(RemindersTool())
        self.register(AppLauncherTool())

    def get_ollama_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_ollama_schema() for tool in self._tools.values()]

    def get_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool = self._tools.get(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found."}
        try:
            logger.info(f"Executing tool '{name}' with args: {arguments}")
            return await tool.execute(**arguments)
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
            return {"success": False, "error": str(e)}

tool_registry = ToolRegistry()
