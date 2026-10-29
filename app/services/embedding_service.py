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

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
            if not text:
                return []

            chunks = []
            start = 0
            text_length = len(text)

            while start < text_length:
                end = start + chunk_size
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start += chunk_size - overlap

            return chunks