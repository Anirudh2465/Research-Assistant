from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from backend.core.paths import EMBEDDING_DIR
from backend.core.logging import logger

class VectorService:
    def __init__(self):
        # Lazy load model to avoid memory cost if not used
        self.model = None
        self.index = None
        self.texts = [] # Metadata store for simple FAISS (In prod use a real vector DB or FAISS disk index)

    def _load_model(self):
        if not self.model:
            logger.info("Loading SentenceTransformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2') 
            # In Phase 0 this lib was excluded, but Phase 2 request allowed adding it to requirements.txt
            # Ensure it's installed.

    def encode(self, text):
        self._load_model()
        return self.model.encode([text])[0]

    def create_batch_index(self, concepts: list):
        """
        Create a temporary index for a list of concept objects {name, description}
        Used for ranking global concepts against a problem statement.
        """
        self._load_model()
        if not concepts:
            return None, []
        
        texts = [f"{c['name']}: {c.get('description', '')}" for c in concepts]
        embeddings = self.model.encode(texts)
        
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype('float32'))
        
        return index, concepts

    def search_local_index(self, query_text, index, candidates, k=10):
        if not index or not candidates:
            return []
        
        self._load_model()
        query_vec = self.model.encode([query_text]).astype('float32')
        D, I = index.search(query_vec, k)
        
        results = []
        for i, idx in enumerate(I[0]):
            if idx != -1 and idx < len(candidates):
                results.append({
                    "concept": candidates[idx],
                    "score": float(D[0][i]) # L2 distance (lower is better, or convert to similarity)
                })
        return results

vector_service = VectorService()
