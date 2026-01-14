import os

from dotenv import load_dotenv


load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 1 week

# OpenRouter AI
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
OPEN_ROUTER_LLM_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPEN_ROUTER_EMBEDDING_API_URL = "https://openrouter.ai/api/v1/embeddings"
REQUEST_TIMEOUT_SECONDS = 30

LLM_NAME = "google/gemini-2.0-flash-001"
EMBEDDING_MODEL_NAME = "qwen/qwen3-embedding-8b"
SYSTEM_PROMPT = """You are an advisor for customers of InfiniteCompute – An online store that sells NVIDIA GPUs.

When presented with a question, """
TEMPERATURE = 0
MAX_TOKENS = 8192
EMBEDDING_DIMENSIONS = 768

# RAG Settings
SEMANTIC_SEARCH_TOP_K = 3
SEMANTIC_SEARCH_SIMILARITY_THRESHOLD = 0.6
KEYWORD_SEARCH_TOP_K = 10

MAX_ITERATIONS = 10
MAX_HEADING_DEPTH = 3

# CORS Settings
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
