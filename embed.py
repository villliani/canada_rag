import os
import pickle
import pandas as pd
import ollama
import chromadb

# ==========================================
# CONFIG
# ==========================================

CSV_FILE = "data/clean_canada_express.csv"
EMBEDDING_MODEL = "nomic-embed-text"

EMBED_BATCH_SIZE = 128
CHROMA_BATCH_SIZE = 5000

EMBEDDING_FILE = "data/express_embeddings.pkl"
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "express_entry"

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(CSV_FILE)

documents = df["clean_text"].fillna("").tolist()

print(f"Loaded {len(documents):,} documents")

# ==========================================
# BUILD METADATA
# ==========================================

metadatas = []

for _, row in df.iterrows():

    metadatas.append({
        "username": str(row["username"]),
        "timestamp": str(row["timestamp"]),
        "thread_title": str(row["thread_title"]),
        "post_id": str(row["post_id"])
    })

# ==========================================
# CREATE OR LOAD EMBEDDINGS
# ==========================================

if os.path.exists(EMBEDDING_FILE):

    print("\nLoading existing embeddings...")

    with open(EMBEDDING_FILE, "rb") as f:
        embeddings = pickle.load(f)

    print("Embeddings loaded.")

else:

    print("\nGenerating embeddings...")

    embeddings = []

    for start in range(0, len(documents), EMBED_BATCH_SIZE):

        end = min(start + EMBED_BATCH_SIZE, len(documents))

        batch = documents[start:end]

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=batch
        )

        embeddings.extend(response["embeddings"])

        print(f"Embedded {end:,}/{len(documents):,}")

    print("\nSaving embeddings...")

    with open(EMBEDDING_FILE, "wb") as f:
        pickle.dump(embeddings, f)

    print("Embeddings saved.")

# ==========================================
# CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

try:
    client.delete_collection(COLLECTION_NAME)
    print("Deleted old collection.")
except:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME
)

print("\nWriting to ChromaDB...")

for start in range(0, len(documents), CHROMA_BATCH_SIZE):

    end = min(start + CHROMA_BATCH_SIZE, len(documents))

    collection.add(
        ids=[str(i) for i in range(start, end)],
        documents=documents[start:end],
        embeddings=embeddings[start:end],
        metadatas=metadatas[start:end]
    )

    print(f"Inserted {end:,}/{len(documents):,}")

print("\n===================================")
print("Finished!")
print(f"Collection size: {collection.count():,}")
print("Embeddings saved to:", EMBEDDING_FILE)
print("Database saved to:", CHROMA_PATH)
print("===================================")