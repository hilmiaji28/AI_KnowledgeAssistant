from groq import resources
import os
import psycopg2

from dotenv import load_dotenv
from collections import deque

from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from tavily import TavilyClient

# ==========================================================
# LOAD ENVIRONMENT
# ==========================================================

load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

# ==========================================================
# TAVILY SEARCH
# ==========================================================
def search_web(query):

    response = tavily.search(
        query=query,
        max_results=3
    )

    context = ""

    for item in response["results"]:

        context += f"""
Title:
{item['title']}

Content:
{item['content']}

Source:
{item['url']}

------------------
"""

    return context

# ==========================================================
# LOAD LLM
# ==========================================================

def load_llm(model_name, temperature):

    return ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=GROQ_API_KEY
    )

llm = load_llm(
    "llama-3.3-70b-versatile",
    0.2
)

# ==========================================================
# EMBEDDING MODEL
# ==========================================================

print("Loading Embedding Model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding Model Loaded")

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

print("Connecting PostgreSQL...")

print("HOST:", DB_HOST)
print("PORT:", DB_PORT)
print("DB:", DB_NAME)
print("USER:", DB_USER)
print("PASSWORD:", DB_PASSWORD)

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

register_vector(conn)

cursor = conn.cursor()

print("Database Connected")

# ==========================================================
# CHAT MEMORY
# ==========================================================

chat_history = deque(
    maxlen=10
)

# ==========================================================
# MEMORY FUNCTIONS
# ==========================================================

def add_history(role, content):

    chat_history.append(
        {
            "role": role,
            "content": content
        }
    )

def clear_history():

    chat_history.clear()

def build_history():

    if len(chat_history) == 0:
        return ""

    history_text = ""

    for item in chat_history:

        history_text += (
            f"{item['role']}: "
            f"{item['content']}\n"
        )

    return history_text

# ==========================================================
# RETRIEVAL
# ==========================================================

def retrieve_context(
    query,
    top_k=3,
    threshold=0.40
):
    if not query:
        return []

    query_embedding = (
        embedding_model
        .encode(query)
        .tolist()
    )

    cursor.execute(
        """
        SELECT
            question,
            answer,
            category,
            tags,
            1 - (
                embedding <=> %s::vector
            ) AS similarity

        FROM knowledge_base

        ORDER BY
            embedding <=> %s::vector

        LIMIT %s
        """,
        (
            query_embedding,
            query_embedding,
            top_k
        )
    )

    results = cursor.fetchall()

    filtered_results = []

    print("\n=== RETRIEVAL DEBUG ===")

    for row in results:

        similarity = row[4]

        print(
            f"Similarity: {similarity:.4f}"
        )

        if similarity >= threshold:

            filtered_results.append(row)

    print(
        f"Retrieved {len(filtered_results)} documents "
        f"(threshold={threshold})"
    )

    return filtered_results

# ==========================================================
# CONTEXT BUILDER
# ==========================================================

def build_context(results):

    context = ""

    for idx, row in enumerate(results):

        question, answer, category, tags, similarity = row

        context += f"""
DOCUMENT {idx+1}

Category:
{category}

Tags:
{tags}

Question:
{question}

Answer:
{answer}

Similarity:
{similarity:.4f}

----------------------------------------
"""

    return context



# ==========================================================
# PROMPT BUILDER
# ==========================================================

def build_prompt(
    user_question,
    context,
    history,
    source
):

    prompt = f"""
You are a helpful AI assistant.

Source:
{source}

Context:
{context}

Question:
{user_question}

Conversation History:
{history}

Retrieved Context:
{context}

Current Question:
{user_question}

Instructions:

1. Use retrieved context when relevant.
2. Use conversation history for follow-up questions.
3. If the user asks:
   - "jawabannya apa"
   - "pertanyaan terakhir apa"
   - "apa artinya"
   - "jelaskan lebih lanjut"

   refer to conversation history.

4. Only say:
   "Information is not available in the knowledge base"

   if neither history nor retrieved context can answer.
"""
    return prompt

# ==========================================================
# KNOWLEDGE BASE TOPICS
# ==========================================================

KB_TOPICS = [
    "machine learning",
    "artificial intelligence",
    "ai",
    "deep learning",
    "data science",
    "data analyst",
    "data analysis",
    "python",
    "sql",
    "statistics",
    "mlops",
    "neural network",
    "computer vision",
    "nlp",
    "programming",
    "model training",
    "feature engineering",
    "classification",
    "regression"
]

def is_kb_topic(question):

    question = question.lower()

    return any(
        topic in question
        for topic in KB_TOPICS
    )

# ==========================================================
# MEMORY HANDLER
# ==========================================================

def handle_memory_question(
    user_question,
    chat_history
):

    question = user_question.lower()

    if not chat_history:
        return None

    user_messages = [
        msg["content"]
        for msg in chat_history
        if msg["role"] == "user"
    ]

    assistant_messages = [
        msg["content"]
        for msg in chat_history
        if msg["role"] == "assistant"
    ]

    # Pertanyaan terakhir
    if any(
        keyword in question
        for keyword in [
            "pertanyaan terakhir",
            "last question",
            "apa yang saya tanyakan"
        ]
    ):

        if len(user_messages) >= 2:

            return (
                "Pertanyaan terakhir Anda adalah:\n\n"
                f"{user_messages[-2]}"
            )

        return "Belum ada pertanyaan sebelumnya."

    # Jawaban terakhir
    if any(
        keyword in question
        for keyword in [
            "jawabannya apa",
            "apa yang kamu jawab",
            "jawaban terakhir"
        ]
    ):

        if assistant_messages:

            return (
                "Jawaban terakhir saya adalah:\n\n"
                f"{assistant_messages[-1]}"
            )

        return "Belum ada jawaban sebelumnya."

    return None

# ==========================================================
# MAIN CHATBOT FUNCTION
# ==========================================================

def ask_chatbot(
    user_question,
    chat_history=None
):

    if not user_question:
        return "Please enter a valid question."

    # ==================================
    # MEMORY CHECK
    # ==================================

    memory_answer = handle_memory_question(
        user_question,
        chat_history
    )

    if memory_answer:
        return memory_answer

    # ==================================
    # LANJUT KE RAG
    # ==================================

    history_text = ""

    if chat_history:
        max_history_chars = 1500
        history_text = "\n".join(
            [
                f"{m['role']}: {m['content']}"
                for m in chat_history[-4:]
            ]
        )
        history_text = history_text[-max_history_chars:]
 
    # ==================================
    # MEMORY CHECK
    # ==================================

    memory_answer = handle_memory_question(
        user_question,
        chat_history
    )

    if memory_answer:
        return memory_answer

    # ==================================
    # TOPIC ROUTING
    # ==================================

    if not is_kb_topic(user_question):

        print(
            "Outside KB Topic -> Internet Search"
        )

        context = search_web(
            user_question
        )

        source = "web"

        docs = []

    else:

        docs = retrieve_context(
            user_question,
            top_k=3,
            threshold=0.40
        )

    if len(docs) == 0:

        print(
            "No KB Match -> Internet Search"
        )

        context = search_web(
            user_question
        )

        source = "web"

    else:

        context = build_context(
            docs
        )

        source = "knowledge_base"

    print("\n========== RETRIEVAL ==========")
    print(f"Documents Found : {len(docs)}")
    print("===============================\n")

    prompt = build_prompt(
        user_question,
        context,
        history_text,
        source 
    )

    response = llm.invoke(
        prompt
    )

    answer = response.content

    # ==================================
    # ADD SOURCE LABEL
    # ==================================

    if source == "knowledge_base":

        similarity_score = docs[0][4] if len(docs) > 0 else 0

        answer = f"""
📚 Source: Knowledge Base
🎯 Similarity: {similarity_score:.2%}

{answer}
"""

    elif source == "web":

        answer = f"""
🌐 Source: Internet Search

{answer}
"""

    # ==================================
    # SAVE HISTORY
    # ==================================

    add_history(
        "User",
        user_question
    )

    add_history(
        "Assistant",
        answer[:500]
    )

    return answer   

# ==========================================================
# DEBUG FUNCTIONS
# ==========================================================

def show_history():

    print("\n=== CHAT HISTORY ===\n")

    for item in chat_history:

        print(
            f"{item['role']}: "
            f"{item['content']}"
        )

def show_retrieval(query):

    docs = retrieve_context(
        query,
        top_k=3
    )

    print("\nTOP RETRIEVED DOCUMENTS\n")

    for idx, doc in enumerate(
        docs,
        start=1
    ):

        question, answer, category, tags, similarity = doc

        print(
            f"\nDocument {idx}"
        )

        print(
            f"Category: {category}"
        )

        print(
            f"Tags: {tags}"
        )

        print(
            f"Similarity: "
            f"{similarity:.4f}"
        )

        print(
            f"Question: "
            f"{question}"
        )

        print(
            f"Answer: "
            f"{answer[:200]}"
        )

# ==========================================================
# CLI TEST
# ==========================================================

if __name__ == "__main__":

    print("\nRAG CHATBOT READY\n")

    while True:

        question = input(
            "\nAsk Question: "
        )

        if question.lower() == "exit":
            break

        if question.lower() == "history":

            show_history()

            continue

        if question.lower().startswith(
            "debug:"
        ):

            query = question.replace(
                "debug:",
                ""
            )

            show_retrieval(
                query
            )

            continue

        answer = ask_chatbot(
            question
        )

        print("\nAnswer:\n")

        print(answer)