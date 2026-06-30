import streamlit as st
import chromadb
import ollama

# =====================================
# CONFIG
# =====================================

MODEL = "qwen2.5:3b"
COLLECTION_NAME = "express_entry"

# =====================================
# LOAD CHROMADB
# =====================================

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_collection(COLLECTION_NAME)

# =====================================
# PAGE
# =====================================

st.set_page_config(
    page_title="Express Entry AI",
    page_icon="🇨🇦",
    layout="wide"
)

st.title("🇨🇦 Canadian Express Entry AI")
st.caption(
    "Ask questions about 10 years of Nairaland immigration discussions."
)

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.header("Corpus")

    st.write(f"Posts: **{collection.count():,}**")
    st.write("Embedding Model: **nomic-embed-text**")
    st.write("LLM: **Qwen2.5 3B**")
    st.write("Vector DB: **ChromaDB**")

    st.divider()

    if st.button("Clear Conversation"):
        st.session_state.messages = []

# =====================================
# CHAT HISTORY
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================
# USER INPUT
# =====================================

question = st.chat_input(
    "Ask anything about Canadian Express Entry..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # =====================================
    # RETRIEVAL
    # =====================================

    query_embedding = ollama.embed(
    model="nomic-embed-text",
    input=question
    )["embeddings"][0]

    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10
)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""

    for doc, meta in zip(documents, metadatas):

        context += f"""
Username: {meta['username']}
Date: {meta['timestamp']}

{doc}

---------------------------------------
"""

    # =====================================
    # PROMPT
    # =====================================

    prompt = f"""
You are an AI research assistant.

You answer questions ONLY using archived
Nairaland discussions about Canadian
Express Entry.

Rules:

- ONLY use the supplied context.
- Look for recurring patterns.
- Summarize the discussion.
- Mention disagreements if they exist.
- Never invent information.
- If the context is insufficient,
  simply say you don't know.

Context:

{context}

Question:

{question}
"""

    # =====================================
    # GENERATE
    # =====================================

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    with st.chat_message("assistant"):

        st.markdown(answer)

        st.divider()

        st.subheader("Sources")

        for doc, meta in zip(documents, metadatas):

            with st.expander(
                f"{meta['username']} • {meta['timestamp']}"
            ):
                st.write(doc)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )