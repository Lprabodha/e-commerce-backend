import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    raise RuntimeError("Set DATABASE_URL in your .env file")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )
    

SECRET_KEY = os.getenv("SECRET_KEY", "aecfc9fec6980b64a9b8130730c08ae95765c2a2ac472f7968642b")
ALGORITHM =  "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

HF_CHAT_MODEL = os.getenv("HF_CHAT_MODEL", "deepseek-ai/DeepSeek-V4-Pro").strip()
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
HF_CHAT_URL = os.getenv("HF_CHAT_URL", "https://router.huggingface.co/v1/chat/completions").strip()
