import sys
from pathlib import Path
 # Make sure we can import config from root if run as script
sys.path.append(str(Path(__file__).parent.parent))

import config
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def ingest_data():
    # --- Initialize Ollama embeddings ---
    print(f"Initializing embeddings with model: {config.EMBEDDING_MODEL}")
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)

    # --- Load and process the corpus ---
    print(f"Loading corpus from {config.CORPUS_PATH}...")
    if not config.CORPUS_PATH.exists():
        print(f"Error: Corpus file not found at {config.CORPUS_PATH}")
        return

    text = config.CORPUS_PATH.read_text()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    texts = text_splitter.split_text(text)

    # Create documents
    documents = [Document(page_content=t) for t in texts]
    print(f"Created {len(documents)} document chunks")

    # --- Create FAISS vector store ---
    print("Creating FAISS vector store with Ollama embeddings...")
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save the vector store locally
    vector_store.save_local(str(config.VECTOR_STORE_PATH))
    print(f"Vector store saved to {config.VECTOR_STORE_PATH}")
    print("\n✅ Ollama ingestion complete!")

if __name__ == "__main__":
    ingest_data()
