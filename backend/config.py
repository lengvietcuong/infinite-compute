import os

from dotenv import load_dotenv


load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 1 week

# Brave Search API
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"

# Fireworks AI (comma-separated keys are load balanced at random)
FIREWORKS_API_KEYS = [
    key.strip()
    for key in os.getenv("FIREWORKS_AI_API_KEY", "").split(",")
    if key.strip()
]
FIREWORKS_LLM_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_EMBEDDING_API_URL = "https://api.fireworks.ai/inference/v1/embeddings"
REQUEST_TIMEOUT_SECONDS = 60

LLM_NAME = "accounts/fireworks/models/minimax-m3p1-flash"
EMBEDDING_MODEL_NAME = "accounts/fireworks/models/qwen3-embedding-8b"

SYSTEM_PROMPT = """You are an advisor for customers of InfiniteCompute – An online store that sells NVIDIA GPUs.

Note: This is an imaginary store created for demonstration purposes only.

If the user asks about a product in the store, get the product information from the database. For other questions, the system will try to find relevant information and provide to you if any is found. If no information is given, or the given information is insufficient, try searching using keywords. If that still does not help, try listing all the documents in the knowledge base, then listing sections from relevant documents, and finally reading the relevant sections. If you still cannot find the necessary information, perform a web search.

When you are unable to assist the user, tell them to contact the store owner at lengvietcuong@gmail.com or +84899150016 (Le Nguyen Viet Cuong).

In your responses, be simple and concise, yet informative. Maintain a friendly tone with a slight sense of humor where appropriate. Politely decline irrelevant queries."""
TEMPERATURE = 0
MAX_TOKENS = 8192
EMBEDDING_DIMENSIONS = 768

# RAG Settings
SEMANTIC_SEARCH_TOP_K = 3
SEMANTIC_SEARCH_SIMILARITY_THRESHOLD = 0.75
KEYWORD_SEARCH_TOP_K = 10

MAX_ITERATIONS = 10
MAX_HEADING_DEPTH = 3
MAX_CONCURRENT_REQUESTS = 10

# CORS Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
