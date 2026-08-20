import pytest
import asyncio
from backend.app.tools.calculator import CalculatorTool
from backend.app.tools.time_tool import TimeTool
from backend.app.tools.app_launcher import AppLauncherTool

@pytest.mark.asyncio
async def test_calculator_tool():
    tool = CalculatorTool()
    res = await tool.execute(expression="25 * 4 + 10")
    assert res["success"] is True
    assert res["result"] == 110

@pytest.mark.asyncio
async def test_time_tool():
    tool = TimeTool()
    res = await tool.execute()
    assert res["success"] is True
    assert "time" in res
    assert "day" in res

@pytest.mark.asyncio
async def test_app_launcher_tool():
    tool = AppLauncherTool()
    res = await tool.execute(app_name="youtube", query="python voice assistant")
    assert res["success"] is True
    assert "youtube.com" in res["url"]
