from anthropic import APIError, Anthropic
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.task import TaskCreate

settings = Settings()
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)


class LLMService:
    def parse_tasks_from_text(self, text: str, context: str = "") -> list[TaskCreate]:
        tool_schema = {
            "name": "create_tasks",
            "description": "Extract a list of actionable technical tasks based on user request and project documentation",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": TaskCreate.model_json_schema(),
                    }
                },
                "required": ["tasks"],
            },
        }

        if context:
            user_content = (
                f"USER INSTRUCTION:\n{text}\n\n"
                f"PROJECT DOCUMENTATION (Extract exact technical steps and details from here):\n{context}"
            )
        else:
            user_content = f"USER INSTRUCTION:\n{text}"

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=(
                    "You are an expert technical project manager. Your goal is to convert the user request "
                    "into concrete, highly specific, and actionable tasks by directly using the technical facts, "
                    "configurations, and requirements found in the provided Project Documentation.\n"
                    "Do NOT create meta-tasks like 'Read documentation' or 'Analyze file'. "
                    "Instead, create actual implementation/configuration tasks with rich descriptions based on the document content.\n"
                    "Ensure all fields (title and description) are fully filled out with technical detail. "
                    "Always generate task titles and descriptions in the exact same language as the user's input."
                ),
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": "create_tasks"},
                messages=[{"role": "user", "content": user_content}],
            )

            tool_use_block = response.content[0]
            raw_tasks = tool_use_block.input["tasks"]

            return [TaskCreate(**task) for task in raw_tasks]

        except APIError as e:
            print(f"Anthropic API Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to communicate with the AI provider.",
            )

        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI service returned an unexpected response format.",
            )
