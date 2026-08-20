from typing import Dict, Any
from backend.app.tools.base import BaseTool
from backend.app.database.session import SessionLocal
from backend.app.database.crud import create_note, get_notes

class NotesTool(BaseTool):
    name = "manage_notes"
    description = "Create a new note or retrieve saved notes from memory."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list"],
                "description": "Action to perform: 'create' a note or 'list' existing notes"
            },
            "title": {
                "type": "string",
                "description": "Title of the note (required for action='create')"
            },
            "content": {
                "type": "string",
                "description": "Body content of the note (required for action='create')"
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, title: str = "", content: str = "", **kwargs) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            if action == "create":
                if not title or not content:
                    return {"success": False, "error": "Title and content are required to create a note."}
                note = create_note(db, title=title, content=content)
                return {"success": True, "message": f"Note '{note.title}' created successfully.", "id": note.id}
            elif action == "list":
                notes = get_notes(db)
                result = [{"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at.isoformat()} for n in notes]
                return {"success": True, "count": len(result), "notes": result}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        finally:
            db.close()
