import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .embedder import Embedder

import os
import dotenv
dotenv.load_dotenv()

embedding_path = os.getenv("EMBEDDING_PATH")

class Retriever:
    def __init__(self, embedding_path=embedding_path):
        self.vectors, self.chunks = Embedder.load_embeddings(embedding_path)

    def query(self, input_text, top_k=5):
        embedder = Embedder()
        query_vector = np.array(embedder.embed_chunks([input_text])[0]).reshape(1, -1)
        similarities = cosine_similarity(query_vector, np.vstack(self.vectors))
        top_indices = similarities[0].argsort()[-top_k:][::-1]
        return [self.chunks[i] for i in top_indices]