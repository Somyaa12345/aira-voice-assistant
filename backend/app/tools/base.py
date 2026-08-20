from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """Abstract Base Class for Aira Assistant Tools."""

    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Executes the tool with keyword arguments and returns a dictionary result."""
        pass

    def to_ollama_schema(self) -> Dict[str, Any]:
        """Converts tool declaration to Ollama / OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
