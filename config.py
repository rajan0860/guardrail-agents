from pathlib import Path

# --- Ollama Configuration ---
OLLAMA_MODEL = "qwen2.5:7b-instruct"
EMBEDDING_MODEL = "nomic-embed-text"

# --- File Paths ---
base_dir = Path(__file__).parent.resolve()
CORPUS_PATH = Path("/Users/rajanmehta/Documents/MLProjects/data_lines.txt")
VECTOR_STORE_PATH = base_dir / "faiss_index"

# --- Constants ---
RECOMMENDED_PROMPT_PREFIX = "Answer the user's question based on the provided tools."
