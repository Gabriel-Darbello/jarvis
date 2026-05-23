from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter as TokenSplitter
import os, chromadb

docs = []
for file in os.listdir('docs'):
    path = os.path.join('docs', file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        docs.append({'arquivo': file, 'conteudo': content})

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
file_chunks = []
for doc in docs:
    splitter = TokenSplitter.from_tiktoken_encoder(
        model_name="llama-3.3-70b-versatile",
        chunk_size=300,
        chunk_overlap=30
    )
    chunks = splitter.split_text(doc["conteudo"])
    for chunk in chunks:
        file_chunks.append({"texto": chunk, "fonte": doc["arquivo"]})

chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("personal_docs")
print("Gerando embeddings e salvando no ChromaDB...")

for i, chunks in enumerate(file_chunks):
    embedding = embedding_model.encode(chunks["texto"]).tolist()
    collection.add(
        documents=[chunks["texto"]],
        embeddings=[embedding],
        metadatas=[{"fonte":chunks["fonte"]}],
        ids=[f"chunk_{i}"]
    )
    print(f"  [{i+1}/{len(file_chunks)}] {chunks['fonte']}")

print("\nIngestão concluída!")
print(f"Total salvo: {collection.count()} chunks")

