import os
from dotenv import load_dotenv

load_dotenv()

# General LLM Settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
DEFAULT_MODEL = os.getenv("MODEL_NAME", "llama3") 
MODEL_NAME = DEFAULT_MODEL
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# Ollama Specific
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

# IdeaForge 2 - Adaptive Orchestration Constants
MAX_ROUNDS = 10
MIN_ROUNDS = 2
MAX_AGENTS = 5
MAX_EXPANSION_RETRIES = 3
SPAWN_ISSUE_THRESHOLD = 3

# Convergence Detector Constants
CONVERGENCE_THRESHOLD = 0.65
CONVERGENCE_STALE_ROUNDS = 2

# Paths
ARTIFACT_STORE = "artifacts/"
