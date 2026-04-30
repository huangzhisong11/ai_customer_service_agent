import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", "data/knowledge_base.md")
DB_PATH = os.getenv("DB_PATH", "customer_service.db")
