# 🇨🇦 Canadian Express Entry RAG

A Retrieval-Augmented Generation (RAG) application built on over **21,000 posts** from more than a decade of Nigerian discussions about Canada's Express Entry immigration program.

Instead of relying on a language model's internal knowledge, this application retrieves relevant discussions from a custom-built vector database and generates answers grounded in real forum conversations.

---

## Motivation

"Japa" has become one of the defining conversations in Nigeria.

Thousands of people have documented their immigration journeys online—asking questions about CRS scores, proof of funds, IELTS, work experience, provincial nominations, application refusals, and permanent residency.

Rather than manually searching thousands of forum pages, this project builds an AI assistant capable of searching and synthesizing over ten years of discussions.

---

## Features

* Custom HTML parser built specifically for Nairaland
* Cleaned corpus containing over **21,000 posts**
* Local embeddings generated using **nomic-embed-text**
* Vector search powered by **ChromaDB**
* Local inference using **Qwen2.5**
* Interactive Streamlit interface
* Source attribution for retrieved posts

---

## Tech Stack

| Component       | Technology                |
| --------------- | ------------------------- |
| Language        | Python                    |
| Parsing         | BeautifulSoup             |
| Data Analysis   | Pandas                    |
| Visualizations  | Matplotlib                |
| Embeddings      | nomic-embed-text (Ollama) |
| LLM             | Qwen2.5                   |
| Vector Database | ChromaDB                  |
| Interface       | Streamlit                 |

---

## Project Structure

```text
.
├── app.py
├── parser.py
├── embed.py
├── requirements.txt
├── README.md
├── data/
│   ├── clean_canada_express.csv
│   └── chroma_db/
└── screenshots/
```

---

## Installation

Clone the repository

```bash
git clone <repo-url>
cd express-entry-rag
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install Ollama and pull the required models

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:3b
```

Generate embeddings

```bash
python embed.py
```

Launch the application

```bash
streamlit run app.py
```

---

## Example Questions

* What advice do successful applicants give newcomers?
* What mistakes commonly lead to application refusals?
* How did category-based draws change discussions?
* What documents confuse applicants the most?
* How do people prepare for proof of funds?

---

## Dataset

* Source: Nairaland Canadian Express Entry discussions
* Posts: 21,143
* Timespan: More than 10 years
* Parsed from archived HTML pages

-

## Future Improvements

* Hybrid search (BM25 + Vector Search)
* Conversation memory
* Metadata filtering by year or thread
* Better source ranking
* Interactive analytics dashboard
* Topic modeling and sentiment analysis


---

## License

MIT License
