#data preparation
import pandas as pd
import re

# ==========================================================
# CATEGORY & TAG GENERATOR
# ==========================================================

def categorize_and_tag(prompt):

    prompt = str(prompt).lower()

    # Greeting
    if re.search(
    r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b", prompt):
        return "Greeting", "greeting"

    # Programming
    elif any(word in prompt for word in [
        "python",
        "java",
        "javascript",
        "code",
        "coding",
        "program",
        "function",
        "algorithm",
        "sql",
        "database"
    ]):
        return "Programming", "coding"

    # Translation
    elif any(word in prompt for word in [
        "translate",
        "translation",
        "translate to",
        "translate into"
    ]):
        return "Translation", "language"

    # Writing
    elif any(word in prompt for word in [
        "essay",
        "email",
        "letter",
        "article",
        "blog",
        "story",
        "write"
    ]):
        return "Writing Assistance", "writing"

    # Reasoning
    elif any(word in prompt for word in [
        "why",
        "how",
        "explain",
        "analysis",
        "analyze",
        "reason"
    ]):
        return "Reasoning", "analysis"

    # Conversation
    elif any(word in prompt for word in [
        "chat",
        "conversation",
        "talk"
    ]):
        return "Conversation", "dialogue"

    # Mathematics
    elif (
        re.search(
            r"\d+\s*[\+\-\*/]\s*\d+",
            prompt
        )
        or "math" in prompt
        or "mathematics" in prompt
        or "calculate" in prompt
        or "solve" in prompt
        or "equation" in prompt
    ):
        return "Mathematics", "math"

    # Default
    else:
        return "General Knowledge", "knowledge"


# ==========================================================
# LOAD DATASET
# ==========================================================

print("Loading dataset...")

df = pd.read_csv(
    "dataset_assignment.csv"
)

print(
    f"Original records: {len(df)}"
)

# ==========================================================
# DROP MISSING VALUES
# ==========================================================

df = df.dropna(
    subset=["prompt", "response"]
)

print(
    f"After removing missing values: {len(df)}"
)

# ==========================================================
# REMOVE DUPLICATES
# ==========================================================

df = df.drop_duplicates()

print(
    f"After removing duplicates: {len(df)}"
)

# ==========================================================
# TEXT NORMALIZATION
# ==========================================================

df["prompt"] = (
    df["prompt"]
    .astype(str)
    .str.lower()
    .str.strip()
)

df["response"] = (
    df["response"]
    .astype(str)
    .str.strip()
)

# ==========================================================
# GENERATE ID
# ==========================================================

df["id"] = [
    f"KB{i:05d}"
    for i in range(
        1,
        len(df) + 1
    )
]

# ==========================================================
# GENERATE CATEGORY & TAGS
# ==========================================================

df[["category", "tags"]] = (
    df["prompt"]
    .apply(
        lambda x:
        pd.Series(
            categorize_and_tag(x)
        )
    )
)

# ==========================================================
# RENAME COLUMNS
# ==========================================================

df.rename(
    columns={
        "prompt": "question",
        "response": "answer"
    },
    inplace=True
)

# ==========================================================
# REORDER COLUMNS
# ==========================================================

df = df[
    [
        "id",
        "category",
        "tags",
        "question",
        "answer"
    ]
]

# ==========================================================
# VALIDATION
# ==========================================================

print("\n=== VALIDATION ===")

print(
    "Missing Question:",
    df["question"].isna().sum()
)

print(
    "Missing Answer:",
    df["answer"].isna().sum()
)

print(
    "Missing Category:",
    df["category"].isna().sum()
)

print(
    "Missing Tags:",
    df["tags"].isna().sum()
)

print(
    "Duplicate Rows:",
    df.duplicated().sum()
)

print(
    "\nTotal Clean Records:",
    len(df)
)

# ==========================================================
# CATEGORY DISTRIBUTION
# ==========================================================

print("\n=== CATEGORY DISTRIBUTION ===")

print(
    df["category"]
    .value_counts()
)

# ==========================================================
# SAVE OUTPUT
# ==========================================================

output_file = "knowledge_base_clean.csv"

df.to_csv(
    output_file,
    index=False
)

print(
    f"\nKnowledge Base saved to: {output_file}"
)

print("\nSample Data:\n")

print(df.head()) 