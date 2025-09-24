import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model)

    def embed_chunks(self, chunks):
        # Returns a list of embedding vectors for each chunk
        return self.model.encode(chunks, convert_to_numpy=True).tolist()

    def save_embeddings(self, chunks, filepath="config/embeddings.npz"):
        vectors = self.embed_chunks(chunks)
        np.savez_compressed(filepath, vectors=vectors, chunks=chunks)

    @staticmethod
    def load_embeddings(filepath="config/embeddings.npz"):
        data = np.load(filepath, allow_pickle=True)
        return data['vectors'], data['chunks']
