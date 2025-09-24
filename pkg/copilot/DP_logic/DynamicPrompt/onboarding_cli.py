print("🟡 Script started")
import sys
print("🟢 Python version:", sys.version)

from pathlib import Path
from dynamic_prompt.embedder import Embedder


def chunk_text_file(filepath):
    return [line.strip() for line in Path(filepath).read_text().splitlines() if line.strip()]


def run_onboarding():
    print("\n--- Dynamic Prompt Framework Onboarding ---")
    source_path = input("Enter path to your data/metrics file (e.g., config/metrics.txt): ").strip()
    output_path = "pkg/copilot/DP_logic/DynamicPrompt/config/embeddings/embeddings.npz"

    if not Path(source_path).exists():
        print(f"Error: file {source_path} does not exist.")
        return

    chunks = chunk_text_file(source_path)
    print(f"Chunked {len(chunks)} blocks. Embedding now...")
    embedder = Embedder()
    embedder.save_embeddings(chunks, filepath=output_path)
    print(f"Embeddings saved to {output_path}")



run_onboarding()