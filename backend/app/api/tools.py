from fastapi import APIRouter
from typing import Dict, Any, List
from backend.app.tools.registry import tool_registry

router = APIRouter(prefix="/api/tools", tags=["Tools"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_tools():
    """Lists all registered tools and their schemas."""
    return tool_registry.get_ollama_schemas()

@router.post("/execute")
async def execute_tool_manual(name: str, args: Dict[str, Any]):
    """Manually executes a registered tool."""
    return await tool_registry.execute_tool(name, args)
