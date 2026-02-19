from sarvamai import SarvamAI
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.environ["SARVAM"]


class Chunk(BaseModel):
    title: str = Field(description="A brief title for this chunk of product, typically 3,4 words that is most likely surfaced in a query")
    summary: str = Field(description="A few sentence summarizing the chunk about the product to answer questions")
    original_text: str = Field(description="The original text of this chunk from the provided document, exactly as is, not changed in any way")


class Chunks(BaseModel):
    chunks: list[Chunk]


def get_response(messages) -> Chunks:
    response = requests.post(
        url="https://openrouter.ai/api/v1/messages",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=json.dumps({
            "model": "anthropic/claude-instant-1.1",
            "messages":messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "Chunks",
                    "strict": True,
                    "schema": Chunks.model_json_schema()
                }
            }
        })
    )

    data = response.json()
    if "error" in data:
        raise RuntimeError(f"API error: {data['error']}")
    raw = data["choices"][0]["message"]["content"]
    return Chunks.model_validate_json(raw)


