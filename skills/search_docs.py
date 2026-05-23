from skills.base import BaseSkill
from sentence_transformers import SentenceTransformer
import chromadb

class SearchDocs(BaseSkill):
    def __init__(self):
        super().__init__()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma.get_or_create_collection("personal docs")

    def execute(self, params):
        message = params.get("message")
        n_results = params.get("n_results") or 3
        embedding = self.embedding_model.encode(message).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results= n_results
        )
        chunks = []
        for i in range(len(results["documents"][0])):
            chunks.append({
                "texto": results["documents"][0][i],
                "fonte": results["metadatas"][0][i]['fonte']
            })
        return "\n\n---\n\n".join(chunks)

