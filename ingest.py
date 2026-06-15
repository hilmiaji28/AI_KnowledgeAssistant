import pandas as pd
import psycopg2
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================================
# CONFIG DATABASE
# ==========================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading Embedding Model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding Model Loaded")

# ==========================================
# CONNECT DATABASE
# ==========================================

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

cursor = conn.cursor()

print("Database Connected")

# ==========================================
# LOAD DATASET
# ==========================================

print("Loading Dataset...")

df = pd.read_csv("knowledge_base_clean.csv")

print(f"Total Records: {len(df)}")

# ==========================================
# INSERT DATA
# ==========================================

print("Generating Embeddings and Inserting Data...")

for _, row in tqdm(df.iterrows(), total=len(df)):

    text_for_embedding = f"""
    Question: {row['question']}
    Answer: {row['answer']}
    """

    embedding = embedding_model.encode(
        text_for_embedding
    ).tolist()

    cursor.execute(
        """
        INSERT INTO knowledge_base
        (
            id,
            category,
            tags,
            question,
            answer,
            embedding
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (id)
        DO NOTHING
        """,
        (
            row["id"],
            row["category"],
            row["tags"],
            row["question"],
            row["answer"],
            embedding
        )
    )

conn.commit()

print("===================================")
print("INGESTION COMPLETED")
print(f"Inserted Records: {len(df)}")
print("===================================")

cursor.close()
conn.close()