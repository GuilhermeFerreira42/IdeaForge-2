import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

# === Limites do Orquestrador (Onda 1) ===
MAX_ROUNDS = int(os.getenv("MAX_ROUNDS", "10"))
MAX_AGENTS = int(os.getenv("MAX_AGENTS", "5"))
MIN_ROUNDS = int(os.getenv("MIN_ROUNDS", "2"))
MAX_EXPANSION_RETRIES = int(os.getenv("MAX_EXPANSION_RETRIES", "3"))

# === Convergência ===
CONVERGENCE_THRESHOLD = float(os.getenv("CONVERGENCE_THRESHOLD", "0.7"))
CONVERGENCE_STALE_ROUNDS = int(os.getenv("CONVERGENCE_STALE_ROUNDS", "2"))

# === Spawning ===
SPAWN_ISSUE_THRESHOLD = int(os.getenv("SPAWN_ISSUE_THRESHOLD", "3"))
