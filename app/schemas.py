from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    intent: str
    need_human: bool
    retrieved_docs: list[str]
