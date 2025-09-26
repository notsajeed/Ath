import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingDB:
    def __init__(self, db_path):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.db_path = db_path
        self.documents = []
        self.embeddings = None
        self.index = None

    def add_document(self, name, content):
        emb = self.model.encode([content])[0]
        self.documents.append({"name": name, "content": content, "embedding": emb})

    def save(self):
        if not self.documents:
            return
        dim = len(self.documents[0]["embedding"])
        self.index = faiss.IndexFlatL2(dim)
        for doc in self.documents:
            vec = np.array([doc["embedding"]], dtype='float32')
            self.index.add(vec)

    def semantic_search(self, query, top_k=5):
        if not self.index:
            return []
        q_emb = self.model.encode([query])[0]
        q_vec = np.array([q_emb], dtype='float32')
        D, I = self.index.search(q_vec, top_k)
        results = []
        for i in I[0]:
            if i < len(self.documents):
                results.append(self.documents[i]["name"])
        return results
