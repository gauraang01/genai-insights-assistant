# agent/text_to_sql_agent.py

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from chromadb import HttpClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import re

# Optional local embeddings
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    raise ImportError("Please install: poetry add langchain-openai langchain-huggingface sentence-transformers")

from .sql_validator import validate_sql
from .query_executor import run_query


# -----------------------------------------------------------
# Embeddings Helper
# -----------------------------------------------------------

def get_embeddings():
    """
    Dynamically choose embeddings based on environment.
    Ensures consistency with the semantic index.
    """
    if os.getenv("OPENAI_API_KEY"):
        print("🔑 Using OpenAI embeddings for retrieval...")
        return OpenAIEmbeddings()
    else:
        print("Using local MiniLM embeddings (offline mode)...")
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# -----------------------------------------------------------
# 🔹 Context Retrieval from Chroma
# -----------------------------------------------------------

def retrieve_context(question: str, top_k: int = 5) -> str:
    """
    Query the Chroma semantic index to retrieve relevant schema/metric context.
    """
    client = HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_HTTP_PORT", 8000)),
        tenant="default_tenant",
        database="default_database",
    )

    coll = client.get_collection("semantic_index")
    embedder = get_embeddings()
    query_embeds = embedder.embed_documents([question])

    results = coll.query(query_embeddings=query_embeds, n_results=top_k)
    docs = results.get("documents", [[]])[0]
    context_text = "\n".join(docs)

    print(f"📚 Retrieved {len(docs)} context snippets from Chroma.")
    return context_text


# -----------------------------------------------------------
# 🔹 SQL Generation via GPT
# -----------------------------------------------------------

def clean_sql_output(raw_output: str) -> str:
    """
    Cleans raw LLM output to extract only the SQL query.
    Removes markdown code fences, explanations, etc.
    """
    # Remove code fences or markdown
    raw_output = re.sub(r"```sql|```", "", raw_output, flags=re.IGNORECASE)
    raw_output = raw_output.strip()

    # Extract SQL between first SELECT and last semicolon if needed
    match = re.search(r"(SELECT.*?;)", raw_output, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_output


def generate_sql(question: str) -> str:
    """
    Generate SQL query via GPT-4 using context + template,
    clean and validate it using SQLGlot.
    """
    context = retrieve_context(question)
    prompt_template = PromptTemplate.from_file("agent/prompt_template.txt")

    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    prompt = prompt_template.format(context=context, question=question)

    # First attempt
    response = llm.invoke(prompt)
    raw_output = response.content.strip()

    print("\n🗒️ Raw model output:\n", raw_output, "\n")

    sql = clean_sql_output(raw_output)

    # Validate SQL
    if not validate_sql(sql):
        print("⚠️ SQL validation failed. Retrying with stricter prompt...")
        retry_prompt = (
            f"Return ONLY a valid SQL SELECT query for this question.\n"
            f"Question: {question}\nContext: {context}\n"
        )
        retry_response = llm.invoke(retry_prompt)
        raw_retry = retry_response.content.strip()
        sql = clean_sql_output(raw_retry)

    if not validate_sql(sql):
        raise ValueError("Generated SQL failed validation after retry")

    print("✅ SQL validation passed.")
    return sql



# -----------------------------------------------------------
# 🔹 Full Query Pipeline
# -----------------------------------------------------------

def query_agent(question: str):
    """
    Full Text-to-SQL pipeline:
    1. Retrieve semantic context
    2. Generate SQL
    3. Validate SQL
    4. Execute SQL
    5. Return dataframe
    """
    sql = generate_sql(question)
    print(f"\n Generated SQL:\n{sql}\n")

    df = run_query(sql)
    print(f"Returned {len(df)} rows.\n")
    print(df.head(5))

    # Optional: persist query logs (future Streamlit use)
    os.makedirs("logs", exist_ok=True)
    with open("logs/query_log.jsonl", "a") as f:
        f.write(json.dumps({"question": question, "sql": sql, "rows": len(df)}) + "\n")

    return df


# -----------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------

if __name__ == "__main__":
    q = input("Ask your question: ")
    query_agent(q)
