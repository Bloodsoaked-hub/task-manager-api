from anthropic import Anthropic, APIError
from pydantic import ValidationError
from fastapi import HTTPException, status

from app.core.config import Settings
from app.schemas.task import TaskCreate

settings = Settings()
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)


class LLMService:
    def parse_tasks_from_text(self, text: str) -> list[TaskCreate]:
        tool_schema = {
            "name": "create_tasks",
            "description": "Extract a list of actionable tasks from natural language",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tasks": {"type": "array", "items": TaskCreate.model_json_schema()}
                },
                "required": ["tasks"],
            },
        }

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system="You are an expert technical project manager. Break down the user's input into"
                "logical, actionable, and clear tasks. Ensure all fields, including both title and "
                "description, are fully filled out. Always generate the task titles and "
                "descriptions in the exact same language as the user's input text.",
                tools=[tool_schema],
                tool_choice={"type": "tool", "name": "create_tasks"},
                messages=[
                    {"role": "user", "content": f"Extract tasks from this text: {text}"}
                ],
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
