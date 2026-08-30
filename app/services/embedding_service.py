from openai import OpenAI

from app.core.config import Settings

settings = Settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


class EmbeddingService:
    def generate_embedding(self, text: str) -> list[float]:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )

        return response.data[0].embedding
