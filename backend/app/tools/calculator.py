import ast
import operator
import math
from typing import Dict, Any
from backend.app.tools.base import BaseTool

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluates basic math expressions safely (e.g. '25 * 4 + 10', 'sqrt(144)', '15% of 200')."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression string to evaluate, e.g., '125 / 5 + 30'"
            }
        },
        "required": ["expression"]
    }

    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    _FUNCTIONS = {
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log
    }

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):  # Numbers
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self._OPERATORS:
                return self._OPERATORS[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self._OPERATORS:
                return self._OPERATORS[op_type](operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name in self._FUNCTIONS:
                args = [self._eval_node(arg) for arg in node.args]
                return self._FUNCTIONS[func_name](*args)
        raise ValueError("Unsupported or unsafe math expression")

    async def execute(self, expression: str = "", **kwargs) -> Dict[str, Any]:
        try:
            expr_clean = expression.replace("^", "**").strip()
            tree = ast.parse(expr_clean, mode="eval")
            result = self._eval_node(tree.body)
            return {"success": True, "result": result, "formatted": f"{expression} = {result}"}
        except Exception as e:
            return {"success": False, "error": f"Invalid expression: {str(e)}"}
