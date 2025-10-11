import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

class Embedder:
    def __init__(self, model="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model)

    def embed_chunks(self, chunks):
        # Returns a list of embedding vectors for each chunk
        return self.model.encode(chunks, convert_to_numpy=True).tolist()

    def save_embeddings(self, chunks, filepath="config/embeddings/embeddings.npz"):
        config_dir = "/".join(filepath.split("/")[:-1])
        if not Path(config_dir).exists():
            Path(config_dir).mkdir(parents=True, exist_ok=True)

        vectors = self.embed_chunks(chunks)
        np.savez_compressed(filepath, vectors=vectors, chunks=chunks)

    @staticmethod
    def load_embeddings(filepath="config/embeddings/embeddings.npz"):
        data = np.load(filepath, allow_pickle=True)
        return data['vectors'], data['chunks']
