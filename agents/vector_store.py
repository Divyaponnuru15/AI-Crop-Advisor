import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_knowledge_base():
    with open("data/crop_rotation_docs.txt", "r", encoding="utf-8") as f:
        documents = f.readlines()

    embeddings = model.encode(documents)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))


    return index, documents, model

def retrieve_context(query, index, documents, model, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)

    results = [documents[i] for i in indices[0]]
    return "\n".join(results)
