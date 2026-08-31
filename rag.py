import os
import json
import ollama


EMBEDDING_MODEL = "nomic-embed-text"

INDEX_DIR = "embeddings"
INDEX_FILE = os.path.join(INDEX_DIR, "index.json")


def get_embedding(text):
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response["embeddings"][0]


def load_document(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def chunk_text(text, chunk_size=100):
    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])

        if chunk.strip():
            chunks.append(chunk)

    return chunks


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))

    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot / (norm_a * norm_b)


def build_index(filename="knowledge.txt"):
    os.makedirs(INDEX_DIR, exist_ok=True)

    text = load_document(filename)
    chunks = chunk_text(text)

    documents = []

    print("Building RAG index...")

    for i, chunk in enumerate(chunks):

        print(f"Embedding chunk {i + 1}/{len(chunks)}")

        embedding = get_embedding(chunk)

        documents.append({
            "text": chunk,
            "embedding": embedding
        })

    with open(INDEX_FILE, "w", encoding="utf-8") as file:
        json.dump(documents, file)

    print("RAG index created successfully.")


def load_index():
    if not os.path.exists(INDEX_FILE):
        return []

    with open(INDEX_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_index(query, top_k=3):

    index = load_index()

    if not index:
        return []

    query_embedding = get_embedding(query)

    scored = []

    for item in index:

        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        scored.append(
            (score, item["text"])
        )

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        text
        for score, text in scored[:top_k]
    ]