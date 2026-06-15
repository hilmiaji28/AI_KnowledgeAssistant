# 🤖 Hybrid Conversational RAG AI Assistant

A Hybrid Conversational Retrieval-Augmented Generation (RAG) AI Assistant built using PostgreSQL, pgvector, Sentence Transformers, ChatGroq, and Streamlit.

This project combines semantic search, conversational memory, topic-based routing, and internet search fallback to provide accurate, contextual, and reliable responses.

---

# 🚀 Features

* Semantic Search using PostgreSQL + pgvector
* Retrieval-Augmented Generation (RAG)
* Conversational Memory Handler
* Knowledge Base Topic Detection
* Similarity Threshold Filtering
* Internet Search Fallback
* Source Attribution
* Export Chat History
* Professional Streamlit Interface
* Hybrid Knowledge Base + Web Search Architecture

---

# 🎯 Project Objectives

The objective of this project is to develop a Hybrid Conversational RAG AI Assistant capable of:

* Answering questions using an internal Knowledge Base.
* Performing semantic retrieval through vector similarity search.
* Understanding conversation history and follow-up questions.
* Reducing hallucination through retrieval-based context.
* Searching the internet when information is unavailable in the Knowledge Base.
* Providing transparent source attribution.
* Delivering a user-friendly conversational experience through Streamlit.

---

# 🏗️ System Architecture

```text
User Question
       │
       ▼
Memory Handler
       │
 ┌─────┴─────┐
 │           │
 ▼           ▼
Memory     Topic Detection
Answer          │
                ▼
         Knowledge Base?
                │
      ┌─────────┴─────────┐
      │                   │
      ▼                   ▼
 PostgreSQL +       Internet Search
   pgvector               │
      │                   │
      └─────────┬─────────┘
                ▼
      Context + Chat History
                ▼
      ChatGroq (Llama 3.3)
                ▼
          Final Response
```

---

# ⚙️ Technology Stack

## Frontend

* Streamlit

## Backend

* Python
* PostgreSQL 18
* pgvector
* psycopg2

## Embedding Model

* sentence-transformers/all-MiniLM-L6-v2

## Large Language Model

* ChatGroq
* Llama 3.3 70B Versatile

## Search

* Semantic Vector Search
* Internet Search Fallback

---

# 📁 Project Structure

```text
Hybrid-RAG-AI-Assistant/
│
├── .env
├── .env.example
├── .gitignore
│
├── dataset_assignment.csv
├── knowledge_base_clean.csv
│
├── preparation.py
├── ingest.py
├── main.py
├── streamlit_app.py
│
├── requirements.txt
├── README.md
│
├── __pycache__/
└── venv/
```

---

# 🔧 Module Description

## preparation.py

Responsible for data cleaning and preprocessing.

Functions:

* Load raw dataset
* Clean and normalize records
* Handle missing values
* Prepare structured knowledge base
* Export cleaned dataset

Output:

```text
knowledge_base_clean.csv
```

---

## ingest.py

Responsible for loading the Knowledge Base into PostgreSQL and generating embeddings.

Functions:

* Read cleaned dataset
* Generate embeddings using all-MiniLM-L6-v2
* Insert records into PostgreSQL
* Store vector embeddings using pgvector

Output:

```text
9106 records inserted into PostgreSQL
```

---

## main.py

Core backend logic of the chatbot.

Functions:

* Memory handling
* Topic routing
* Semantic retrieval
* Similarity filtering
* Context building
* Internet search fallback
* Prompt generation
* LLM interaction

---

## streamlit_app.py

Frontend application built with Streamlit.

Functions:

* Chat interface
* Conversation history
* Source attribution
* Export chat
* System information dashboard
* User interaction management

---

# 📊 Knowledge Base

| Item                 | Value                 |
| -------------------- | --------------------- |
| Total Records        | 9,106                 |
| Embedding Model      | all-MiniLM-L6-v2      |
| Embedding Dimension  | 384                   |
| Vector Database      | PostgreSQL + pgvector |
| Similarity Threshold | 0.40                  |

---

# 🔄 Data Pipeline

```text
dataset_assignment.csv
          │
          ▼
    preparation.py
          │
          ▼
knowledge_base_clean.csv
          │
          ▼
       ingest.py
          │
          ▼
 PostgreSQL + pgvector
          │
          ▼
        main.py
          │
          ▼
   streamlit_app.py
```

---

# 🔄 Chatbot Workflow

### 1. User Query

The user submits a question through the Streamlit interface.

### 2. Memory Detection

The system checks whether the query is related to conversation history.

Examples:

* What was my previous question?
* What did you answer earlier?
* Pertanyaan terakhir apa?

### 3. Topic Detection

The system determines whether the query belongs to the Knowledge Base domain.

### 4. Semantic Retrieval

The query is converted into embeddings and searched against PostgreSQL using pgvector similarity search.

### 5. Similarity Filtering

A similarity threshold is applied to filter irrelevant documents.

```python
SIMILARITY_THRESHOLD = 0.40
```

### 6. Context Building

Relevant documents are transformed into context for the LLM.

### 7. Internet Search Fallback

If no relevant documents are found, the system automatically performs web search.

### 8. Response Generation

ChatGroq (Llama 3.3 70B) generates a contextual response using:

* Retrieved Context
* Conversation History
* User Question

### 9. Source Attribution

The system indicates whether the response comes from:

```text
📚 Knowledge Base
```

or

```text
🌐 Internet Search
```

---

# 🗄️ Database Setup

## Enable pgvector

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Create Table

```sql
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    question TEXT,
    answer TEXT,
    category TEXT,
    tags TEXT,
    embedding VECTOR(384)
);
```

---

# 📥 Data Ingestion

Run the ingestion pipeline:

```bash
python ingest.py
```

Expected Output:

```text
Loading Dataset...
Generating Embeddings...
Inserted Records: 9106

INGESTION COMPLETED
```

---

# ▶️ Running the Application

## Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Streamlit

```bash
streamlit run streamlit_app.py
```

Application URL:

```text
http://localhost:8501
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowledgebase
DB_USER=postgres
DB_PASSWORD=your_password

GROQ_API_KEY=your_groq_api_key
```

---

# 🌐 Deployment

Recommended deployment architecture:

## Frontend

* Streamlit Community Cloud

## Database

* Neon PostgreSQL + pgvector

## LLM

* ChatGroq

Architecture:

```text
User
 │
 ▼
Streamlit Cloud
 │
 ▼
Neon PostgreSQL + pgvector
 │
 ▼
ChatGroq API
```

---

# 📸 Example Queries

## Knowledge Base

```text
What are the steps in machine learning process?
```

---

## Follow-Up Question

```text
Apa artinya dalam bahasa Indonesia?
```

---

## Memory Question

```text
Pertanyaan terakhir apa?
```

---

## Internet Search

```text
Siapa juara dunia sepakbola tahun 2010?
```

---

# 📈 Future Improvements

* Voice Assistant (Speech-to-Text)
* Text-to-Speech Responses
* Multi-Agent Architecture
* Dynamic Document Upload
* Hybrid Search (Vector + Keyword Search)
* User Authentication
* Analytics Dashboard
* Feedback and Rating System

---

# 👨‍💻 Author

**Hilmi Aji**

Built as a Hybrid Conversational RAG AI Assistant using PostgreSQL, pgvector, Streamlit, Sentence Transformers, and ChatGroq.